from __future__ import annotations
import ast
from dataclasses import dataclass
from typing import Any
from ..lang.cond_ast import *

@dataclass
class ParsedCode:
    rules: list[dict[str, Any]]
    status: str = "PARSED"
    reason: str | None = None

def _value(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (str, int, float, bool)): return node.value
    if isinstance(node, (ast.List, ast.Tuple)) and all(isinstance(x, ast.Constant) and isinstance(x.value, str) for x in node.elts): return [x.value for x in node.elts]
    raise ValueError("only literal values are supported")

def _condition(node):
    if isinstance(node, ast.BoolOp):
        cls = And if isinstance(node.op, ast.And) else Or
        return cls(tuple(_condition(x) for x in node.values))
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not): raise ValueError("not expressions require a normalized atom")
    if isinstance(node, ast.Compare) and len(node.ops) == 1:
        left, op, right = node.left, node.ops[0], node.comparators[0]
        if isinstance(left, ast.Subscript) and isinstance(left.value, ast.Name) and left.value.id == "ticket":
            field = _value(left.slice)
        elif isinstance(left, ast.Call) and isinstance(left.func, ast.Attribute) and left.func.attr == "get": field = _value(left.args[0])
        else: raise ValueError("condition must read ticket[field]")
        value = _value(right) if not isinstance(right, ast.Constant) or right.value is not None else None
        ops = {ast.Eq: "==", ast.NotEq: "!=", ast.Lt: "<", ast.LtE: "<=", ast.Gt: ">", ast.GtE: ">="}
        if isinstance(op, ast.Is) and isinstance(right, ast.Constant) and isinstance(right.value, bool): return Eq(field, right.value)
        if isinstance(op, ast.Is): return IsMissing(field)
        if isinstance(op, ast.IsNot): return IsPresent(field)
        if isinstance(op, ast.In): return In(field, tuple(value))
        if isinstance(op, ast.Eq): return Eq(field, value)
        if type(op) not in ops: raise ValueError("unsupported comparison")
        if value is None: raise ValueError("None is only supported with is/is not")
        if ops[type(op)] == "!=": raise ValueError("!= is not supported in the normalized subset")
        return Cmp(field, ops[type(op)], __import__('fractions').Fraction(str(value)))
    raise ValueError("unsupported condition")

def parse_snippet(source: str) -> ParsedCode:
    try:
        tree = ast.parse(source)
        funcs = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "route"]
        if len(funcs) != 1 or len(tree.body) != 1: raise ValueError("source must contain exactly def route(ticket)")
        def walk(nodes):
            rules = []
            for node in nodes:
                if isinstance(node, ast.If):
                    route = node.body[0].value.value if node.body and isinstance(node.body[0], ast.Return) and isinstance(node.body[0].value, ast.Constant) else None
                    if route is None: raise ValueError("branches must return string literals")
                    rules.append({"id": f"code:{node.lineno}", "order": node.lineno, "condition": _condition(node.test), "route": route})
                    if node.orelse:
                        if isinstance(node.orelse[0], ast.If): rules.extend(walk(node.orelse))
                        elif isinstance(node.orelse[0], ast.Return) and isinstance(node.orelse[0].value, ast.Constant): rules.append({"id": f"code:{node.orelse[0].lineno}", "order": node.orelse[0].lineno, "condition": TrueCond(), "route": node.orelse[0].value.value})
                    return rules
            raise ValueError("route must contain if/elif/else")
        return ParsedCode(walk(funcs[0].body))
    except (SyntaxError, ValueError, KeyError, TypeError) as exc:
        return ParsedCode([], "UNSUPPORTED", str(exc))
