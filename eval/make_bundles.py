"""Generate the fixed development and held-out routing corpus.

This file only writes artifact inputs. The reviewer never imports it.
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

BASE_REQ = [
    ("REQ-1", "If category is missing, route to manual_review."),
    ("REQ-2", "If the ticket is urgent, route to priority_queue."),
    ("REQ-3", "If waiting time is at least {threshold} minutes, route to escalation."),
    ("REQ-4", "All remaining tickets go to normal_queue."),
]

def rules(threshold="30", op=">=", unit="minutes", order=None, vip=False, security=False):
    output = [
        {"id": "r1", "order": 1, "implements": ["REQ-1"], "condition": {"op": "is_missing", "field": "category"}, "route": "manual_review"},
        {"id": "r2", "order": 2, "implements": ["REQ-2"], "condition": {"op": "eq", "field": "urgent", "value": True}, "route": "priority_queue"},
        {"id": "r3", "order": 3, "implements": ["REQ-3"], "condition": {"op": "cmp", "field": "waiting_time", "cmp": op, "value": {"n": threshold, "unit": unit}}, "route": "escalation"},
    ]
    if vip:
        output.append({"id": "r5", "order": 4, "implements": ["REQ-5"], "condition": {"op": "and", "args": [{"op": "eq", "field": "customer_tier", "value": "vip"}, {"op": "cmp", "field": "waiting_time", "cmp": ">=", "value": {"n": "15", "unit": "minutes"}}]}, "route": "escalation"})
    if security:
        output.append({"id": "r6", "order": 5, "implements": ["REQ-6"], "condition": {"op": "and", "args": [{"op": "eq", "field": "urgent", "value": True}, {"op": "eq", "field": "category", "value": "security"}]}, "route": "security_queue"})
    output.append({"id": "r4", "order": 99, "implements": ["REQ-4"], "condition": {"op": "true"}, "route": "normal_queue"})
    if order:
        for item in output: item["order"] = order.get(item["id"], item["order"])
    return output

def requirements(threshold="30", vip=False, security=False, unsupported=False):
    lines = [f"[{anchor}] {text.format(threshold=threshold)}" for anchor, text in BASE_REQ[:3]]
    if vip: lines.append("[REQ-5] If customer tier is vip and waiting time is at least 15 minutes, route to escalation.")
    if security: lines.append("[REQ-6] If urgent and category is security, route to security_queue.")
    if unsupported: lines.append("[REQ-7] Generally escalate unusual enterprise histories.")
    lines.append(f"[{BASE_REQ[3][0]}] {BASE_REQ[3][1]}")
    return "\n".join(lines) + "\n"

def make_bundle(bundle_id, *, threshold="30", spec_threshold=None, op=">=", unit="minutes", vip=False, spec_vip=None, security=False, unsupported=False, spec_order=None, workflow_swap=False, dangling=False, approval=None, model=None):
    root = ROOT / "data" / "bundles" / bundle_id
    (root / "snippets").mkdir(parents=True, exist_ok=True)
    (root / "bundle.json").write_text(json.dumps({"bundle_id": bundle_id, "review_target": {"requirements_version": "v1", "spec_version": "v1"}, "config": {"model": model or {"mode": "none"}}}, indent=2), encoding="utf-8")
    (root / "requirements.v1.md").write_text(requirements(threshold, vip, security, unsupported), encoding="utf-8")
    spec = rules(spec_threshold or threshold, op, unit, spec_order, vip if spec_vip is None else spec_vip, security)
    if workflow_swap:
        spec[2]["route"] = "normal_queue"
        spec[-1]["route"] = "escalation"
    (root / "spec.v1.json").write_text(json.dumps({"rules": spec}, indent=2), encoding="utf-8")
    approvals = [] if approval is None else approval
    (root / "approvals.json").write_text(json.dumps(approvals, indent=2), encoding="utf-8")
    if dangling:
        (root / "workflow.v1.json").write_text(json.dumps({"nodes": [{"id": "start", "type": "start", "branches": [{"label": "true", "to": "missing"}]}]}, indent=2), encoding="utf-8")
    else:
        nodes = [{"id": "start", "type": "start", "branches": [{"label": "true", "to": "d1"}]}]
        for index, item in enumerate(spec):
            decision = f"d{index + 1}"; terminal = f"t{index + 1}"; next_id = f"d{index + 2}" if index + 1 < len(spec) else terminal
            nodes.append({"id": decision, "type": "decision", "condition": item["condition"], "branches": [{"label": "true", "to": terminal}, {"label": "false", "to": next_id}]})
            nodes.append({"id": terminal, "type": "terminal", "route": item["route"]})
        if workflow_swap and len(spec) >= 3:
            branches = nodes[3]["branches"]
            branches[0]["to"], branches[1]["to"] = branches[1]["to"], branches[0]["to"]
        (root / "workflow.v1.json").write_text(json.dumps({"nodes": nodes}, indent=2), encoding="utf-8")
    code_threshold = spec_threshold or threshold
    extra_vip = '    elif ticket.get("customer_tier") == "vip" and ticket.get("waiting_time") is not None and ticket.get("waiting_time") >= 15:\n        return "escalation"\n' if vip else ''
    extra_security = '    elif ticket.get("urgent") is True and ticket.get("category") == "security":\n        return "security_queue"\n' if security else ''
    code = f'''def route(ticket):
    if ticket.get("category") is None:
        return "manual_review"
    elif ticket.get("urgent") is True:
        return "priority_queue"
{extra_vip}{extra_security}    elif ticket.get("waiting_time") is not None and ticket.get("waiting_time") {op} {code_threshold}:
        return "escalation"
    else:
        return "normal_queue"
'''
    if bundle_id == "H02": code = code.replace(str(code_threshold), "35")
    (root / "snippets" / "route_v1.py").write_text(code, encoding="utf-8")

def main():
    configs = {
        "D01": {}, "D02": {}, "D03": {"threshold": "25", "spec_threshold": "25", "approval": [{"id": "AP-1", "target": {"doc": "requirements", "version": "v1", "anchor": "REQ-3", "field": "threshold"}, "from": "30", "to": "25", "status": "approved", "seq": 1}]}, "D04": {},
        "D05": {"op": ">"}, "D06": {"threshold": "30", "spec_threshold": "25"}, "D07": {"spec_order": {"r1": 2, "r2": 1}},
        "D08": {"unit": "hours"}, "D09": {"vip": True, "spec_vip": False}, "D10": {"threshold": "30", "spec_threshold": "30", "approval": [{"id": "AP-1", "target": {"doc": "requirements", "version": "v1", "anchor": "REQ-3", "field": "threshold"}, "from": "30", "to": "25", "status": "approved", "seq": 1}, {"id": "AP-2", "target": {"doc": "requirements", "version": "v1", "anchor": "REQ-3", "field": "threshold"}, "from": "30", "to": "20", "status": "approved", "seq": 1}]},
        "D11": {"unsupported": True}, "D12": {"model": {"mode": "fake", "script": "timeout"}}, "H01": {"workflow_swap": True}, "H02": {"spec_threshold": "35"},
        "H03": {"vip": True, "security": True, "spec_order": {"r5": 2, "r2": 3, "r6": 4}}, "H04": {"threshold": "25", "spec_threshold": "25", "vip": True},
        "H05": {"dangling": True},
    }
    for bundle_id, config in configs.items(): make_bundle(bundle_id, **config)

if __name__ == "__main__": main()
