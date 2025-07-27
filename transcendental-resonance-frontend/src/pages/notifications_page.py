"""User notifications page."""

from nicegui import ui, background_tasks

from utils.api import api_call, TOKEN
from utils.styles import get_theme
from .login_page import login_page


@ui.page('/notifications')
async def notifications_page():
    """Display user notifications."""
    if not TOKEN:
        ui.open(login_page)
        return

    THEME = get_theme()
    with ui.column().classes('w-full p-4').style(
        f'background: {THEME["gradient"]}; color: {THEME["text"]};'
    ):
        ui.label('Notifications').classes('text-2xl font-bold mb-4').style(
            f'color: {THEME["accent"]};'
        )

        notifs_list = ui.column().classes('w-full')

        async def refresh_notifs():
            notifs = await api_call('GET', '/notifications/') or []
            notifs_list.clear()
            for n in notifs:
                with notifs_list:
                    with ui.card().classes('w-full mb-2').style('border: 1px solid #333; background: #1e1e1e;'):
                        ui.label(n['message']).classes('text-sm')
                        if not n['is_read']:
                            async def mark_read(n_id=n['id']):
                                async def task():
                                    await api_call('PUT', f'/notifications/{n_id}/read')
                                    await refresh_notifs()

                                background_tasks.create(task())
                            ui.button('Mark Read', on_click=mark_read).style(
                                f'background: {THEME["primary"]}; color: {THEME["text"]};'
                            )

        background_tasks.create(refresh_notifs())
        ui.timer(30, lambda: background_tasks.create(refresh_notifs()))
