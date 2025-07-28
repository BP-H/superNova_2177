from __future__ import annotations

from typing import Any, Dict

from frontend_bridge import register_route
from hook_manager import HookManager
from hooks import events

from .guardian_interceptor_agent import GuardianInterceptorAgent

# Exposed hook manager and agent instance
guardian_hook_manager = HookManager()
guardian_agent = GuardianInterceptorAgent()


async def inspect_suggestion_ui(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Inspect a suggestion from the UI via ``GuardianInterceptorAgent``."""
    result = guardian_agent.inspect_suggestion(payload)
    await guardian_hook_manager.trigger(events.SUGGESTION_INSPECTED, result)
    return result


async def propose_fix_ui(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Propose a fix for an issue via ``GuardianInterceptorAgent``."""
    result = guardian_agent.propose_fix(payload)
    await guardian_hook_manager.trigger(events.FIX_PROPOSED, result)
    return result


# Register with the central frontend router
register_route(
    "inspect_suggestion",
    inspect_suggestion_ui,
    description="Inspect a suggestion",
    category="guardian",
)
register_route(
    "propose_fix",
    propose_fix_ui,
    description="Propose a guardian fix",
    category="guardian",
)
