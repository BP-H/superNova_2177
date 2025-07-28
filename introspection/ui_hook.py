from __future__ import annotations

from typing import Any, Dict

from sqlalchemy.orm import Session

from hook_manager import HookManager

from .introspection_pipeline import run_full_audit

# Exposed hook manager so other modules can subscribe to audit events
ui_hook_manager = HookManager()


async def trigger_full_audit_ui(payload: Dict[str, Any], db: Session) -> Dict[str, Any]:
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
    await ui_hook_manager.trigger("full_audit_completed", audit_bundle)

    return audit_bundle
