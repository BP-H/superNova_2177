from __future__ import annotations

from typing import Any, Dict

from db_models import SessionLocal
from hook_manager import HookManager
from frontend_bridge import register_route_once
from hypothesis_meta_evaluator import run_meta_evaluation

ui_hook_manager = HookManager()


async def trigger_meta_evaluation_ui(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Run meta-evaluation and emit an event."""
    db = SessionLocal()
    try:
        key = run_meta_evaluation(db)
    finally:
        db.close()
    result = {"result_key": key}
    await ui_hook_manager.trigger("meta_evaluation_run", result)
    return result


register_route_once(
    "trigger_meta_evaluation",
    trigger_meta_evaluation_ui,
    "Run meta evaluation",
    "hypothesis",
)
