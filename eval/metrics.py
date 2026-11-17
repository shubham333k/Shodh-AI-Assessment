from __future__ import annotations
from collections import Counter

def summarize(reports: dict, labels: dict):
    confusion = Counter()
    correct = 0
    for bundle_id, report in reports.items():
        expected = labels[bundle_id]["status"]
        actual = report["status"]
        confusion[(expected, actual)] += 1
        correct += expected == actual
    return {"bundles": len(reports), "decision_correct": correct, "decision_accuracy": correct / len(reports) if reports else 0, "confusion": {f"{a}->{b}": n for (a, b), n in confusion.items()}}
