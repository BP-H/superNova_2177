"""Main entry point for the Transcendental Resonance frontend."""

from nicegui import ui, background_tasks, app
import asyncio
from fastapi import WebSocket, WebSocketDisconnect

from utils.api import clear_token, api_call
from utils.styles import apply_global_styles, set_theme, get_theme, THEMES
from pages import *  # register all pages

ui.context.client.on_disconnect(clear_token)
apply_global_styles()


def toggle_theme() -> None:
    """Switch between light and dark themes."""
    current = get_theme()
    new_name = "light" if current is THEMES["dark"] else "dark"
    set_theme(new_name)


async def keep_backend_awake() -> None:
    """Periodically ping the backend to keep data fresh."""
    while True:
        api_call('GET', '/status')
        await asyncio.sleep(300)


# --- WebSocket support ---
notification_clients: set[WebSocket] = set()
message_clients: set[WebSocket] = set()


@app.websocket('/ws/notifications')
async def notifications_ws(websocket: WebSocket) -> None:
    await websocket.accept()
    notification_clients.add(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        notification_clients.discard(websocket)


@app.websocket('/ws/messages')
async def messages_ws(websocket: WebSocket) -> None:
    await websocket.accept()
    message_clients.add(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        message_clients.discard(websocket)


async def emit_fake_events() -> None:
    count = 0
    while True:
        await asyncio.sleep(10)
        for ws in list(notification_clients):
            try:
                await ws.send_json({'message': f'Notification #{count}'})
            except Exception:
                notification_clients.discard(ws)
        for ws in list(message_clients):
            try:
                await ws.send_json({'sender': 'system', 'content': f'Hello #{count}'})
            except Exception:
                message_clients.discard(ws)
        count += 1


ui.button(
    "Toggle Theme",
    on_click=toggle_theme,
).classes("fixed top-0 right-0 m-2")

ui.on_startup(lambda: background_tasks.create(keep_backend_awake(), name='backend-pinger'))
ui.on_startup(lambda: background_tasks.create(emit_fake_events(), name='fake-events'))

# Potential future enhancements:
# - Real-time updates via WebSockets
# - Internationalization support
# - Theming options

ui.run(title='Transcendental Resonance', dark=True, favicon='🌌', reload=False)
