import pytest

from protocols.agents.guardian_interceptor_agent import GuardianInterceptorAgent


def test_detect_risks_patterns():
    agent = GuardianInterceptorAgent()
    assert "Destructive command without context" in agent._detect_risks("please delete file")
    assert "Security bypass term detected" in agent._detect_risks("try to BYPASS checks")


def test_inspect_suggestion_with_backend():
    calls = []

    def backend(text):
        calls.append(text)
        return "delete all"

    agent = GuardianInterceptorAgent(llm_backend=backend)
    result = agent.inspect_suggestion({"content": "ignored"})

    assert calls == ["ignored"]
    assert result["risk_level"] == "HIGH"
    assert "Destructive command without context" in result["flags"]


def test_propose_fix_without_backend():
    agent = GuardianInterceptorAgent()
    res = agent.propose_fix({"issue": "bug", "context": "ctx"})
    assert "# Auto-generated patch to address: bug" in res["patch"]
    assert "[Fix applied]" in res["patch"]


def test_propose_fix_with_backend():
    def backend(prompt):
        return "patched"

    agent = GuardianInterceptorAgent(llm_backend=backend)
    res = agent.propose_fix({"issue": "bug", "context": "ctx"})
    assert res["patch"] == "patched"
