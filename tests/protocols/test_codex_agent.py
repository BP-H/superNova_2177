from protocols.agents.codex_agent import CodexAgent


def test_memory_helpers():
    agent = CodexAgent()
    agent.remember("k", 42)
    assert agent.recall("k") == 42
    assert agent.recall("missing", 0) == 0
