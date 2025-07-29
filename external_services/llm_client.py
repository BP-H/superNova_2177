from __future__ import annotations

"""Client for speculative text generation via LLM."""

import asyncio
import os

import httpx

from .base_client import BaseClient


class LLMClient(BaseClient):
    """Asynchronous LLM client with offline fallback and BYOK support."""

    def __init__(self, api_url: str | None = None, api_key: str | None = None) -> None:
        url = api_url or os.getenv(
            "LLM_API_URL", "https://your-llm-endpoint.com/generate"
        )
        key = api_key or os.getenv("LLM_API_KEY", "")
        super().__init__(url, key)

    def get_prompt_template(self) -> str:
        return "Give 3 short speculative futures for: '{description}' in style: {style}"

    async def get_speculative_futures(
        self, description: str, style: str = "humorous/chaotic good"
    ) -> dict:
        if self.offline:
            futures = [
                f"Offline Mode // Simulated future 1: {description} becomes a meme.",
                f"Offline Mode // Simulated future 2: {description} triggers a time loop.",
            ]
            return self._wrap("LLMClient", {"futures": futures})
        try:
            payload = {
                "prompt": self.get_prompt_template().format(
                    description=description, style=style
                ),
                "max_tokens": 300,
            }
            headers = {"Authorization": f"Bearer {self.api_key}"}
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    self.api_url, json=payload, headers=headers, timeout=10
                )
                futures = resp.json().get("futures", [])
            return self._wrap("LLMClient", {"futures": futures})
        except Exception as e:  # pragma: no cover - network errors
            return self._wrap("LLMClient", {"futures": [f"[LLM ERROR] {e}"]})

    def get_speculative_futures_sync(
        self, description: str, style: str = "humorous/chaotic good"
    ) -> dict:
        return asyncio.run(self.get_speculative_futures(description, style))


async def get_speculative_futures(
    description: str, style: str = "humorous/chaotic good"
) -> list[str]:
    """Backward compatible wrapper returning just the futures list."""
    client = LLMClient()
    result = await client.get_speculative_futures(description, style)
    return result.get("futures", [])


__all__ = ["LLMClient", "get_speculative_futures"]
