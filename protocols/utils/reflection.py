"""Self-reflection helpers for agents."""

__all__ = ["self_reflect"]
from typing import List


def self_reflect(agent, memory_log: List[dict]) -> dict:
    last_output = memory_log[-1] if memory_log else {}
    if "ERROR" in str(last_output):
        agent.send("SELF_FIX", {"note": "attempting auto-correction"})
        return agent.process_event({"event": "RETRY", "payload": last_output})
    return {"status": "ok"}
