"""Agent profile structures describing traits and powers."""
from typing import List


class AgentProfile:
    """Defines traits and capabilities of autonomous agents."""
    def __init__(self, name: str, traits: List[str], powers: List[str]):
        self.name = name
        self.traits = traits
        self.powers = powers

    def can(self, task: str) -> bool:
        return task in self.powers

    def describe(self) -> str:
        return f"{self.name}: {'/'.join(self.traits)} with powers: {', '.join(self.powers)}"
