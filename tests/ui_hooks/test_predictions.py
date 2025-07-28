import pytest

import prediction.ui_hook as pred_ui_hook
import predictions.ui_hook as legacy_hook
from frontend_bridge import dispatch_route


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

    def schedule_annual_audit_proposal(self):
        self.calls.append(("schedule",))
        return "audit123"


@pytest.mark.asyncio
async def test_prediction_routes_dispatch(monkeypatch):
    mgr = DummyManager()
    monkeypatch.setattr(pred_ui_hook, "prediction_manager", mgr, raising=False)
    monkeypatch.setattr(legacy_hook, "prediction_manager", mgr, raising=False)

    db_dummy = object()

    # store
    result = await dispatch_route(
        "store_prediction", {"prediction": {"foo": 1}}, db=db_dummy
    )
    assert result == {"prediction_id": "pid123"}
    # get
    result2 = await dispatch_route(
        "get_prediction", {"prediction_id": "pid123"}, db=db_dummy
    )
    # schedule audit
    result_sched = await dispatch_route("schedule_audit_proposal", {}, db=db_dummy)
    assert result2 == {"prediction_id": "pid123", "data": {"foo": 1}}
    # update
    result3 = await dispatch_route(
        "update_prediction_status",
        {"prediction_id": "pid123", "status": "done", "actual_outcome": {"a": 1}},
    )
    assert result3 == {"prediction_id": "pid123", "status": "done"}

    assert result_sched == {"proposal_id": "audit123"}

    assert mgr.calls == [
        ("store", {"foo": 1}),
        ("get", "pid123"),
        ("schedule",),
        ("update", "pid123", "done", {"a": 1}),
    ]
