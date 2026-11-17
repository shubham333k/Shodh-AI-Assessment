from __future__ import annotations
import re

_PATTERNS = (r"ignore (?:previous|all) instructions", r"reviewer\s*:\s*(?:output|return)", r"this (?:was|is) approved")

def scan_instructions(text: str):
    findings = []
    for line_no, line in enumerate(text.splitlines(), 1):
        if any(re.search(pattern, line, re.I) for pattern in _PATTERNS):
            findings.append({"category": "INJECTED_INSTRUCTION", "severity": "INFO", "location": f"L{line_no}", "quote": line.strip()})
    return findings
