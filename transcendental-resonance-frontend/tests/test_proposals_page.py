import inspect
import pytest
from pages.proposals_page import proposals_page

@pytest.mark.asyncio
async def test_proposals_page_is_async():
    assert inspect.iscoroutinefunction(proposals_page)
