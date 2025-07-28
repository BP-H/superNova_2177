import asyncio
import streamlit as st

from frontend_bridge import dispatch_route
from streamlit_helpers import alert


def _run_async(coro):
    """Execute an async coroutine and return the result."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    else:
        if loop.is_running():
            return asyncio.run_coroutine_threadsafe(coro, loop).result()
        return loop.run_until_complete(coro)


def render_social_tab() -> None:
    """Display simple social network interactions."""
    if dispatch_route is None:
        alert("Social routes not enabled—enable them in config.", "warning")
        return

    st.subheader("Follow / Unfollow")
    username = st.text_input("Target Username")
    if st.button("Toggle Follow") and username:
        try:
            res = _run_async(dispatch_route("follow_user", {"username": username}))
            st.write(res.get("message", res))
        except Exception as exc:
            alert(f"Action failed: {exc}", "error")

    st.divider()
    st.subheader("Simulate Social Entanglement")
    col1, col2 = st.columns(2)
    user1 = col1.number_input("User 1 ID", value=1, step=1)
    user2 = col2.number_input("User 2 ID", value=2, step=1)
    if st.button("Run Simulation"):
        payload = {"user1_id": int(user1), "user2_id": int(user2)}
        try:
            result = _run_async(dispatch_route("simulate_entanglement", payload))
            st.json(result)
        except Exception as exc:
            alert(f"Simulation failed: {exc}", "error")
