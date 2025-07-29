# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
import importlib
import sys
import types

import requests

import llm_backends as lb


def test_default_gpt_backend_env(monkeypatch):
    calls = {}

    def fake_post(url, headers=None, json=None, params=None, timeout=None):
        calls['url'] = url
        calls['headers'] = headers
        class R:
            def raise_for_status(self):
                pass
            def json(self):
                return {"choices": [{"message": {"content": "ok"}}]}
        return R()

    monkeypatch.setattr(requests, "post", fake_post)
    monkeypatch.setenv("OPENAI_API_KEY", "envkey")

    backend = lb.default_gpt_backend()
    result = backend("hi")

    assert result == "ok"
    assert calls['headers']["Authorization"] == "Bearer envkey"


def test_claude_backend_secrets(monkeypatch):
    calls = {}
    stub = types.SimpleNamespace(secrets={"ANTHROPIC_API_KEY": "sek"})
    monkeypatch.setattr(lb, "st", stub)

    def fake_post(url, headers=None, json=None, params=None, timeout=None):
        calls['headers'] = headers
        class R:
            def raise_for_status(self):
                pass
            def json(self):
                return {"content": [{"text": "claude"}]}
        return R()

    monkeypatch.setattr(requests, "post", fake_post)

    backend = lb.claude_backend()
    result = backend("hello")

    assert result == "claude"
    assert calls['headers']["x-api-key"] == "sek"


def test_gemini_backend_error(monkeypatch):
    stub = types.SimpleNamespace(secrets={})
    monkeypatch.setattr(lb, "st", stub)
    monkeypatch.setenv("GOOGLE_API_KEY", "g")

    def fake_post(*a, **k):
        raise requests.RequestException("boom")

    monkeypatch.setattr(requests, "post", fake_post)

    backend = lb.gemini_backend()
    assert backend("x") == ""
