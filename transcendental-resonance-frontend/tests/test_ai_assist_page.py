import inspect
import pytest
from pages.ai_assist_page import ai_assist_page

@pytest.mark.asyncio
async def test_ai_assist_page_is_async():
    assert inspect.iscoroutinefunction(ai_assist_page)
