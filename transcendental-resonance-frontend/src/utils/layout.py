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

