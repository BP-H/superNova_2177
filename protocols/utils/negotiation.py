"""Delegation helpers for multi-agent collaboration."""
from protocols.core.profiles import AgentProfile


class AgentNegotiation:
    @staticmethod
    def propose_delegation(from_agent, to_agent: AgentProfile, task: str, payload: dict):
        if to_agent.can(task):
            from_agent.send("DELEGATE_PROPOSAL", {"to": to_agent.name, "task": task})
            return to_agent.process_event({"event": task, "payload": payload})
        return {"error": f"{to_agent.name} can't handle task '{task}'"}
