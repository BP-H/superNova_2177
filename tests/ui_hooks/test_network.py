import pytest

from frontend_bridge import dispatch_route


@pytest.mark.asyncio
async def test_coordination_analysis_bridge_returns_keys():
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

    result = await dispatch_route("coordination_analysis", payload)

    assert "overall_risk_score" in result  # nosec B101
    assert "graph" in result  # nosec B101
