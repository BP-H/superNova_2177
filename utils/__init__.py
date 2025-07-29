"""Compatibility wrapper exposing frontend utilities under ``utils`` package."""

from importlib import import_module

_frontend_utils = import_module("transcendental_resonance_frontend.src.utils")

__all__ = getattr(_frontend_utils, "__all__", [])

def __getattr__(name: str):
    return getattr(_frontend_utils, name)

# expose common modules directly
from . import api, layout, styles, demo_data  # noqa: F401
