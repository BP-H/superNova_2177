# protocols/agents/patch_reviewer.py

"""
PatchReviewer Agent
- Watches incoming PR diffs
- Analyzes for common failure signatures
- Comments inline with suggestions
- Can auto-format code based on repo lint config
- Can use LLM backend via hook for style improvement
"""

from typing import List, Dict, Any, Optional
import difflib

class PatchReviewer:
    def __init__(self, name="PatchReviewer", llm_hook: Optional[Any] = None):
        self.name = name
        self.llm_hook = llm_hook

    def review_diff(self, filename: str, old: str, new: str) -> List[str]:
        """Return list of suggestions or comments."""
        comments = []
        diff = list(difflib.unified_diff(
            old.splitlines(), new.splitlines(), lineterm=""
        ))

        for i, line in enumerate(diff):
            if line.startswith("+") and "print(" in line:
                comments.append(f"Avoid using print in production: `{line}`")
            elif line.startswith("-") and "assert " in line:
                comments.append(f"Check removed assert: `{line}`")

        # Optional: LLM-based style feedback
        if self.llm_hook:
            feedback = self.llm_hook.suggest_style(filename, new)
            if feedback:
                comments.append("LLM style suggestions: " + feedback)

        return comments

    def auto_format(self, content: str) -> str:
        # Naive replacement for tabs/spaces, could plug into black/ruff etc
        return content.replace("\t", "    ")

    def handle_pr(self, pr_files: Dict[str, Dict[str, str]]) -> Dict[str, List[str]]:
        """
        Accepts a dict:
        {
            "filename.py": {"old": "...", "new": "..."},
            ...
        }
        Returns per-file comments.
        """
        review = {}
        for fname, changes in pr_files.items():
            review[fname] = self.review_diff(fname, changes.get("old", ""), changes.get("new", ""))
        return review


# Optional mock LLM hook for stylistic advice
class DummyLLMHook:
    def suggest_style(self, filename: str, content: str) -> str:
        if "TODO" in content:
            return "Consider removing TODO comments before merge."
        return ""


if __name__ == "__main__":
    agent = PatchReviewer(llm_hook=DummyLLMHook())
    test_files = {
        "example.py": {
            "old": "def test():\n    print(\"Hello\")\n",
            "new": "def test():\n    print(\"Hi\")\n    # TODO: clean up\n"
        }
    }
    print(agent.handle_pr(test_files))
