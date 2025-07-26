import inspect
import pytest
from pages.notifications_page import notifications_page

@pytest.mark.asyncio
async def test_notifications_page_is_async():
    assert inspect.iscoroutinefunction(notifications_page)
