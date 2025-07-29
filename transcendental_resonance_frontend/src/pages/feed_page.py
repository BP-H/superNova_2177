# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
"""Unified feed combining VibeNodes, Events, and Notifications."""

from nicegui import ui

from utils.api import TOKEN, api_call
from utils.layout import page_container
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
        ui.label('Feed').classes('text-2xl font-bold mb-4').style(
            f'color: {theme["accent"]};'
        )

        feed_column = ui.column().classes('w-full')

        dialog = ui.dialog()
        with dialog:
            with ui.card().classes('w-full p-4'):
                post_input = ui.textarea('Post text').classes('w-full mb-2')

                async def submit_post() -> None:
                    data = {'description': post_input.value}
                    await api_call('POST', '/vibenodes/', data)
                    dialog.close()
                    await refresh_feed()

                ui.button('Post', on_click=lambda: ui.run_async(submit_post())).classes('w-full')

        ui.button(icon='add', on_click=dialog.open).props('fab fixed bottom-0 right-0')

        async def refresh_feed() -> None:
            feed_column.clear()
            # show temporary skeletons while loading data
            placeholders = [
                ui.skeleton().props('type=rect animated').style('height: 80px').classes('w-full mb-2')
                for _ in range(3)
            ]
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
