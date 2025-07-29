import pytest
import logging

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


@pytest.mark.asyncio
async def test_quantum_prediction_route_handles_non_dict(monkeypatch, caplog):
    dummy = DummyHookManager()
    monkeypatch.setattr(q_ui, "ui_hook_manager", dummy, raising=False)

    def bad_engine(uids):
        return "oops"

    monkeypatch.setattr(q_ui, "quantum_prediction_engine", bad_engine)

    with caplog.at_level(logging.WARNING):
        result = await dispatch_route("quantum_prediction", {"user_ids": ["x"]})

    assert result == {
        "predicted_interactions": {},
        "overall_quantum_coherence": 0.0,
        "uncertainty_estimate": 0.0,
    }
    assert dummy.events == [("quantum_prediction_run", (result,), {})]
    assert any("non-dict" in rec.message for rec in caplog.records)

