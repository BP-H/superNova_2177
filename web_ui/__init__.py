import warnings
from importlib import import_module

warnings.warn(
    "The 'web_ui' package has been renamed to 'transcendental_resonance_frontend'.",
    DeprecationWarning,
    stacklevel=2,
)
module = import_module('transcendental_resonance_frontend')
globals().update(module.__dict__)
