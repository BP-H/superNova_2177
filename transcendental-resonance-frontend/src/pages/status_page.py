"""System status metrics page."""

from nicegui import ui

from utils.api import api_call, THEME


@ui.page('/status')
async def status_page():
    """Display real-time system metrics."""
    with ui.column().classes('w-full p-4').style(
        f'background: {THEME["gradient"]}; color: {THEME["text"]};'
    ):
        ui.label('System Status').classes('text-2xl font-bold mb-4').style(
            f'color: {THEME["accent"]};'
        )

        async def refresh_status():
            status = api_call('GET', '/status')
            if status:
                ui.label(f"Status: {status['status']}").classes('mb-2')
                ui.label(
                    f"Total Harmonizers: {status['metrics']['total_harmonizers']}"
                ).classes('mb-2')
                ui.label(
                    f"Total VibeNodes: {status['metrics']['total_vibenodes']}"
                ).classes('mb-2')
                ui.label(
                    f"Entropy: {status['metrics']['current_system_entropy']}"
                ).classes('mb-2')

        await refresh_status()
        ui.timer(60, refresh_status)
