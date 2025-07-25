import inspect
from pages.status_page import status_page

def test_status_page_is_async():
    assert inspect.iscoroutinefunction(status_page)
