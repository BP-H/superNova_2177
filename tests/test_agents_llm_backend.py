import types
from collections import defaultdict

from protocols.agents.ci_pr_protector_agent import CI_PRProtectorAgent
from protocols.agents.guardian_interceptor_agent import GuardianInterceptorAgent
from protocols.agents.meta_validator_agent import MetaValidatorAgent
from protocols.agents.observer_agent import ObserverAgent


def test_ci_pr_protector_uses_llm_backend():
    calls = []

    def backend(prompt):
        calls.append(prompt)
        return """```python\nprint('ok')\n```"""

    def default(prompt):
        raise AssertionError("default LLM should not be called")

    agent = CI_PRProtectorAgent(default, llm_backend=backend)
    result = agent.handle_ci_failure({"repo": "r", "branch": "b", "logs": "fail"})

    assert calls and "fail" in calls[0]
    assert result["proposed_patch"] == "print('ok')"


def test_guardian_interceptor_llm_backend():
    calls = []

    def backend(text):
        calls.append(text)
        return text

    agent = GuardianInterceptorAgent(llm_backend=backend)
    result = agent.inspect_suggestion({"content": "delete all"})

    assert calls and calls[0] == "delete all"
    assert result["risk_level"] == "HIGH"


def test_meta_validator_repair_plan_backend():
    calls = []

    def backend(prompt):
        calls.append(prompt)
        return "use hammer"

    agent = MetaValidatorAgent({}, llm_backend=backend)
    plan = agent.suggest_repair_plan({"patch": "x", "issue": "bug"})

    assert calls and "bug" in calls[0]
    assert plan["repair_plan"] == ["use hammer"]


def test_observer_agent_llm_backend_called():
    calls = []

    def backend(prompt):
        calls.append(prompt)

    class Hub:
        def subscribe(self, *args):
            pass

    class Fatigue:
        task_count = defaultdict(int)

        def fatigue_score(self, task):
            return 0

    registry = {"a": object()}
    agent = ObserverAgent(Hub(), registry, Fatigue(), llm_backend=backend)
    msg = types.SimpleNamespace(data={"agent": "a", "task": "t", "result": {}})
    agent.observe(msg)

    assert calls and "agent a" in calls[0]


from protocols.agents.anomaly_spotter_agent import AnomalySpotterAgent
from protocols.agents.cross_universe_bridge_agent import CrossUniverseBridgeAgent
from protocols.agents.quantum_resonance_agent import QuantumResonanceAgent


def test_anomaly_spotter_llm_backend():
    calls = []

    def backend(text):
        calls.append(text)
        return text

    agent = AnomalySpotterAgent(llm_backend=backend)
    result = agent.inspect_data({"metrics": [1, 2], "notes": "attack"})

    assert calls and "attack" in calls[0]
    assert result["flagged"]


def test_cross_universe_bridge_llm_backend():
    calls = []

    def backend(prompt):
        calls.append(prompt)

    agent = CrossUniverseBridgeAgent(llm_backend=backend)
    agent.register_bridge(
        {
            "coin_id": "c1",
            "source_universe": "u1",
            "source_coin": "s1",
            "proof": "p",
        }
    )

    assert calls and calls[0].startswith("verify")


def test_quantum_resonance_llm_backend():
    calls = []

    def backend(prompt):
        calls.append(prompt)
        return "note"

    agent = QuantumResonanceAgent(llm_backend=backend)
    result = agent.query_resonance({"users": ["a"]})

    assert calls and "Resonance summary" in calls[0]
    assert result["llm_note"] == "note"
