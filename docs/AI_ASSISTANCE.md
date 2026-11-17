# AI assistance

AI assistance generated scaffolding, parser/evaluator implementation, adapters, tests, corpus generator, and evaluation plumbing. The supported domain, status semantics, exact arithmetic requirement, coverage policy, and held-out case labels follow the implementation plan and are kept outside `src/reviewer`.

Verification was performed with the configured Python interpreter, pytest, a baseline CLI review, and workspace diagnostics. Model output is treated as untrusted advisory data; labels and oracle code are never imported by the reviewer.
