import inspect
from pages.introspection_page import introspection_page


def test_introspection_page_is_async():
    assert inspect.iscoroutinefunction(introspection_page)


def test_introspection_page_has_widgets():
    src = inspect.getsource(introspection_page)
    assert "ui.input('Hypothesis ID'" in src or "ui.input(\"Hypothesis ID\"" in src
    assert "ui.button('Run Audit'" in src
