import inspect
from pages.notifications_page import notifications_page

def test_notifications_page_is_async():
    assert inspect.iscoroutinefunction(notifications_page)
