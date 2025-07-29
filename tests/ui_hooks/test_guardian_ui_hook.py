# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
import pytest

from frontend_bridge import dispatch_route
import protocols.agents.guardian_ui_hook as ui_hook
from hooks import events
from protocols.agents.guardian_interceptor_agent import GuardianInterceptorAgent


class DummyHookManager:
    def __init__(self):
        self.events = []

    async def trigger(self, name, *args, **kwargs):
        self.events.append((name, args, kwargs))


@pytest.mark.asyncio
async def test_guardian_routes(monkeypatch):
    dummy = DummyHookManager()
    agent = GuardianInterceptorAgent()
    monkeypatch.setattr(ui_hook, "guardian_hook_manager", dummy, raising=False)
    monkeypatch.setattr(ui_hook, "guardian_agent", agent, raising=False)

    payload = {"content": "delete file"}
    judgment = await dispatch_route("inspect_suggestion", payload)
    assert judgment["risk_level"] == "HIGH"
    assert dummy.events == [(events.SUGGESTION_INSPECTED, (judgment,), {})]

    fix_payload = {"issue": "bug", "context": "ctx"}
    patch = await dispatch_route("propose_fix", fix_payload)
    assert "patch" in patch
    assert dummy.events[-1] == (events.FIX_PROPOSED, (patch,), {})
