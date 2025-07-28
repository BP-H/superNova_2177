from __future__ import annotations

from typing import List, Dict, Any

from hook_manager import HookManager
from .network_coordination_detector import analyze_coordination_patterns

# Hook manager allowing observers to react to coordination analysis events
ui_hook_manager = HookManager()


async def trigger_coordination_analysis(data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Run ``analyze_coordination_patterns`` on ``data`` and emit a hook.

    Parameters
    ----------
    data:
        List of validation dictionaries passed from the UI layer.

    Returns
    -------
    dict
        The full coordination analysis result.
    """
    result = analyze_coordination_patterns(data)
    await ui_hook_manager.trigger("coordination_analysis_run", result)
    return result
