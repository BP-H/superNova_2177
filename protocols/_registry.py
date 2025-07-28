"""Registry of core protocol agents and their purposes."""

from .agents.ci_pr_protector_agent import CI_PRProtectorAgent
from .agents.guardian_interceptor_agent import GuardianInterceptorAgent
from .agents.meta_validator_agent import MetaValidatorAgent
from .agents.observer_agent import ObserverAgent

# Mapping of agent names to (class, short description)
AGENT_REGISTRY = {
    "CI_PRProtectorAgent": (
        CI_PRProtectorAgent,
        "Repairs CI/PR failures by proposing patches.",
    ),
    "GuardianInterceptorAgent": (
        GuardianInterceptorAgent,
        "Inspects LLM suggestions for risky content.",
    ),
    "MetaValidatorAgent": (
        MetaValidatorAgent,
        "Audits patches and adjusts trust scores.",
    ),
    "ObserverAgent": (
        ObserverAgent,
        "Monitors agent outputs and suggests forks when needed.",
    ),
}
