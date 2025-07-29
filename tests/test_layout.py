# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
import pytest

nicegui = pytest.importorskip("nicegui")
try:
    from nicegui.element import Element
except Exception:
    pytest.skip("nicegui.element not available", allow_module_level=True)

from utils.layout import page_container


def test_page_container_returns_element():
    cm = page_container()
    assert hasattr(cm, "__enter__") and hasattr(cm, "__exit__")
    with cm as element:
        assert isinstance(element, Element)

