# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
"""Reusable Streamlit components for API key entry and model selection."""

from __future__ import annotations

import os
import streamlit as st

# Mapping of provider names to environment/session keys
PROVIDERS = {
    "OpenAI": "OPENAI_API_KEY",
    "Anthropic": "ANTHROPIC_API_KEY",
    "Groq": "GROQ_API_KEY",
    "Google": "GOOGLE_API_KEY",
}

DEFAULT_MODELS = ["GPT-4o", "Claude-3", "Gemini", "Groq"]


def render_api_key_inputs(container: "st.delta_generator.DeltaGenerator" | None = None) -> None:
    """Render text inputs for API keys and store them in ``st.session_state``."""
    if container is None:
        container = st

    keys = st.session_state.get("api_keys", {})
    container.subheader("LLM API Keys")
    for name, env_var in PROVIDERS.items():
        default = keys.get(env_var) or os.getenv(env_var, "")
        key = container.text_input(f"{name} API Key", value=default, type="password")
        if key:
            keys[env_var] = key
    st.session_state["api_keys"] = keys

    model = container.selectbox("Model", DEFAULT_MODELS, index=0, key="selected_model")
    st.session_state["selected_model"] = model


def get_api_key(env_var: str) -> str:
    """Return the stored API key for ``env_var`` if available."""
    return st.session_state.get("api_keys", {}).get(env_var, "")


def render_future_simulation_stub(container: "st.delta_generator.DeltaGenerator" | None = None) -> None:
    """Display placeholders for upcoming simulation features."""
    if container is None:
        container = st
    container.subheader("Simulation Inputs (coming soon)")
    container.info(
        "Video uploads, causal event modeling, and symbolic voting will appear here.",
    )
