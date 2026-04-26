"""OpenAI connector for GPT-4."""

from __future__ import annotations

from typing import Any

from screenbridge.connectors.base import BaseLLMConnector


class OpenAIConnector(BaseLLMConnector):
    """OpenAI GPT connector with function calling."""

    def __init__(self, api_key: str, model: str = "gpt-4-turbo") -> None:
        self.api_key = api_key
        self.model = model
        self._client: Any = None

    async def initialize(self) -> None:
        """Initialize OpenAI client."""
        # TODO: Import and initialize openai.AsyncOpenAI
        pass

    async def cleanup(self) -> None:
        """Cleanup OpenAI resources."""
        pass

    async def send_message(
        self,
        summary: dict[str, Any],
        task: str,
        history: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Send to OpenAI and receive actions."""
        # TODO: Implement OpenAI API call
        return {"actions": []}

    @property
    def name(self) -> str:
        return "OpenAI"
