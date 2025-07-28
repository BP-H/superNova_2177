import pytest

from frontend_bridge import dispatch_route
from proposals.engine import DEFAULT_PROPOSALS, ProposalEngine
from ui_hooks import universe_ui


class DummyHookManager:
    def __init__(self):
        self.events = []

    async def trigger(self, name, *args, **kwargs):
        self.events.append((name, args, kwargs))


class DummyUniverseManager:
    def __init__(self):
        self.calls = []

    def get_overview(self, uid):
        self.calls.append(("overview", uid))
        return {"id": uid}

    def get_karma(self, user_id):
        self.calls.append(("karma", user_id))
        return 42

    def get_state(self, uid):
        self.calls.append(("state", uid))
        return {"status": "ok"}

    def submit_proposal(self, uid, proposal):
        self.calls.append(("submit", uid, proposal))
        return "p1"


class DummyProposalEngine:
    def __init__(self):
        self.calls = []

    def list_proposals(self, karma, state):
        self.calls.append(("list", karma, state))
        return [{"pid": "p1"}]


@pytest.mark.asyncio
async def test_universe_ui_routes(monkeypatch):
    hook_mgr = DummyHookManager()
    um = DummyUniverseManager()
    pe = DummyProposalEngine()
    monkeypatch.setattr(universe_ui, "ui_hook_manager", hook_mgr, raising=False)
    monkeypatch.setattr(universe_ui, "universe_manager", um, raising=False)
    monkeypatch.setattr(universe_ui, "proposal_engine", pe, raising=False)

    result1 = await dispatch_route("get_universe_overview", {"universe_id": "U1"})
    assert result1 == {"id": "U1"}

    payload = {"user_id": "u", "universe_id": "U1"}
    result2 = await dispatch_route("list_available_proposals", payload)
    assert result2 == {"proposals": [{"pid": "p1"}]}

    result3 = await dispatch_route(
        "submit_universe_proposal", {"universe_id": "U1", "proposal": {"a": 1}}
    )
    assert result3 == {"proposal_id": "p1"}

    assert um.calls == [
        ("overview", "U1"),
        ("karma", "u"),
        ("state", "U1"),
        ("submit", "U1", {"a": 1}),
    ]
    assert pe.calls == [("list", 42, {"status": "ok"})]
    assert hook_mgr.events == [
        ("universe_overview_returned", ({"id": "U1"},), {}),
        ("proposal_list_returned", ([{"pid": "p1"}],), {}),
        ("proposal_submitted", ({"proposal_id": "p1"},), {}),
    ]


@pytest.mark.asyncio
async def test_universe_ui_with_real_engine(monkeypatch):
    hook_mgr = DummyHookManager()
    um = DummyUniverseManager()
    engine = ProposalEngine(min_karma=10)
    monkeypatch.setattr(universe_ui, "ui_hook_manager", hook_mgr, raising=False)
    monkeypatch.setattr(universe_ui, "universe_manager", um, raising=False)
    monkeypatch.setattr(universe_ui, "proposal_engine", engine, raising=False)

    payload = {"user_id": "u", "universe_id": "U1"}
    result = await dispatch_route("list_available_proposals", payload)

    assert len(result["proposals"]) == len(DEFAULT_PROPOSALS)
    assert hook_mgr.events == [("proposal_list_returned", (result["proposals"],), {})]
