import pytest

from frontend_bridge import dispatch_route
from consensus.ui_hook import ui_hook_manager


@pytest.mark.asyncio
async def test_forecast_consensus_via_router():
    events = []

    async def listener(data):
        events.append(data)

    ui_hook_manager.register_hook("consensus_forecast_run", listener)

    payload = {
        "validations": [
            {"score": 0.1, "timestamp": "2025-01-01T00:00:00Z"},
            {"score": 0.2, "timestamp": "2025-01-02T00:00:00Z"},
            {"score": 0.3, "timestamp": "2025-01-03T00:00:00Z"},
        ]
    }

    result = await dispatch_route("forecast_consensus", payload)

    assert result["trend"] == "increasing"
    assert events == [result]
