"""Registry of core protocol agents and their purposes."""

from .agents.ci_pr_protector_agent import CI_PRProtectorAgent
from .agents.guardian_interceptor_agent import GuardianInterceptorAgent
from .agents.meta_validator_agent import MetaValidatorAgent
from .agents.observer_agent import ObserverAgent
from .agents.collaborative_planner_agent import CollaborativePlannerAgent

# Mapping of agent names to tuples of (class, description, metadata)
AGENT_REGISTRY = {
    "CI_PRProtectorAgent": (
        CI_PRProtectorAgent,
        "Repairs CI/PR failures by proposing patches.",
        {"llm_capable": True},
    ),
    "GuardianInterceptorAgent": (
        GuardianInterceptorAgent,
        "Inspects LLM suggestions for risky content.",
        {"llm_capable": True},
    ),
    "MetaValidatorAgent": (
        MetaValidatorAgent,
        "Audits patches and adjusts trust scores.",
        {"llm_capable": True},
    ),
    "ObserverAgent": (
        ObserverAgent,
        "Monitors agent outputs and suggests forks when needed.",
        {"llm_capable": False},
    ),
    "CollaborativePlannerAgent": (
        CollaborativePlannerAgent,
        "Coordinates tasks and delegates to the best agent.",
        {"llm_capable": False},
    ),
}
