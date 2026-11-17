from __future__ import annotations
from fractions import Fraction
from itertools import product
import random

def partition_tickets(fields: dict, constants: dict[str, set[Fraction | str]] | None = None, max_cells=500_000, mode="exhaustive", samples=50, seed=7):
    constants = constants or {}
    choices = {}
    for name, spec in fields.items():
        if spec.get("type") == "enum": choices[name] = [None, *spec.get("values", []), "__OTHER__"]
        elif spec.get("type") == "bool": choices[name] = [None, False, True]
        else:
            cuts = sorted(Fraction(x) for x in constants.get(name, set()))
            vals = [None]
            if cuts: vals.append(max(Fraction(0), cuts[0] - 1))
            for i, cut in enumerate(cuts):
                vals.append(cut)
                if i + 1 < len(cuts): vals.append((cut + cuts[i + 1]) / 2)
                else: vals.append(cut + 1)
            choices[name] = list(dict.fromkeys(vals))
    count = 1
    for x in choices.values(): count *= len(x)
    if count > max_cells or mode == "sampled":
        rng = random.Random(seed)
        keys = list(choices)
        return [dict(zip(keys, [rng.choice(choices[key]) for key in keys])) for _ in range(samples)], "sampled"
    return [dict(zip(choices, values)) for values in product(*choices.values())], "exhaustive"
