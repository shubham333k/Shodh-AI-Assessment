# Repository rules

- Python 3.11+, CPU-only core; keep dependencies to the standard library, pydantic, and pytest.
- Never execute artifact code. Parse Python with `ast` and interpret only the declared subset.
- Deterministic checks alone decide PASS, CHANGES_REQUIRED, or INCOMPLETE.
- Unsupported and ambiguous input stays visible in coverage.
- Use `Fraction` for threshold and unit arithmetic; never compare floats for semantic equality.
- `src/reviewer` must not import evaluation labels or oracle code.
