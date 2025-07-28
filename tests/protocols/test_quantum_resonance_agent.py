import pytest

from protocols.agents.quantum_resonance_agent import QuantumResonanceAgent
from quantum_sim import QuantumContext


def stub_entangle(self, src, dst, influence_factor=1.0, bidirectional=True):
    stub_entangle.calls.append((src, dst, influence_factor, bidirectional))
    return "entangled"


def stub_prediction(self, users):
    stub_prediction.calls.append(list(users))
    return {
        "predicted_interactions": {u: 0.5 for u in users},
        "overall_quantum_coherence": 0.7,
        "uncertainty_estimate": 0.1,
        "method": "stub",
    }


def stub_measure(self, input_value, error_rate=0.0):
    stub_measure.calls.append(input_value)
    return {"value": 0.42}


def stub_decoherence(self, entropy):
    stub_decoherence.calls.append(entropy)
    return 0.123


def test_record_interaction(monkeypatch):
    stub_entangle.calls = []
    monkeypatch.setattr(QuantumContext, "entangle_entities", stub_entangle)

    agent = QuantumResonanceAgent()
    result = agent.record_interaction({"source": "a", "target": "b", "strength": 2})

    assert result == {"status": "ok"}
    assert stub_entangle.calls == [("a", "b", 2.0, True)]


def test_query_resonance_llm_backend(monkeypatch):
    stub_prediction.calls = []
    stub_measure.calls = []
    monkeypatch.setattr(QuantumContext, "quantum_prediction_engine", stub_prediction)
    monkeypatch.setattr(QuantumContext, "measure_superposition", stub_measure)

    llm_calls = []

    def backend(prompt):
        llm_calls.append(prompt)
        return "note"

    agent = QuantumResonanceAgent(llm_backend=backend)
    result = agent.query_resonance({"users": ["x", "y"]})

    assert result["resonance_level"] == 0.42
    assert result["predicted_interactions"] == {"x": 0.5, "y": 0.5}
    assert result["llm_note"] == "note"
    assert llm_calls and "Resonance summary" in llm_calls[0]
    assert stub_prediction.calls == [["x", "y"]]
    assert pytest.approx(stub_measure.calls[0]) == 0.5


def test_adjust_for_entropy(monkeypatch):
    stub_decoherence.calls = []
    monkeypatch.setattr(QuantumContext, "adapt_decoherence_rate", stub_decoherence)

    agent = QuantumResonanceAgent()
    result = agent.adjust_for_entropy({"entropy": 10})

    assert result == {"decoherence_rate": 0.123}
    assert stub_decoherence.calls == [10.0]

