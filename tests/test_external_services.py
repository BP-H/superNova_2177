# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
import importlib

import os
import inspect

from external_services.llm_client import LLMClient
from external_services.video_client import VideoClient
from external_services.vision_client import VisionClient


def test_clients_importable():
    assert inspect.isclass(LLMClient)
    assert inspect.isclass(VideoClient)
    assert inspect.isclass(VisionClient)


def test_llm_client_offline(monkeypatch):
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    client = LLMClient()
    out = client.generate("hello")
    assert "offline" in out


def test_video_client_offline(monkeypatch):
    monkeypatch.delenv("VIDEO_API_KEY", raising=False)
    client = VideoClient()
    out = client.summarize("demo.mp4")
    assert "offline" in out


def test_vision_client_offline(monkeypatch):
    monkeypatch.delenv("VISION_API_KEY", raising=False)
    client = VisionClient()
    out = client.analyze(b"img")
    assert out.get("status") == "offline"
