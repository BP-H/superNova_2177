import streamlit as st

KEY_MAP = {
    "GPT-4o": "OPENAI_API_KEY",
    "Claude-3": "ANTHROPIC_API_KEY",
    "Gemini": "GOOGLE_API_KEY",
    "Groq": "GROQ_API_KEY",
}
MODELS = list(KEY_MAP.keys())


def render_api_key_ui() -> str | None:
    """Render API key inputs and return the selected model."""
    if "api_keys" not in st.session_state:
        st.session_state["api_keys"] = {}

    st.subheader("Bring Your Own API Key")
    for label, sess_key in KEY_MAP.items():
        try:
            val = st.text_input(
                f"{label} API Key",
                value=st.session_state["api_keys"].get(sess_key, ""),
                type="password",
            )
            if val:
                st.session_state["api_keys"][sess_key] = val
        except Exception:
            st.warning(f"Failed to capture {label} key")

    try:
        model = st.selectbox("Model", MODELS, index=0)
    except Exception:
        model = None
    st.session_state["selected_model"] = model
    return model


def get_api_key_for_model(model: str | None) -> str | None:
    """Return the session key for ``model`` if known."""
    return KEY_MAP.get(model or "")


def render_future_simulation_stub() -> None:
    """Placeholder for upcoming simulation inputs."""
    st.subheader("Simulation Inputs (coming soon)")
    st.caption("Video, causal event modeling, and symbolic voting will appear here.")
