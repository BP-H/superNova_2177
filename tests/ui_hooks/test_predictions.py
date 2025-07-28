import pytest

from frontend_bridge import dispatch_route
import predictions.ui_hook as pred_ui_hook


class DummyManager:
    def __init__(self):
        self.calls = []

    def store_prediction(self, data):
        self.calls.append(("store", data))
        return "pid123"

    def get_prediction(self, pid):
        self.calls.append(("get", pid))
        return {"prediction_id": pid, "data": {"foo": 1}}

    def update_prediction_status(self, pid, status, actual_outcome=None):
        self.calls.append(("update", pid, status, actual_outcome))
        return None


@pytest.mark.asyncio
async def test_prediction_routes_dispatch(monkeypatch):
    mgr = DummyManager()
    monkeypatch.setattr(pred_ui_hook, "prediction_manager", mgr, raising=False)

    # store
    result = await dispatch_route("store_prediction", {"prediction": {"foo": 1}})
    assert result == {"prediction_id": "pid123"}
    # get
    result2 = await dispatch_route("get_prediction", {"prediction_id": "pid123"})
    assert result2 == {"prediction_id": "pid123", "data": {"foo": 1}}
    # update
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
