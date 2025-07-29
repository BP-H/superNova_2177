"""Streamlit entry point to launch the NiceGUI-based Transcendental Resonance UI."""

from __future__ import annotations

import sys
from importlib import import_module
from pathlib import Path


# Ensure we can import the package whether launched locally or on Streamlit Cloud
ROOT = Path(__file__).resolve().parents[1]
PKG_DIR = ROOT / "transcendental_resonance_frontend"
SRC_DIR = PKG_DIR / "src"

for path in (ROOT, PKG_DIR, SRC_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

# Importing the package starts the NiceGUI app via src.main
import_module("transcendental_resonance_frontend")
