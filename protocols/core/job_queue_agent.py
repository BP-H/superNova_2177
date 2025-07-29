from __future__ import annotations

import asyncio
import inspect
import uuid
from typing import Any, Awaitable, Callable, Dict

from .internal_protocol import InternalAgentProtocol


class JobQueueAgent(InternalAgentProtocol):
    """Simple agent that manages async background jobs."""

    def __init__(self) -> None:
        super().__init__()
        self.jobs: Dict[str, Dict[str, Any]] = {}

    def enqueue_job(
        self,
        func: Callable[..., Any],
        *args: Any,
        on_complete: Callable[[Any], Awaitable[None] | None] | None = None,
        **kwargs: Any,
    ) -> str:
        """Schedule ``func`` to run asynchronously and return a job ID."""

        job_id = uuid.uuid4().hex
        self.jobs[job_id] = {"status": "queued", "result": None, "error": None}

        async def runner() -> None:
            self.jobs[job_id]["status"] = "running"
            try:
                result = func(*args, **kwargs)
                if inspect.isawaitable(result):
                    result = await result
                self.jobs[job_id]["status"] = "done"
                self.jobs[job_id]["result"] = result
                if on_complete:
                    result = on_complete(result)
                    if inspect.isawaitable(result):
                        await result
            except Exception as e:  # pragma: no cover - log only
                self.jobs[job_id]["status"] = "error"
                self.jobs[job_id]["error"] = str(e)
                if on_complete:
                    result = on_complete({"error": str(e)})
                    if inspect.isawaitable(result):
                        await result

        asyncio.create_task(runner())
        return job_id

    def get_status(self, job_id: str) -> Dict[str, Any]:
        """Return job status and result if available."""
        return self.jobs.get(job_id, {"status": "unknown"})
