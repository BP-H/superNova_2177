"""Creative patch-suggestion agent profile."""
from protocols.core.profiles import AgentProfile

DreamWeaver = AgentProfile(
    name="DreamWeaver",
    traits=["creative", "collaborative"],
    powers=["propose_patch", "ideate"],
)
