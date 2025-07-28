"""Meticulous audit-focused agent profile."""
from protocols.core.profiles import AgentProfile

ValidatorElf = AgentProfile(
    name="ValidatorElf",
    traits=["meticulous", "audit-focused"],
    powers=["validate_patch", "score_integrity"],
)
