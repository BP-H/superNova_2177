import os
import uuid
import pytest

from external_services import LLMClient, VideoClient, VisionClient


@pytest.mark.asyncio
async def test_llm_offline_deterministic(monkeypatch):
    monkeypatch.setenv("OFFLINE_MODE", "1")
    client = LLMClient()
    res = await client.get_speculative_futures("dream")
    assert res[0]["source"] == "offline"
    assert res[0]["text"] == "Offline future 1: dream becomes a meme."
    uuid.UUID(res[0]["trace_id"])  # raises if invalid
    assert res[0]["timestamp"].endswith("Z")


@pytest.mark.asyncio
async def test_video_client_fallback(monkeypatch):
    monkeypatch.delenv("OFFLINE_MODE", raising=False)
    monkeypatch.setenv("VIDEO_API_KEY", "k")
    monkeypatch.setenv("VIDEO_API_URL", "http://api")
    client = VideoClient()
    data = await client.generate_video_preview("hello")
    assert data["source"] == "offline"
    assert "error" in data
    assert data["url"].endswith("placeholder.mp4")


@pytest.mark.asyncio
async def test_uniform_keys(monkeypatch):
    monkeypatch.setenv("OFFLINE_MODE", "1")
    l = LLMClient()
    v = VideoClient()
    vi = VisionClient()
    t = await l.get_speculative_futures("hi")
    vid = await v.generate_video_preview("hi")
    vis = await vi.analyze_image(b"data")
    base_keys = set(t[0].keys())
    assert base_keys.issuperset({"text", "source", "trace_id", "timestamp", "disclaimer"})
    assert set(vid.keys()).issuperset({"url", "source", "trace_id", "timestamp", "disclaimer"})
    assert set(vis.keys()).issuperset({"text", "source", "trace_id", "timestamp", "disclaimer"})
