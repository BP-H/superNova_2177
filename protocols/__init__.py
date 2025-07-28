# protocols/__init__.py

from .core.profiles import AgentProfile
from .core.contracts import AgentTaskContract
from .utils.reflection import self_reflect
from .utils.remote import ping_agent, handshake
from .utils.forking import fork_agent
from .profiles.validator_elf import ValidatorElf
from .profiles.dream_weaver import DreamWeaver

from .agents.ci_pr_protector_agent import CI_PRProtectorAgent
from .agents.guardian_interceptor_agent import GuardianInterceptorAgent
from .agents.meta_validator_agent import MetaValidatorAgent
from .agents.observer_agent import ObserverAgent

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
]
