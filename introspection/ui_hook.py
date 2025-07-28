# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
from __future__ import annotations

from typing import Any, Dict

from sqlalchemy.orm import Session

from db_models import SessionLocal
from frontend_bridge import register_route_once
from hook_manager import HookManager
from hooks import events
from protocols.core import JobQueueAgent

from .introspection_pipeline import run_full_audit

# Exposed hook manager so other modules can subscribe to audit events
ui_hook_manager = HookManager()
queue_agent = JobQueueAgent()


async def trigger_full_audit_ui(
    payload: Dict[str, Any], db: Session, **_: Any
) -> Dict[str, Any]:
    """Run a full introspection audit triggered from the UI.

    Parameters
    ----------
    payload : dict
        Dictionary containing ``"hypothesis_id"`` key specifying the hypothesis to audit.
    db : Session
        Database session used during the audit.

    Returns
    -------
    dict
        Structured audit bundle produced by :func:`run_full_audit`.
    """
    hypothesis_id = payload["hypothesis_id"]  # raises KeyError if missing

    audit_bundle = run_full_audit(hypothesis_id, db)

    # Allow external listeners to process the audit result asynchronously
    await ui_hook_manager.trigger(events.FULL_AUDIT_COMPLETED, audit_bundle)

    return audit_bundle


async def queue_full_audit_ui(payload: Dict[str, Any]) -> Dict[str, str]:
    """Queue a full audit job and return its job identifier."""
    hypothesis_id = payload["hypothesis_id"]

    async def job() -> Dict[str, Any]:
        db = SessionLocal()
        try:
            return run_full_audit(hypothesis_id, db)
        finally:
            db.close()

    async def done(result: Any) -> None:
        await ui_hook_manager.trigger("full_audit_completed", result)

    job_id = queue_agent.enqueue_job(job, on_complete=done)
    return {"job_id": job_id}


async def poll_full_audit_ui(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Return the status of a previously queued full audit."""
    job_id = payload.get("job_id", "")
    return queue_agent.get_status(job_id)


register_route_once(
    "queue_full_audit",
    queue_full_audit_ui,
    "Queue a full audit job",
    "introspection",
)
register_route_once(
    "poll_full_audit",
    poll_full_audit_ui,
    "Poll status of a full audit job",
    "introspection",
)
register_route_once(
    "trigger_full_audit",
    trigger_full_audit_ui,
    "Run a full introspection audit",
    "introspection",
)
