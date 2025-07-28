# protocols/agents/ci_watcher.py

from protocols.internal_protocol import InternalAgentProtocol

class CIRepairman(InternalAgentProtocol):
    """
    CIRepairman listens for CI errors and attempts repairs using LLM hooks.
    Can be extended with GitHub/GitLab API calls for PR comments.
    """
    def __init__(self, model_hook=None):
        super().__init__()
        self.name = "CIRepairman"
        self.hook = model_hook  # Callable GPT function or LLM agent

    def analyze_logs(self, ci_logs: str) -> dict:
        if self.hook is None:
            return {"error": "No LLM hook provided"}
        prompt = f"You are a CI specialist. Given the logs:\n{ci_logs}\n\nWhat’s wrong? Suggest a fix."
        return self.hook(prompt)

    def handle_ci_failure(self, logs: str) -> dict:
        analysis = self.analyze_logs(logs)
        self.send("CI_FIX_PROPOSAL", analysis)
        return analysis
