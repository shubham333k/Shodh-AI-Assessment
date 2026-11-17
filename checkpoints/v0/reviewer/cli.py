from __future__ import annotations
import argparse, json, subprocess, sys
from pathlib import Path
from .ingest.loader import load_bundle
from .checks.equivalence import compare
from .checks.classify import classify
from .checks.domain import partition_tickets
from .workflow.graph import route_workflow
from .code.py_subset import parse_snippet
from .lang.cond_ast import cond_from_dict
from .lang.evaluator import route_of
from .model.validate import validate_response
from .model.prompt import build_prompt
from .report.builder import build_report
from .schemas.models import Coverage, Check, Finding
from .report.cache import cache_key

def _rules(raw):
    return [{**r, "condition": cond_from_dict(r["condition"]) if isinstance(r.get("condition"), dict) else r["condition"]} for r in raw.get("rules", [])]

def _collect_constants(rule_list):
    values = {"waiting_time": set()}
    def visit(condition):
        if getattr(condition, "field", None) == "waiting_time" and hasattr(condition, "value"):
            values["waiting_time"].add(condition.value)
        for child in getattr(condition, "args", ()):
            visit(child)
    for rule in rule_list: visit(rule.get("condition"))
    return values

def _fields():
    return {"category": {"type": "enum", "values": ["billing", "technical", "security", "other"]}, "urgent": {"type": "bool"}, "waiting_time": {"type": "number"}, "customer_tier": {"type": "enum", "values": ["standard", "vip"]}}

def review(bundle_path, out, model="none", no_cache=False, fake_script=None, verification_mode="exhaustive"):
    bundle = load_bundle(bundle_path); coverage = Coverage(requirements_total=len(bundle["requirements"]))
    configured_model = model if model != "none" else bundle.get("manifest", {}).get("config", {}).get("model", {}).get("mode", "none")
    cache_payload = {"hashes": bundle["hashes"], "model": configured_model, "verification": verification_mode, "reviewer_version": "0.2.0"}
    cache_id = cache_key(cache_payload)
    if not no_cache and Path(out).exists():
        try:
            cached = json.loads(Path(out).read_text(encoding="utf-8"))
            if cached.get("cache", {}).get("key") == cache_id:
                cached["cache"]["hit"] = True
                Path(out).write_text(json.dumps(cached, indent=2), encoding="utf-8")
                from .schemas.models import ReviewReport
                return ReviewReport.model_validate(cached)
        except (OSError, ValueError, TypeError):
            pass
    approvals = bundle.get("approvals", []); by_target = {}
    for approval in approvals:
        target = approval.get("target", {}); key = (target.get("anchor"), target.get("field"), approval.get("seq", 0)); by_target.setdefault(key, []).append(approval)
    for key, records in by_target.items():
        if len({record.get("to") for record in records}) > 1: coverage.approval_conflicts.append({"target": key[0], "field": key[1], "approval_ids": [r.get("id") for r in records], "reason": "same-sequence approved changes disagree"})
    req_rules = []
    for req in bundle["requirements"]:
        if req["parse_status"] == "PARSED":
            parsed = req["rule"]; req_rules.append({"id": req["anchor"], "order": len(req_rules), "condition": parsed.condition, "route": parsed.route}); coverage.requirements_reviewed += 1
        else:
            entry = {"anchor": req["anchor"], "location": req["line_span"], "reason": req["parse_reason"]}; (coverage.ambiguous if req["parse_status"] == "AMBIGUOUS" else coverage.unsupported).append(entry)
    spec_rules = _rules(bundle.get("spec", {})); fields = _fields(); constants = _collect_constants(req_rules + spec_rules)
    mismatches, mode = compare(req_rules, spec_rules, fields, constants, mode=verification_mode); coverage.verification_mode = mode
    findings = []
    for mismatch in mismatches[:200]: findings.append(Finding(id=f"F-{len(findings)+1:03d}", severity="BLOCKER", category=classify(mismatch), artifact="spec", location=f"/rules/{mismatch['actual_by']}", counterexample=mismatch, correction="Make the reviewed artifact agree with the effective requirement.", verification=mode))
    checks = [Check(name="spec_equivalence", outcome="passed" if not mismatches else "failed", mode=mode, details=f"{len(mismatches)} counterexamples")]
    workflow = bundle.get("workflow", {})
    if workflow.get("nodes"):
        node_ids = {node.get("id") for node in workflow["nodes"]}
        for node in workflow["nodes"]:
            for branch in node.get("branches", []):
                if branch.get("to") not in node_ids: coverage.unreviewed.append({"artifact": "workflow", "location": f"/nodes/{node.get('id')}/branches", "reason": "dangling workflow target"})
        tickets, workflow_mode = partition_tickets(fields, _collect_constants(req_rules), mode=verification_mode); workflow_mismatches = []
        for ticket in tickets:
            expected, expected_by = route_of(req_rules, ticket); actual, actual_by, reason = route_workflow(workflow, ticket)
            if expected != actual: workflow_mismatches.append({"ticket": ticket, "expected_route": expected, "expected_by": expected_by, "actual_route": actual, "actual_by": actual_by, "reason": reason})
        for mismatch in workflow_mismatches[:200]:
            if mismatch.get("reason") is not None: continue
            findings.append(Finding(id=f"F-{len(findings)+1:03d}", severity="BLOCKER", category="WRONG_BRANCH", artifact="workflow", location=f"/nodes/{mismatch['actual_by']}", counterexample=mismatch, verification=workflow_mode, correction="Repair the workflow branch or terminal route."))
        checks.append(Check(name="workflow_equivalence", outcome="passed" if not workflow_mismatches else "failed", mode=workflow_mode, details=f"{len(workflow_mismatches)} counterexamples"))
    for snippet in bundle.get("snippets", []):
        parsed = parse_snippet(snippet.read_text(encoding="utf-8"))
        if parsed.status != "PARSED":
            coverage.unreviewed.append({"artifact": "code", "location": snippet.name, "reason": parsed.reason}); checks.append(Check(name="code_syntax", outcome="error", mode="static", details=parsed.reason or "unsupported Python subset")); continue
        code_mismatches, code_mode = compare(req_rules, parsed.rules, fields, _collect_constants(req_rules + parsed.rules), mode=verification_mode)
        for mismatch in code_mismatches[:200]: findings.append(Finding(id=f"F-{len(findings)+1:03d}", severity="BLOCKER", category="CODE_DISAGREEMENT", artifact="code", location=snippet.name, counterexample=mismatch, verification=code_mode, correction="Align the interpreted snippet with the requirement."))
        checks.append(Check(name="code_equivalence", outcome="passed" if not code_mismatches else "failed", mode=code_mode, details=f"{len(code_mismatches)} counterexamples"))
    model_config = bundle.get("manifest", {}).get("config", {}).get("model", {}); configured_mode = configured_model; configured_script = fake_script or model_config.get("script", "ok")
    model_calls = 0; model_retries = 0; model_findings = []
    if configured_mode in ("fake", "real"):
        try:
            if configured_mode == "fake":
                from .model.fake import FakeClient; client = FakeClient(configured_script)
            else:
                from .model.real import RealClient; client = RealClient()
            raw = None
            for _ in range(3):
                try: raw = client.review(build_prompt(f"bundle={bundle['manifest'].get('bundle_id')}")); model_calls += 1; break
                except Exception: model_retries += 1
            if raw is None: raise TimeoutError("model request exhausted bounded retries")
            validated = validate_response(raw, {req["anchor"] for req in bundle["requirements"]})
            if not validated["ok"]: raise ValueError(validated["reason"])
            model_findings = validated["findings"]; checks.append(Check(name="model_advisory", outcome="passed", mode="unverified", details=f"dropped={validated.get('dropped', 0)}"))
        except Exception as exc: checks.append(Check(name="model_advisory", outcome="error", mode="unverified", details=str(exc)))
    report = build_report(bundle["manifest"].get("bundle_id", Path(bundle_path).name), findings, coverage, checks, {"client_kind": configured_mode, "model_findings": model_findings}, {"model_calls": model_calls, "retries": model_retries}, {"key": cache_id, "hit": False})
    Path(out).write_text(json.dumps(report.model_dump(mode="python"), indent=2, default=str), encoding="utf-8"); return report

