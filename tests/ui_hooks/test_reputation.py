import pytest

from frontend_bridge import dispatch_route
from validators.ui_hook import ui_hook_manager


@pytest.mark.asyncio
async def test_reputation_update_via_router():
    calls = []

    async def listener(data):
        calls.append(data)

    ui_hook_manager.register_hook("validator_reputations_updated", listener)

    payload = {
        "validations": [
            {"validator_id": "v1", "score": 0.8},
            {"validator_id": "v1", "score": 0.9},
        ]
    }

    result = await dispatch_route("reputation_update", payload)

    assert "validator_count" in result  # nosec B101
    assert "avg_reputation" in result  # nosec B101
    assert calls == [result]  # nosec B101
