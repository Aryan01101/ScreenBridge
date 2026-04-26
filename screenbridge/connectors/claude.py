"""Claude connector via Anthropic SDK."""

from __future__ import annotations

from typing import Any

from screenbridge.connectors.base import BaseLLMConnector


class ClaudeConnector(BaseLLMConnector):
    """Anthropic Claude connector.

    Supports both direct API and MCP server mode.
    """

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-5-20250929") -> None:
        self.api_key = api_key
        self.model = model
        self._client: Any = None

    async def initialize(self) -> None:
        """Initialize Anthropic client."""
        # TODO: Import and initialize anthropic.AsyncAnthropic
        pass

    async def cleanup(self) -> None:
        """Cleanup Claude resources."""
        pass

    async def send_message(
        self,
        summary: dict[str, Any],
        task: str,
        history: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Send to Claude and receive actions."""
        # TODO: Implement Claude API call
        return {"actions": []}

    @property
    def name(self) -> str:
        return "Claude"
