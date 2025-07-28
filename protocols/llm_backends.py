"""Backend helper functions for common LLM providers."""
from typing import Callable, Any


# The returned callable takes a prompt and optional kwargs and returns the text
# content from the provider or an error string.

def default_gpt_backend(api_key: str) -> Callable[[str], str]:
    """Create a simple OpenAI ChatGPT caller."""

    def call(prompt: str, model: str = "gpt-3.5-turbo", **kwargs: Any) -> str:
        try:
            import openai

            openai.api_key = api_key
            response = openai.ChatCompletion.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                **kwargs,
            )
            return response.choices[0].message["content"]
        except Exception as exc:  # noqa: BLE001
            return f"ERROR: {exc}"

    return call


def claude_backend(api_key: str) -> Callable[[str], str]:
    """Create an Anthropic Claude caller."""

    def call(prompt: str, model: str = "claude-3-opus-20240229", **kwargs: Any) -> str:
        try:
            import anthropic

            client = (
                anthropic.Anthropic(api_key=api_key)
                if hasattr(anthropic, "Anthropic")
                else anthropic.Client(api_key)
            )
            response = client.messages.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                **kwargs,
            )
            content = getattr(response, "content", None)
            if isinstance(content, list) and content and hasattr(content[0], "text"):
                return content[0].text
            if isinstance(content, str):
                return content
            return str(content)
        except Exception as exc:  # noqa: BLE001
            return f"ERROR: {exc}"

    return call


def gemini_backend(api_key: str) -> Callable[[str], str]:
    """Create a Google Gemini caller."""

    def call(prompt: str, model: str = "gemini-pro", **kwargs: Any) -> str:
        try:
            import google.generativeai as genai

            genai.configure(api_key=api_key)
            model_obj = genai.GenerativeModel(model)
            response = model_obj.generate_content(prompt, **kwargs)
            return response.text
        except Exception as exc:  # noqa: BLE001
            return f"ERROR: {exc}"

    return call

