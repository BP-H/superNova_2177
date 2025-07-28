import asyncio
import logging
from config import Config
from agent_core import RemixAgent

logger = logging.getLogger(__name__)
logger.propagate = False

async def self_improvement_task(agent: RemixAgent) -> None:
    """Periodically trigger ``RemixAgent.self_improve``."""
    while True:
        try:
            await asyncio.sleep(Config.SELF_IMPROVE_INTERVAL_SECONDS)
            suggestions = agent.self_improve()
            if suggestions:
                logger.info("Self improvement suggestions: %s", "; ".join(suggestions))
        except asyncio.CancelledError:
            logger.info("self_improvement_task cancelled")
            break
        except Exception:
            logger.error("self_improvement_task error", exc_info=True)
