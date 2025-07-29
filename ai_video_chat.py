"""
STRICTLY A SOCIAL MEDIA PLATFORM
Intellectual Property & Artistic Inspiration
Legal & Ethical Safeguards
"""

from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Participant:
    """Client connected to a video chat session."""

    user_id: str
    ws: Optional[object] = None  # placeholder for websocket connection


@dataclass
class VideoChatSession:
    """Represents an active video chat room."""

    session_id: str
    participants: Dict[str, Participant] = field(default_factory=dict)
    active: bool = False

    async def start(self) -> None:
        """Mark the session active."""
        self.active = True

    async def end(self) -> None:
        """End the session and close connections."""
        self.active = False
        for participant in list(self.participants.values()):
            if participant.ws and hasattr(participant.ws, "close"):
                try:
                    await participant.ws.close()
                except Exception:
                    pass
        self.participants.clear()

    async def add_participant(self, participant: Participant) -> None:
        """Add a participant to the session."""
        self.participants[participant.user_id] = participant

    async def remove_participant(self, user_id: str) -> None:
        """Remove a participant from the session."""
        self.participants.pop(user_id, None)

    async def broadcast(self, data: bytes) -> None:
        """Send raw frame data to all participants."""
        for participant in list(self.participants.values()):
            if participant.ws and hasattr(participant.ws, "send"):
                try:
                    await participant.ws.send(data)
                except Exception:
                    pass


def create_session(participant_ids: List[str]) -> VideoChatSession:
    """Initialize a new video chat session with given participant IDs."""
    session = VideoChatSession(session_id=str(uuid.uuid4()))
    for uid in participant_ids:
        session.participants[uid] = Participant(user_id=uid)
    return session
