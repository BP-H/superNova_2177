import os
import re
import pytest

from external_services.llm_client import get_speculative_futures
from external_services.video_client import generate_video_preview
from external_services.vision_client import analyze_image

ISO_RE = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:")


@pytest.mark.asyncio
async def test_llm_offline(monkeypatch):
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    monkeypatch.delenv("LLM_API_URL", raising=False)
    res = await get_speculative_futures("test", num=2)
    assert res["source"] == "offline"
    assert len(res["texts"]) == 2
    assert ISO_RE.match(res["timestamp"])
    assert res.get("trace_id")


@pytest.mark.asyncio
async def test_llm_fallback_not_implemented(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "x")
    monkeypatch.setenv("LLM_API_URL", "http://example.com")
    res = await get_speculative_futures("test", num=1)
    assert res["source"] == "offline"
    assert res.get("error")


@pytest.mark.asyncio
async def test_video_offline(monkeypatch):
    monkeypatch.delenv("VIDEO_API_KEY", raising=False)
    monkeypatch.delenv("VIDEO_API_URL", raising=False)
    res = await generate_video_preview("hello")
    assert res["source"] == "offline"
    assert res["video_url"].startswith("http")
    assert res.get("trace_id")


@pytest.mark.asyncio
async def test_video_fallback_not_implemented(monkeypatch):
    monkeypatch.setenv("VIDEO_API_KEY", "x")
    monkeypatch.setenv("VIDEO_API_URL", "http://example.com")
    res = await generate_video_preview("hi")
    assert res["source"] == "offline"
    assert res.get("error")


@pytest.mark.asyncio
async def test_vision_offline(monkeypatch):
    monkeypatch.delenv("VISION_API_KEY", raising=False)
    monkeypatch.delenv("VISION_API_URL", raising=False)
    res = await analyze_image(b"123")
    assert res["source"] == "offline"
    assert "Vision" in res["text"] or res["text"]


@pytest.mark.asyncio
async def test_vision_fallback_not_implemented(monkeypatch):
    monkeypatch.setenv("VISION_API_KEY", "x")
    monkeypatch.setenv("VISION_API_URL", "http://example.com")
    res = await analyze_image(b"123")
    assert res["source"] == "offline"
    assert res.get("error")
