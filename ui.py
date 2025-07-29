# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
"""Streamlit entry point launching the NiceGUI-based frontend."""

from __future__ import annotations

import os
import sys
import threading
from importlib import import_module
from pathlib import Path

import streamlit as st

HEALTH_CHECK_PARAM = "healthz"

# Fast path for Streamlit Cloud health checks
if st.query_params.get(HEALTH_CHECK_PARAM) == "1" or os.environ.get("PATH_INFO", "").rstrip("/") == "/healthz":
    st.write("ok")
    st.stop()

ROOT = Path(__file__).resolve().parent
PKG_DIR = ROOT / "transcendental_resonance_frontend"
SRC_DIR = PKG_DIR / "src"

for path in (ROOT, PKG_DIR, SRC_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


def _start_nicegui() -> None:
    """Import the frontend module which launches the NiceGUI server."""
    import_module("transcendental_resonance_frontend.__main__")


if HEALTH_CHECK_PARAM not in st.session_state:
    thread = threading.Thread(target=_start_nicegui, daemon=True)
    thread.start()
    st.session_state[HEALTH_CHECK_PARAM] = True

st.markdown("[Open Transcendental Resonance UI](http://localhost:8080)")
