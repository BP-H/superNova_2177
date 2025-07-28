# protocols/__init__.py

from ._registry import AGENT_REGISTRY
from .core.contracts import AgentTaskContract
from .core.profiles import AgentProfile
from .profiles.dream_weaver import DreamWeaver
from .profiles.validator_elf import ValidatorElf
from .utils.forking import fork_agent
from .utils.reflection import self_reflect
from .utils.remote import handshake, ping_agent

# Expose agent classes for convenience
for _name, _info in AGENT_REGISTRY.items():
    globals()[_name] = _info["cls"]

__all__ = [
    "AgentProfile",
    "AgentTaskContract",
    "self_reflect",
    "ping_agent",
    "handshake",
    "fork_agent",
    "ValidatorElf",
    "DreamWeaver",
] + list(AGENT_REGISTRY.keys()) + ["AGENT_REGISTRY"]
