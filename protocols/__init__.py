# protocols/__init__.py

from ._registry import AGENT_REGISTRY
from .agents.ci_pr_protector_agent import CI_PRProtectorAgent
from .agents.guardian_interceptor_agent import GuardianInterceptorAgent
from .agents.meta_validator_agent import MetaValidatorAgent
from .agents.observer_agent import ObserverAgent
from .core.contracts import AgentTaskContract
from .core.profiles import AgentProfile
from .profiles.dream_weaver import DreamWeaver
from .profiles.validator_elf import ValidatorElf
from .utils.forking import fork_agent
from .utils.reflection import self_reflect
from .utils.remote import handshake, ping_agent

__all__ = [
    "AgentProfile",
    "AgentTaskContract",
    "self_reflect",
    "ping_agent",
    "handshake",
    "fork_agent",
    "ValidatorElf",
    "DreamWeaver",
    "CI_PRProtectorAgent",
    "GuardianInterceptorAgent",
    "MetaValidatorAgent",
    "ObserverAgent",
    "AGENT_REGISTRY",
]
