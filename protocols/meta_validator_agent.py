# protocols/meta_validator_agent.py

"""
MetaValidatorAgent: evaluates other agents' outputs for coherence, risk, and trust.
Used for second-order consensus and to detect hallucinations or bad logic in patches.
It also catches LLM responses and probes them for deeper reasoning.
"""

from protocols.agent_protocols_suite import InternalAgentProtocol
import uuid
import time
import random

class MetaValidatorAgent(InternalAgentProtocol):
    def __init__(self, trust_registry: dict):
        super().__init__()
        self.name = "MetaValidator"
        self.trust_registry = trust_registry  # {agent_name: float}
        self.receive("EVALUATE_PATCH", self.evaluate_patch)
        self.receive("LLM_RESPONSE", self.intercept_llm)

    def evaluate_patch(self, payload):
        proposer = payload.get("agent")
        patch = payload.get("patch")
        explanation = payload.get("explanation")
        belief = self.trust_registry.get(proposer, 0.5)

        score = self.judge_patch(patch, explanation, belief)
        self.adjust_trust(proposer, score)
        return {"trust_update": self.trust_registry[proposer], "verdict": score}

    def judge_patch(self, patch, explanation, belief):
        """Fake scoring system based on heuristics + randomness for now."""
        if not patch.strip() or "# No valid patch" in patch:
            return -0.5
        score = belief + random.uniform(-0.1, 0.3)
        if "explo" in explanation.lower():
            score += 0.2
        return min(max(score, 0), 1)

    def adjust_trust(self, agent, score):
        prior = self.trust_registry.get(agent, 0.5)
        updated = (prior + score) / 2
        self.trust_registry[agent] = updated

    def intercept_llm(self, payload):
        """Receives raw LLM outputs and probes them for hallucination or depth."""
        content = payload.get("text", "")
        tokens = len(content.split())
        hallucination_warning = any(word in content.lower() for word in ["obviously", "clearly", "definitely"])

        quality = "HIGH" if tokens > 50 and not hallucination_warning else "LOW"
        return {
            "length": tokens,
            "hallucination": hallucination_warning,
            "quality": quality,
            "llm_id": payload.get("llm_id", str(uuid.uuid4()))
        }


# Example Usage:
# trust_map = {"PatchBot": 0.6, "CI_PRProtector": 0.8}
# meta = MetaValidatorAgent(trust_map)
# meta.send("EVALUATE_PATCH", {"agent": "PatchBot", "patch": "print('fix')", "explanation": "Fixes null ptr"})
