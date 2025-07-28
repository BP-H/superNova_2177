import pytest

from frontend_bridge import dispatch_route
from validators.ui_hook import ui_hook_manager


@pytest.mark.asyncio
async def test_compute_diversity_route():
    events = []

    async def listener(data):
        events.append(data)

    ui_hook_manager.register_hook("diversity_score_computed", listener)

    payload = {
        "validations": [
            {"validator_id": "v1", "specialty": "x", "affiliation": "y"},
            {"validator_id": "v2", "specialty": "z", "affiliation": "y"},
        ]
    }

    result = await dispatch_route("compute_diversity", payload)

    assert "diversity_score" in result  # nosec B101
    assert events == [result]  # nosec B101


@pytest.mark.asyncio
async def test_diversity_certify_route(monkeypatch):
    events = []

    async def listener(data):
        events.append(data)

    from diversity.ui_hook import ui_hook_manager

    ui_hook_manager.register_hook("diversity_certified", listener)

    called = {}

    def fake_certify(vals):
        called["vals"] = vals
        return {
            "consensus_score": 0.7,
            "recommended_certification": "provisional",
            "diversity": {"diversity_score": 0.4},
        }

    monkeypatch.setattr("diversity.ui_hook.certify_validations", fake_certify)

    payload = {"validations": [{"validator_id": "v"}]}
    result = await dispatch_route("diversity_certify", payload)

    expected = {
        "consensus_score": 0.7,
        "recommended_certification": "provisional",
        "diversity_score": 0.4,
    }
    assert result == expected  # nosec B101
    assert events == [expected]  # nosec B101
    assert called["vals"] == payload["validations"]  # nosec B101
