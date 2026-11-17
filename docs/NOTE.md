# Engineering note

This implementation reviews support-ticket routing inside a deliberately small declared language. Requirements and JSON specs are converted into routing functions. Missing values, exact time units, explicit rule order, unsupported prose, and ambiguous thresholds remain visible rather than being guessed.

The semantic core uses exhaustive partition representatives for the fields in the registry and exact `Fraction` arithmetic. Deterministic findings alone decide status. Model output is advisory and validated for JSON shape and known references; it cannot promote an incomplete review to PASS or erase a deterministic blocker.

The repository includes a generated 17-bundle corpus, an independent plain-Python oracle, labels, an evaluation harness, and a seeded sampling ablation. Workflow graphs and the supported Python snippet subset are interpreted and compared as additional routing functions. The optional real model adapter is OpenAI-compatible and environment-variable based; offline evaluation uses the fake/no-model paths. The implementation is CPU-only and does not claim arbitrary Python or arbitrary prose verification.
