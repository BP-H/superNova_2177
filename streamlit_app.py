# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards

import json
import asyncio
import streamlit as st

from frontend_bridge import dispatch_route, ROUTES
from streamlit_helpers import apply_theme, header


def _run_async(coro):
    """Execute ``coro`` or schedule it if a loop is already running."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    else:
        if loop.is_running():
            return asyncio.run_coroutine_threadsafe(coro, loop).result()
        return loop.run_until_complete(coro)


def main() -> None:
    apply_theme("dark")
    header("superNova_2177 Interface")

    routes = sorted(ROUTES.keys())
    if routes:
        route_name = st.selectbox("Route", routes)
    else:
        route_name = st.text_input("Route Name")

    payload_text = st.text_area("JSON Payload (optional)", "{}", height=200)

    if st.button("Dispatch"):
        try:
            payload = json.loads(payload_text) if payload_text.strip() else {}
        except json.JSONDecodeError as exc:
            st.error(f"Invalid JSON payload: {exc}")
            return

        with st.spinner("Calling route..."):
            try:
                result = _run_async(dispatch_route(route_name, payload))
            except Exception as exc:
                st.error(f"Route failed: {exc}")
            else:
                if isinstance(result, asyncio.Task):
                    st.info("Background task started")
                else:
                    st.json(result)


if __name__ == "__main__":
    main()
