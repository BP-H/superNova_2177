import pytest

from frontend_bridge import dispatch_route


@pytest.mark.asyncio
async def test_list_routes_contains_all_registered():
    result = await dispatch_route("list_routes", {})
    routes = set(result["routes"])
    expected = {
        "coordination_analysis",
        "queue_coordination_analysis",
        "poll_coordination_analysis",
        "forecast_consensus",
        "queue_consensus_forecast",
        "poll_consensus_forecast",
        "reputation_analysis",
        "update_validator_reputations",
        "reputation_update",
        "compute_diversity",
        "queue_full_audit",
        "poll_full_audit",
        "cross_universe_register_bridge",
        "cross_universe_get_provenance",
        "inspect_suggestion",
        "propose_fix",
        "generate_midi",
    }
    assert expected.issubset(routes)  # nosec B101
