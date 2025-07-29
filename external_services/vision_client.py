from __future__ import annotations

"""Stub client for AI-powered vision timeline analysis."""

import hashlib
import os

import httpx

from .base_client import BaseClient


class VisionClient(BaseClient):
    """Asynchronous vision analysis client with deterministic offline fallback."""

    def __init__(self, api_url: str | None = None, api_key: str | None = None) -> None:
        url = api_url or os.getenv("VISION_API_URL", "")
        key = api_key or os.getenv("VISION_API_KEY", "")
        super().__init__(url, key)

    async def analyze_timeline(self, video_url: str) -> dict:
        if self.offline:
            digest = hashlib.md5(video_url.encode(), usedforsecurity=False).hexdigest()[
                :6
            ]
            caption = f"offline-caption-{digest}"
            events = ["Offline Mode // No vision analysis available"]
            return self._wrap("VisionClient", {"events": events, "caption": caption})
        try:
            payload = {"video_url": video_url}
            headers = {"Authorization": f"Bearer {self.api_key}"}
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    self.api_url, json=payload, headers=headers, timeout=10
                )
                events = resp.json().get("events", [])
                caption = resp.json().get("caption", "")
            return self._wrap("VisionClient", {"events": events, "caption": caption})
        except Exception as e:  # pragma: no cover - network errors
            return self._wrap(
                "VisionClient", {"events": [f"[VISION ERROR] {e}"], "caption": ""}
            )


async def analyze_timeline(video_url: str) -> list[str]:
    """Backward compatible wrapper returning only the events list."""
    client = VisionClient()
    result = await client.analyze_timeline(video_url)
    return result.get("events", [])


__all__ = ["VisionClient", "analyze_timeline"]
