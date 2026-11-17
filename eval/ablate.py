from __future__ import annotations
import argparse, json
from pathlib import Path
from .run_eval import ROOT
from reviewer.cli import review
from .metrics import summarize

def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--name", default="sampled_vs_exhaustive"); parser.add_argument("--out", default="results/ablation"); args = parser.parse_args()
    out = ROOT / args.out; out.mkdir(parents=True, exist_ok=True)
    labels = json.loads((ROOT / "data/labels/expected.json").read_text())
    reports = {}
    for bundle_id in labels:
        target = out / f"{bundle_id}.json"
        review(ROOT / "data/bundles" / bundle_id, target, "none", verification_mode="sampled")
        reports[bundle_id] = json.loads(target.read_text(encoding="utf-8"))
    result = {"name": args.name, "seed": 7, "samples": 50, "verification": "sampled", "metrics": summarize(reports, labels)}
    (out / "metrics.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))

if __name__ == "__main__": main()
