import inspect
import pytest
from pages.upload_page import upload_page

@pytest.mark.asyncio
async def test_upload_page_is_async():
    assert inspect.iscoroutinefunction(upload_page)
