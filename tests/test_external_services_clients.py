# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
"""Basic import and offline-mode checks for external service clients."""

import pytest

from external_services.llm_client import get_speculative_futures
from external_services.video_client import generate_video_preview
from external_services.vision_client import analyze_timeline


@pytest.mark.asyncio
async def test_llm_client_offline(monkeypatch):
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    monkeypatch.delenv("LLM_API_URL", raising=False)
    results = await get_speculative_futures("test")
    assert results and "Offline Mode" in results[0]  # nosec B101


@pytest.mark.asyncio
async def test_video_client_offline(monkeypatch):
    monkeypatch.delenv("VIDEO_API_KEY", raising=False)
    monkeypatch.delenv("VIDEO_API_URL", raising=False)
    url = await generate_video_preview("hello")
    assert "placeholder" in url  # nosec B101


@pytest.mark.asyncio
async def test_vision_client_offline(monkeypatch):
    monkeypatch.delenv("VISION_API_KEY", raising=False)
    monkeypatch.delenv("VISION_API_URL", raising=False)
    notes = await analyze_timeline("https://example.com/video.mp4")
    assert notes and "Offline" in notes[0]  # nosec B101
