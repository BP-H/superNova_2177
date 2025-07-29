"""Streamlit entry point to launch the NiceGUI-based Transcendental Resonance UI."""

from __future__ import annotations

import sys
from importlib import import_module
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Importing the package starts the NiceGUI app via src.main
import_module("transcendental_resonance_frontend")
