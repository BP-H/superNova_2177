# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
"""WebSocket endpoints for experimental video chat."""

from __future__ import annotations

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List

router = APIRouter()


class ConnectionManager:
    """Track active video chat websocket connections."""

    def __init__(self) -> None:
        self.active: List[WebSocket] = []

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket) -> None:
        if ws in self.active:
            self.active.remove(ws)

    async def broadcast(self, message: str, sender: WebSocket) -> None:
        for conn in list(self.active):
            if conn is not sender:
                try:
                    await conn.send_text(message)
                except Exception:
                    self.disconnect(conn)


manager = ConnectionManager()


@router.websocket("/ws/video")
async def video_ws(websocket: WebSocket) -> None:
    """Relay video chat signaling messages between participants."""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(data, sender=websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
