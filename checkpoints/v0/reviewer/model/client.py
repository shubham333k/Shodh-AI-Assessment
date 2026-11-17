from typing import Protocol

class ModelClient(Protocol):
    def review(self, prompt: str) -> str: ...
