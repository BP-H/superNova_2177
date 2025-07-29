"""STRICTLY A SOCIAL MEDIA PLATFORM
Intellectual Property & Artistic Inspiration
Legal & Ethical Safeguards

Experimental page for generating short video previews.

This functionality is highly experimental and requires a running backend
service capable of producing video previews. In offline mode a placeholder
URL will be shown.
"""

from __future__ import annotations

import asyncio

import streamlit as st
from external_services.video_client import generate_video_preview

# Optional import showcasing future real-time capabilities
try:  # pragma: no cover - optional dependency
    from realtime_comm.video_chat import VideoChatManager
except Exception:  # pragma: no cover - missing optional backend
    VideoChatManager = None


def _run_async(coro):
    """Execute ``coro`` regardless of the current event loop state."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    else:
        if loop.is_running():
            return asyncio.run_coroutine_threadsafe(coro, loop).result()
        return loop.run_until_complete(coro)


def main() -> None:
    """Render the video preview generator demo."""
    st.header("Video Preview Generator")
    st.write(
        "Enter a short prompt to generate a demo video. "
        "This experimental feature depends on the backend video service."
    )

    prompt = st.text_input(
        "Prompt",
        "A serene landscape at sunrise",
    )
    if st.button("Generate"):
        with st.spinner("Generating preview..."):
            url = _run_async(generate_video_preview(prompt))
        st.write(f"Preview URL: {url}")
        if url:
            st.video(url)

    if VideoChatManager is not None:
        st.caption("Future versions may integrate with real-time video chat.")
    else:
        st.caption("Video chat components not available in this build.")
