import streamlit as st

# Map service labels to session state keys
SERVICE_KEYS = {
    "OpenAI": "OPENAI_API_KEY",
    "Anthropic": "ANTHROPIC_API_KEY",
    "Groq": "GROQ_API_KEY",
    "Gemini": "GOOGLE_API_KEY",
}


def render_api_key_inputs() -> None:
    """Render simple sidebar inputs for user provided API keys."""
    st.sidebar.subheader("LLM API Keys")
    for label, key in SERVICE_KEYS.items():
        default = st.session_state.get(key, "")
        st.session_state[key] = st.sidebar.text_input(
            f"{label} API Key",
            value=default,
            type="password",
        )

    model = st.sidebar.selectbox(
        "Default Model",
        ["gpt-4o", "claude-3", "gemini", "groq"],
        index=0,
    )
    st.session_state["MODEL_CHOICE"] = model

