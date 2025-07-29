import inspect
from pages.feed_page import feed_page


def test_feed_page_is_async():
    assert inspect.iscoroutinefunction(feed_page)
