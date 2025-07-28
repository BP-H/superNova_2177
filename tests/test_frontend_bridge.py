import asyncio
import pytest

import frontend_bridge
from frontend_bridge import (
    dispatch_route,
    ROUTES,
    register_route_once as register_route,
    long_running,
)


@pytest.mark.asyncio
async def test_list_routes_returns_registered_names():
    result = await dispatch_route("list_routes", {})
    assert set(result["routes"]) == set(ROUTES.keys())


@pytest.mark.asyncio
async def test_new_routes_exposed():
    result = await dispatch_route("list_routes", {})
    for name in [
        "trigger_meta_evaluation",
        "auto_flag_stale",
        "run_integrity_analysis",
        "update_reputations",
        "forecast_consensus_agent",
    ]:
        assert name in result["routes"]


@pytest.mark.asyncio
async def test_help_lists_routes_by_category():
    result = await dispatch_route("help", {})
    categories = result["categories"]
    names = {entry["name"] for routes in categories.values() for entry in routes}
    assert names == set(ROUTES.keys())


class DummyAgent:
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
        return self.jobs.get(jid, {"status": "unknown"})


@pytest.mark.asyncio
async def test_long_running_job_enqueued(monkeypatch):
    agent = DummyAgent()
    monkeypatch.setattr(frontend_bridge, "queue_agent", agent)

    async def slow(payload):
        await asyncio.sleep(0)
        return {"value": payload["x"]}

    def handler(payload):
        return long_running(slow(payload))

    register_route("slow_test", handler)
    try:
        job = await dispatch_route("slow_test", {"x": 5})
        assert job == {"job_id": "job1"}
        await asyncio.sleep(0)
        await asyncio.sleep(0)
        status = await dispatch_route("job_status", {"job_id": "job1"})
        assert status == {"status": "done", "result": {"value": 5}}
    finally:
        ROUTES.pop("slow_test", None)
