import pytest

from network import ui_hook as net_ui_hook


@pytest.mark.asyncio
async def test_trigger_coordination_analysis_ui(monkeypatch):
    events = []

    async def listener(data):
        events.append(data)

    net_ui_hook.ui_hook_manager.register_hook("coordination_analysis_run", listener)

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
    assert events == [result]
    assert called["validations"] == payload["validations"]
