from layout import build_layout
from nicegui import element


def test_build_layout_returns_ui_element():
    layout_el = build_layout()
    assert isinstance(layout_el, element.Element)
