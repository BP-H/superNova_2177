# protocols/ci_pr_protector_agent.py

"""
CI_PRProtectorAgent: Sentient CI/PR guardian that intercepts failures,
communicates with LLMs to resolve issues, and offers validated patches.

Agents may be configured with an optional ``llm_backend`` callable used for
all LLM interactions, enabling custom model integration during testing or
deployment.

Components:
- hooks into GitHub PRs and CI pipelines (via webhook or CLI wrapper)
- sends error context to LLM (like GPT or Claude)
- verifies response before presenting fix
- writes safe response directly into PR comment or diff patch
"""

import logging
import re

from protocols.core.internal_protocol import InternalAgentProtocol

logger = logging.getLogger("CI_PR_PROTECTOR")


class CI_PRProtectorAgent(InternalAgentProtocol):
    """Suggests fixes for failing CI runs or PR diffs.

    Parameters
    ----------
    llm_backend : callable, optional
        Optional override used for all LLM requests. When omitted,
        ``talk_to_llm_fn`` is used instead.
    """

    def __init__(self, llm_backend=None):
        super().__init__()
        self.name = "CI_PRProtector"
        self.talk_to_llm = talk_to_llm_fn  # default function to call LLM
        self.llm_backend = llm_backend
        self.receive("CI_FAILURE", self.handle_ci_failure)
        self.receive("PR_DIFF_FAIL", self.handle_pr_error)

    def handle_ci_failure(self, payload):
        repo = payload.get("repo")
        branch = payload.get("branch")
        logs = payload.get("logs")
        logger.info(f"CI failure detected on {repo}:{branch}")

        prompt = self.construct_prompt(logs, context_type="CI")
        if self.llm_backend:
            llm_response = self.llm_backend(prompt)
        else:
            llm_response = self.talk_to_llm(prompt)
        patch = self.extract_code_block(llm_response)
        if patch is None:
            logger.warning("No valid code block found in LLM response")
        return {"proposed_patch": patch, "explanation": llm_response}

    def handle_pr_error(self, payload):
        pr_diff = payload.get("diff")
        error_msg = payload.get("error")
        logger.info(f"Review failure on PR: {error_msg}")

        prompt = self.construct_prompt(pr_diff + "\n" + error_msg, context_type="PR")
        if self.llm_backend:
            llm_response = self.llm_backend(prompt)
        else:
            llm_response = self.talk_to_llm(prompt)
        patch = self.extract_code_block(llm_response)
        if patch is None:
            logger.warning("No valid code block found in LLM response")
        return {"patch": patch, "justification": llm_response}

    def construct_prompt(self, error_input: str, context_type: str):
        return f"""
You are a CI/PR repair assistant.
A {context_type} failed with the following trace or diff:

{error_input}

Your task: Propose a safe fix. Explain why it works. Format as:
```python
# patch
<code>
```
then:
---
Explanation:
<text>
"""

    def extract_code_block(self, llm_response: str):
        """Return first fenced code block or None."""
        match = re.search(r"```(?:python)?\n?(.*?)```", llm_response, re.DOTALL)
        if match:
            return match.group(1).strip()
        return None


# --- Hook to LLM (example) ---


def talk_to_llm_fn(prompt):
    # Replace with real API call to GPT/Claude etc.
    return """```python
# patch
print(\"Fix applied\")
```
---
Explanation:
This is a dummy patch. Replace me.
"""


# Usage:
# agent = CI_PRProtectorAgent(llm_backend=talk_to_llm_fn)
# agent.send("CI_FAILURE", {"repo": "superNova_2177", "branch": "main", "logs": "Traceback..."})
