"""Base connector interface for LLM integrations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseLLMConnector(ABC):
    """Abstract base class for LLM connectors.

    All LLM connectors must implement this interface to ensure
    consistent behavior across different providers.
    """

    @abstractmethod
    async def send_message(
        self,
        summary: dict[str, Any],
        task: str,
        history: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Send summary to LLM and receive actions.

        Args:
            summary: Structured screen summary
            task: User's task description
            history: Previous conversation history

        Returns:
            LLM response with actions to execute
        """
        pass

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize connector resources."""
        pass

    @abstractmethod
    async def cleanup(self) -> None:
        """Cleanup connector resources."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Connector name for logging."""
        pass
