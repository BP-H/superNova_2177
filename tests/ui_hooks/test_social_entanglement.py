# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
import pytest

from frontend_bridge import dispatch_route
import social.ui_hook as social_hook


class DummyHookManager:
    def __init__(self):
        self.events = []

    async def trigger(self, name, *args, **kwargs):
        self.events.append((name, args, kwargs))


@pytest.mark.asyncio
async def test_simulate_entanglement_route(monkeypatch):
    dummy = DummyHookManager()
    monkeypatch.setattr(social_hook, "ui_hook_manager", dummy, raising=False)

    called = {}

    def fake_sim(db, u1, u2):
        called["args"] = (db, u1, u2)
        return {"influence": 0.42}

    monkeypatch.setattr(social_hook, "simulate_social_entanglement", fake_sim)

    db = object()
    payload = {"user1_id": 1, "user2_id": 2}
    result = await dispatch_route("simulate_entanglement", payload, db=db)

    assert result == {"influence": 0.42}
    assert called["args"] == (db, 1, 2)
    assert dummy.events == [("social_entanglement", (result,), {})]
