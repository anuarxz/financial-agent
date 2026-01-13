"""LLM client using LiteLLM for multi-provider support."""

import warnings
from typing import Any, Literal

import litellm
from litellm import completion

from src.config import get_settings


# Disable LiteLLM's default logging and pydantic warnings
litellm.suppress_debug_info = True
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

# Type alias for reasoning effort levels
ReasoningEffort = Literal["none", "low", "medium", "high"]


class LLMClient:
    def __init__(self, model: str | None = None, reasoning_effort: ReasoningEffort | None = None):
        settings = get_settings()
        self._model = model or settings.model_name
        self._reasoning_effort = reasoning_effort or settings.reasoning_effort

    def chat_completion(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        temperature: float = 0.7,
    ) -> dict[str, Any]:
        kwargs: dict[str, Any] = {
            "model": self._model,
            "messages": messages,
            "temperature": temperature,
        }

        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"

        # Add thinking config for Gemini 2.5+ models
        if self._reasoning_effort and self._reasoning_effort != "none":
            # Map reasoning_effort to budget_tokens
            budget_map = {"low": 1024, "medium": 4096, "high": 8192}
            budget = budget_map.get(self._reasoning_effort, 1024)
            kwargs["thinking"] = {
                "type": "enabled",
                "budget_tokens": budget,
            }

        response = completion(**kwargs)
        return response.model_dump()

    def extract_response(self, response: dict[str, Any]) -> dict[str, Any]:
        choice = response.get("choices", [{}])[0]
        message = choice.get("message", {})

        return {
            "content": message.get("content"),
            "tool_calls": message.get("tool_calls"),
            "finish_reason": choice.get("finish_reason"),
            "reasoning_content": message.get("reasoning_content"),
        }


OpenRouterClient = LLMClient
