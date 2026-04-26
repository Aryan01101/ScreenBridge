"""LLM communication bridge and agentic loop manager."""

from __future__ import annotations

from typing import Any


class LLMBridge:
    """Manages communication with LLMs and agentic loop state.

    Translates between canonical ScreenBridge format and LLM-specific formats.
    """

    def __init__(self, llm_connector: Any, config: Any) -> None:
        self.llm_connector = llm_connector
        self.config = config

    async def initialize(self) -> None:
        """Initialize LLM connector."""
        pass

    async def cleanup(self) -> None:
        """Cleanup LLM resources."""
        pass

    async def send_summary(self, summary: dict[str, Any]) -> list[dict[str, Any]]:
        """Send summary to LLM and get action instructions.

        Args:
            summary: Structured summary from processor

        Returns:
            List of actions to execute
        """
        # TODO: Implement LLM communication
        return []
