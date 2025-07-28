"""Shared page layout utilities including persistent header."""

from nicegui import ui

from .styles import set_theme, get_theme_name, THEMES, get_theme
from .api import clear_token, TOKEN


def toggle_theme() -> None:
    """Cycle through available themes."""
    order = list(THEMES.keys())
    current = get_theme_name()
    try:
        idx = order.index(current)
    except ValueError:
        idx = 0
    new_name = order[(idx + 1) % len(order)]
    set_theme(new_name)


def logout() -> None:
    """Clear token and navigate to login page."""
    clear_token()
    from pages.login_page import login_page
    ui.open(login_page)


def header() -> None:
    """Render the persistent navigation header."""
    theme = get_theme()
    with ui.header(elevated=True).classes('items-center justify-between px-4').style(
        f"background: {theme['background']}; color: {theme['text']};"
    ):
        with ui.row().classes('gap-2'):
            ui.button('Profile', on_click=lambda: ui.open('/profile')).props('flat')
            ui.button('VibeNodes', on_click=lambda: ui.open('/vibenodes')).props('flat')
            ui.button('Groups', on_click=lambda: ui.open('/groups')).props('flat')
            ui.button('Events', on_click=lambda: ui.open('/events')).props('flat')
            ui.button('Proposals', on_click=lambda: ui.open('/proposals')).props('flat')
            ui.button('Notifications', on_click=lambda: ui.open('/notifications')).props('flat')
            ui.button('Messages', on_click=lambda: ui.open('/messages')).props('flat')
            ui.button('Upload', on_click=lambda: ui.open('/upload')).props('flat')
            ui.button('Music', on_click=lambda: ui.open('/music')).props('flat')
            ui.button('Status', on_click=lambda: ui.open('/status')).props('flat')
            ui.button('Network', on_click=lambda: ui.open('/network')).props('flat')
            ui.button('Insights', on_click=lambda: ui.open('/system-insights')).props('flat')
            ui.button('Forks', on_click=lambda: ui.open('/forks')).props('flat')
        with ui.row().classes('gap-2'):
            ui.button('Theme', on_click=toggle_theme).props('flat')
            if TOKEN:
                ui.button('Logout', on_click=logout).props('flat color=negative')
            else:
                ui.button('Login', on_click=lambda: ui.open('/')).props('flat')
