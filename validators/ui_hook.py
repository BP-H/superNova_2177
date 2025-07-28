from __future__ import annotations

from typing import Any, Dict, List
import logging

from validator_reputation_tracker import update_validator_reputations
from protocols.utils.messaging import MessageHub

logger = logging.getLogger(__name__)
logger.propagate = False

# Message bus used to track reputation update events
message_bus = MessageHub()


async def update_reputations_ui(validations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Update validator reputations from UI data and emit status events."""
    message_bus.publish("reputation_update", {"status": "start", "count": len(validations)})
    result = update_validator_reputations(validations)
    message_bus.publish(
        "reputation_update",
        {"status": "complete", "reputation_count": len(result.get("reputations", {}))},
    )
    return result
