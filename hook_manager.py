import asyncio
import inspect
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Dict, List


@dataclass
class HookManager:
    """Mystical plugin bus to orchestrate quantum hooks across the metaverse."""

    hooks: Dict[str, List[Callable[..., Any]]] = field(
        default_factory=lambda: defaultdict(list)
    )

    def register_hook(self, name: str, func: Callable[..., Any]) -> None:
        """Safely register a hook callback under a cosmic name."""
        if not callable(func):
            raise TypeError("Hook must be callable")
        self.hooks[name].append(func)
        logging.debug("🔮 Registered hook '%s' -> %s", name, getattr(func, "__name__", repr(func)))

    async def _invoke(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        try:
            if inspect.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            result = func(*args, **kwargs)
            if inspect.isawaitable(result):
                return await result
            return result
        except Exception:  # pragma: no cover - we log but never raise
            logging.exception("💥 Hook '%s' raised an exception", getattr(func, "__name__", repr(func)))
            return None

    async def trigger(self, name: str, *args: Any, **kwargs: Any) -> List[Any]:
        """Invoke all callbacks bound to *name* with given arguments."""
        callbacks = list(self.hooks.get(name, []))
        logging.debug("✨ Triggering hook '%s' with %d callbacks", name, len(callbacks))
        results: List[Any] = []
        for func in callbacks:
            result = await self._invoke(func, *args, **kwargs)
            results.append(result)
            logging.debug(
                "🌠 Hook '%s' executed %s -> %r",
                name,
                getattr(func, "__name__", repr(func)),
                result,
            )
        return results

    def fire_hooks(self, name: str, *args: Any, **kwargs: Any) -> List[Any]:
        """Public entry point to trigger hooks synchronously or asynchronously."""
        coro = self.trigger(name, *args, **kwargs)
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(coro)
        else:
            return loop.run_until_complete(coro)

    def dump_hooks(self) -> Dict[str, List[str]]:
        """Inspect current hook bindings for audit clarity."""
        return {n: [getattr(f, "__name__", repr(f)) for f in cbs] for n, cbs in self.hooks.items()}
