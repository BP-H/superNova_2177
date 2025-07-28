import pytest

from frontend_bridge import dispatch_route, ROUTES


@pytest.mark.asyncio
async def test_list_routes_returns_registered_names():
    result = await dispatch_route("list_routes", {})
    assert set(result["routes"]) == set(ROUTES.keys())


@pytest.mark.asyncio
async def test_new_routes_exposed():
    result = await dispatch_route("list_routes", {})
    for name in [
        "trigger_meta_evaluation",
        "auto_flag_stale",
        "run_integrity_analysis",
        "update_reputations",
        "forecast_consensus_agent",
    ]:
        assert name in result["routes"]
