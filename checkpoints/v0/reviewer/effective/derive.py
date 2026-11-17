from __future__ import annotations
from .approvals import derive_value

def effective_requirements(requirements, approvals, version="v1"):
    output, conflicts, not_applicable = [], [], []
    for req in requirements:
        item = dict(req)
        if req.get("parse_status") != "PARSED": output.append(item); continue
        rule = req["rule"]
        # Approval fields are represented as explicit target changes; the parser's AST remains immutable.
        changes = [a for a in approvals if a.get("target", {}).get("anchor") == req["anchor"]]
        for a in approvals:
            if a.get("target", {}).get("anchor") == req["anchor"] and a.get("target", {}).get("version") != version:
                not_applicable.append({"approval": a.get("id"), "reason": "wrong_version"})
        for change in changes:
            field = change.get("target", {}).get("field")
            if field == "threshold":
                value, applied, conflict = derive_value(None, req["anchor"], field, [x for x in changes if x.get("target", {}).get("version") == version])
                if conflict: conflicts.append(conflict.__dict__)
                item.setdefault("provenance", {})[field] = {"value": value, "applied": applied}
        output.append(item)
    return output, conflicts, not_applicable
