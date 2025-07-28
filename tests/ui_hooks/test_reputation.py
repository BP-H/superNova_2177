import pytest

from frontend_bridge import dispatch_route
from validators.ui_hook import ui_hook_manager


@pytest.mark.asyncio
async def test_reputation_analysis_via_router():
    calls = []

    async def listener(data):
        calls.append(data)

    ui_hook_manager.register_hook("reputation_analysis_run", listener)

    payload = {
        "validations": [
            {
                "validator_id": "v1",
                "hypothesis_id": "h1",
                "score": 0.9,
                "timestamp": "2025-01-01T00:00:00Z",
            },
            {
                "validator_id": "v2",
                "hypothesis_id": "h1",
                "score": 0.8,
                "timestamp": "2025-01-01T00:00:00Z",
            },
        ],
        "consensus_scores": {"h1": 0.85},
    }

    result = await dispatch_route("reputation_analysis", payload)

    assert "validator_reputations" in result  # nosec B101
    assert "stats" in result  # nosec B101
    assert calls == [result]  # nosec B101


@pytest.mark.asyncio
async def test_reputation_update_via_router():
    events = []

    async def listener(data):
        events.append(data)

    ui_hook_manager.register_hook("reputation_update_run", listener)

    payload = {
        "validations": [
            {"validator_id": "v1", "score": 0.6},
            {"validator_id": "v1", "score": 0.7},
            {"validator_id": "v2", "score": 0.4},
            {"validator_id": "v2", "score": 0.5},
        ]
    }

    result = await dispatch_route("reputation_update", payload)

    assert "reputations" in result  # nosec B101
    assert "diversity" in result  # nosec B101
    assert "stats" in result  # nosec B101
    assert events == [result]  # nosec B101
