from __future__ import annotations
import re
from dataclasses import dataclass
from fractions import Fraction
from .cond_ast import *
from .units import normalise_time

@dataclass(frozen=True)
class ParsedRule:
    condition: Cond
    route: str
    status: str = "PARSED"
    reason: str | None = None

_NUM = r"(?:\d+(?:\.\d+)?)"

def _atom(text: str) -> Cond:
    t = text.strip().lower()
    if t in ("true", "all tickets"): return TrueCond()
    m = re.fullmatch(r"(?:the )?ticket is (not )?urgent", t)
    if m: return Eq("urgent", not bool(m.group(1)))
    m = re.fullmatch(r"([\w ]+?)\s+is\s+(missing|present)", t)
    if m: return IsMissing(m.group(1).strip().replace(" ", "_")) if m.group(2) == "missing" else IsPresent(m.group(1).strip().replace(" ", "_") )
    m = re.fullmatch(r"([\w ]+?)\s+is one of\s+(.+)", t)
    if m:
        vals = tuple(x.strip().strip("'\"") for x in re.split(r"[,/]", m.group(2)))
        return In(m.group(1).strip().replace(" ", "_"), vals)
    m = re.fullmatch(r"([\w ]+?)\s+(is not|is|equals)\s+([a-z_][\w-]*)", t)
    if m:
        field, op, value = m.groups()
        field = field.strip().replace(" ", "_")
        if op == "is not":
            raise ValueError("not-equal enum conditions are outside the declared subset")
        return Eq(field, value)
    m = re.fullmatch(r"([\w ]+?)\s+(is at least|is more than|is over|is greater than|is at most|is less than|is under|at least|more than|over|greater than|at most|less than|under|exactly|is|equals|is not)\s+(%s)(?:\s*(minutes?|hours?))?" % _NUM, t)
    if m:
        field, op, num, unit = m.groups(); field = field.strip().replace(" ", "_")
        cmp = {"at least": ">=", "is at least": ">=", "more than": ">", "is more than": ">", "over": ">", "is over": ">", "greater than": ">", "is greater than": ">", "at most": "<=", "is at most": "<=", "less than": "<", "is less than": "<", "under": "<", "is under": "<", "exactly": "==", "is": "==", "equals": "==", "is not": "!="}[op]
        if cmp == "!=": raise ValueError("not-equal numeric conditions are outside the declared subset")
        if field == "waiting_time" and unit is None: raise ValueError("time value has no declared unit")
        return Cmp(field, cmp, normalise_time(num, unit) if unit else Fraction(num), unit)
    raise ValueError("unsupported condition atom")

def _condition(text: str) -> Cond:
    text = text.strip().strip("()")
    ors = re.split(r"\s+or\s+", text, flags=re.I)
    if len(ors) > 1: return Or(tuple(_condition(x) for x in ors))
    ands = re.split(r"\s+and\s+", text, flags=re.I)
    if len(ands) > 1: return And(tuple(_condition(x) for x in ands))
    return _atom(text)

def parse_sentence(sentence: str) -> ParsedRule:
    text = sentence.strip().rstrip(".")
    text = re.sub(r"^\[REQ-[^\]]+\]\s*", "", text, flags=re.I)
    m = re.match(r"(?:otherwise,\s*)?if\s+(.+?)(?:,\s*then)?\s*,?\s+route to\s+([\w-]+)$", text, re.I)
    if not m:
        m = re.match(r"(.+?)\s*->\s*([\w-]+)$", text, re.I)
    if not m:
        m = re.match(r"all remaining tickets\s+(?:go to|route to)\s+([\w-]+)$", text, re.I)
        if m: return ParsedRule(TrueCond(), m.group(1))
    if not m: raise ValueError("unsupported requirement form")
    if len(m.groups()) == 2: return ParsedRule(_condition(m.group(1)), m.group(2))
    raise ValueError("unsupported requirement form")

def parse_requirement(sentence: str) -> ParsedRule:
    try: return parse_sentence(sentence)
    except ValueError as exc:
        reason = str(exc)
        status = "AMBIGUOUS" if "unit" in reason or any(x in sentence.lower() for x in ("usually", "soon", "most")) else "UNSUPPORTED"
        return ParsedRule(TrueCond(), "ERROR", status, reason)
