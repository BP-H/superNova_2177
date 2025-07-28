"""Entry point for UI actions triggered by the frontend."""

from __future__ import annotations

import asyncio
import inspect
from typing import Any, Awaitable, Callable, Dict, Optional

from hook_manager import HookManager

# Central action registry powered by :class:`HookManager`
action_manager = HookManager()


def register_action(name: str, func: Callable[..., Any]) -> None:
    """Register ``func`` under the given action ``name``."""
    action_manager.register_hook(name, func)


async def _invoke(func: Callable[..., Any], payload: Dict[str, Any], db: Any) -> Any:
    """Invoke ``func`` handling sync/async semantics."""
    if db is not None:
        result = func(payload, db)
    else:
        result = func(payload)
    if inspect.isawaitable(result):
        return await result
    return result


async def dispatch(action: str, payload: Dict[str, Any], db: Optional[Any] = None, *, background: bool = False) -> Any:
    """Dispatch ``payload`` to the handler registered for ``action``."""

    handlers = action_manager.hooks.get(action)
    if not handlers:
        raise KeyError(action)

    func = handlers[0]

    if background:
        loop = asyncio.get_running_loop()
        return loop.create_task(_invoke(func, payload, db))

    return await _invoke(func, payload, db)

