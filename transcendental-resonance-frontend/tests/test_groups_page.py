import inspect
from pages.groups_page import groups_page

def test_groups_page_is_async():
    assert inspect.iscoroutinefunction(groups_page)
