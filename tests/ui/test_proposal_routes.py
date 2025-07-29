# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
import pytest
from sqlalchemy import create_engine

from frontend_bridge import dispatch_route
import proposals.ui_hook as proposals_ui
import vote_registry.ui_hook as vote_ui
from vote_registry import _VOTES
from tests.conftest import _setup_sqlite


class DummyHookManager:
    def __init__(self):
        self.events = []

    async def trigger(self, name, *args, **kwargs):
        self.events.append((name, args, kwargs))


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
async def test_proposal_routes(monkeypatch, patched_db):
    prop_dummy = DummyHookManager()
    vote_dummy = DummyHookManager()
    monkeypatch.setattr(proposals_ui, "ui_hook_manager", prop_dummy, raising=False)
    monkeypatch.setattr(vote_ui, "ui_hook_manager", vote_dummy, raising=False)

    _VOTES.clear()

    list_empty = await dispatch_route("list_proposals", {})
    assert list_empty == {"proposals": []}
    assert prop_dummy.events[-1] == ("proposals_listed", (list_empty,), {})

    create_payload = {"title": "Test", "author_id": 1, "description": ""}
    res_create = await dispatch_route("create_proposal", create_payload)
    assert "proposal_id" in res_create
    assert prop_dummy.events[-1] == ("proposal_created", (res_create,), {})

    list_after = await dispatch_route("list_proposals", {})
    assert len(list_after["proposals"]) == 1

    vote_payload = {"proposal_id": res_create["proposal_id"], "harmonizer_id": 2, "vote": "yes"}
    res_vote = await dispatch_route("vote_proposal", vote_payload)
    assert "vote_id" in res_vote
    assert prop_dummy.events[-1] == (
        "proposal_voted",
        ({"proposal_id": vote_payload["proposal_id"], "vote_id": res_vote["vote_id"]},),
        {},
    )

    await dispatch_route("record_vote", {"validator_id": "v1", "species": "human", "vote": "yes"})
    votes_res = await dispatch_route("load_votes", {})
    assert votes_res == {"votes": [{"validator_id": "v1", "species": "human", "vote": "yes"}]}
    assert vote_dummy.events[-1] == ("votes_loaded", (votes_res,), {})


@pytest.mark.asyncio
async def test_proposal_route_validation(monkeypatch, patched_db):
    monkeypatch.setattr(proposals_ui, "ui_hook_manager", DummyHookManager(), raising=False)
    with pytest.raises(ValueError):
        await dispatch_route("create_proposal", {"title": "Only title"})
    with pytest.raises(ValueError):
        await dispatch_route("vote_proposal", {"proposal_id": 1})
