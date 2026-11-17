from __future__ import annotations

def decide(findings, coverage, checks):
    def val(obj, name, default=None):
        return getattr(obj, name, default) if not isinstance(obj, dict) else obj.get(name, default)
    blockers = [f for f in findings if val(f, "severity") == "BLOCKER" and val(f, "verification") in ("exhaustive", "static") and val(f, "source", "deterministic") == "deterministic"]
    if blockers: return "CHANGES_REQUIRED"
    unsupported = val(coverage, "unsupported", [])
    ambiguous = val(coverage, "ambiguous", [])
    conflicts = val(coverage, "approval_conflicts", [])
    unreviewed = val(coverage, "unreviewed", [])
    mode = val(coverage, "verification_mode", "exhaustive")
    if unsupported or ambiguous or conflicts or unreviewed or mode != "exhaustive" or any(c.get("required", True) and c.get("outcome") in ("failed", "error", "skipped") for c in checks): return "INCOMPLETE"
    return "PASS"
