"""Aggregate UI hook modules and dispatch events to handlers."""

from __future__ import annotations

from typing import Any, Awaitable, Callable, Dict, List, Union

from hook_manager import HookManager

Handler = Callable[[Dict[str, Any]], Union[Dict[str, Any], Awaitable[Dict[str, Any]]]]

# Central hook manager used to register all UI handlers
hook_manager = HookManager()


def register_route(name: str, func: Handler) -> None:
    """Register *func* as the handler for the given route ``name``."""
    hook_manager.register_hook(name, func)


async def dispatch_route(name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Dispatch ``payload`` to the handler bound to ``name``."""
    if name not in hook_manager.hooks:
        raise KeyError(name)
    results: List[Dict[str, Any]] = await hook_manager.trigger(name, payload)
    return results[0] if results else {}


# Backwards compatible API
dispatch = dispatch_route
register = register_route


def _load_builtin_hooks() -> None:
    """Import builtin hook modules so their routes register."""
    try:  # network hooks automatically register themselves
        __import__("network.ui_hook")
    except Exception:  # pragma: no cover - optional in minimal installs
        pass

    try:  # audit hooks need explicit registration
        from audit.ui_hook import log_hypothesis_ui, attach_trace_ui

        register_route("log_hypothesis", log_hypothesis_ui)
        register_route("attach_trace", attach_trace_ui)
    except Exception:  # pragma: no cover - optional dependency
        pass


_load_builtin_hooks()

