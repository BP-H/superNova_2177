"""Reusable helpers for API key input in the Streamlit UI."""

from __future__ import annotations

try:
    import streamlit as st
except Exception:  # pragma: no cover - streamlit not available
    st = None  # type: ignore

# Mapping of display name -> (model identifier, session_state key)
PROVIDERS = {
    "Dummy": ("dummy", None),
    "GPT-4o (OpenAI)": ("gpt-4o", "OPENAI_API_KEY"),
    "Claude-3 (Anthropic)": ("claude-3", "ANTHROPIC_API_KEY"),
    "Gemini (Google)": ("gemini", "GOOGLE_API_KEY"),
    "Mixtral (Groq)": ("mixtral", "GROQ_API_KEY"),
}


def render_api_key_ui(default: str = "Dummy") -> dict[str, str | None]:
    """Render model selection and API key fields.

    Returns a dictionary with ``model`` and ``api_key`` keys.
    """
    if st is None:
        return {"model": "dummy", "api_key": None}

    names = list(PROVIDERS.keys())
    if default in names:
        index = names.index(default)
    else:
        index = 0
    choice = st.selectbox("LLM Model", names, index=index)
    model, key_name = PROVIDERS[choice]
    key_val = ""
    if key_name is not None:
        key_val = st.text_input(
            f"{choice} API Key",
            type="password",
            value=st.session_state.get(key_name, ""),
        )
        if key_val:
            st.session_state[key_name] = key_val
    st.session_state["selected_model"] = model
    return {"model": model, "api_key": key_val or st.session_state.get(key_name)}


def render_simulation_stubs() -> None:
    """Placeholder inputs for upcoming simulation features."""
    if st is None:
        return
    with st.expander("Future Simulation Inputs", expanded=False):
        st.text("Video upload - coming soon")
        st.text("Causal event modeling - TODO")
        st.text("Symbolic voting - TODO")
