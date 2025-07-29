# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
"""Client for speculative text generation via an LLM service."""

from __future__ import annotations

import os
from typing import Any, Dict, List

import httpx

from .base_client import BaseClient


class LLMClient(BaseClient):
    """LLM client with offline fallbacks."""

    PLACEHOLDERS = [
        "Offline future 1: {desc} becomes a meme.",
        "Offline future 2: {desc} triggers a time loop.",
    ]

    def __init__(self, api_key: str | None = None, api_url: str | None = None, offline: bool | None = None) -> None:
        api_key = api_key or os.getenv("LLM_API_KEY", "")
        api_url = api_url or os.getenv("LLM_API_URL", "https://your-llm-endpoint.com/generate")
        super().__init__(api_key, api_url, offline)

    async def get_speculative_futures(self, description: str, style: str = "humorous/chaotic good") -> List[Dict[str, Any]]:
        """Return speculative future strings from the remote service."""
        placeholder_base = {
            "disclaimer": self.OFFLINE_DISCLAIMER,
        }
        placeholders = [
            {"text": p.format(desc=description), **placeholder_base} for p in self.PLACEHOLDERS
        ]
        if self.offline:
            return [self._offline_response(p) for p in placeholders]
        try:
            payload = {
                "prompt": f"Give 3 short speculative futures for: '{description}' in style: {style}",
                "max_tokens": 300,
            }
            headers = {"Authorization": f"Bearer {self.api_key}"}
            async with httpx.AsyncClient() as client:
                resp = await client.post(self.api_url, json=payload, headers=headers, timeout=10)
                resp.raise_for_status()
                texts = resp.json().get("futures", [])
                return [self._api_response({"text": t}) for t in texts]
        except Exception as e:  # pragma: no cover - network errors
            return [self._error_response(e, p) for p in placeholders]


__all__ = ["LLMClient"]
