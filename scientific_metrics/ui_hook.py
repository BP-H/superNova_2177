from __future__ import annotations

from typing import Any, Dict

from frontend_bridge import register_route_once
from hook_manager import HookManager
from scientific_metrics import (
    predict_user_interactions,
    calculate_influence_score,
    build_causal_graph,
)

# Exposed hook manager so observers can listen to events
ui_hook_manager = HookManager()


async def predict_user_interactions_ui(
    payload: Dict[str, Any], db, **_: Any
) -> Dict[str, Any]:
    """Return minimal predictions for user actions."""
    user_id = payload.get("user_id")
    window = payload.get("prediction_window_hours", 24)
    result = predict_user_interactions(user_id, db, window)
    minimal = {
        "user_id": user_id,
        "predictions": {
            "will_create_content": result["predictions"]["will_create_content"][
                "probability"
            ],
            "will_like_posts": result["predictions"]["will_like_posts"]["probability"],
            "will_follow_users": result["predictions"]["will_follow_users"][
                "probability"
            ],
        },
    }
    await ui_hook_manager.trigger("user_interaction_prediction", minimal)
    return minimal


async def calculate_influence_ui(
    payload: Dict[str, Any], db, **_: Any
) -> Dict[str, Any]:
    """Compute influence score for a user."""
    user_id = payload.get("user_id")
    graph = build_causal_graph(db)
    result = calculate_influence_score(graph.graph, user_id)
    minimal = {"user_id": user_id, "influence_score": result.get("value", 0.0)}
    await ui_hook_manager.trigger("influence_score_computed", minimal)
    return minimal


# Register routes for the UI
register_route_once(
    "predict_user_interactions",
    predict_user_interactions_ui,
    "Predict user interactions",
    "metrics",
)
register_route_once(
    "calculate_influence",
    calculate_influence_ui,
    "Calculate user influence score",
    "metrics",
)
