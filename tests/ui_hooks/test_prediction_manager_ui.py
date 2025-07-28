import pytest

from frontend_bridge import dispatch_route
from prediction_manager import ui_hook as pm_ui_hook


class DummyManager:
    def __init__(self) -> None:
        self.calls = []

    def store_prediction(self, data):
        self.calls.append(("store", data))
        return "pid42"

    def get_prediction(self, pid):
        self.calls.append(("get", pid))
        return {"prediction_id": pid, "data": {"bar": 2}}


@pytest.mark.asyncio
async def test_prediction_manager_routes(monkeypatch):
    mgr = DummyManager()
    monkeypatch.setattr(pm_ui_hook, "prediction_manager", mgr, raising=False)

    res1 = await dispatch_route("save_prediction", {"prediction": {"bar": 2}})
    assert res1 == {"prediction_id": "pid42"}

    res2 = await dispatch_route("get_saved_prediction", {"prediction_id": "pid42"})
    assert res2 == {"prediction_id": "pid42", "data": {"bar": 2}}

    assert mgr.calls == [("store", {"bar": 2}), ("get", "pid42")]
