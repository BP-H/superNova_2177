# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
"""Streamlit helpers for social network interactions."""

from __future__ import annotations

import streamlit as st
from streamlit_helpers import alert

try:
    from streamlit_app import _run_async
except Exception:

    def _run_async(coro):
        import asyncio

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(coro)
        else:
            if loop.is_running():
                return asyncio.run_coroutine_threadsafe(coro, loop).result()
            return loop.run_until_complete(coro)

try:
    from frontend_bridge import dispatch_route
except Exception:  # pragma: no cover - optional dependency
    dispatch_route = None


def render_social_tab() -> None:
    """Render follow/unfollow and entanglement tools."""
    st.subheader("Friends & Followers")
    if dispatch_route is None:
        st.info("Social routes unavailable")
        return

    username = st.text_input("Username to follow/unfollow")
    if st.button("Toggle Follow") and username:
        try:
            res = _run_async(dispatch_route("follow_user", {"username": username}))
            st.json(res)
        except Exception as exc:  # pragma: no cover - optional
            alert(f"Follow failed: {exc}", "error")

    st.divider()
    st.subheader("Simulate Entanglement")
    user1 = st.text_input("User 1 ID", key="ent_user1")
    user2 = st.text_input("User 2 ID", key="ent_user2")
    if st.button("Run Simulation") and user1 and user2:
        try:
            payload = {"user1_id": int(user1), "user2_id": int(user2)}
            res = _run_async(dispatch_route("simulate_entanglement", payload))
            st.json(res)
        except Exception as exc:  # pragma: no cover - optional
            alert(f"Simulation failed: {exc}", "error")
