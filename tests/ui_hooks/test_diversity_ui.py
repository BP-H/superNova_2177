import pytest

from frontend_bridge import dispatch_route
from validators.ui_hook import ui_hook_manager


@pytest.mark.asyncio
async def test_compute_diversity_route():
    events = []

    async def listener(data):
        events.append(data)

    ui_hook_manager.register_hook("diversity_score_computed", listener)

    payload = {
        "validations": [
            {"validator_id": "v1", "specialty": "x", "affiliation": "y"},
            {"validator_id": "v2", "specialty": "z", "affiliation": "y"},
        ]
    }

    result = await dispatch_route("compute_diversity", payload)

    assert "diversity_score" in result
    assert events == [result]
