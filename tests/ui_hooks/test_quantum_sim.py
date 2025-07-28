import pytest

from frontend_bridge import dispatch_route
import quantum_sim.ui_hook as q_ui


class DummyHookManager:
    def __init__(self):
        self.events = []

    async def trigger(self, name, *args, **kwargs):
        self.events.append((name, args, kwargs))


@pytest.mark.asyncio
async def test_quantum_prediction_route(monkeypatch):
    dummy = DummyHookManager()
    monkeypatch.setattr(q_ui, "ui_hook_manager", dummy, raising=False)

    def fake_engine(uids):
        return {
            "predicted_interactions": {uid: 0.5 for uid in uids},
            "overall_quantum_coherence": 0.7,
            "uncertainty_estimate": 0.2,
        }

    monkeypatch.setattr(q_ui, "quantum_prediction_engine", fake_engine)

    payload = {"user_ids": ["a", "b"]}
    result = await dispatch_route("quantum_prediction", payload)

    assert result == {
        "predicted_interactions": {"a": 0.5, "b": 0.5},
        "overall_quantum_coherence": 0.7,
        "uncertainty_estimate": 0.2,
    }
    assert dummy.events == [("quantum_prediction_run", (result,), {})]

