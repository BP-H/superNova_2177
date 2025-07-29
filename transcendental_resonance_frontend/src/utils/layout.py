from __future__ import annotations

from contextlib import contextmanager
from typing import Optional, Generator

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


@contextmanager
def nav_bar(theme: Optional[dict] = None) -> Generator[Element, None, None]:
    """Context manager for a simple navigation bar.

    Yields a ``ui.row`` containing buttons that link to major pages. The
    appearance of the buttons adapts to the provided ``theme``.
    """
    theme = theme or get_theme()
    with ui.row().classes("w-full gap-2 mb-4") as bar:
        style = f"background: {theme['primary']}; color: {theme['text']};"
        links = [
            ("Profile", "/profile"),
            ("Groups", "/groups"),
            ("Events", "/events"),
            ("VibeNodes", "/vibenodes"),
            ("Proposals", "/proposals"),
            ("Messages", "/messages"),
            ("Notifications", "/notifications"),
        ]
        for label, path in links:
            ui.button(label, on_click=lambda p=path: ui.open(p)).style(style)
        yield bar


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
        yield container

