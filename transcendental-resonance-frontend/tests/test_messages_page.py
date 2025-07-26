import inspect
import pytest
from pages.messages_page import messages_page

@pytest.mark.asyncio
async def test_messages_page_is_async():
    assert inspect.iscoroutinefunction(messages_page)
