from __future__ import annotations

"""Example simulation loop showing agent evolution via skill reuse."""

import random
import time
from protocols.utils.skills import EmbodiedAgent, Skill
from protocols.utils.forking import fork_agent
from protocols.utils.fatigue import FatigueMemoryMixin
from protocols.utils.messaging import MessageHub, Message

# --- Setup ---
bus = MessageHub()
all_agents: list['EvolvableAgent'] = []


def dummy_analyze(data: str) -> dict[str, str]:
    return {"analysis": f"len={len(str(data))}"}


def dummy_patch(data: dict[str, str]) -> dict[str, str]:
    return {"patch": f"fixed_{data.get('bug', 'issue')}"}

# --- Evolving Agent Class ---


class EvolvableAgent(EmbodiedAgent, FatigueMemoryMixin):
    def __init__(self, name: str) -> None:
        EmbodiedAgent.__init__(self, name)
        FatigueMemoryMixin.__init__(self)
        self.memory['success'] = 0
        self.memory['runs'] = 0

    def success_rate(self) -> float:
        runs = self.memory['runs']
        return self.memory['success'] / runs if runs > 0 else 0

    def record_outcome(self, success: bool = True) -> None:
        self.memory['runs'] += 1
        if success:
            self.memory['success'] += 1


# --- Create Founders ---
founder1 = EvolvableAgent("AgentAlpha")
founder1.register_skill(Skill("analyze", dummy_analyze))
founder2 = EvolvableAgent("AgentBeta")
founder2.register_skill(Skill("patch", dummy_patch))

all_agents.extend([founder1, founder2])

# --- Message Flow ---


def on_new_task(msg: Message) -> None:
    task_type = msg.data.get("type")
    for agent in all_agents:
        if task_type in agent.skills:
            fatigue = agent.fatigue_score(task_type)
            print(f"[{agent.name}] fatigue={fatigue:.2f}")
            if fatigue < 0.7:
                agent.register_task(task_type)
                result = agent.invoke(task_type, msg.data)
                print(f"[{agent.name}] did {task_type}: {result}")
                agent.record_outcome(success=random.random() > 0.2)  # 80% chance success

                # evolution
                if agent.success_rate() > 0.9 and agent.memory['runs'] >= 5:
                    clone = fork_agent(agent, {"name": f"{agent.name}_v{random.randint(2, 9)}"})
                    all_agents.append(clone)
                    print(f"🌱 {clone.name} forked from {agent.name}")


bus.subscribe("task:new", on_new_task)

# --- Simulate Loop ---
tasks = [
    {"type": "analyze", "data": "something"},
    {"type": "patch", "bug": "nullpointer"},
    {"type": "analyze", "data": "database index missing"},
    {"type": "patch", "bug": "race condition"},
]

print("--- Simulation Running ---")

for i in range(12):
    task = random.choice(tasks)
    print(f"\n--- TICK {i+1}: Publishing task {task['type']} ---")
    bus.publish("task:new", task)
    time.sleep(1)

print("\n--- Simulation Ended ---")
