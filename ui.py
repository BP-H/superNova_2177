# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
"""Lightweight Streamlit landing page for superNova_2177."""

from __future__ import annotations

import os
import streamlit as st

st.set_page_config(page_title="superNova_2177", page_icon="🚀", layout="centered")

HEALTH_CHECK_PARAM = "healthz"

if st.query_params.get(HEALTH_CHECK_PARAM) == "1" or os.environ.get("PATH_INFO", "").rstrip("/") == "/healthz":
    st.write("ok")
    st.stop()

st.title("superNova_2177")
st.write(
    "Welcome to **superNova_2177** — a scientifically grounded social metaverse engine for collaborative creativity."
)

st.write(
    "This Streamlit page provides a simple health check and introduction. The full NiceGUI interface is available in the project for deeper exploration."
)

st.markdown(
    "[Launch the NiceGUI version](https://example.com)"  # Replace with actual URL when deployed
)
