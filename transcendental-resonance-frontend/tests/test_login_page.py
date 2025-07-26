import inspect
import pytest
from pages.login_page import login_page

@pytest.mark.asyncio
async def test_login_page_is_async():
    assert inspect.iscoroutinefunction(login_page)
