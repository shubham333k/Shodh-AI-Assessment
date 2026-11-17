from __future__ import annotations
import argparse, json
from pathlib import Path
from reviewer.cli import review
from .metrics import summarize

ROOT = Path(__file__).resolve().parents[1]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--impl", choices=("v0", "final"), default="final")
    parser.add_argument("--set", choices=("all", "dev", "heldout"), default="all")
    parser.add_argument("--out", default="results/final")
    args = parser.parse_args()
    labels = json.loads((ROOT / "data/labels/expected.json").read_text())
    ids = list(labels)
    if args.set == "dev": ids = [x for x in ids if x.startswith("D")]
    if args.set == "heldout": ids = [x for x in ids if x.startswith("H")]
    out = ROOT / args.out; out.mkdir(parents=True, exist_ok=True)
    reports = {}
    for bundle_id in ids:
        target = out / f"{bundle_id}.json"
        review(ROOT / "data/bundles" / bundle_id, target, "none")
        reports[bundle_id] = json.loads(target.read_text(encoding="utf-8"))
    metrics = summarize(reports, labels)
    (out / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(json.dumps(metrics, indent=2))

if __name__ == "__main__": main()
