# protocols/meta_validator_agent.py

"""
MetaValidatorAgent++: enhanced with LLM interrogation, repair planning, and ethics probing.
Catches hallucinated patches, misaligned behavior, and decays untrustworthy agents.

The class now accepts an optional ``llm_backend`` callable used for generating
repair plans or other text analyses when provided.
"""

import random
import uuid

from protocols.core.internal_protocol import InternalAgentProtocol


class MetaValidatorAgent(InternalAgentProtocol):
    """Scores patches and agents to enforce quality control.

    Parameters
    ----------
    trust_registry : dict
        Mutable mapping of agent names to trust scores.
    llm_backend : callable, optional
        Optional function used to generate repair plans or analyses.
    """

    def __init__(self, trust_registry: dict, llm_backend=None):
        super().__init__()
        self.name = "MetaValidator"
        self.trust_registry = trust_registry  # {agent_name: float}
        self.llm_backend = llm_backend
        self.receive("EVALUATE_PATCH", self.evaluate_patch)
        self.receive("LLM_RESPONSE", self.intercept_llm)
        self.receive("AGENT_REPORT", self.audit_agent_behavior)
        self.receive("REPAIR_PLAN_REQUEST", self.suggest_repair_plan)

    def evaluate_patch(self, payload):
        proposer = payload.get("agent")
        patch = payload.get("patch")
        explanation = payload.get("explanation")
        belief = self.trust_registry.get(proposer, 0.5)

        score = self.judge_patch(patch, explanation, belief)
        self.adjust_trust(proposer, score)
        return {"trust_update": self.trust_registry[proposer], "verdict": score}

    def judge_patch(self, patch, explanation, belief):
        if not patch.strip() or "# No valid patch" in patch:
            return -0.5
        score = belief + random.uniform(-0.1, 0.3)
        if "explo" in explanation.lower():
            score += 0.2
        return min(max(score, 0), 1)

    def adjust_trust(self, agent, score):
        prior = self.trust_registry.get(agent, 0.5)
        updated = round((prior + score) / 2, 4)
        self.trust_registry[agent] = updated

    def intercept_llm(self, payload):
        content = payload.get("text", "")
        tokens = len(content.split())
        hallucination_warning = any(
            word in content.lower()
            for word in ["obviously", "clearly", "definitely", "guaranteed"]
        )
        oversell = any(
            phrase in content.lower() for phrase in ["perfect fix", "always works"]
        )

        quality = (
            "HIGH"
            if tokens > 50 and not hallucination_warning and not oversell
            else "LOW"
        )
        return {
            "length": tokens,
            "hallucination": hallucination_warning,
            "oversell": oversell,
            "quality": quality,
            "llm_id": payload.get("llm_id", str(uuid.uuid4())),
        }

    def audit_agent_behavior(self, payload):
        agent_name = payload.get("agent")
        ops = payload.get("operations", [])
        drift = sum(1 for op in ops if op.get("alignment_score", 1) < 0.5)

        if drift > 3:
            self.trust_registry[agent_name] = max(
                0.0, self.trust_registry.get(agent_name, 0.5) - 0.1
            )
            return {
                "drift_detected": True,
                "action": "decayed_trust",
                "new_score": self.trust_registry[agent_name],
            }
        return {"status": "ok"}

    def suggest_repair_plan(self, payload):
        broken_patch = payload.get("patch")
        issue = payload.get("issue", "unknown")

        if self.llm_backend:
            prompt = (
                "Generate a brief repair plan for" f" issue '{issue}':\n{broken_patch}"
            )
            plan_text = self.llm_backend(prompt)
            plan = [plan_text]
            estimate = "unknown"
        else:
            plan = [
                f"Scan patch for unsafe functions related to '{issue}'",
                "Apply CI sandbox test",
                "Run hallucination detector on response trace",
                "Propose 2-step retry patch with comment logging",
            ]
            estimate = "<2min"
        return {"repair_plan": plan, "estimated_fix_time": estimate}


# Example Usage:
# trust_map = {"PatchBot": 0.6, "CI_PRProtector": 0.8}
# meta = MetaValidatorAgent(trust_map)
# meta.send("EVALUATE_PATCH", {"agent": "PatchBot", "patch": "print('fix')", "explanation": "Fixes null ptr"})
