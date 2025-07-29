"""System status metrics page."""

from nicegui import ui
from utils.api import api_call
from utils.layout import page_container, navigation_bar
from utils.styles import get_theme


@ui.page("/status")
async def status_page():
    """Display real-time system metrics."""
    THEME = get_theme()
    with page_container(THEME):
        if TOKEN:
            navigation_bar()
        ui.label("System Status").classes("text-2xl font-bold mb-4").style(
            f'color: {THEME["accent"]};'
        )

        status_label = ui.label().classes("mb-2")
        harmonizers_label = ui.label().classes("mb-2")
        vibenodes_label = ui.label().classes("mb-2")
        entropy_label = ui.label().classes("mb-2")

        async def refresh_status() -> None:
            status = await api_call("GET", "/status")
            if status:
                status_label.text = f"Status: {status['status']}"
                harmonizers_label.text = (
                    f"Total Harmonizers: {status['metrics']['total_harmonizers']}"
                )
                vibenodes_label.text = (
                    f"Total VibeNodes: {status['metrics']['total_vibenodes']}"
                )
                entropy_label.text = (
                    f"Entropy: {status['metrics']['current_system_entropy']}"
                )

        await refresh_status()
        ui.timer(5, lambda: ui.run_async(refresh_status()))
