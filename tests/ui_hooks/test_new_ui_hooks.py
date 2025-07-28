import pytest

from frontend_bridge import dispatch_route
import hypothesis_meta_evaluator_ui_hook as meta_hook
import hypothesis_reasoner_ui_hook as reasoner_hook
import validation_certifier_ui_hook as cert_hook
import validator_reputation_tracker_ui_hook as rep_hook
from consensus import ui_hook as cf_hook


class DummyManager:
    def __init__(self):
        self.events = []

    async def trigger(self, name, *args, **kwargs):
        self.events.append((name, args, kwargs))


@pytest.mark.asyncio
async def test_trigger_meta_evaluation_route(monkeypatch):
    dummy = DummyManager()
    monkeypatch.setattr(meta_hook, "ui_hook_manager", dummy, raising=False)

    called = {}

    def fake_run(db):
        called["db"] = db
        return "k"

    monkeypatch.setattr(meta_hook, "run_meta_evaluation", fake_run)
    class DummyDB:
        def close(self):
            pass

    dummy_db = DummyDB()
    monkeypatch.setattr(meta_hook, "SessionLocal", lambda: dummy_db)

    result = await dispatch_route("trigger_meta_evaluation", {})

    assert result == {"result_key": "k"}
    assert called["db"] is dummy_db
    assert dummy.events == [("meta_evaluation_run", (result,), {})]


@pytest.mark.asyncio
async def test_auto_flag_stale_route(monkeypatch):
    dummy = DummyManager()
    monkeypatch.setattr(reasoner_hook, "ui_hook_manager", dummy, raising=False)

    called = {}

    def fake_flag(db):
        called["db"] = db
        return ["H1"]

    monkeypatch.setattr(reasoner_hook, "auto_flag_stale_or_redundant", fake_flag)
    class DummyDB:
        def close(self):
            pass

    dummy_db = DummyDB()
    monkeypatch.setattr(reasoner_hook, "SessionLocal", lambda: dummy_db)

    result = await dispatch_route("auto_flag_stale", {})

    assert result == {"flagged": ["H1"]}
    assert called["db"] is dummy_db
    assert dummy.events == [("stale_flagged", (result,), {})]


@pytest.mark.asyncio
async def test_run_integrity_analysis_route(monkeypatch):
    dummy = DummyManager()
    monkeypatch.setattr(cert_hook, "ui_hook_manager", dummy, raising=False)

    called = {}

    def fake_analyze(vals):
        called["vals"] = vals
        return {
            "consensus_score": 0.4,
            "recommended_certification": "strong",
            "integrity_analysis": {"overall_integrity_score": 0.9, "risk_level": "low"},
        }

    monkeypatch.setattr(cert_hook, "analyze_validation_integrity", fake_analyze)

    payload = {"validations": [{"v": 1}]}
    result = await dispatch_route("run_integrity_analysis", payload)

    expected = {
        "consensus_score": 0.4,
        "recommended_certification": "strong",
        "integrity_score": 0.9,
        "risk_level": "low",
    }
    assert result == expected
    assert called["vals"] == payload["validations"]
    assert dummy.events == [("integrity_analysis_run", (expected,), {})]


@pytest.mark.asyncio
async def test_update_reputations_route(monkeypatch):
    dummy = DummyManager()
    monkeypatch.setattr(rep_hook, "ui_hook_manager", dummy, raising=False)

    called = {}

    def fake_update(vals):
        called["vals"] = vals
        return {"reputations": {"v1": 0.5}}

    monkeypatch.setattr(rep_hook, "update_validator_reputations", fake_update)

    payload = {"validations": [{"validator_id": "v1"}]}
    result = await dispatch_route("update_reputations", payload)

    assert result == {"reputations": {"v1": 0.5}}
    assert called["vals"] == payload["validations"]
    assert dummy.events == [("reputation_update", (result,), {})]


@pytest.mark.asyncio
async def test_forecast_consensus_route(monkeypatch):
    dummy = DummyManager()
    monkeypatch.setattr(cf_hook, "ui_hook_manager", dummy, raising=False)

    called = {}

    def fake_forecast(vals, network_analysis=None):
        called["args"] = (vals, network_analysis)
        return {"forecast_score": 0.7, "trend": "increasing"}

    monkeypatch.setattr(cf_hook, "forecast_consensus_trend", fake_forecast)

    payload = {
        "validations": [{"score": 0.6}],
        "network_analysis": {"overall_risk_score": 0.1},
    }
    result = await dispatch_route("forecast_consensus", payload)

    assert result == {"forecast_score": 0.7, "trend": "increasing"}
    assert called["args"] == (payload["validations"], payload["network_analysis"])
    assert dummy.events == [("consensus_forecast_run", (result,), {})]

