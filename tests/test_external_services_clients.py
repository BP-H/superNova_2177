# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
"""Basic import and offline-mode checks for external service clients."""

import pytest

from external_services.llm_client import LLMClient
from external_services.video_client import VideoClient
from external_services.vision_client import VisionClient


@pytest.mark.asyncio
async def test_llm_client_offline(monkeypatch):
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    monkeypatch.delenv("LLM_API_URL", raising=False)
    monkeypatch.setenv("OFFLINE_MODE", "1")
    client = LLMClient()
    result = await client.get_speculative_futures("test")
    assert result["futures"] and "Offline Mode" in result["futures"][0]  # nosec B101
    for key in ("source", "timestamp", "trace_id", "disclaimer"):
        assert key in result  # nosec B101


@pytest.mark.asyncio
async def test_video_client_offline(monkeypatch):
    monkeypatch.delenv("VIDEO_API_KEY", raising=False)
    monkeypatch.delenv("VIDEO_API_URL", raising=False)
    monkeypatch.setenv("OFFLINE_MODE", "1")
    client = VideoClient()
    result = await client.generate_video_preview("hello")
    assert "placeholder" in result["video_url"]  # nosec B101
    for key in ("source", "timestamp", "trace_id", "disclaimer"):
        assert key in result  # nosec B101


@pytest.mark.asyncio
async def test_vision_client_offline(monkeypatch):
    monkeypatch.delenv("VISION_API_KEY", raising=False)
    monkeypatch.delenv("VISION_API_URL", raising=False)
    monkeypatch.setenv("OFFLINE_MODE", "1")
    client = VisionClient()
    result = await client.analyze_timeline("https://example.com/video.mp4")
    assert result["events"] and "Offline" in result["events"][0]  # nosec B101
    for key in ("source", "timestamp", "trace_id", "disclaimer"):
        assert key in result  # nosec B101


@pytest.mark.asyncio
async def test_frontend_api_offline(monkeypatch):
    """``api_call`` should not attempt HTTP requests when OFFLINE_MODE is set."""
    monkeypatch.setenv("OFFLINE_MODE", "1")
    from importlib import reload
    from transcendental_resonance_frontend.src.utils import api as api_utils

    api_utils = reload(api_utils)

    class Dummy:
        def __init__(self, *a, **k):
            raise AssertionError("HTTP call executed")

    monkeypatch.setattr(api_utils.httpx, "AsyncClient", Dummy)

    result = await api_utils.api_call("GET", "/users")
    assert result == []
