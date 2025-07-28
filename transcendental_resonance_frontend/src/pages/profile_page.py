"""User profile view and editing."""

from nicegui import ui

from utils.api import (
    api_call,
    TOKEN,
    clear_token,
    get_followers,
    get_following,
)
from utils.styles import (
    get_theme,
    set_theme,
    set_accent,
    get_theme_name,
    THEMES,
)
from utils.layout import page_container
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

    user_data = await api_call('GET', '/users/me')
    if not user_data:
        clear_token()
        ui.open(login_page)
        return

    score_data = await api_call('GET', '/users/me/influence-score') or {}

    THEME = get_theme()
    with page_container(THEME):
        ui.label(f'Welcome, {user_data["username"]}').classes(
            'text-2xl font-bold mb-4'
        ).style(f'color: {THEME["accent"]};')

        ui.label(f'Harmony Score: {user_data["harmony_score"]}').classes('mb-2')
        ui.label(f'Creative Spark: {user_data["creative_spark"]}').classes('mb-2')
        ui.label(
            f'Influence Score: {score_data.get("influence_score", "N/A")}'
        ).classes('mb-2')
        ui.label(f'Species: {user_data["species"]}').classes('mb-2')

        bio = ui.input('Bio', value=user_data.get('bio', '')).classes('w-full mb-2')

        async def update_bio():
            resp = await api_call('PUT', '/users/me', {'bio': bio.value})
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

        with ui.row().classes('w-full mt-4'):
            theme_select = ui.select(
                list(THEMES.keys()),
                value=get_theme_name(),
                on_change=lambda e: set_theme(e.value),
            ).classes('mr-2')
            ui.color_input(
                'Accent',
                value=THEME['accent'],
                on_change=lambda e: set_accent(e.value),
            )


@ui.page('/profile/{username}')
async def other_profile_page(username: str):
    """View another user's profile with follow option."""
    if not TOKEN:
        ui.open(login_page)
        return

    me = await api_call('GET', '/users/me')
    if not me:
        clear_token()
        ui.open(login_page)
        return
    if username == me.get('username'):
        ui.open(profile_page)
        return

    user_data = await api_call('GET', f'/users/{username}')
    if not user_data:
        ui.notify('User not found', color='negative')
        return

    follower_data = await get_followers(username) or {"followers": 0}
    following_data = await get_following(username) or {"following": 0}

    THEME = get_theme()
    with page_container(THEME):
        ui.label(f"{user_data['username']}'s Profile").classes(
            'text-2xl font-bold mb-4'
        ).style(f'color: {THEME["accent"]};')

        ui.label(f"Harmony Score: {user_data['harmony_score']}").classes('mb-2')
        ui.label(f"Creative Spark: {user_data['creative_spark']}").classes('mb-2')
        ui.label(f"Species: {user_data['species']}").classes('mb-2')
        follow_count_label = ui.label(
            f"Followers: {follower_data['followers']}"
        ).classes('mb-2')
        following_label = ui.label(
            f"Following: {following_data['following']}"
        ).classes('mb-4')

        follow_btn = ui.button('Follow').classes('mb-4').style(
            f'background: {THEME["primary"]}; color: {THEME["text"]};'
        )

        async def toggle_follow():
            resp = await api_call('POST', f'/users/{username}/follow')
            if resp:
                follow_btn.text = 'Unfollow' if resp['message'] == 'Followed' else 'Follow'
                new_counts = await get_followers(username)
                if new_counts:
                    follower_data['followers'] = new_counts['followers']
                    follow_count_label.text = f"Followers: {follower_data['followers']}"

        follow_btn.on('click', toggle_follow)

        ui.button(
            'Back to My Profile',
            on_click=lambda: ui.open(profile_page)
        ).classes('w-full').style(
            f'background: {THEME["accent"]}; color: {THEME["background"]};'
        )
