# internal_protocol.py

class InternalAgentProtocol:
    """
    Internal protocol to standardize how agent modules communicate
    with the UI and each other.
    """
    def __init__(self):
        self.memory = {}  # store transient agent state
        self.cache = {}   # for temporary results or datasets
        self.flags = set()  # feature or behavior toggles

    def send(self, msg_type: str, payload: dict) -> dict:
        """
        Agents send standardized messages.
        - msg_type: e.g., 'INTEGRITY_RESULT', 'ANALYSIS_META', 'RFC_SUMMARY'
        - payload: any dict-compatible data
        """
        self.memory[msg_type] = payload
        return {"ack": True, "received": msg_type}

    def retrieve(self, msg_type: str) -> dict:
        return self.memory.get(msg_type, {})


# tests/conftest.py
import pytest
import sys
import types

@pytest.fixture(autouse=True)
def mock_streamlit(monkeypatch):
    """Patch streamlit globally across all tests."""
    stub = types.ModuleType("streamlit")
    stub.__getattr__ = lambda name: lambda *args, **kwargs: None
    stub.secrets = {}
    monkeypatch.setitem(sys.modules, "streamlit", stub)


# Optional CI agent check (ci_agent.py)
from internal_protocol import InternalAgentProtocol

def run_ci_diagnostics():
    protocol = InternalAgentProtocol()
    # replace with actual logic to parse RFCs or validations
    protocol.send("RFC_SUMMARY", {"count": 7})
    return protocol.retrieve("RFC_SUMMARY")


# GitHub CI config snippet (.github/workflows/test.yml)
# name: run-tests
#
# on:
#   pull_request:
#   push:
#
# jobs:
#   test:
#     runs-on: ubuntu-latest
#     env:
#       PYTHONUNBUFFERED: 1
#       ENV: ci
#     steps:
#       - uses: actions/checkout@v3
#       - name: Set up Python
#         uses: actions/setup-python@v4
#         with:
#           python-version: "3.10"
#       - run: pip install -e .[dev]
#       - run: pytest --tb=short -q
