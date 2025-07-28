"""Deprecated compatibility shim for the old ``web_ui`` package.

This module forwards imports to :mod:`transcendental_resonance_frontend` and
emits a :class:`DeprecationWarning`. It will be removed in a future release.
"""

import warnings
from importlib import import_module

warnings.warn(
    "The 'web_ui' package has been renamed to 'transcendental_resonance_frontend'.",
    DeprecationWarning,
    stacklevel=2,
)
module = import_module('transcendental_resonance_frontend')
globals().update(module.__dict__)
