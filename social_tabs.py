import asyncio
import json
import streamlit as st

try:
    from frontend_bridge import dispatch_route
except Exception:  # pragma: no cover - optional
    dispatch_route = None


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
    """Display follow interactions and social entanglement."""
    st.subheader("Friends & Followers")
    if dispatch_route is None:
        st.info("Social routes not available")
        return

    username = st.text_input("Username to follow/unfollow")
    if st.button("Toggle Follow") and username:
        try:
            res = _run_async(dispatch_route("follow_user", {"username": username}))
            msg = res.get("message") if isinstance(res, dict) else "ok"
            st.success(msg)
        except Exception as exc:
            st.error(f"Follow failed: {exc}")

    st.divider()
    st.subheader("Simulate Entanglement")
    u1 = st.number_input("User 1 ID", value=1, step=1)
    u2 = st.number_input("User 2 ID", value=2, step=1)
    if st.button("Run Simulation"):
        try:
            res = _run_async(
                dispatch_route(
                    "simulate_entanglement",
                    {"user1_id": int(u1), "user2_id": int(u2)},
                )
            )
            st.json(res)
        except Exception as exc:
            st.error(f"Simulation failed: {exc}")
