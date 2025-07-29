# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
"""Client for speculative text generation via LLM."""

from __future__ import annotations

import os

import httpx

LLM_API_URL = os.getenv("LLM_API_URL", "https://your-llm-endpoint.com/generate")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")  # <-- user inserts key here


async def get_speculative_futures(
    description: str, style: str = "humorous/chaotic good"
) -> list[str]:
    """Return speculative future strings from a remote LLM service."""
    if not LLM_API_KEY:
        return [
            f"Offline Mode // Simulated future 1: {description} becomes a meme.",
            f"Offline Mode // Simulated future 2: {description} triggers a time loop.",
        ]
    try:
        payload = {
            "prompt": f"Give 3 short speculative futures for: '{description}' in style: {style}",
            "max_tokens": 300,
        }
        headers = {"Authorization": f"Bearer {LLM_API_KEY}"}
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                LLM_API_URL, json=payload, headers=headers, timeout=10
            )
            return resp.json().get("futures", [])
    except Exception as e:  # pragma: no cover - network errors
        return [f"[LLM ERROR] {e}"]


__all__ = ["get_speculative_futures"]
