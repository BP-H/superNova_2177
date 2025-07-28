"""Skill management utilities.

This module defines a minimal skill system consisting of the ``Skill``
class and an ``EmbodiedAgent`` capable of registering and invoking skills.
"""

__all__ = ["Skill", "EmbodiedAgent"]
from typing import Callable, Dict
from protocols.core.internal_protocol import InternalAgentProtocol


class Skill:
    def __init__(self, name: str, action: Callable[[dict], dict], description: str = ""):
        self.name = name
        self.action = action
        self.description = description

    def run(self, input_data: dict) -> dict:
        return self.action(input_data)


class EmbodiedAgent(InternalAgentProtocol):
    def __init__(self, name: str):
        super().__init__()
        self.name = name
        self.skills: Dict[str, Skill] = {}

    def register_skill(self, skill: Skill) -> None:
        self.skills[skill.name] = skill

    def invoke(self, skill_name: str, data: dict) -> dict:
        if skill_name in self.skills:
            return self.skills[skill_name].run(data)
        return {"error": f"Skill '{skill_name}' not found in {self.name}."}
