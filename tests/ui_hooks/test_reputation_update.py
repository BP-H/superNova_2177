import pytest

from frontend_bridge import dispatch_route
from validators.ui_hook import ui_hook_manager


@pytest.mark.asyncio
async def test_reputation_update_via_router():
    calls = []

    async def listener(data):
        calls.append(data)

    ui_hook_manager.register_hook("reputation_update_run", listener)

    payload = {
        "validations": [
            {"validator_id": "v1", "score": 0.9, "certification": "strong"},
            {"validator_id": "v2", "score": 0.7, "certification": "provisional"},
        ]
    }

    result = await dispatch_route("reputation_update", payload)

    assert "reputations" in result
    assert "diversity" in result
    assert calls == [result]
