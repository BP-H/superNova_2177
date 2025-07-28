import uuid
from collections import defaultdict
from typing import Callable, Dict, List, Any


class Message:
    """A versioned agent message with metadata."""
    def __init__(self, topic: str, data: dict, version: str = "1.0"):
        self.id = str(uuid.uuid4())
        self.topic = topic
        self.version = version
        self.data = data


class MessageHub:
    """
    Shared communication hub for agents, tools, and diagnostics.
    Supports publish/subscribe model.
    """
    def __init__(self):
        self.subscribers: Dict[str, List[Callable[[Message], None]]] = defaultdict(list)
        self.history: List[Message] = []

    def publish(self, topic: str, data: dict, version: str = "1.0") -> str:
        """Broadcast a message to all subscribers of the topic."""
        message = Message(topic, data, version)
        self.history.append(message)
        for callback in self.subscribers.get(topic, []):
            callback(message)
        return message.id

    def subscribe(self, topic: str, handler: Callable[[Message], None]) -> None:
        """Register a handler function to receive future messages of a topic."""
        self.subscribers[topic].append(handler)

    def get_messages(self, topic: str = None) -> List[Message]:
        """Fetch past messages (optionally filtered by topic)."""
        if topic:
            return [msg for msg in self.history if msg.topic == topic]
        return self.history

EXAMPLE USE

from protocols.message_hub import MessageHub

hub = MessageHub()

def audit_logger(msg):
    print(f"[AUDIT] v{msg.version}: {msg.data}")

hub.subscribe("INTEGRITY_RESULT", audit_logger)

# somewhere else in the app:
hub.publish("INTEGRITY_RESULT", {"score": 0.88, "status": "PASS"})
