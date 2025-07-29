from __future__ import annotations

from nicegui import ui

from ..utils.api import api_call
from ..utils.styles import get_theme
from ..pages.notifications_page import notifications_page


def notification_bell() -> ui.element.Element:
    """Display a notifications icon with unread count."""
    theme = get_theme()
    with ui.row().classes('items-center') as container:
        button = ui.button(icon='notifications', on_click=lambda: ui.open(notifications_page)).classes('relative')
        badge = ui.badge('0', color=theme['accent'], text_color=theme['background']).classes('ml-1')

    async def refresh_count() -> None:
        notifications = await api_call('GET', '/notifications/') or []
        unread = sum(1 for n in notifications if not n.get('is_read'))
        badge.text = str(unread)
        badge.visible = unread > 0

    ui.run_async(refresh_count())
    ui.timer(30, lambda: ui.run_async(refresh_count()))
    return container
