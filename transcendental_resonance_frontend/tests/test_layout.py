import inspect
from utils.layout import search_widget, page_container


def test_search_widget_defined():
    assert inspect.isfunction(search_widget)


def test_search_widget_uses_combined_search():
    src = inspect.getsource(search_widget)
    assert "combined_search" in src


def test_page_container_calls_search_widget():
    src = inspect.getsource(page_container)
    assert "search_widget()" in src
