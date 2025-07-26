"""User profile view and editing."""

from nicegui import ui

from utils.api import api_call, TOKEN, clear_token
from utils.styles import get_theme
from .login_page import login_page
from .vibenodes_page import vibenodes_page
from .groups_page import groups_page
from .events_page import events_page
from .proposals_page import proposals_page
from .notifications_page import notifications_page
from .messages_page import messages_page


@ui.page('/profile')
async def profile_page():
    """Display and edit the user's profile."""
    if not TOKEN:
        ui.open(login_page)
        return

    user_data = api_call('GET', '/users/me')
    if not user_data:
        clear_token()
        ui.open(login_page)
        return

    THEME = get_theme()
    with ui.column().classes('w-full p-4').style(
        f'background: {THEME["gradient"]}; color: {THEME["text"]};'
    ):
        ui.label(f'Welcome, {user_data["username"]}').classes(
            'text-2xl font-bold mb-4'
        ).style(f'color: {THEME["accent"]};')

        ui.label(f'Harmony Score: {user_data["harmony_score"]}').classes('mb-2')
        ui.label(f'Creative Spark: {user_data["creative_spark"]}').classes('mb-2')
        ui.label(f'Species: {user_data["species"]}').classes('mb-2')

        bio = ui.input('Bio', value=user_data.get('bio', '')).classes('w-full mb-2')

        async def update_bio():
            resp = api_call('PUT', '/users/me', {'bio': bio.value})
            if resp:
                ui.notify('Bio updated', color='positive')

        ui.button('Update Bio', on_click=update_bio).classes('mb-4').style(
            f'background: {THEME["primary"]}; color: {THEME["text"]};'
        )

        ui.button('VibeNodes', on_click=lambda: ui.open(vibenodes_page)).classes(
            'w-full mb-2'
        ).style(f'background: {THEME["accent"]}; color: {THEME["background"]};')
        ui.button('Groups', on_click=lambda: ui.open(groups_page)).classes('w-full mb-2').style(
            f'background: {THEME["accent"]}; color: {THEME["background"]};'
        )
        ui.button('Events', on_click=lambda: ui.open(events_page)).classes('w-full mb-2').style(
            f'background: {THEME["accent"]}; color: {THEME["background"]};'
        )
        ui.button('Proposals', on_click=lambda: ui.open(proposals_page)).classes('w-full mb-2').style(
            f'background: {THEME["accent"]}; color: {THEME["background"]};'
        )
        ui.button('Notifications', on_click=lambda: ui.open(notifications_page)).classes('w-full mb-2').style(
            f'background: {THEME["accent"]}; color: {THEME["background"]};'
        )
        ui.button('Messages', on_click=lambda: ui.open(messages_page)).classes('w-full mb-2').style(
            f'background: {THEME["accent"]}; color: {THEME["background"]};'
        )
        from .system_insights_page import system_insights_page  # lazy import
        ui.button('System Insights', on_click=lambda: ui.open(system_insights_page)).classes('w-full mb-2').style(
            f'background: {THEME["accent"]}; color: {THEME["background"]};'
        )
        ui.button(
            'Logout',
            on_click=lambda: (clear_token(), ui.open(login_page)),
        ).classes('w-full').style(f'background: red; color: {THEME["text"]};')
