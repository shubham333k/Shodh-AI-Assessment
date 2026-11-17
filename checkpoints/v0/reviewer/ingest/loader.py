from __future__ import annotations
import hashlib, json, re
from pathlib import Path
from typing import Any
from ..lang.nl_parser import parse_requirement

class BundleError(ValueError): pass

def content_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def _json(path: Path):
    try: return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc: raise BundleError(f"{path.name}: invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}") from exc

def load_bundle(path: str | Path) -> dict[str, Any]:
    root = Path(path)
    manifest = _json(root / "bundle.json")
    result: dict[str, Any] = {"root": root, "manifest": manifest, "hashes": {}}
    for name in ("requirements.v1.md", "approvals.json"):
        file = root / name
        if file.exists(): result["hashes"][name] = content_hash(file)
    req_file = root / f"requirements.{manifest.get('review_target', {}).get('requirements_version', 'v1')}.md"
    if not req_file.exists(): req_file = root / "requirements.v1.md"
    requirements = []
    for line_no, line in enumerate(req_file.read_text(encoding="utf-8").splitlines(), 1):
        m = re.match(r"\s*\[(REQ-[^\]]+)\]\s*(.*)", line)
        if not m: continue
        parsed = parse_requirement(m.group(2))
        requirements.append({"anchor": m.group(1), "text": m.group(2), "line_span": f"L{line_no}", "parse_status": parsed.status, "parse_reason": parsed.reason, "rule": parsed})
    result["requirements"] = requirements
    for key in ("spec", "workflow", "approvals"):
        file = root / f"{key}.v1.json"
        if not file.exists(): file = root / f"{key}.json"
        if file.exists(): result[key] = _json(file); result["hashes"][file.name] = content_hash(file)
        else: result[key] = {} if key != "approvals" else []
    result["snippets"] = list((root / "snippets").glob("*.py")) if (root / "snippets").exists() else []
    return result
