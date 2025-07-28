"""Base protocol for memory-bound, message-driven agents."""
from typing import Callable, Dict, Any, List
import logging
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class InternalAgentProtocol:
    """Standard interface for agent communication and state."""
    def __init__(self) -> None:
        self.memory: Dict[str, Any] = {}
        self.inbox: List[dict] = []
        self.name: str = self.__class__.__name__
        self.hooks: Dict[str, Callable[[dict], Any]] = {}

    # ------------------------------------------------------------------
    # Core communication helpers
    # ------------------------------------------------------------------

    def send(self, topic: str, payload: dict) -> None:
        """Queue an outbound event and log it."""
        logger.info(f"[{self.name}] SEND {topic}: {payload}")
        self.inbox.append({"topic": topic, "payload": payload})

    def receive(self, topic: str, handler: Callable[[dict], Any]) -> None:
        """Register a handler for ``topic`` events."""
        self.hooks[topic] = handler

    def validate_event(self, event: dict) -> bool:
        """Basic schema check for incoming events."""
        if not isinstance(event, dict):
            logger.error(f"[{self.name}] Invalid event type: {type(event)}")
            return False
        if "event" not in event:
            logger.error(f"[{self.name}] Event missing 'event' field: {event}")
            return False
        return True

    def process_event(self, event: dict):
        """Dispatch an event to a registered handler after validation."""
        if not self.validate_event(event):
            return {"error": "invalid_event"}

        topic = event.get("event")
        payload = event.get("payload", {})
        if topic in self.hooks:
            return self.hooks[topic](payload)
        logger.warning(f"[{self.name}] Unknown event: {topic}")
        return {"error": f"Unhandled event {topic}"}

    # ------------------------------------------------------------------
    # Memory utilities
    # ------------------------------------------------------------------
    def snapshot_memory(self, path: str) -> None:
        """Persist the agent's current memory and inbox to ``path``."""
        data = {"memory": self.memory, "inbox": self.inbox}
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        logger.info(f"[{self.name}] Memory snapshot saved to {path}")

    def load_snapshot(self, path: str) -> None:
        """Restore memory and inbox from a snapshot file if it exists."""
        p = Path(path)
        if not p.exists():
            logger.warning(f"[{self.name}] Snapshot {path} not found")
            return
        with open(p, "r") as f:
            data = json.load(f)
        self.memory = data.get("memory", {})
        self.inbox = data.get("inbox", [])
        logger.info(f"[{self.name}] Memory snapshot loaded from {path}")
