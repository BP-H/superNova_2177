import inspect
import pytest
from pages.profile_page import profile_page

@pytest.mark.asyncio
async def test_profile_page_is_async():
    assert inspect.iscoroutinefunction(profile_page)
