class FakeClient:
    def __init__(self, script="ok"): self.script = script
    def review(self, prompt):
        if self.script == "timeout": raise TimeoutError("fake model timeout")
        if self.script == "truncated_json": return '{"findings": ['
        if self.script == "malformed_json": return "not-json"
        if self.script == "invented_ref": return '{"findings":[{"rule_ref":"req:missing"}]}'
        if self.script == "conflicting_claims": return '{"findings":[{"severity":"INFO","category":"MODEL_CLAIM"}]}'
        if self.script == "obeys_injection": return '{"findings":[]}'
        return '{"findings":[]}'
