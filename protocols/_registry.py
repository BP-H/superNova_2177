"""Registry of core protocol agents and their purposes."""

from .agents.ci_pr_protector_agent import CI_PRProtectorAgent
from .agents.guardian_interceptor_agent import GuardianInterceptorAgent
from .agents.meta_validator_agent import MetaValidatorAgent
from .agents.observer_agent import ObserverAgent
from .agents.anomaly_spotter_agent import AnomalySpotterAgent

# Mapping of agent names to metadata dictionaries
AGENT_REGISTRY = {
    "CI_PRProtectorAgent": {
        "cls": CI_PRProtectorAgent,
        "description": "Repairs CI/PR failures by proposing patches.",
        "llm_capable": True,
    },
    "GuardianInterceptorAgent": {
        "cls": GuardianInterceptorAgent,
        "description": "Inspects LLM suggestions for risky content.",
        "llm_capable": True,
    },
    "MetaValidatorAgent": {
        "cls": MetaValidatorAgent,
        "description": "Audits patches and adjusts trust scores.",
        "llm_capable": True,
    },
    "ObserverAgent": {
        "cls": ObserverAgent,
        "description": "Monitors agent outputs and suggests forks when needed.",
        "llm_capable": False,
    },
    "AnomalySpotterAgent": {
        "cls": AnomalySpotterAgent,
        "description": "Flags unusual metrics for early risk detection.",
        "llm_capable": False,
    },
}
