from __future__ import annotations
import json

def validate_response(raw: str, known_refs: set[str], max_findings: int = 100):
    try: data = json.loads(raw)
    except json.JSONDecodeError as exc: return {"ok": False, "reason": f"malformed JSON: {exc.msg}", "findings": []}
    if not isinstance(data, dict) or not isinstance(data.get("findings", []), list): return {"ok": False, "reason": "response must be an object with a findings list", "findings": []}
    clean, dropped = [], 0
    for finding in data["findings"][:max_findings]:
        if not isinstance(finding, dict): dropped += 1; continue
        ref = finding.get("rule_ref")
        if ref is not None and ref not in known_refs: dropped += 1; continue
        clean.append(finding)
    return {"ok": True, "reason": None, "findings": clean, "dropped": dropped}
