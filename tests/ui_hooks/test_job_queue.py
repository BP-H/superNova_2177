import asyncio
import pytest
from unittest.mock import MagicMock

from frontend_bridge import dispatch_route
import introspection.ui_hook as iuh
import network.ui_hook as nethook
import consensus.ui_hook as conhook


class DummyJobAgent:
    def __init__(self):
        self.jobs = {}

    def enqueue_job(self, func, *args, on_complete=None, **kwargs):
        job_id = "job1"

        async def runner():
            result = await func(*args, **kwargs)
            self.jobs[job_id] = {"status": "done", "result": result}
            if on_complete:
                await on_complete(result)

        asyncio.create_task(runner())
        return job_id

    def get_status(self, jid):
        return self.jobs[jid]


class DummyHookManager:
    def __init__(self, events):
        self.events = events

    async def trigger(self, name, payload):
        self.events.append(payload)


@pytest.mark.asyncio
async def test_queue_full_audit_and_poll(monkeypatch):
    events = []
    dummy_agent = DummyJobAgent()
    monkeypatch.setattr(iuh, "queue_agent", dummy_agent, raising=False)
    monkeypatch.setattr(iuh, "ui_hook_manager", DummyHookManager(events), raising=False)
    monkeypatch.setattr(iuh, "run_full_audit", lambda hid, db: {"bundle": True})

    job = await dispatch_route("queue_full_audit", {"hypothesis_id": "H"})
    assert job == {"job_id": "job1"}
    await asyncio.sleep(0)
    status = await dispatch_route("poll_full_audit", {"job_id": "job1"})
    assert status == {"status": "done", "result": {"bundle": True}}
    assert events == [{"bundle": True}]


@pytest.mark.asyncio
async def test_queue_coordination_analysis_and_poll(monkeypatch):
    events = []
    dummy_agent = DummyJobAgent()
    monkeypatch.setattr(nethook, "queue_agent", dummy_agent, raising=False)
    monkeypatch.setattr(nethook, "ui_hook_manager", DummyHookManager(events), raising=False)
    monkeypatch.setattr(nethook, "analyze_coordination_patterns", lambda v: {"overall_risk_score": 1.0, "graph": {}})

    job = await dispatch_route("queue_coordination_analysis", {"validations": []})
    assert job == {"job_id": "job1"}
    await asyncio.sleep(0)
    status = await dispatch_route("poll_coordination_analysis", {"job_id": "job1"})
    assert status == {"status": "done", "result": {"overall_risk_score": 1.0, "graph": {}}}
    assert events == [{"overall_risk_score": 1.0, "graph": {}}]


@pytest.mark.asyncio
async def test_queue_consensus_forecast_and_poll(monkeypatch):
    events = []
    dummy_agent = DummyJobAgent()
    monkeypatch.setattr(conhook, "queue_agent", dummy_agent, raising=False)
    monkeypatch.setattr(conhook, "ui_hook_manager", DummyHookManager(events), raising=False)
    monkeypatch.setattr(conhook, "forecast_consensus_trend", lambda v, n: {"forecast_score": 0.5, "trend": "up"})

    job = await dispatch_route("queue_consensus_forecast", {"validations": []})
    assert job == {"job_id": "job1"}
    await asyncio.sleep(0)
    status = await dispatch_route("poll_consensus_forecast", {"job_id": "job1"})
    assert status == {"status": "done", "result": {"forecast_score": 0.5, "trend": "up"}}
    assert events == [{"forecast_score": 0.5, "trend": "up"}]
