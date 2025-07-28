import pytest

from frontend_bridge import dispatch_route, ROUTES
import importlib


class DummyManager:
    def __init__(self):
        self.events = []

    async def trigger(self, name, *args, **kwargs):
        self.events.append((name, args, kwargs))


@pytest.mark.asyncio
async def test_compute_diversity_route_minimal(monkeypatch):
    da_hook = importlib.import_module("diversity_analyzer.ui_hook")
    dummy = DummyManager()
    monkeypatch.setattr(da_hook, "ui_hook_manager", dummy, raising=False)

    def fake_compute(vals):
        return {"diversity_score": 0.8, "flags": []}

    monkeypatch.setattr(da_hook, "compute_diversity_score", fake_compute)

    # ensure our handler is registered for this test only
    monkeypatch.setitem(ROUTES, "compute_diversity", da_hook.compute_diversity_ui)

    payload = {"validations": [{"validator_id": "v"}]}
    result = await dispatch_route("compute_diversity", payload)

    assert result == {"diversity_score": 0.8, "flags": []}
    assert dummy.events == [("diversity_score_computed", (result,), {})]


@pytest.mark.asyncio
async def test_certify_validations_route_minimal(monkeypatch):
    da_hook = importlib.import_module("diversity_analyzer.ui_hook")
    dummy = DummyManager()
    monkeypatch.setattr(da_hook, "ui_hook_manager", dummy, raising=False)

    def fake_certify(vals):
        return {
            "consensus_score": 0.6,
            "recommended_certification": "strong",
        }

    monkeypatch.setattr(da_hook, "certify_validations", fake_certify)

    monkeypatch.setitem(ROUTES, "certify_validations", da_hook.certify_validations_ui)

    payload = {"validations": [{"v": 1}]}
    result = await dispatch_route("certify_validations", payload)

    assert result == {
        "consensus_score": 0.6,
        "recommended_certification": "strong",
    }
    assert dummy.events == [("validations_certified", (result,), {})]
