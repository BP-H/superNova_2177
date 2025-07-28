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


def render_voting_tab() -> None:
    """Render generic vote registry operations."""
    if dispatch_route is None:
        st.info("Governance routes not enabled")
        return

    if st.button("Refresh Votes"):
        try:
            res = _run_async(dispatch_route("load_votes", {}))
            st.session_state["votes_cache"] = res.get("votes", [])
        except Exception as exc:
            st.error(f"Failed to load votes: {exc}")

    votes = st.session_state.get("votes_cache", [])
    if votes:
        st.table(votes)

    with st.form("record_vote_form"):
        st.write("Record Vote")
        species = st.selectbox("Species", ["human", "ai", "company"])
        extra_json = st.text_input("Extra Fields (JSON)", value="{}")
        submit = st.form_submit_button("Record")
    if submit:
        try:
            extra = json.loads(extra_json or "{}")
        except Exception as exc:
            st.error(f"Invalid JSON: {exc}")
        else:
            payload = {"species": species, **extra}
            try:
                _run_async(dispatch_route("record_vote", payload))
                st.success("Vote recorded")
            except Exception as exc:
                st.error(f"Record failed: {exc}")
