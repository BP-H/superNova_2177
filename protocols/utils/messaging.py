"""Publish/subscribe message hub for agents."""

import uuid
from collections import defaultdict
from typing import Callable, Dict, List


class Message:
    """A versioned agent message with metadata."""

    def __init__(self, topic: str, data: dict, version: str = "1.0"):
        self.id = str(uuid.uuid4())
        self.topic = topic
        self.version = version
        self.data = data


class MessageHub:
    """Shared communication hub for agents, tools, and diagnostics."""

    def __init__(self):
        self.subscribers: Dict[str, List[Callable[[Message], None]]] = defaultdict(list)
        self.history: List[Message] = []

    def publish(self, topic: str, data: dict, version: str = "1.0") -> str:
        message = Message(topic, data, version)
        self.history.append(message)
        for callback in self.subscribers.get(topic, []):
            callback(message)
        return message.id

    def subscribe(self, topic: str, handler: Callable[[Message], None]) -> None:
        self.subscribers[topic].append(handler)

    def unsubscribe(self, topic: str, handler: Callable[[Message], None]) -> None:
        """Remove ``handler`` for ``topic`` if present."""
        handlers = self.subscribers.get(topic)
        if not handlers:
            return
        try:
            handlers.remove(handler)
        except ValueError:
            # handler wasn't subscribed
            pass

    def get_messages(self, topic: str | None = None) -> List[Message]:
        if topic:
            return [msg for msg in self.history if msg.topic == topic]
        return self.history
