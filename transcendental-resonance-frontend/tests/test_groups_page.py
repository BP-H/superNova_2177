import inspect
import pytest
from pages.groups_page import groups_page

@pytest.mark.asyncio
async def test_groups_page_is_async():
    assert inspect.iscoroutinefunction(groups_page)
