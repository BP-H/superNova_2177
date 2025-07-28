# protocols/agents/ci_repairman.py

from protocols.internal_protocol import InternalAgentProtocol
from typing import Callable, Optional
import logging

logger = logging.getLogger(__name__)

class CIRepairman(InternalAgentProtocol):
    """
    CIRepairman is a stability-focused autonomous agent responsible for
    identifying and fixing CI or PR issues. It uses external LLM hooks (like GPT)
    to suggest fixes and can communicate with GitHub APIs or internal systems.
    """
    def __init__(self, model_hook: Optional[Callable[[str], dict]] = None):
        super().__init__()
        self.name = "CIRepairman"
        self.hook = model_hook  # LLM or diagnostic function callable
        self.memory["last_logs"] = ""

    def update_logs(self, log_text: str) -> None:
        self.memory["last_logs"] = log_text
        logger.info("Logs updated in CIRepairman memory.")

    def suggest_fix(self) -> dict:
        logs = self.memory.get("last_logs", "")
        if not logs:
            return {"error": "No CI logs provided"}

        if not self.hook:
            logger.warning("No model hook connected to CIRepairman.")
            return {"error": "No hook connected"}

        prompt = f"You're a CI assistant. Analyze the following logs and suggest fixes:\n\n{logs}\n\nFix in bullet points."
        response = self.hook(prompt)
        self.send("CI_FIX_PROPOSAL", response)
        return response

    def describe_role(self) -> str:
        return (
            f"Agent {self.name}: connects to CI logs, suggests fixes using external models, "
            "can trigger retry protocols or post comments to PRs."
        )

# Optional: register this agent with a factory or orchestration system
