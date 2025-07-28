"""Attachable missions or tasks agents may attempt."""
from typing import Callable, Dict


class AgentTaskContract:
    def __init__(self, task_name: str, criteria: Callable[[dict], bool], action: Callable[[dict], dict]):
        self.task_name = task_name
        self.criteria = criteria
        self.action = action

    def attempt(self, payload: dict) -> Dict:
        if self.criteria(payload):
            return self.action(payload)
        return {"skipped": True}
