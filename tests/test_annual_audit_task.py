import asyncio
import ast
from pathlib import Path
import types
import pytest

# Dynamically load the annual_audit_task definition without importing heavy deps
src = Path(__file__).resolve().parents[1] / "superNova_2177.py"
text = src.read_text()
tree = ast.parse(text)
func_code = None
for node in tree.body:
    if isinstance(node, ast.AsyncFunctionDef) and node.name == "annual_audit_task":
        func_code = ast.get_source_segment(text, node)
        break
namespace = {}
globals()['CosmicNexus'] = object
globals()['logger'] = types.SimpleNamespace(info=lambda *a, **k: None)
exec(func_code, globals(), namespace)
annual_audit_task = namespace["annual_audit_task"]

class DummyConfig:
    ANNUAL_AUDIT_INTERVAL_SECONDS = 0.01

class DummyNexus:
    def __init__(self):
        self.calls = 0
    def quantum_audit(self):
        self.calls += 1

def test_annual_audit_task_triggers_quantum_audit():
    globals()["Config"] = DummyConfig
    nexus = DummyNexus()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    task = loop.create_task(annual_audit_task(nexus))
    loop.run_until_complete(asyncio.sleep(0.02))
    task.cancel()
    try:
        loop.run_until_complete(task)
    except asyncio.CancelledError:
        pass
    assert nexus.calls >= 1
    loop.close()
