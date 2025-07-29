# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
"""Registry of core protocol agents and their purposes."""

from .agents.ci_pr_protector_agent import CI_PRProtectorAgent
from .agents.guardian_interceptor_agent import GuardianInterceptorAgent
from .agents.meta_validator_agent import MetaValidatorAgent
from .agents.observer_agent import ObserverAgent
from .agents.collaborative_planner_agent import CollaborativePlannerAgent
from .agents.coordination_sentinel_agent import CoordinationSentinelAgent
from .agents.harmony_synthesizer_agent import HarmonySynthesizerAgent
from .agents.temporal_audit_agent import TemporalAuditAgent
from .agents.cross_universe_bridge_agent import CrossUniverseBridgeAgent
from .agents.anomaly_spotter_agent import AnomalySpotterAgent
from .agents.quantum_resonance_agent import QuantumResonanceAgent
from .agents.codex_agent import CodexAgent

# Mapping of agent names to metadata dictionaries
AGENT_REGISTRY = {
    "CI_PRProtectorAgent": {
        "class": CI_PRProtectorAgent,
        "description": "Repairs CI/PR failures by proposing patches.",
        "llm_capable": True,
    },
    "GuardianInterceptorAgent": {
        "class": GuardianInterceptorAgent,
        "description": "Inspects LLM suggestions for risky content.",
        "llm_capable": True,
    },
    "MetaValidatorAgent": {
        "class": MetaValidatorAgent,
        "description": "Audits patches and adjusts trust scores.",
        "llm_capable": True,
    },
    "ObserverAgent": {
        "class": ObserverAgent,
        "description": "Monitors agent outputs and suggests forks when needed.",
        "llm_capable": False,
    },
    "CollaborativePlannerAgent": {
        "class": CollaborativePlannerAgent,
        "description": "Coordinates tasks and delegates to the best agent.",
        "llm_capable": False,
    },
    "CoordinationSentinelAgent": {
        "class": CoordinationSentinelAgent,
        "description": "Detects suspicious validator coordination patterns.",
        "llm_capable": False,
    },
    "HarmonySynthesizerAgent": {
        "class": HarmonySynthesizerAgent,
        "description": "Transforms metrics into short MIDI snippets.",
        "llm_capable": False,
    },
    "TemporalAuditAgent": {
        "class": TemporalAuditAgent,
        "description": "Audits timestamps for suspicious gaps or disorder.",
        "llm_capable": False,
    },
    "CrossUniverseBridgeAgent": {
        "class": CrossUniverseBridgeAgent,
        "description": "Validates cross-universe remix provenance.",
        "llm_capable": True,
    },
    "AnomalySpotterAgent": {
        "class": AnomalySpotterAgent,
        "description": "Flags anomalies in metrics streams.",
        "llm_capable": True,
    },
    "QuantumResonanceAgent": {
        "class": QuantumResonanceAgent,
        "description": "Tracks resonance via quantum simulation.",
        "llm_capable": True,
    },
    "CodexAgent": {
        "class": CodexAgent,
        "description": "Base agent with in-memory utilities.",
        "llm_capable": False,
    },
}
