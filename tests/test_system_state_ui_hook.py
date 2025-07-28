import json
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from frontend_bridge import dispatch_route
from db_models import Base, SystemState


@pytest.fixture
def local_db(tmp_path):
    engine = create_engine(
        f"sqlite:///{tmp_path/'sys.db'}", connect_args={"check_same_thread": False}
    )
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = Session()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


class DummyHookManager:
    def __init__(self):
        self.events = []

    async def trigger(self, name, *args, **kwargs):
        self.events.append((name, args, kwargs))


@pytest.mark.asyncio
async def test_log_event_ui_persists(local_db, monkeypatch):
    dummy = DummyHookManager()
    monkeypatch.setattr("system_state_utils.ui_hook.ui_hook_manager", dummy, raising=False)

    payload = {"category": "ui", "payload": {"foo": "bar"}}

    result = await dispatch_route("log_event", payload, db=local_db)

    state = (
        local_db.query(SystemState)
        .filter(SystemState.key == "log:ui")
        .first()
    )
    assert state is not None
    data = json.loads(state.value)
    assert data[-1]["foo"] == "bar"

    assert dummy.events == [(
        "system_state_event_logged",
        ({"category": "ui", "foo": "bar"},),
        {},
    )]
    assert result == {"category": "ui", "foo": "bar"}
