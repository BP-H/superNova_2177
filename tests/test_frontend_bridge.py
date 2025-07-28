import pytest

from frontend_bridge import dispatch_route
from tank_registry import registry


@pytest.mark.asyncio
async def test_list_routes_returns_registered_names():
    result = await dispatch_route("list_routes", {})
    assert set(result["routes"]) == set(registry.list_routes())
