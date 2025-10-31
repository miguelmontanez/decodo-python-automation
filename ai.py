from typing import Any


class AIClient:
    """Placeholder AI client used by generators.

    In a real implementation, connect to an LLM here.
    """

    async def generate(self, prompt: str, **kwargs) -> str:
        # Minimal echo behavior for now
        return f"[AI OUTPUT] {prompt[:200]}"

    async def close(self) -> None:
        return None


