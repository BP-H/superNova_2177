import inspect
from pages.ai_assist_page import ai_assist_page

def test_ai_assist_page_is_async():
    assert inspect.iscoroutinefunction(ai_assist_page)
