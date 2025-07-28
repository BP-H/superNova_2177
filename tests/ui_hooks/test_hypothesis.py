import json
import pytest

from frontend_bridge import dispatch_route
from hypothesis.ui_hook import ui_hook_manager
from hypothesis_tracker import (
    register_hypothesis,
    update_hypothesis_score,
    _get_hypothesis_record,
)
from tests.conftest import _setup_sqlite
from sqlalchemy import create_engine
from db_models import SystemState
import hypothesis_reasoner


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


@pytest.fixture(autouse=True)
def config_patch(monkeypatch):
    monkeypatch.setattr(hypothesis_reasoner, "CONFIG", type("C", (), {"TEXT_SIMILARITY_THRESHOLD": 0.7})())
    yield


def _sync_state(db, hyp_id):
    record = _get_hypothesis_record(db, hyp_id)
    if record is None:
        return
    record = dict(record)
    record["hypothesis_id"] = record.pop("id")
    db.add(SystemState(key=f"hypothesis_{hyp_id}", value=json.dumps(record)))
    db.commit()


@pytest.mark.asyncio
async def test_hypothesis_ui_routes(patched_db):
    events = []

    async def ranking_listener(data):
        events.append(("rank", data))

    async def conflict_listener(data):
        events.append(("conflict", data))

    ui_hook_manager.register_hook("hypothesis_ranking", ranking_listener)
    ui_hook_manager.register_hook("hypothesis_conflicts", conflict_listener)

    h1 = register_hypothesis("same text", patched_db)
    h2 = register_hypothesis("same text", patched_db)
    h3 = register_hypothesis("different text", patched_db)

    update_hypothesis_score(patched_db, h1, 0.9)
    update_hypothesis_score(patched_db, h2, 0.1)
    update_hypothesis_score(patched_db, h3, 0.5)

    _sync_state(patched_db, h1)
    _sync_state(patched_db, h2)
    _sync_state(patched_db, h3)

    ranking = await dispatch_route("rank_hypotheses_by_confidence", {"top_k": 2})
    assert len(ranking["ranking"]) == 2
    assert events[0] == ("rank", ranking["ranking"])

    conflicts = await dispatch_route("detect_conflicting_hypotheses", {})
    assert events[1] == ("conflict", conflicts["conflicts"])
    assert any(set(pair) == {h1, h2} for pair in conflicts["conflicts"])


@pytest.mark.asyncio
async def test_rank_and_synthesize_routes(patched_db, monkeypatch):
    h1 = register_hypothesis("alpha", patched_db)
    h2 = register_hypothesis("beta", patched_db)

    update_hypothesis_score(patched_db, h1, 0.8)
    update_hypothesis_score(patched_db, h2, 0.4)

    _sync_state(patched_db, h1)
    _sync_state(patched_db, h2)

    ranking = await dispatch_route("rank_hypotheses", {"top_k": 1})
    assert ranking["ranking"] and ranking["ranking"][0]["hypothesis_id"] in {h1, h2}

    monkeypatch.setattr(
        "hypothesis.ui_hook._synthesize_consensus_hypothesis", lambda ids, db: "NEW_HYP"
    )
    synth = await dispatch_route(
        "synthesize_consensus",
        {"hypothesis_ids": [h1, h2]},
    )
    assert synth == {"hypothesis_id": "NEW_HYP"}
