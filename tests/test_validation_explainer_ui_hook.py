# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
import pytest
from sqlalchemy import create_engine

from frontend_bridge import dispatch_route
import audit_explainer.ui_hook as ui_hook
from tests.conftest import _setup_sqlite


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


@pytest.mark.asyncio
async def test_explain_validation_route(patched_db, monkeypatch):
    events = []

    async def listener(data):
        events.append(data)

    ui_hook.ui_hook_manager.register_hook("validation_explained", listener)

    called = {}

    def fake_explain(hid, vid, db):
        called["args"] = (hid, vid, db)
        return {"summary": "ok"}

    monkeypatch.setattr(ui_hook, "explain_validation_reasoning", fake_explain)

    payload = {"hypothesis_id": "H1", "validation_id": 42}
    result = await dispatch_route("explain_validation_reasoning", payload, db=patched_db)

    assert result == {"summary": "ok"}
    assert called["args"] == ("H1", 42, patched_db)
    assert events == [result]
