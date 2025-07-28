"""Fatigue and belief tracking utilities."""
import time
from collections import defaultdict


class FatigueMemoryMixin:
    def __init__(self):
        self.task_count = defaultdict(int)
        self.last_reset = time.time()

    def fatigue_score(self, task: str) -> float:
        elapsed = time.time() - self.last_reset
        base = self.task_count[task]
        decay = max(1.0 - (elapsed / 300), 0.1)
        return min(base * decay, 1.0)

    def register_task(self, task: str):
        self.task_count[task] += 1


class ProbabilisticBeliefSystem:
    def __init__(self):
        self.beliefs = defaultdict(lambda: 0.5)

    def update_belief(self, key: str, evidence: float):
        prior = self.beliefs[key]
        self.beliefs[key] = (prior + evidence) / 2

    def belief(self, key: str) -> float:
        return self.beliefs[key]
