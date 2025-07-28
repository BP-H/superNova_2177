# protocols/observer_agent.py

"""
ObserverAgent watches agent activity via MessageHub and suggests evolutionary forks,
skill swaps, or role specialization based on performance trends and behavioral anomalies.

An optional ``llm_backend`` callable can be supplied for additional LLM-driven
analysis of observed results.
"""

import logging
import time
from collections import defaultdict, deque

from protocols.core.internal_protocol import InternalAgentProtocol
from protocols.utils.forking import fork_agent

logger = logging.getLogger("ObserverAgent")


class ObserverAgent(InternalAgentProtocol):
    """Watches tasks and recommends agent forks or upgrades.

    Parameters
    ----------
    hub : MessageHub-like
        Event hub that the agent subscribes to.
    agent_registry : dict
        Mapping of agent names to agent instances.
    fatigue_tracker : object
        Tracker providing ``task_count`` and ``fatigue_score`` methods.
    llm_backend : callable, optional
        Optional backend for future LLM-based observations.
    """

    def __init__(self, hub, agent_registry, fatigue_tracker, llm_backend=None):
        super().__init__()
        self.name = "Observer"
        self.hub = hub
        self.registry = agent_registry
        self.fatigue_tracker = fatigue_tracker
        self.llm_backend = llm_backend
        self.task_history = defaultdict(deque)  # agent_id -> deque of (task, result)
        self.max_history = 20
        self.subscribed = False
        self.receive("AGENT_TASK_RESULT", self.observe)

    def start(self):
        if not self.subscribed:
            self.hub.subscribe(
                "AGENT_TASK_RESULT",
                lambda m: self.process_event({"event": "AGENT_TASK_RESULT", "payload": m.data}),
            )
            self.subscribed = True
            logger.info("ObserverAgent subscribed to AGENT_TASK_RESULT")

    def observe(self, payload: dict):
        agent_id = payload.get("agent")
        task = payload.get("task")
        result = payload.get("result", {})

        if self.llm_backend:
            prompt = (
                f"Analyze agent {agent_id} result for task '{task}': {result}"
            )
            self.llm_backend(prompt)

        self.task_history[agent_id].append((task, result))
        if len(self.task_history[agent_id]) > self.max_history:
            self.task_history[agent_id].popleft()

        fatigue = self.fatigue_tracker.task_count[task]
        belief_score = self.fatigue_tracker.fatigue_score(task)

        if self.should_fork(agent_id, task, fatigue, belief_score):
            mutation = {"name": f"{agent_id}_forked_{int(time.time())}"}
            new_agent = fork_agent(self.registry[agent_id], mutation)
            logger.info(
                f"Forked agent {agent_id} -> {new_agent.name} due to fatigue={fatigue}, belief={belief_score:.2f}"
            )
            # Optionally auto-register
            self.registry[new_agent.name] = new_agent
            self.send(
                "AGENT_FORKED",
                {"original": agent_id, "fork": new_agent.name, "mutation": mutation},
            )

    def should_fork(self, agent_id, task, fatigue, belief_score) -> bool:
        if fatigue > 10 and belief_score < 0.2:
            return True  # Overloaded and losing confidence
        recent_tasks = [t for (t, _) in self.task_history[agent_id] if t == task]
        if len(recent_tasks) >= 5:
            return True  # Repeating too much
        return False
