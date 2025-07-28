# protocols/__init__.py

from ._registry import AGENT_REGISTRY  # noqa: F401
from .core.contracts import AgentTaskContract  # noqa: F401
from .core.profiles import AgentProfile  # noqa: F401
from .profiles.dream_weaver import DreamWeaver  # noqa: F401
from .profiles.validator_elf import ValidatorElf  # noqa: F401
from .utils.forking import fork_agent  # noqa: F401
from .utils.reflection import self_reflect  # noqa: F401
from .utils.remote import handshake, ping_agent  # noqa: F401

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
