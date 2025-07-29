"""Proxy package exposing frontend utilities at the repo root."""

from transcendental_resonance_frontend.src.utils import (
    api as api_module,
    layout as layout_module,
    styles as styles_module,
    demo_data as demo_data_module,
)  # type: ignore
import sys

# expose submodules under the ``utils`` namespace
sys.modules.setdefault(__name__ + '.api', api_module)
sys.modules.setdefault(__name__ + '.layout', layout_module)
sys.modules.setdefault(__name__ + '.styles', styles_module)
sys.modules.setdefault(__name__ + '.demo_data', demo_data_module)

api = api_module
layout = layout_module
styles = styles_module
demo_data = demo_data_module

__all__ = ["api", "layout", "styles", "demo_data"]
