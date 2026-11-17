from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction
from typing import Any

class Cond:
    def to_dict(self) -> dict[str, Any]: raise NotImplementedError

@dataclass(frozen=True)
class TrueCond(Cond):
    def to_dict(self): return {"op": "true"}

@dataclass(frozen=True)
class IsMissing(Cond):
    field: str
    def to_dict(self): return {"op": "is_missing", "field": self.field}

@dataclass(frozen=True)
class IsPresent(Cond):
    field: str
    def to_dict(self): return {"op": "is_present", "field": self.field}

@dataclass(frozen=True)
class Cmp(Cond):
    field: str
    cmp: str
    value: Fraction
    unit: str | None = None
    def to_dict(self): return {"op": "cmp", "field": self.field, "cmp": self.cmp, "value": {"n": str(self.value), "unit": self.unit}}

@dataclass(frozen=True)
class In(Cond):
    field: str
    values: tuple[str, ...]
    def to_dict(self): return {"op": "in", "field": self.field, "values": list(self.values)}

@dataclass(frozen=True)
class Eq(Cond):
    field: str
    value: Any
    def to_dict(self): return {"op": "eq", "field": self.field, "value": self.value}

@dataclass(frozen=True)
class And(Cond):
    args: tuple[Cond, ...]
    def to_dict(self): return {"op": "and", "args": [x.to_dict() for x in self.args]}

@dataclass(frozen=True)
class Or(Cond):
    args: tuple[Cond, ...]
    def to_dict(self): return {"op": "or", "args": [x.to_dict() for x in self.args]}

def cond_from_dict(value: dict[str, Any]) -> Cond:
    op = value.get("op")
    if op == "true": return TrueCond()
    if op == "is_missing": return IsMissing(value["field"])
    if op == "is_present": return IsPresent(value["field"])
    if op == "cmp":
        raw = value["value"]
        return Cmp(value["field"], value["cmp"], Fraction(str(raw["n"])), raw.get("unit"))
    if op == "in": return In(value["field"], tuple(value["values"]))
    if op == "eq": return Eq(value["field"], value["value"])
    if op in ("and", "or"):
        cls = And if op == "and" else Or
        return cls(tuple(cond_from_dict(x) for x in value["args"]))
    raise ValueError(f"unsupported condition op: {op!r}")
