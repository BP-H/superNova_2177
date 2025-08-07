"""Unified pages package for tests.

This package exposes Streamlit pages located in the
``transcendental_resonance_frontend`` namespace so that tests can simply
import modules from ``pages``.
"""

from pathlib import Path

_root = Path(__file__).resolve().parent.parent
__path__ = [
    str(_root / "transcendental_resonance_frontend" / "pages"),
    str(_root / "transcendental_resonance_frontend" / "src" / "pages"),
]
