"""Compatibility wrapper for running ``web_ui`` as a module."""

import warnings
from runpy import run_module

warnings.warn(
    "The 'web_ui' package has been renamed to 'transcendental_resonance_frontend'.",
    DeprecationWarning,
    stacklevel=2,
)
run_module("transcendental_resonance_frontend", run_name="__main__")
