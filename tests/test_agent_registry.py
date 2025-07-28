import importlib
import inspect
import pkgutil

from protocols import AGENT_REGISTRY


def test_all_agents_registered():
    package = importlib.import_module("protocols.agents")
    for _, mod_name, is_pkg in pkgutil.iter_modules(package.__path__):
        if is_pkg:
            continue
        module = importlib.import_module(f"protocols.agents.{mod_name}")
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if name.endswith("Agent"):
                assert name in AGENT_REGISTRY, f"{name} missing from AGENT_REGISTRY"


def test_registry_classes_correct():
    package = importlib.import_module("protocols.agents")
    for _, mod_name, is_pkg in pkgutil.iter_modules(package.__path__):
        if is_pkg:
            continue
        module = importlib.import_module(f"protocols.agents.{mod_name}")
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if name.endswith("Agent"):
                assert AGENT_REGISTRY[name]["class"] is obj

