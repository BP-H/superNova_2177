import pytest

from frontend_bridge import dispatch_route, ROUTES


@pytest.mark.asyncio
async def test_list_routes_returns_registered_names():
    result = await dispatch_route("list_routes", {})
    assert set(result["routes"]) == set(ROUTES.keys())
