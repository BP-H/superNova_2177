# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
"""Experimental video chat page."""

from __future__ import annotations

import json
from nicegui import ui

from utils.api import TOKEN, connect_ws, listen_ws, WS_CONNECTION
from utils.layout import page_container, navigation_bar
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

        local_cam = ui.camera().classes("w-full mb-4")
        remote_view = ui.video().props("autoplay playsinline").classes("w-full mb-4")

        async def handle_event(event: dict) -> None:
            if event.get("type") == "frame":
                remote_view.source = event.get("data")

        async def join_call() -> None:
            ws_task = listen_ws(handle_event)
            await ws_task

        async def send_frame() -> None:
            if WS_CONNECTION and local_cam.value:
                await WS_CONNECTION.send_text(
                    json.dumps({"type": "frame", "data": local_cam.value})
                )

        local_cam.on("capture", lambda _: ui.run_async(send_frame()))
        ui.button("Join Call", on_click=lambda: ui.run_async(join_call()))
