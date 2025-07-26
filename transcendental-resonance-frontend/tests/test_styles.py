import importlib
from utils.styles import apply_global_styles


def test_apply_global_styles_injects_css(stub_nicegui):
    apply_global_styles()
    assert "futuristic-gradient" in stub_nicegui.head_html

