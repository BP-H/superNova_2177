import pytest

from frontend_bridge import ROUTES, dispatch_route


@pytest.mark.asyncio
async def test_list_routes_returns_registered_names():
    result = await dispatch_route("list_routes", {})
    names = {r["name"] for r in result["routes"]}
    assert names == set(ROUTES.keys())
    for r in result["routes"]:
        assert {"category", "name", "doc"} <= r.keys()
