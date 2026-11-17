from __future__ import annotations
from .domain import partition_tickets
from ..lang.evaluator import route_of

def compare(requirement_rules, actual_rules, fields, constants=None, mode="exhaustive", samples=50, seed=7):
    tickets, mode = partition_tickets(fields, constants, mode=mode, samples=samples, seed=seed)
    mismatches = []
    for ticket in tickets:
        expected, expected_by = route_of(requirement_rules, ticket)
        actual, actual_by = route_of(actual_rules, ticket)
        if expected != actual: mismatches.append({"ticket": ticket, "expected_route": expected, "expected_by": expected_by, "actual_route": actual, "actual_by": actual_by})
    return mismatches, mode
