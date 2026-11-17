from __future__ import annotations
import json, os, urllib.request

class RealClient:
    """Optional OpenAI-compatible HTTP adapter; never required for offline review."""
    def __init__(self, endpoint=None, api_key=None, model=None, timeout=15):
        self.endpoint = endpoint or os.environ.get("SHODH_MODEL_ENDPOINT")
        self.api_key = api_key or os.environ.get("SHODH_MODEL_KEY")
        self.model = model or os.environ.get("SHODH_MODEL", "gpt-4o-mini")
        self.timeout = timeout
        if not self.endpoint or not self.api_key: raise ValueError("real model requires SHODH_MODEL_ENDPOINT and SHODH_MODEL_KEY")
    def review(self, prompt: str) -> str:
        body = json.dumps({"model": self.model, "messages": [{"role": "user", "content": prompt}]}).encode()
        request = urllib.request.Request(self.endpoint, body, {"Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}"})
        with urllib.request.urlopen(request, timeout=self.timeout) as response:
            payload = json.loads(response.read().decode())
        return payload["choices"][0]["message"]["content"]
