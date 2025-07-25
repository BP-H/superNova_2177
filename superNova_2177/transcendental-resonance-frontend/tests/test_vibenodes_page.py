import inspect
from pages.vibenodes_page import vibenodes_page

def test_vibenodes_page_is_async():
    assert inspect.iscoroutinefunction(vibenodes_page)
