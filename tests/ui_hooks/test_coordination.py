import pytest

from frontend_bridge import dispatch
from network.ui_hook import ui_hook_manager


@pytest.mark.asyncio
async def test_coordination_analysis_via_router():
    calls = []

    async def listener(data):
        calls.append(data)

    ui_hook_manager.register_hook("coordination_analysis_run", listener)

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

    result = await dispatch("network.run", payload)

    assert "overall_risk_score" in result  # nosec B101
    assert "graph" in result  # nosec B101
    assert calls == [result]  # nosec B101
