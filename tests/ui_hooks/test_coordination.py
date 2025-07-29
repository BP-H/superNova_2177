# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
import pytest

from frontend_bridge import dispatch_route
from network.ui_hook import ui_hook_manager
from hooks import events


@pytest.mark.asyncio
async def test_coordination_analysis_via_router():
    calls = []

    async def listener(data):
        calls.append(data)

    ui_hook_manager.register_hook(events.COORDINATION_ANALYSIS_RUN, listener)

    payload = {
        "validations": [
            {
                "validator_id": "v1",
                "hypothesis_id": "h1",
                "score": 0.9,
                "timestamp": "2025-01-01T00:00:00Z",
                "note": "ok",
            }
        ]
    }

    result = await dispatch_route("coordination_analysis", payload, db=object())

    assert "overall_risk_score" in result  # nosec B101
    assert "graph" in result  # nosec B101
    assert calls == [result]  # nosec B101
