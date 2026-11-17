from __future__ import annotations
from fractions import Fraction
from typing import Any, Iterable
from .cond_ast import *
from .units import normalise_time

def is_missing(ticket: dict[str, Any], field: str) -> bool:
    value = ticket.get(field)
    return value is None or (isinstance(value, str) and not value.strip())

def evaluate(cond: Cond, ticket: dict[str, Any]) -> bool:
    if isinstance(cond, TrueCond): return True
    if isinstance(cond, IsMissing): return is_missing(ticket, cond.field)
    if isinstance(cond, IsPresent): return not is_missing(ticket, cond.field)
    if isinstance(cond, And): return all(evaluate(x, ticket) for x in cond.args)
    if isinstance(cond, Or): return any(evaluate(x, ticket) for x in cond.args)
    if isinstance(cond, In): return not is_missing(ticket, cond.field) and ticket.get(cond.field) in cond.values
    if isinstance(cond, Eq): return not is_missing(ticket, cond.field) and ticket.get(cond.field) == cond.value
    if isinstance(cond, Cmp):
        if is_missing(ticket, cond.field): return False
        raw = ticket[cond.field]
        actual = normalise_time(raw, cond.unit) if cond.unit else Fraction(str(raw))
        if cond.cmp == ">=": return actual >= cond.value
        if cond.cmp == ">": return actual > cond.value
        if cond.cmp == "<=": return actual <= cond.value
        if cond.cmp == "<": return actual < cond.value
        if cond.cmp == "==": return actual == cond.value
    raise TypeError(f"unknown condition: {cond!r}")

def route_of(rules: Iterable[dict[str, Any]], ticket: dict[str, Any]):
    for rule in sorted(rules, key=lambda r: r.get("order", 0)):
        cond = rule["condition"] if isinstance(rule["condition"], Cond) else cond_from_dict(rule["condition"])
        if evaluate(cond, ticket): return rule.get("route", "ERROR"), rule.get("id")
    return "NO_ROUTE", None
