# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
"""Experimental video chat page."""

from __future__ import annotations

import json

from nicegui import ui

from utils import ErrorOverlay
from utils.api import TOKEN, WS_CONNECTION, listen_ws
from utils.layout import navigation_bar, page_container
from utils.styles import get_theme

from .login_page import login_page


@ui.page("/video-chat")
async def video_chat_page() -> None:
    """Simple camera demo with WebSocket signaling."""
    if not TOKEN:
        ui.open(login_page)
        return

    THEME = get_theme()
    with page_container(THEME):
        if TOKEN:
            navigation_bar()
        ui.label("Video Chat").classes("text-2xl font-bold mb-4").style(
            f'color: {THEME["accent"]};'
        )

        error_overlay = ErrorOverlay()

        local_cam = ui.camera().classes("w-full mb-4")
        remote_view = ui.video().props("autoplay playsinline").classes("w-full mb-4")

        async def handle_event(event: dict) -> None:
            if event.get("type") == "frame":
                remote_view.source = event.get("data")

        join_button = ui.button("Join Call")

        async def join_call() -> None:
            try:
                ws_task = listen_ws(handle_event)
                await ws_task
            except Exception:  # pragma: no cover - network issues
                ui.notify("Unable to join video chat", color="negative")
                join_button.disable()
                local_cam.disable()
                error_overlay.show("Realtime updates unavailable")

        join_button.on_click(lambda: ui.run_async(join_call()))

        async def send_frame() -> None:
            if WS_CONNECTION and local_cam.value:
                await WS_CONNECTION.send_text(
                    json.dumps({"type": "frame", "data": local_cam.value})
                )

        local_cam.on("capture", lambda _: ui.run_async(send_frame()))
        ui.label("Note: Video chat is unavailable when offline.").classes(
            "text-xs opacity-75 mt-2"
        )
