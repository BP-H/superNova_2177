"""User profile view and editing."""

from nicegui import ui
from utils.api import (TOKEN, api_call, clear_token, get_followers,
                       get_following, get_user, toggle_follow)
from utils.layout import page_container, nav_bar
from utils.styles import (THEMES, get_theme, get_theme_name, set_accent,
                          set_theme)

from .events_page import events_page
from .groups_page import groups_page
from .login_page import login_page
from .messages_page import messages_page
from .notifications_page import notifications_page
from .proposals_page import proposals_page
from .vibenodes_page import vibenodes_page


@ui.page("/profile")
@ui.page("/profile/{username}")
async def profile_page(username: str | None = None):
    """Display and edit the user's profile."""
    if not TOKEN:
        ui.open(login_page)
        return

    my_data = await api_call("GET", "/users/me")
    if not my_data:
        clear_token()
        ui.open(login_page)
        return

    target_username = username or my_data["username"]
    if target_username == my_data["username"]:
        user_data = my_data
        score_data = await api_call("GET", "/users/me/influence-score") or {}
    else:
        user_data = await get_user(target_username)
        if not user_data:
            ui.notify("User not found", color="negative")
            return
        score_data = {}

    followers = await get_followers(target_username)
    following = await get_following(target_username)

    THEME = get_theme()
    with page_container(THEME):
        with nav_bar(THEME):
            pass
        ui.label(f'Welcome, {user_data["username"]}').classes(
            "text-2xl font-bold mb-4"
        ).style(f'color: {THEME["accent"]};')

        ui.label(f'Harmony Score: {user_data["harmony_score"]}').classes("mb-2")
        ui.label(f'Creative Spark: {user_data["creative_spark"]}').classes("mb-2")
        ui.label(
            f'Influence Score: {score_data.get("influence_score", "N/A")}'
        ).classes("mb-2")
        ui.label(f'Species: {user_data["species"]}').classes("mb-2")
        followers_label = ui.label(f'Followers: {followers.get("count", 0)}').classes(
            "mb-2"
        )
        following_label = ui.label(f'Following: {following.get("count", 0)}').classes(
            "mb-4"
        )

        if target_username == my_data["username"]:
            bio = ui.input("Bio", value=user_data.get("bio", "")).classes("w-full mb-2")

            async def update_bio():
                resp = await api_call("PUT", "/users/me", {"bio": bio.value})
                if resp:
                    ui.notify("Bio updated", color="positive")

            ui.button("Update Bio", on_click=update_bio).classes("mb-4").style(
                f'background: {THEME["primary"]}; color: {THEME["text"]};'
            )
        else:
            ui.label(user_data.get("bio", "")).classes("mb-4")
            is_following = my_data["username"] in followers.get("followers", [])

            async def toggle() -> None:
                await toggle_follow(target_username)
                new_data = await get_followers(target_username)
                followers_label.text = f"Followers: {new_data.get('count', 0)}"
                button.text = (
                    "Unfollow"
                    if my_data["username"] in new_data.get("followers", [])
                    else "Follow"
                )

            button = (
                ui.button(
                    "Unfollow" if is_following else "Follow",
                    on_click=lambda: ui.run_async(toggle()),
                )
                .classes("mb-4")
                .style(f'background: {THEME["primary"]}; color: {THEME["text"]};')
            )

        ui.button("VibeNodes", on_click=lambda: ui.open(vibenodes_page)).classes(
            "w-full mb-2"
        ).style(f'background: {THEME["accent"]}; color: {THEME["background"]};')
        ui.button("Groups", on_click=lambda: ui.open(groups_page)).classes(
            "w-full mb-2"
        ).style(f'background: {THEME["accent"]}; color: {THEME["background"]};')
        ui.button("Events", on_click=lambda: ui.open(events_page)).classes(
            "w-full mb-2"
        ).style(f'background: {THEME["accent"]}; color: {THEME["background"]};')
        ui.button("Proposals", on_click=lambda: ui.open(proposals_page)).classes(
            "w-full mb-2"
        ).style(f'background: {THEME["accent"]}; color: {THEME["background"]};')
        ui.button(
            "Notifications", on_click=lambda: ui.open(notifications_page)
        ).classes("w-full mb-2").style(
            f'background: {THEME["accent"]}; color: {THEME["background"]};'
        )
        ui.button("Messages", on_click=lambda: ui.open(messages_page)).classes(
            "w-full mb-2"
        ).style(f'background: {THEME["accent"]}; color: {THEME["background"]};')
        from .system_insights_page import system_insights_page  # lazy import

        ui.button(
            "System Insights", on_click=lambda: ui.open(system_insights_page)
        ).classes("w-full mb-2").style(
            f'background: {THEME["accent"]}; color: {THEME["background"]};'
        )
        ui.button(
            "Logout",
            on_click=lambda: (clear_token(), ui.open(login_page)),
        ).classes("w-full").style(f'background: red; color: {THEME["text"]};')

        with ui.row().classes("w-full mt-4"):
            theme_select = ui.select(
                list(THEMES.keys()),
                value=get_theme_name(),
                on_change=lambda e: set_theme(e.value),
            ).classes("mr-2")
            ui.color_input(
                "Accent",
                value=THEME["accent"],
                on_change=lambda e: set_accent(e.value),
            )
