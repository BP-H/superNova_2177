# protocols/observer_agent.py

"""
ObserverAgent watches agent activity via MessageHub and suggests evolutionary forks,
skill swaps, or role specialization based on performance trends and behavioral anomalies.
"""

from protocols.agent_protocols_suite import fork_agent
from collections import defaultdict, deque
import time
import logging

logger = logging.getLogger("ObserverAgent")

class ObserverAgent:
    def __init__(self, hub, agent_registry, fatigue_tracker):
        self.hub = hub
        self.registry = agent_registry
        self.fatigue_tracker = fatigue_tracker
        self.task_history = defaultdict(deque)  # agent_id -> deque of (task, result)
        self.max_history = 20
        self.subscribed = False

    def start(self):
        if not self.subscribed:
            self.hub.subscribe("AGENT_TASK_RESULT", self.observe)
            self.subscribed = True
            logger.info("ObserverAgent subscribed to AGENT_TASK_RESULT")

    def observe(self, message):
        data = message.data
        agent_id = data.get("agent")
        task = data.get("task")
        result = data.get("result", {})

        self.task_history[agent_id].append((task, result))
        if len(self.task_history[agent_id]) > self.max_history:
            self.task_history[agent_id].popleft()

        fatigue = self.fatigue_tracker.task_count[task]
        belief_score = self.fatigue_tracker.fatigue_score(task)

        if self.should_fork(agent_id, task, fatigue, belief_score):
            mutation = {"name": f"{agent_id}_forked_{int(time.time())}"}
            new_agent = fork_agent(self.registry[agent_id], mutation)
            logger.info(f"Forked agent {agent_id} -> {new_agent.name} due to fatigue={fatigue}, belief={belief_score:.2f}")
            # Optionally auto-register
            self.registry[new_agent.name] = new_agent

    def should_fork(self, agent_id, task, fatigue, belief_score) -> bool:
        if fatigue > 10 and belief_score < 0.2:
            return True  # Overloaded and losing confidence
        recent_tasks = [t for (t, _) in self.task_history[agent_id] if t == task]
        if len(recent_tasks) >= 5:
            return True  # Repeating too much
        return False
