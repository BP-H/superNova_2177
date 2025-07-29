from __future__ import annotations

from contextlib import contextmanager
from typing import Optional, Generator

# global notification state used for navbar badge
NOTIFICATION_COUNT: int = 0
NOTIFICATION_BADGE = None

def set_notification_count(count: int) -> None:
    """Update the unread notification count and badge text."""
    global NOTIFICATION_COUNT, NOTIFICATION_BADGE
    NOTIFICATION_COUNT = count
    if NOTIFICATION_BADGE is not None:
        NOTIFICATION_BADGE.text = str(count) if count else ''

try:  # pragma: no cover - allow import without NiceGUI installed
    from nicegui import ui
    from nicegui.element import Element
except Exception:  # pragma: no cover - fallback stub for testing
    import types

    class Element:  # type: ignore
        """Fallback element used when NiceGUI is unavailable."""
        pass

    class _DummyContext:
        def __enter__(self) -> Element:
            return Element()

        def __exit__(self, *_exc) -> None:
            pass

        def classes(self, *_args, **_kw) -> "_DummyContext":
            return self

        def style(self, *_args, **_kw) -> "_DummyContext":
            return self

    def _dummy_column() -> _DummyContext:
        return _DummyContext()

    ui = types.SimpleNamespace(column=_dummy_column)

from .styles import get_theme


def navigation_bar() -> Element:
    """Render a simple navigation bar linking major pages."""
    theme = get_theme()
    try:
        from pages.profile_page import profile_page
        from pages.messages_page import messages_page
        from pages.groups_page import groups_page
        from pages.events_page import events_page
        from pages.notifications_page import notifications_page
        from pages.status_page import status_page
    except Exception:
        # During testing, NiceGUI or page modules may not be available
        return Element()

    with ui.row().classes('w-full justify-around mb-4') as nav:
        ui.button('Profile', on_click=lambda: ui.open(profile_page)).style(
            f'background: {theme["primary"]}; color: {theme["text"]};'
        )
        ui.button('Messages', on_click=lambda: ui.open(messages_page)).style(
            f'background: {theme["accent"]}; color: {theme["background"]};'
        )
        ui.button('Groups', on_click=lambda: ui.open(groups_page)).style(
            f'background: {theme["accent"]}; color: {theme["background"]};'
        )
        ui.button('Events', on_click=lambda: ui.open(events_page)).style(
            f'background: {theme["accent"]}; color: {theme["background"]};'
        )

        with ui.row().classes('items-center'):
            ui.button(
                on_click=lambda: ui.open(notifications_page),
                icon='notifications',
            ).style(
                f'background: {theme["accent"]}; color: {theme["background"]};'
            )
            global NOTIFICATION_BADGE
            NOTIFICATION_BADGE = ui.badge(
                str(NOTIFICATION_COUNT) if NOTIFICATION_COUNT else '',
                color='red',
                text_color='white',
            )

        ui.button('Status', on_click=lambda: ui.open(status_page)).style(
            f'background: {theme["accent"]}; color: {theme["background"]};'
        )
    return nav


@contextmanager
def page_container(theme: Optional[dict] = None) -> Generator[Element, None, None]:
    """Context manager for a themed page container.

    Creates a ``ui.column`` with the standard padding and background
    gradient for the currently active theme.
    """
    theme = theme or get_theme()
    with ui.column().classes('w-full p-4').style(
        f"background: {theme['gradient']}; color: {theme['text']};"
    ) as container:
        navigation_bar()
        yield container

