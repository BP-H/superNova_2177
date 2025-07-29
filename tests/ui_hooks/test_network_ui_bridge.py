# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
import pytest

from network import ui_hook as net_ui_hook
from hooks import events


@pytest.mark.asyncio
async def test_trigger_coordination_analysis_ui(monkeypatch):
    received = []

    async def listener(data):
        received.append(data)

    net_ui_hook.ui_hook_manager.register_hook(events.COORDINATION_ANALYSIS_RUN, listener)

    called = {}

    def fake_analyze(validations):
        called["validations"] = validations
        return {
            "overall_risk_score": 0.5,
            "graph": {"nodes": [], "edges": []},
            "flags": ["ok"],
        }

    monkeypatch.setattr(net_ui_hook, "analyze_coordination_patterns", fake_analyze)

    payload = {"validations": [{"validator_id": "v", "hypothesis_id": "h"}]}

    result = await net_ui_hook.trigger_coordination_analysis_ui(payload)

    assert result == {"overall_risk_score": 0.5, "graph": {"nodes": [], "edges": []}}
    assert received == [result]
    assert called["validations"] == payload["validations"]
