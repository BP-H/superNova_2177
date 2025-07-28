import pytest

from frontend_bridge import dispatch_route, ROUTES_BY_CATEGORY


@pytest.mark.asyncio
async def test_list_routes_groups_and_describes():
    result = await dispatch_route("list_routes", {})

    returned = [
        entry["name"]
        for entries in result["routes"].values()
        for entry in entries
    ]
    expected = [name for entries in ROUTES_BY_CATEGORY.values() for name, _ in entries]
    assert set(returned) == set(expected)

    for entries in result["routes"].values():
        for entry in entries:
            assert "description" in entry
            assert isinstance(entry["description"], str)
