# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
import pytest

from frontend_bridge import dispatch_route
import diversity_analyzer.ui_hook as da_hook


class DummyManager:
    def __init__(self):
        self.events = []

    async def trigger(self, name, *args, **kwargs):
        self.events.append((name, args, kwargs))


@pytest.mark.asyncio
async def test_diversity_score_route(monkeypatch):
    dummy = DummyManager()
    monkeypatch.setattr(da_hook, "ui_hook_manager", dummy, raising=False)

    called = {}

    def fake_compute(vals):
        called["vals"] = vals
        return {"diversity_score": 0.8, "flags": ["ok"]}

    monkeypatch.setattr(da_hook, "compute_diversity_score", fake_compute)

    payload = {"validations": [{"validator_id": "v1"}]}
    result = await dispatch_route("diversity_score", payload)

    assert result == {"diversity_score": 0.8, "flags": ["ok"]}
    assert called["vals"] == payload["validations"]
    assert dummy.events == [("diversity_score", (result,), {})]


@pytest.mark.asyncio
async def test_certify_validations_route(monkeypatch):
    dummy = DummyManager()
    monkeypatch.setattr(da_hook, "ui_hook_manager", dummy, raising=False)

    called = {}

    def fake_certify(vals):
        called["vals"] = vals
        return {
            "consensus_score": 0.6,
            "recommended_certification": "strong",
            "flags": ["f"],
        }

    monkeypatch.setattr(da_hook, "certify_validations", fake_certify)

    payload = {"validations": [{"validator_id": "v2"}]}
    result = await dispatch_route("certify_validations", payload)

    assert result == {
        "consensus_score": 0.6,
        "recommended_certification": "strong",
        "flags": ["f"],
    }
    assert called["vals"] == payload["validations"]
    assert dummy.events == [("certify_validations", (result,), {})]
