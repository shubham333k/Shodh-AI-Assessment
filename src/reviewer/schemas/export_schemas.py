from __future__ import annotations
import json
from pathlib import Path
from .models import ReviewReport, Finding, Coverage

def export(directory: str | Path):
    target = Path(directory); target.mkdir(parents=True, exist_ok=True)
    for model in (ReviewReport, Finding, Coverage):
        (target / f"{model.__name__}.json").write_text(json.dumps(model.model_json_schema(), indent=2), encoding="utf-8")
