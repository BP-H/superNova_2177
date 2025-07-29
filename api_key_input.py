"""Reusable Streamlit widgets for API key input."""

from __future__ import annotations

import streamlit as st

# Map provider display names to environment variable keys and model options
PROVIDERS = {
    "OpenAI": {"env": "OPENAI_API_KEY", "models": ["gpt-4o", "gpt-3.5-turbo"]},
    "Anthropic": {"env": "ANTHROPIC_API_KEY", "models": ["claude-3-opus", "claude-3-haiku"]},
    "Groq": {"env": "GROQ_API_KEY", "models": ["mixtral-8x7b", "llama3-70b"]},
}


def render_api_key_inputs() -> dict[str, str]:
    """Render provider/model selectors and store keys in ``st.session_state``.

    Returns a dictionary with ``provider``, ``api_key`` and ``model`` fields.
    """
    if "api_keys" not in st.session_state:
        st.session_state["api_keys"] = {}

    provider = st.selectbox("Model Provider", list(PROVIDERS))
    meta = PROVIDERS[provider]
    key_name = meta["env"]
    default = st.session_state["api_keys"].get(key_name, "")
    api_key = st.text_input(f"{provider} API Key", value=default, type="password")
    st.session_state["api_keys"][key_name] = api_key

    model = st.selectbox("Model", meta.get("models", []), key=f"model_{provider}")
    st.session_state["api_keys"][f"model_{provider}"] = model

    return {"provider": provider, "api_key": api_key, "model": model}


__all__ = ["render_api_key_inputs", "PROVIDERS"]
