from __future__ import annotations

from typing import Callable, Awaitable, Tuple
from nicegui import ui

from .emoji_toolbar import emoji_toolbar
from utils.safe_markdown import safe_markdown


def create_post_composer(theme: dict) -> Tuple[ui.select, ui.textarea]:
    """Simple composer for feed posts with markdown preview."""

    with ui.card().classes('w-full mb-2').style('background:#1e1e1e;border:1px solid #333;'):
        post_type = ui.select(['text', 'image', 'video'], value='text').classes('mb-2')
        content = ui.textarea('Share something...').classes('w-full mb-2')
        preview = ui.markdown().classes('w-full mb-2')
        content.on('update:model-value', lambda e: preview.set_content(safe_markdown(e.value)))
        ui.button('Post', on_click=lambda: ui.notify('Posting coming soon'),
                  ).classes('w-full').style(f'background:{theme["primary"]};color:{theme["text"]};')
    return post_type, content


def video_chat_scaffold(theme: dict):
    """Return a dialog placeholder for live video chat."""
    dialog = ui.dialog()
    with dialog:
        with ui.card().classes('w-80 p-2'):
            ui.label('Live Video Chat').classes('text-lg mb-2').style(f'color:{theme["accent"]};')
            ui.label('Coming soon...').classes('text-sm')
            ui.button('Close', on_click=dialog.close).classes('mt-2').props('flat')
    return dialog


def message_composer(theme: dict, on_send: Callable[[str], Awaitable[None]]):
    """Message input area with emoji toolbar and send button."""
    content = ui.textarea('Message').classes('w-full mb-2')
    emoji_toolbar(content)
    ui.button('Attach Clip', on_click=lambda: ui.notify('Attach clip coming soon')).props('outline').classes('mb-2')

    async def _send() -> None:
        try:
            await on_send(content.value)
            content.value = ''
        except Exception:
            ui.notify('Failed to send message', color='negative')

    ui.button('Send', on_click=lambda: ui.run_async(_send())).classes('w-full').style(
        f'background:{theme["primary"]};color:{theme["text"]};')
    return content
