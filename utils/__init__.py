"""Compatibility wrapper exposing frontend utilities under ``utils`` package."""

from importlib import import_module
import sys

_frontend_utils = import_module("transcendental_resonance_frontend.src.utils")

__all__ = getattr(_frontend_utils, "__all__", [])
__path__ = _frontend_utils.__path__

# expose submodules for package-style imports
for name in ["features", "layout", "styles", "api", "demo_data", "loading_overlay", "error_overlay", "api_status_footer", "safe_markdown"]:
    if f"utils.{name}" not in sys.modules:
        sys.modules[f"utils.{name}"] = import_module(f"transcendental_resonance_frontend.src.utils.{name}")

def __getattr__(name: str):
    return getattr(_frontend_utils, name)

# expose common modules directly
from . import api, layout, styles, demo_data  # noqa: F401
