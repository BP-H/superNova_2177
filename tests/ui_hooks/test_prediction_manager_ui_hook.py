import pytest

from frontend_bridge import dispatch_route
import prediction_manager.ui_hook as pm_ui_hook


class DummyManager:
    def __init__(self):
        self.calls = []

    def store_prediction(self, data):
        self.calls.append(("store", data))
        return "pid123"

    def get_prediction(self, pid):
        self.calls.append(("get", pid))
        return {"prediction_id": pid, "status": "created", "data": {"foo": 1}}

    def update_prediction_status(self, pid, status, actual_outcome=None):
        self.calls.append(("update", pid, status, actual_outcome))
        return None


@pytest.mark.asyncio
async def test_prediction_manager_routes(monkeypatch):
    mgr = DummyManager()
    monkeypatch.setattr(pm_ui_hook, "prediction_manager", mgr, raising=False)

    result = await dispatch_route("store_prediction", {"prediction": {"foo": 1}})
    assert result == {"prediction_id": "pid123"}

    result2 = await dispatch_route("get_prediction", {"prediction_id": "pid123"})
    assert result2 == {"prediction_id": "pid123", "status": "created"}

    result3 = await dispatch_route(
        "update_prediction_status",
        {"prediction_id": "pid123", "status": "done", "actual_outcome": {"a": 1}},
    )
    assert result3 == {"prediction_id": "pid123", "status": "done"}

    assert mgr.calls == [
        ("store", {"foo": 1}),
        ("get", "pid123"),
        ("update", "pid123", "done", {"a": 1}),
    ]
