import pytest

from network.ui_hook import run_coordination_analysis
from hooks import events


class DummyHookManager:
    def __init__(self):
        self.events = []

    def fire_hooks(self, name, *args, **kwargs):
        self.events.append((name, args, kwargs))


@pytest.mark.asyncio
async def test_run_coordination_analysis(monkeypatch):
    dummy = DummyHookManager()
    monkeypatch.setattr("network.ui_hook.hook_manager", dummy, raising=False)

    payload = {
        "validations": [
            {
                "validator_id": "v1",
                "hypothesis_id": "h1",
                "score": 0.9,
                "timestamp": "2025-01-01T00:00:00Z",
                "note": "ok",
            }
        ]
    }

    result = await run_coordination_analysis(payload)

    assert "overall_risk_score" in result  # nosec B101
    assert "flags" in result  # nosec B101
    assert "clusters" in result  # nosec B101
    assert dummy.events == [(events.NETWORK_ANALYSIS, (result,), {})]  # nosec B101


@pytest.mark.asyncio
async def test_run_coordination_analysis_invalid():
    with pytest.raises(ValueError):
        await run_coordination_analysis({"invalid": 1})
