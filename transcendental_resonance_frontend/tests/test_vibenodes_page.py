import inspect
from pages.vibenodes_page import vibenodes_page

def test_vibenodes_page_is_async():
    assert inspect.iscoroutinefunction(vibenodes_page)

def test_vibenodes_page_has_search_widgets():
    src = inspect.getsource(vibenodes_page)
    assert "ui.input('Search'" in src
    assert "ui.select(['name', 'date']" in src
