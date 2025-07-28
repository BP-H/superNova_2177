import inspect
from pages.system_insights_page import system_insights_page

def test_system_insights_page_is_async():
    assert inspect.iscoroutinefunction(system_insights_page)
