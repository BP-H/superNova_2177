# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
import pytest

from consensus import ui_hook as cons_ui_hook
from hooks import events


class DummyHookManager:
    def __init__(self):
        self.events = []

    async def trigger(self, name, *args, **kwargs):
        self.events.append((name, args, kwargs))


@pytest.mark.asyncio
async def test_forecast_consensus_ui(monkeypatch):
    dummy = DummyHookManager()
    monkeypatch.setattr("consensus.ui_hook.ui_hook_manager", dummy, raising=False)

    called = {}

    def fake_forecast(validations, network_analysis=None):
        called["args"] = (validations, network_analysis)
        return {"forecast_score": 0.7, "trend": "increasing"}

    monkeypatch.setattr(cons_ui_hook, "forecast_consensus_trend", fake_forecast)

    payload = {
        "validations": [{"score": 0.6}],
        "network_analysis": {"overall_risk_score": 0.1},
    }

    result = await cons_ui_hook.forecast_consensus_ui(payload)

    assert result == {"forecast_score": 0.7, "trend": "increasing"}
    assert called["args"] == (payload["validations"], payload["network_analysis"])
    assert dummy.events == [(events.CONSENSUS_FORECAST_RUN, (result,), {})]
