from __future__ import annotations

import inspect
import logging
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Dict, List, Optional, Union

Handler = Callable[..., Union[Dict[str, Any], Awaitable[Dict[str, Any]]]]


@dataclass
class TankManifest:
    """Describe available routes and metadata for a tank."""

    routes: Dict[str, Handler] = field(default_factory=dict)
    payload_schema: Optional[Dict[str, Any]] = None
    mutable: bool = False
    source: str = ""


class TankRegistry:
    """Central registry for UI route handlers."""

    def __init__(self) -> None:
        self.routes: Dict[str, Handler] = {}
        self.sources: Dict[str, str] = {}

    def register_route_once(self, name: str, handler: Handler, source: str) -> None:
        """Register ``handler`` for ``name`` if not already present."""
        if name in self.routes:
            if self.routes[name] is not handler:
                logging.warning(
                    "Route '%s' from %s already registered by %s",
                    name,
                    source,
                    self.sources[name],
                )
            return
        self.routes[name] = handler
        self.sources[name] = source
        logging.debug("Registered route '%s' from %s", name, source)

    async def dispatch(self, name: str, payload: Dict[str, Any], **kwargs: Any) -> Dict[str, Any]:
        """Dispatch ``payload`` to registered ``name`` handler."""
        if name not in self.routes:
            raise KeyError(name)
        handler = self.routes[name]
        result = handler(payload, **kwargs)
        if inspect.isawaitable(result):
            result = await result
        return result

    def list_routes(self) -> List[str]:
        return sorted(self.routes.keys())


registry = TankRegistry()


def register_route(name: str, func: Handler) -> None:
    """Backward compatible alias to register a route once."""
    registry.register_route_once(name, func, getattr(func, "__module__", ""))


async def dispatch_route(name: str, payload: Dict[str, Any], **kwargs: Any) -> Dict[str, Any]:
    """Dispatch through the global registry."""
    return await registry.dispatch(name, payload, **kwargs)
