import pytest

from frontend_bridge import dispatch_route
from consensus.ui_hook import ui_hook_manager
from hooks import events


@pytest.mark.asyncio
async def test_forecast_consensus_via_router():
    received = []

    async def listener(data):
        received.append(data)

    ui_hook_manager.register_hook(events.CONSENSUS_FORECAST_RUN, listener)

    payload = {
        "validations": [
            {"score": 0.1, "timestamp": "2025-01-01T00:00:00Z"},
            {"score": 0.2, "timestamp": "2025-01-02T00:00:00Z"},
            {"score": 0.3, "timestamp": "2025-01-03T00:00:00Z"},
        ]
    }

    result = await dispatch_route("forecast_consensus", payload)

    assert result["trend"] == "increasing"
    assert received == [result]
