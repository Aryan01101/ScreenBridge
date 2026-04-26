"""Google Gemini connector."""

from __future__ import annotations

from typing import Any

from screenbridge.connectors.base import BaseLLMConnector


class GeminiConnector(BaseLLMConnector):
    """Google Gemini connector."""

    def __init__(self, api_key: str, model: str = "gemini-2.0-flash-exp") -> None:
        self.api_key = api_key
        self.model = model
        self._client: Any = None

    async def initialize(self) -> None:
        """Initialize Gemini client."""
        # TODO: Import and initialize google.generativeai
        pass

    async def cleanup(self) -> None:
        """Cleanup Gemini resources."""
        pass

    async def send_message(
        self,
        summary: dict[str, Any],
        task: str,
        history: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Send to Gemini and receive actions."""
        # TODO: Implement Gemini API call
        return {"actions": []}

    @property
    def name(self) -> str:
        return "Gemini"
