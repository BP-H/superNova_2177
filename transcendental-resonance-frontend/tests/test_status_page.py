import inspect
import pytest
from pages.status_page import status_page

@pytest.mark.asyncio
async def test_status_page_is_async():
    assert inspect.iscoroutinefunction(status_page)
