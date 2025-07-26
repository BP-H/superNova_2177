import inspect
import pytest
from pages.events_page import events_page

@pytest.mark.asyncio
async def test_events_page_is_async():
    assert inspect.iscoroutinefunction(events_page)
