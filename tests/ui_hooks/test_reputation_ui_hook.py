import pytest

from protocols.utils.messaging import MessageHub
from validators.ui_hook import update_reputations_ui


@pytest.mark.asyncio
async def test_update_reputations_ui_emits_and_returns(monkeypatch):
    hub = MessageHub()
    monkeypatch.setattr("validators.ui_hook.message_bus", hub, raising=False)

    received = []
    hub.subscribe("reputation_update", lambda msg: received.append(msg.data))

    vals = [
        {"validator_id": "v1", "score": 0.7},
        {"validator_id": "v1", "score": 0.8},
    ]

    result = await update_reputations_ui(vals)

    assert result["reputations"]  # reputations returned
    assert len(received) == 2
    assert received[0]["status"] == "start"
    assert received[1]["status"] == "complete"
