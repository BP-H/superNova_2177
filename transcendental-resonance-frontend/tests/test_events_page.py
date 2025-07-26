import inspect
from pages.events_page import events_page

def test_events_page_is_async():
    assert inspect.iscoroutinefunction(events_page)

def test_events_page_has_search_widgets():
    src = inspect.getsource(events_page)
    assert "ui.input('Search'" in src
    assert "ui.select(['name', 'date']" in src
