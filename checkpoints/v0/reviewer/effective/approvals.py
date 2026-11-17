from __future__ import annotations
from dataclasses import dataclass
from typing import Any

@dataclass
class ApprovalConflict:
    anchor: str
    field: str
    approval_ids: list[str]
    reason: str

def derive_value(original: Any, anchor: str, field: str, approvals: list[dict[str, Any]]):
    applicable = [a for a in approvals if a.get("status") == "approved" and a.get("target", {}).get("anchor") == anchor and a.get("target", {}).get("field") == field]
    applicable.sort(key=lambda x: (x.get("seq", 0), x.get("id", "")))
    current, applied = original, []
    for item in applicable:
        supersedes = set(item.get("supersedes", []))
        if any(x.get("seq", 0) == item.get("seq", 0) and x.get("to") != item.get("to") and x.get("id") not in supersedes for x in applicable if x is not item):
            return original, applied, ApprovalConflict(anchor, field, [x["id"] for x in applicable], "approved changes conflict at the same sequence")
        if item.get("from") != current and not (supersedes & set(applied)):
            return original, applied, ApprovalConflict(anchor, field, [item["id"]], "approval chain does not match the current value")
        current = item.get("to"); applied.append(item["id"])
    return current, applied, None
