import inspect
from pages.proposals_page import proposals_page

def test_proposals_page_is_async():
    assert inspect.iscoroutinefunction(proposals_page)
