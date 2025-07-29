# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
import pytest

from diversity.ui_hook import diversity_analysis_ui


class DummyHookManager:
    def __init__(self):
        self.events = []

    async def trigger(self, name, *args, **kwargs):
        self.events.append((name, args, kwargs))


@pytest.mark.asyncio
async def test_diversity_analysis_ui(monkeypatch):
    dummy = DummyHookManager()
    monkeypatch.setattr("diversity.ui_hook.ui_hook_manager", dummy, raising=False)

    called = {}

    def fake_certify(vals):
        called["vals"] = vals
        return {
            "consensus_score": 0.8,
            "recommended_certification": "strong",
            "diversity": {"diversity_score": 0.5},
        }

    monkeypatch.setattr("diversity.ui_hook.certify_validations", fake_certify)

    payload = {"validations": [{"validator_id": "v"}]}
    result = await diversity_analysis_ui(payload)

    expected = {
        "consensus_score": 0.8,
        "recommended_certification": "strong",
        "diversity_score": 0.5,
    }
    assert result == expected  # nosec B101
    assert called["vals"] == payload["validations"]  # nosec B101
    assert dummy.events == [("diversity_certified", (expected,), {})]  # nosec B101


@pytest.mark.asyncio
async def test_diversity_analysis_ui_invalid():
    with pytest.raises(ValueError):
        await diversity_analysis_ui({"validations": "foo"})
