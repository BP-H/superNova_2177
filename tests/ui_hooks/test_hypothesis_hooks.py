import pytest

from hypothesis import ui_hook as hyp_ui_hook
from hypothesis_tracker import _get_hypothesis_record
from tests.conftest import _setup_sqlite
from sqlalchemy import create_engine


@pytest.fixture
def patched_db(tmp_path, monkeypatch):
    monkeypatch.setattr(create_engine, "__module__", "sqlalchemy.engine", raising=False)
    engine, SessionLocal, teardown = _setup_sqlite(monkeypatch, tmp_path / "test.db")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        teardown()

class DummyHookManager:
    def __init__(self):
        self.events = []

    async def trigger(self, name, *args, **kwargs):
        self.events.append((name, args, kwargs))

@pytest.mark.asyncio
async def test_register_hypothesis_ui_and_update(patched_db, monkeypatch):
    dummy = DummyHookManager()
    monkeypatch.setattr(hyp_ui_hook, "hook_manager", dummy, raising=False)

    payload = {"text": "test hypothesis"}
    hid = await hyp_ui_hook.register_hypothesis_ui(payload, patched_db)
    assert isinstance(hid, str)

    record = _get_hypothesis_record(patched_db, hid)
    assert record is not None
    assert dummy.events == [("hypothesis_registered", ({"hypothesis_id": hid},), {})]

    update_payload = {"hypothesis_id": hid, "score": 0.8, "status": "validated"}
    res = await hyp_ui_hook.update_hypothesis_score_ui(update_payload, patched_db)
    assert res is True

    updated = _get_hypothesis_record(patched_db, hid)
    assert updated["score"] == 0.8
    assert updated["status"] == "validated"
    assert dummy.events[-1] == (
        "hypothesis_score_updated",
        ({"hypothesis_id": hid, "score": 0.8, "status": "validated"},),
        {},
    )

