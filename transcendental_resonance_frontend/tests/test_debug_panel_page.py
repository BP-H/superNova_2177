import inspect
from pages.debug_panel_page import debug_panel_page


def test_debug_panel_page_is_async():
    assert inspect.iscoroutinefunction(debug_panel_page)


def test_debug_panel_page_uses_routes():
    source = inspect.getsource(debug_panel_page)
    assert "ROUTES" in source
