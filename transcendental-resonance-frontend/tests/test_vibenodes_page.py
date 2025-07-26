import inspect
import pytest
from pages.vibenodes_page import vibenodes_page

@pytest.mark.asyncio
async def test_vibenodes_page_is_async():
    assert inspect.iscoroutinefunction(vibenodes_page)
