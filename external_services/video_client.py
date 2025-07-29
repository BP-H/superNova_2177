from __future__ import annotations

"""Stub client for AI-driven video previews."""

import os

import httpx

from .base_client import BaseClient


class VideoClient(BaseClient):
    """Asynchronous video generation client with offline fallback."""

    def __init__(self, api_url: str | None = None, api_key: str | None = None) -> None:
        url = api_url or os.getenv("VIDEO_API_URL", "")
        key = api_key or os.getenv("VIDEO_API_KEY", "")
        super().__init__(url, key)

    async def generate_video_preview(self, prompt: str) -> dict:
        if self.offline:
            return self._wrap(
                "VideoClient", {"video_url": "https://example.com/placeholder.mp4"}
            )
        try:
            payload = {"prompt": prompt}
            headers = {"Authorization": f"Bearer {self.api_key}"}
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    self.api_url, json=payload, headers=headers, timeout=10
                )
                url = resp.json().get(
                    "video_url", "https://example.com/placeholder.mp4"
                )
            return self._wrap("VideoClient", {"video_url": url})
        except Exception as e:  # pragma: no cover - network errors
            return self._wrap("VideoClient", {"video_url": f"[VIDEO ERROR] {e}"})


async def generate_video_preview(prompt: str) -> str:
    """Backward compatible wrapper returning just the URL string."""
    client = VideoClient()
    result = await client.generate_video_preview(prompt)
    return result.get("video_url", "")


__all__ = ["VideoClient", "generate_video_preview"]
