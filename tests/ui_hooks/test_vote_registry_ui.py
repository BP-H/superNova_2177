import pytest

from frontend_bridge import dispatch_route
from vote_registry import _VOTES


class DummyHookManager:
    def __init__(self):
        self.events = []

    async def trigger(self, name, *args, **kwargs):
        self.events.append((name, args, kwargs))


@pytest.mark.asyncio
async def test_record_and_load_votes(monkeypatch):
    dummy = DummyHookManager()
    monkeypatch.setattr('vote_registry.ui_hook.ui_hook_manager', dummy, raising=False)

    _VOTES.clear()
    vote = {"validator_id": "v1", "species": "human", "vote": "yes"}

    res_record = await dispatch_route("record_vote", vote)
    assert res_record == {"recorded": True}
    assert dummy.events == [("vote_recorded", (vote,), {})]

    res_load = await dispatch_route("load_votes", {})
    assert res_load == {"votes": [vote]}
    assert dummy.events[-1] == ("votes_loaded", (res_load,), {})
