"""Unified feed combining VibeNodes, Events, and Notifications."""

from nicegui import ui

from utils.api import TOKEN, api_call
from utils.layout import page_container, navigation_bar
from utils.styles import get_theme

from .login_page import login_page


@ui.page('/feed')
async def feed_page() -> None:
    """Display a combined feed of recent activity."""
    if not TOKEN:
        ui.open(login_page)
        return

    theme = get_theme()
    with page_container(theme):
        if TOKEN:
            navigation_bar()
        ui.label('Feed').classes('text-2xl font-bold mb-4').style(
            f'color: {theme["accent"]};'
        )

        feed_column = ui.column().classes('w-full')

        async def refresh_feed() -> None:
            vibenodes = await api_call('GET', '/vibenodes/') or []
            events = await api_call('GET', '/events/') or []
            notifs = await api_call('GET', '/notifications/') or []

            feed_column.clear()
            for vn in vibenodes:
                with feed_column:
                    with ui.card().classes('w-full mb-2').style('border: 1px solid #333; background: #1e1e1e;'):
                        ui.label('VibeNode').classes('text-sm font-bold')
                        ui.label(vn.get('description', '')).classes('text-sm')
                        ui.link('View', f"/vibenodes/{vn['id']}")
            for ev in events:
                with feed_column:
                    with ui.card().classes('w-full mb-2').style('border: 1px solid #333; background: #1e1e1e;'):
                        ui.label('Event').classes('text-sm font-bold')
                        ui.label(ev.get('description', '')).classes('text-sm')
                        ui.link('View', f"/events/{ev['id']}")
            for n in notifs:
                with feed_column:
                    with ui.card().classes('w-full mb-2').style('border: 1px solid #333; background: #1e1e1e;'):
                        ui.label('Notification').classes('text-sm font-bold')
                        ui.label(n.get('message', '')).classes('text-sm')
                        ui.link('View', f"/notifications/{n['id']}")

        await refresh_feed()
