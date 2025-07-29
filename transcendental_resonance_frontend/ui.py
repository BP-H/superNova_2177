"""Streamlit entry point to launch the NiceGUI-based Transcendental Resonance UI."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import streamlit as st

HEALTH_CHECK_PARAM = "healthz"

# Ensure we can import the package whether launched locally or on Streamlit Cloud
ROOT = Path(__file__).resolve().parents[1]
PKG_DIR = ROOT / "transcendental_resonance_frontend"
SRC_DIR = PKG_DIR / "src"

for path in (ROOT, PKG_DIR, SRC_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

# Respond quickly to Cloud health probes before importing heavy modules
if (
    st.query_params.get(HEALTH_CHECK_PARAM) == "1"
    or os.environ.get("PATH_INFO", "").rstrip("/") == "/healthz"
):
    st.write("ok")
    st.stop()

# Import and execute the NiceGUI launcher
from transcendental_resonance_frontend.__main__ import run  # noqa: E402

run()
