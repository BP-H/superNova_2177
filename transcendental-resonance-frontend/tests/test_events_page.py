import inspect
from pages.events_page import events_page

def test_events_page_is_async():
    assert inspect.iscoroutinefunction(events_page)
