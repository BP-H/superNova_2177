from __future__ import annotations

from typing import Any, Dict

from frontend_bridge import register_route_once
from hook_manager import HookManager
from validation_certifier import analyze_validation_integrity

ui_hook_manager = HookManager()


async def run_integrity_analysis_ui(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Run validation integrity analysis and emit results."""
    validations = payload.get("validations", [])
    result = analyze_validation_integrity(validations)
    minimal = {
        "consensus_score": result.get("consensus_score"),
        "recommended_certification": result.get("recommended_certification"),
        "integrity_score": result.get("integrity_analysis", {}).get(
            "overall_integrity_score"
        ),
        "risk_level": result.get("integrity_analysis", {}).get("risk_level"),
    }
    await ui_hook_manager.trigger("integrity_analysis_run", minimal)
    return minimal


register_route_once(
    "run_integrity_analysis",
    run_integrity_analysis_ui,
    "Analyze validation integrity",
    "audit",
)
