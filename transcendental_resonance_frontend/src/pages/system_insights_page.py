# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
"""Detailed system insights metrics page."""

from nicegui import ui
from utils.api import TOKEN, api_call
from utils.layout import page_container, navigation_bar
from utils.styles import get_theme

from .login_page import login_page


@ui.page("/system-insights")
async def system_insights_page():
    """Render global epistemic metrics and entropy details."""
    if not TOKEN:
        ui.open(login_page)
        return

    THEME = get_theme()
    with page_container(THEME):
        if TOKEN:
            navigation_bar()
        ui.label("System Insights").classes("text-2xl font-bold mb-4").style(
            f'color: {THEME["accent"]};'
        )

        entropy_label = ui.label().classes("mb-2")
        uncertainty_label = ui.label().classes("mb-2")
        hypotheses_label = ui.label().classes("mb-2")

        async def refresh_metrics() -> None:
            state = await api_call("GET", "/api/global-epistemic-state") or {}
            details = await api_call("GET", "/system/entropy-details") or {}

            entropy_label.text = f"Entropy: {details.get('current_entropy', 'N/A')}"
            uncertainty_label.text = f"Uncertainty: {state.get('uncertainty', 'N/A')}"
            hypotheses_label.text = (
                f"Active Hypotheses: {state.get('active_hypotheses', 'N/A')}"
            )

        await refresh_metrics()
        ui.timer(10, lambda: ui.run_async(refresh_metrics()))
