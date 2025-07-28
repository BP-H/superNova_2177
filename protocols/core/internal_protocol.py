"""Base protocol for memory-bound, message-driven agents."""
from typing import Callable, Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class InternalAgentProtocol:
    """Standard interface for agent communication and state."""
    def __init__(self) -> None:
        self.memory: Dict[str, Any] = {}
        self.inbox: List[dict] = []
        self.name: str = self.__class__.__name__
        self.hooks: Dict[str, Callable[[dict], Any]] = {}

    def send(self, topic: str, payload: dict) -> None:
        logger.info(f"[{self.name}] SEND {topic}: {payload}")
        self.inbox.append({"topic": topic, "payload": payload})

    def receive(self, topic: str, handler: Callable[[dict], Any]) -> None:
        self.hooks[topic] = handler

    def process_event(self, event: dict):
        topic = event.get("event")
        payload = event.get("payload", {})
        if topic in self.hooks:
            return self.hooks[topic](payload)
        logger.warning(f"[{self.name}] Unknown event: {topic}")
        return {"error": f"Unhandled event {topic}"}
