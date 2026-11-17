from __future__ import annotations
from ..lang.cond_ast import cond_from_dict, TrueCond
from ..lang.evaluator import evaluate

def route_workflow(workflow: dict, ticket: dict):
    nodes = {node["id"]: node for node in workflow.get("nodes", [])}
    current = next((n for n in nodes.values() if n.get("type") == "start" or n.get("id") == "start"), None)
    if current is None: return "NO_ROUTE", None, "missing start node"
    seen = set()
    while current:
        if current["id"] in seen: return "ERROR", current["id"], "CYCLE"
        seen.add(current["id"])
        if current.get("type") == "terminal": return current.get("route", "ERROR"), current["id"], None
        branches = {b.get("label"): b.get("to") for b in current.get("branches", [])}
        cond = current.get("condition")
        if cond is None:
            target = branches.get("true") or current.get("to")
        else:
            condition = cond_from_dict(cond) if isinstance(cond, dict) else cond
            target = branches.get("true" if evaluate(condition, ticket) else "false")
        if not target or target not in nodes: return "NO_ROUTE", current["id"], "missing branch"
        current = nodes[target]
    return "NO_ROUTE", None, "workflow ended without terminal"
