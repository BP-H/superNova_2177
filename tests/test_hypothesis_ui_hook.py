import pytest

from hypothesis import ui_hook as hyp_ui_hook


class DummyHookManager:
    def __init__(self):
        self.events = []

    async def trigger(self, name, *args, **kwargs):
        self.events.append((name, args, kwargs))


@pytest.mark.asyncio
async def test_rank_hypotheses_ui(monkeypatch):
    dummy = DummyHookManager()
    monkeypatch.setattr(hyp_ui_hook, "ui_hook_manager", dummy, raising=False)

    called = {}

    def fake_rank(db, top_k=5):
        called["args"] = (db, top_k)
        return [{"id": "h1"}]

    monkeypatch.setattr(
        hyp_ui_hook, "_rank_hypotheses_by_confidence", fake_rank, raising=False
    )

    db = object()
    payload = {"top_k": 3}

    result = await hyp_ui_hook.rank_hypotheses_ui(payload, db)

    assert result == {"ranking": [{"id": "h1"}]}
    assert called["args"] == (db, 3)
    assert dummy.events == [("hypothesis_ranking", ([{"id": "h1"}],), {})]


@pytest.mark.asyncio
async def test_synthesize_consensus_ui(monkeypatch):
    dummy = DummyHookManager()
    monkeypatch.setattr(hyp_ui_hook, "ui_hook_manager", dummy, raising=False)

    called = {}

    def fake_synth(ids, db):
        called["args"] = (ids, db)
        return "H_NEW"

    monkeypatch.setattr(
        hyp_ui_hook, "_synthesize_consensus_hypothesis", fake_synth, raising=False
    )

    db = object()
    payload = {"hypothesis_ids": ["h1", "h2"]}

    result = await hyp_ui_hook.synthesize_consensus_ui(payload, db)

    assert result == {"hypothesis_id": "H_NEW"}
    assert called["args"] == (payload["hypothesis_ids"], db)
    assert dummy.events == [("consensus_synthesized", ("H_NEW",), {})]

