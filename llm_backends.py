from __future__ import annotations

"""Minimal pluggable LLM backend wrappers."""

from typing import Any, Dict
import requests


class LLMBackend:
    """Base backend wrapping a text generation API."""

    def __init__(self, api_key: str | None) -> None:
        self.api_key = api_key or ""

    def chat(self, prompt: str) -> str:
        raise NotImplementedError

    __call__ = chat


class GPT4oBackend(LLMBackend):
    """OpenAI GPT‑4o backend."""

    def chat(self, prompt: str) -> str:
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload: Dict[str, Any] = {
            "model": "gpt-4o",
            "messages": [{"role": "user", "content": prompt}],
        }
        try:
            r = requests.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers, timeout=20)
            r.raise_for_status()
            data = r.json()
            return data.get("choices", [{}])[0].get("message", {}).get("content", "")
        except Exception as exc:  # pragma: no cover - network failures
            raise RuntimeError(str(exc))


class Claude3Backend(LLMBackend):
    """Anthropic Claude‑3 backend."""

    def chat(self, prompt: str) -> str:
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        payload = {
            "model": "claude-3-sonnet-20240229",
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": prompt}],
        }
        try:
            r = requests.post("https://api.anthropic.com/v1/messages", json=payload, headers=headers, timeout=20)
            r.raise_for_status()
            data = r.json()
            return data.get("content", [{}])[0].get("text", "")
        except Exception as exc:  # pragma: no cover - network failures
            raise RuntimeError(str(exc))


class GeminiBackend(LLMBackend):
    """Google Gemini backend."""

    def chat(self, prompt: str) -> str:
        params = {"key": self.api_key}
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        try:
            r = requests.post(
                "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent",
                params=params,
                json=payload,
                timeout=20,
            )
            r.raise_for_status()
            data = r.json()
            return data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
        except Exception as exc:  # pragma: no cover - network failures
            raise RuntimeError(str(exc))
