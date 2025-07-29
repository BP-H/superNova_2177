# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
"""Interactive debug panel for dispatching frontend routes."""

from __future__ import annotations

import json
from nicegui import ui

from utils.styles import get_theme
from utils.layout import page_container
from frontend_bridge import ROUTES, dispatch_route

# Minimal example payloads for some routes
SAMPLE_PAYLOADS = {
    "rank_hypotheses_by_confidence": {"top_k": 3},
    "register_hypothesis": {"text": "Example hypothesis"},
    "update_hypothesis_score": {
        "hypothesis_id": "H1",
        "new_score": 0.5,
    },
    "forecast_consensus": {"validations": []},
    "coordination_analysis": {"validations": []},
    "temporal_consistency": {"values": [1, 2, 3]},
    "store_prediction": {"prediction": {"foo": 1}},
    "get_prediction": {"prediction_id": "pid123"},
}


@ui.page("/ui/debug_panel")
async def debug_panel_page() -> None:
    """Render controls for invoking ``frontend_bridge`` routes."""
    theme = get_theme()
    with page_container(theme):
        ui.label("Debug Panel").classes("text-2xl font-bold mb-4").style(
            f"color: {theme['accent']};"
        )

        for name, handler in ROUTES.items():
            description = (handler.__doc__ or "").strip().splitlines()[0]
            with ui.expansion(name).classes("w-full mb-2"):
                ui.label(description or "No description").classes("text-sm mb-2")

                payload = json.dumps(SAMPLE_PAYLOADS.get(name, {}), indent=2)
                payload_area = ui.textarea(value=payload).classes("w-full mb-2")
                result_area = ui.textarea(readonly=True).classes("w-full mb-2")

                async def send(name=name, p=payload_area, r=result_area) -> None:
                    try:
                        data = json.loads(p.value or "{}")
                    except json.JSONDecodeError:
                        ui.notify("Invalid JSON", color="negative")
                        return
                    result = await dispatch_route(name, data)
                    r.value = json.dumps(result, indent=2)

                ui.button("Invoke", on_click=send).style(
                    f"background: {theme['primary']}; color: {theme['text']};"
                )

