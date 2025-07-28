"""Create mutated copies of existing agents."""
from typing import Any, Dict
import copy


def fork_agent(agent: Any, mutation: Dict[str, Any]) -> Any:
    child = copy.deepcopy(agent)
    for key, value in mutation.items():
        setattr(child, key, value)
    child.send("FORK_NOTICE", {"from": agent.__class__.__name__})
    return child
