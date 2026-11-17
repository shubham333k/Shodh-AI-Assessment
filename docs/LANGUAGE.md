# Supported routing language

The reviewer supports a deliberately small language for support-ticket routing. Requirements are anchored lines of the form `[REQ-n] if <condition>, route to <route>.` or `all remaining tickets go to <route>.` Conditions can be nested with `and` and `or`, test missing/present fields, compare numeric time thresholds, or test enum membership.

Time thresholds are represented as exact `Fraction` values in minutes. `0.5 hours`, `30 minutes`, and an equivalent integer expression therefore compare exactly. A time threshold without a unit is ambiguous and remains visible in coverage.

The first matching rule by explicit `order` wins. Missing values are absent, null, or blank strings. Comparisons on missing fields are false; only `is missing` and `is present` inspect missingness.

Unsupported prose is reported as unsupported rather than guessed. The reviewer does not claim to verify arbitrary natural language or arbitrary Python.
