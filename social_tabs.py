import asyncio
import streamlit as st
from streamlit_helpers import alert

try:
    from frontend_bridge import dispatch_route
except Exception:  # pragma: no cover - optional dependency
    dispatch_route = None  # type: ignore


def _run_async(coro):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    else:
        if loop.is_running():
            return asyncio.run_coroutine_threadsafe(coro, loop).result()
        return loop.run_until_complete(coro)


def render_social_tab() -> None:
    """Render simple follow/unfollow controls."""
    st.subheader("Friends & Followers")
    if dispatch_route is None:
        st.info("Social routes not available")
        return
    username = st.text_input("Username")
    if st.button("Follow/Unfollow") and username:
        try:
            result = _run_async(dispatch_route("follow_user", {"username": username}))
            st.json(result)
        except Exception as exc:  # pragma: no cover - UI feedback
            alert(f"Operation failed: {exc}", "error")
