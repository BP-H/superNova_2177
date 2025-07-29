"""Streamlit launcher for the NiceGUI-based Transcendental Resonance UI."""

from __future__ import annotations

import os
import sys
from importlib import import_module
from pathlib import Path

import streamlit as st

HEALTH_CHECK_PARAM = "healthz"

# Respond to Streamlit Cloud health probes quickly
if st.query_params.get(HEALTH_CHECK_PARAM) == "1" or os.environ.get("PATH_INFO", "").rstrip("/") == "/healthz":
    st.write("ok")
    st.stop()

st.write("Booting...")

ROOT = Path(__file__).resolve().parent
PKG_DIR = ROOT / "transcendental_resonance_frontend"
SRC_DIR = PKG_DIR / "src"

for path in (ROOT, PKG_DIR, SRC_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import_module("transcendental_resonance_frontend.__main__")
