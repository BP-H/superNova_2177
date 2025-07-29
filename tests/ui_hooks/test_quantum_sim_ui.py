import pytest

import quantum_sim.ui_hook as qhook
from frontend_bridge import dispatch_route
from hooks import events


class DummyManager:
    def __init__(self):
        self.events = []

    async def trigger(self, name, payload):
        self.events.append((name, payload))


@pytest.mark.asyncio
async def test_simulate_entanglement_route(monkeypatch):
    dummy = DummyManager()
    monkeypatch.setattr(qhook, "ui_hook_manager", dummy, raising=False)
    from frontend_bridge import ROUTES

    ROUTES["simulate_entanglement"] = qhook.simulate_entanglement_ui

    called = {}

    class DummyMod:
        @staticmethod
        def simulate_social_entanglement(db, u1, u2):
            called["args"] = (db, u1, u2)
            return {"source": u1, "target": u2, "probabilistic_influence": 0.5}

    monkeypatch.setattr(qhook, "import_module", lambda name: DummyMod)

    class DummyDB:
        pass

    db = DummyDB()
    payload = {"user1_id": 1, "user2_id": 2}

    result = await dispatch_route("simulate_entanglement", payload, db=db)

    assert result == {
        "source": 1,
        "target": 2,
        "probabilistic_influence": 0.5,
    }  # nosec B101
    assert called["args"] == (db, 1, 2)  # nosec B101
    assert dummy.events == [(events.ENTANGLEMENT_SIMULATION_RUN, result)]  # nosec B101


@pytest.mark.asyncio
async def test_simulate_entanglement_missing(monkeypatch):
    monkeypatch.setattr(qhook, "ui_hook_manager", DummyManager(), raising=False)

    class DummyDB:
        pass

    db = DummyDB()
    with pytest.raises(KeyError):
        await dispatch_route("simulate_entanglement", {"user1_id": 1}, db=db)


@pytest.mark.asyncio
async def test_simulate_entanglement_import_error(monkeypatch):
    monkeypatch.setattr(qhook, "ui_hook_manager", DummyManager(), raising=False)
    from frontend_bridge import ROUTES

    ROUTES["simulate_entanglement"] = qhook.simulate_entanglement_ui

    def bad_import(name):
        raise ImportError("missing")

    monkeypatch.setattr(qhook, "import_module", bad_import)

    result = await dispatch_route(
        "simulate_entanglement",
        {"user1_id": 1, "user2_id": 2},
        db=object(),
    )

    assert "unavailable" in result.get("error", "")  # nosec B101


@pytest.mark.asyncio
async def test_simulate_entanglement_attribute_error(monkeypatch):
    monkeypatch.setattr(qhook, "ui_hook_manager", DummyManager(), raising=False)
    from frontend_bridge import ROUTES

    ROUTES["simulate_entanglement"] = qhook.simulate_entanglement_ui

    class DummyMod:
        pass

    monkeypatch.setattr(qhook, "import_module", lambda name: DummyMod)

    result = await dispatch_route(
        "simulate_entanglement",
        {"user1_id": 1, "user2_id": 2},
        db=object(),
    )

    assert "unavailable" in result.get("error", "")  # nosec B101
