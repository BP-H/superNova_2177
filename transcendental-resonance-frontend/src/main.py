"""Main entry point for the Transcendental Resonance frontend."""

from nicegui import ui, background_tasks
import asyncio

from .utils.api import clear_token, api_call
from .utils.styles import apply_global_styles, set_theme, get_theme, THEMES
from .utils.layout import create_header, update_header_style
from .pages import *  # register all pages
from .pages.system_insights_page import system_insights_page  # noqa: F401
from .pages.login_page import login_page

page_header = None

ui.context.client.on_disconnect(clear_token)
apply_global_styles()


def toggle_theme() -> None:
    """Switch between light and dark themes."""
    current = get_theme()
    new_name = "light" if current is THEMES["dark"] else "dark"
    set_theme(new_name)
    if page_header is not None:
        update_header_style(page_header)


def logout() -> None:
    """Clear token and return to login page."""
    clear_token()
    ui.open(login_page)


async def keep_backend_awake() -> None:
    """Periodically ping the backend to keep data fresh."""
    while True:
        api_call('GET', '/status')
        await asyncio.sleep(300)


# navigation links for the persistent header
PAGE_LINKS = [
    ("Profile", profile_page),
    ("VibeNodes", vibenodes_page),
    ("Groups", groups_page),
    ("Events", events_page),
    ("Proposals", proposals_page),
    ("Notifications", notifications_page),
    ("Messages", messages_page),
    ("Upload", upload_page),
    ("Music", music_page),
    ("Status", status_page),
    ("Network", network_page),
    ("Insights", system_insights_page),
    ("Forks", forks_page),
]

# create persistent header
page_header = create_header(PAGE_LINKS, toggle_theme, logout)

ui.on_startup(lambda: background_tasks.create(keep_backend_awake(), name='backend-pinger'))

# Potential future enhancements:
# - Real-time updates via WebSockets
# - Internationalization support
# - Theming options

ui.run(title='Transcendental Resonance', dark=True, favicon='🌌', reload=False)
