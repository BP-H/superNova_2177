"""Base agent class for Codex experiments."""

from protocols.core.internal_protocol import InternalAgentProtocol
from protocols.utils.introspection import IntrospectiveMixin


class CodexAgent(IntrospectiveMixin, InternalAgentProtocol):
    """Enhanced agent with handy memory helpers."""

    def __init__(self, name: str | None = None) -> None:
        super().__init__()
        if name:
            self.name = name

    # CODExAgent: future mixins may hook here for analytics or trust scoring

    def remember(self, key: str, value: object) -> None:
        """Store ``value`` under ``key`` in ``self.memory``."""
        self.memory[key] = value

    def recall(self, key: str, default: object | None = None) -> object | None:
        """Retrieve from memory."""
        return self.memory.get(key, default)
