from typing import Callable, Dict, Optional
import os
import requests


def dummy_backend(prompt: str, api_key: str | None = None) -> str:
    """Return a canned response for testing."""
    return "[dummy]" + prompt


def gpt4o_backend(prompt: str, api_key: str | None = None) -> str:
    """Call OpenAI GPT-4o and return the response text."""
    if api_key is None:
        api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        raise ValueError("OPENAI_API_KEY required for GPT-4o backend")
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}"}
    data = {"model": "gpt-4o", "messages": [{"role": "user", "content": prompt}]}
    r = requests.post(url, headers=headers, json=data, timeout=30)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]


def claude3_backend(prompt: str, api_key: str | None = None) -> str:
    """Call Anthropic Claude-3 and return the response text."""
    if api_key is None:
        api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY required for Claude-3 backend")
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
    }
    data = {"model": "claude-3-opus-20240229", "max_tokens": 1024, "messages": [{"role": "user", "content": prompt}]}
    r = requests.post(url, headers=headers, json=data, timeout=30)
    r.raise_for_status()
    return r.json()["content"][0]["text"]


def gemini_backend(prompt: str, api_key: str | None = None) -> str:
    """Call Google Gemini and return the response text."""
    if api_key is None:
        api_key = os.getenv("GOOGLE_API_KEY", "")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY required for Gemini backend")
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
    )
    params = {"key": api_key}
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    r = requests.post(url, params=params, json=data, timeout=30)
    r.raise_for_status()
    candidates = r.json().get("candidates", [])
    if candidates:
        return candidates[0]["content"]["parts"][0]["text"]
    return ""


BACKENDS: Dict[str, Callable[[str, str | None], str]] = {
    "dummy": dummy_backend,
    "gpt-4o": gpt4o_backend,
    "claude-3": claude3_backend,
    "gemini": gemini_backend,
}


def get_backend(name: str, api_key: str | None = None) -> Optional[Callable[[str], str]]:
    """Retrieve the backend callable by name and bind the API key if provided."""
    base = BACKENDS.get(name)
    if base is None:
        return None

    def call(prompt: str) -> str:
        return base(prompt, api_key)

    return call
