import inspect
import pytest
from pages.network_analysis_page import network_page

@pytest.mark.asyncio
async def test_network_page_is_async():
    assert inspect.iscoroutinefunction(network_page)
