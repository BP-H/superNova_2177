"""Proxy package exposing NiceGUI utilities."""
from importlib import import_module
import sys

__all__ = ["layout", "api", "styles", "demo_data"]


def __getattr__(name: str):
    if name in __all__:
        module = import_module(f"transcendental_resonance_frontend.src.utils.{name}")
        sys.modules[f"utils.{name}"] = module
        return module
    raise AttributeError(name)
