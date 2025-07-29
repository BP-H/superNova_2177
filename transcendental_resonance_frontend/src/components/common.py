from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from nicegui import ui
from nicegui.element import Element


@contextmanager
def standard_card() -> Iterator[Element]:
    """Reusable styled card container."""
    with ui.card().classes('w-full mb-2').style(
        'border: 1px solid #333; background: #1e1e1e;'
    ) as card:
        yield card


def loading_skeleton(height: str = '4rem') -> Element:
    """Display a skeleton placeholder block."""
    return ui.skeleton().classes('w-full mb-2').style(f'height: {height};')


def video_preview(url: str) -> Element:
    """Render a video preview with graceful fallback."""
    try:
        return ui.video(url).props('controls').classes('w-full')
    except Exception:
        return ui.icon('videocam_off').classes('text-negative')
