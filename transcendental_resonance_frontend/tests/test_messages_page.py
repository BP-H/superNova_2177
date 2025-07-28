import inspect
from pages.messages_page import messages_page

def test_messages_page_is_async():
    assert inspect.iscoroutinefunction(messages_page)
