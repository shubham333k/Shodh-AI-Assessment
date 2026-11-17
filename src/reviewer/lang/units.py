from fractions import Fraction

UNIT_MINUTES = {"minute": Fraction(1), "minutes": Fraction(1), "hour": Fraction(60), "hours": Fraction(60)}

def normalise_time(value: str | int | float | Fraction, unit: str | None) -> Fraction:
    if unit is None: raise ValueError("time value has no declared unit")
    key = unit.lower().strip()
    if key not in UNIT_MINUTES: raise ValueError(f"unsupported time unit: {unit}")
    return Fraction(str(value)) * UNIT_MINUTES[key]
