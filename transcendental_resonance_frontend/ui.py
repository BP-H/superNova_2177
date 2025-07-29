"""Streamlit entry point for the Transcendental Resonance UI."""

from __future__ import annotations

import sys
from importlib import import_module
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

PAGES_DIR = Path(__file__).resolve().parent / "pages"
page_names = sorted(p.stem for p in PAGES_DIR.glob("*.py"))

st.sidebar.title("Navigation")
choice = st.sidebar.selectbox("Page", page_names)

if choice:
    import_module(f"transcendental_resonance_frontend.pages.{choice}")
