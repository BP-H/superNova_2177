"""STRICTLY A SOCIAL MEDIA PLATFORM
Intellectual Property & Artistic Inspiration
Legal & Ethical Safeguards

Preview page for upcoming video chat features.
"""

from __future__ import annotations

import streamlit as st

from ai_video_chat import create_session
from realtime_comm.video_chat import VideoChatManager

manager = VideoChatManager()


def main() -> None:
    """Render the video chat scaffolding page."""
    st.header("Video Chat Preview")
    st.write("This experimental page exposes placeholders for future video sessions.")

    user_ids = st.text_input("Participant IDs (comma separated)", "alice,bob")
    if st.button("Create Demo Session"):
        ids = [u.strip() for u in user_ids.split(",") if u.strip()]
        session = create_session(ids)
        manager.start_call(ids)
        st.success(
            f"Created session {session.session_id} with {len(session.participants)} participants"
        )
        st.info("Streaming not implemented yet – backend scaffolding only.")
