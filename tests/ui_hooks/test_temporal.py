# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
import pytest

from frontend_bridge import dispatch_route
from temporal.ui_hook import ui_hook_manager


@pytest.mark.asyncio
async def test_temporal_analysis_via_router():
    events = []

    async def listener(data):
        events.append(data)

    ui_hook_manager.register_hook("temporal_analysis_run", listener)

    payload = {
        "validations": [
            {"timestamp": "2025-01-01T00:00:00Z", "score": 0.5}
        ]
    }

    result = await dispatch_route("temporal_consistency", payload)

    assert "avg_delay_hours" in result
    assert "consensus_volatility" in result
    assert events == [result]
