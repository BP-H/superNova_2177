"""Unified feed combining VibeNodes, Events, and Notifications."""

from nicegui import ui

from utils.api import TOKEN, api_call
from utils.layout import page_container, navigation_bar
from utils.styles import get_theme
from components.media_renderer import render_media_block
from components.social_ui import create_post_composer

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

        post_type, post_content = create_post_composer(theme)
        ui.separator().classes('my-2')

        feed_column = ui.column().classes('w-full')
        loading_column = ui.column().classes('w-full')

        async def refresh_feed() -> None:
            for _ in range(3):
                with loading_column:
                    ui.skeleton().classes('w-full h-20 mb-2').props('animation="wave"')

            vibenodes = await api_call('GET', '/vibenodes/') or []
            events = await api_call('GET', '/events/') or []
            notifs = await api_call('GET', '/notifications/') or []

            feed_column.clear()
            loading_column.clear()
            for vn in vibenodes:
                with feed_column:
                    with ui.card().classes('w-full mb-2').style('border: 1px solid #333; background: #1e1e1e;'):
                        ui.label('VibeNode').classes('text-sm font-bold')
                        ui.label(vn.get('description', '')).classes('text-sm')
                        render_media_block(vn.get('media_url'), vn.get('media_type'))
                        ui.link('View', f"/vibenodes/{vn['id']}")
            for ev in events:
                with feed_column:
                    with ui.card().classes('w-full mb-2').style('border: 1px solid #333; background: #1e1e1e;'):
                        ui.label('Event').classes('text-sm font-bold')
                        ui.label(ev.get('description', '')).classes('text-sm')
                        render_media_block(ev.get('media_url'), ev.get('media_type'))
                        ui.link('View', f"/events/{ev['id']}")
            for n in notifs:
                with feed_column:
                    with ui.card().classes('w-full mb-2').style('border: 1px solid #333; background: #1e1e1e;'):
                        ui.label('Notification').classes('text-sm font-bold')
                        ui.label(n.get('message', '')).classes('text-sm')
                        ui.link('View', f"/notifications/{n['id']}")

        await refresh_feed()
