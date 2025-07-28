"""Mixins for exporting agent reasoning context."""


class IntrospectiveMixin:
    def export_reasoning(self) -> dict:
        return {
            "name": self.name,
            "memory": self.memory,
            "recent_events": self.inbox[-5:],
            "handlers": list(self.hooks.keys()),
        }