def main():
    parser = argparse.ArgumentParser(prog="reviewer"); sub = parser.add_subparsers(dest="command", required=True)
    review_cmd = sub.add_parser("review"); review_cmd.add_argument("bundle"); review_cmd.add_argument("--model", default="none"); review_cmd.add_argument("--out", required=True); review_cmd.add_argument("--no-cache", action="store_true"); review_cmd.add_argument("--fake-script", default=None); review_cmd.add_argument("--verification", choices=("exhaustive", "sampled"), default="exhaustive")
    eval_cmd = sub.add_parser("eval"); eval_cmd.add_argument("--impl", default="final"); eval_cmd.add_argument("--set", default="all"); eval_cmd.add_argument("--out", default="results/final")
    ablate_cmd = sub.add_parser("ablate"); ablate_cmd.add_argument("--name", default="sampled_vs_exhaustive"); ablate_cmd.add_argument("--out", default="results/ablation")
    schema_cmd = sub.add_parser("schema"); schema_cmd.add_argument("--export", default="schemas"); args = parser.parse_args()
    if args.command == "review": print(json.dumps(review(args.bundle, args.out, args.model, args.no_cache, args.fake_script, args.verification).model_dump(mode="python"), indent=2, default=str))
    elif args.command == "eval": subprocess.run([sys.executable, "-m", "eval.run_eval", "--impl", args.impl, "--set", args.set, "--out", args.out], check=True)
    elif args.command == "ablate": subprocess.run([sys.executable, "-m", "eval.ablate", "--name", args.name, "--out", args.out], check=True)
    elif args.command == "schema":
        from .schemas.export_schemas import export; export(args.export)

if __name__ == "__main__": main()
