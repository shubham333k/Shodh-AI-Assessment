from __future__ import annotations

def classify(mismatch: dict) -> str:
    expected = mismatch.get("expected_route")
    actual = mismatch.get("actual_route")
    if actual == "NO_ROUTE": return "MISSING_BRANCH"
    if actual == "ERROR": return "CODE_DISAGREEMENT"
    if mismatch.get("expected_by") and mismatch.get("actual_by") and expected != actual:
        return "BEHAVIOUR_MISMATCH"
    return "UNCLASSIFIED_BEHAVIOUR_MISMATCH"
