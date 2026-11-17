from __future__ import annotations
from .status import decide
from ..schemas.models import ReviewReport, Coverage, Check, Finding

def build_report(bundle_id, findings=None, coverage=None, checks=None, provenance=None, resources=None, cache=None):
    findings = findings or []
    coverage = coverage or Coverage()
    checks = checks or []
    status = decide(findings, coverage, [x.model_dump() if hasattr(x, "model_dump") else x for x in checks])
    return ReviewReport(bundle_id=bundle_id, status=status, summary={"PASS": "All reviewed artifacts agree.", "CHANGES_REQUIRED": "Deterministic evidence found behavior changes.", "INCOMPLETE": "The review has unreviewed or ambiguous scope."}[status], findings=findings, coverage=coverage, checks=checks, provenance=provenance or {}, resources=resources or {}, cache=cache or {})
