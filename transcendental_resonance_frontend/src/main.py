"""Main entry point for the Transcendental Resonance frontend."""

# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards

import asyncio
import logging
import time

from nicegui import background_tasks, ui

from .pages import *  # register all pages  # noqa: F401,F403
from .pages.explore_page import explore_page  # noqa: F401
from .pages.system_insights_page import system_insights_page  # noqa: F401
from .pages.feed_page import feed_page  # noqa: F401
from .utils.api import (
    api_call,
    clear_token,
    listen_ws,
    on_ws_status_change,
    OFFLINE_MODE,
)
from .utils.loading_overlay import LoadingOverlay
from .utils.styles import (
    THEMES,
    apply_global_styles,
    get_theme_name,
    set_theme,
    toggle_high_contrast,
)
from .utils.features import (
    notification_drawer,
    high_contrast_switch,
    shortcut_help_dialog,
    theme_personalization_panel,
    onboarding_overlay,
)
from .utils import ErrorOverlay, ApiStatusFooter

ui.context.client.on_disconnect(clear_token)
apply_global_styles()
LoadingOverlay()

drawer = notification_drawer()
help_dialog = shortcut_help_dialog(["N = new post", "/ = search"])
onboarding = onboarding_overlay()
contrast_toggle = high_contrast_switch()
contrast_toggle.on("change", lambda e: toggle_high_contrast(e.value))
theme_personalization_panel()
error_overlay = ErrorOverlay()
api_status = ApiStatusFooter()

ws_status = (
    ui.icon("circle")
    .classes("fixed bottom-0 left-0 m-2")
    .style("color: red")
)

# Show whether the frontend is running in offline mode
if OFFLINE_MODE:
    # Label bar across the bottom
    ui.label("OFFLINE MODE – using mock services.")
        .classes("fixed bottom-0 w-full text-center bg-red-600 text-white text-sm")

    # Icon indicator (cloud_off)
    ui.icon("cloud_off")
        .classes("fixed bottom-0 right-0 m-2")
        .style("color: red")
else:
    # Icon indicator (cloud_done)
    ui.icon("cloud_done")
        .classes("fixed bottom-0 right-0 m-2")
        .style("color: green")


def _update_ws_status(status: str) -> None:
    color = "green" if status == "connected" else "red"
    ws_status.style(f"color: {color}")
    if status == "connected":
        ui.notify("WebSocket connected", color="positive")
        error_overlay.hide()
    else:
        ui.notify("WebSocket disconnected", color="warning")
        error_overlay.show("Connection lost. Trying to reconnect...")

on_ws_status_change(_update_ws_status)

logger = logging.getLogger(__name__)


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


async def keep_backend_awake() -> None:
    """Periodically ping the backend to keep data fresh."""
    while True:
        if not await api_call("GET", "/status"):
            logger.warning("Backend ping failed")
        await asyncio.sleep(300)


async def notification_listener() -> None:
    """Listen for real-time events and show toast notifications."""

    async def handle_event(event: dict) -> None:
        if event.get("type") == "notification":
            message = event.get("message", "You have a new notification!")
            ui.notify(message, type="info", position="bottom-right")

    ws_task = listen_ws(handle_event)
    await ws_task


@ui.page("*")
async def not_found() -> None:
    """Redirect unknown routes to the main feed."""
    ui.open("/feed")


ui.button(
    "Theme",
    on_click=toggle_theme,
).classes("fixed top-0 right-0 m-2")

ui.on_startup(
    lambda: background_tasks.create(keep_backend_awake(), name="backend-pinger")
)

ui.on_startup(
    lambda: background_tasks.create(
        notification_listener(), name="notification-listener"
    )
)

# Potential future enhancements:
# - Real-time updates via WebSockets
# - Internationalization support
# - Theming options

def run_app() -> None:
    """Run the NiceGUI app."""
    ui.run(
        title="Transcendental Resonance",
        dark=True,
        favicon="🌌",
        reload=False,
    )


if __name__ == "__main__":
    run_app()
