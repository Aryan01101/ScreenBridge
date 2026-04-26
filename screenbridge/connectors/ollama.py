"""Ollama connector for local LLMs."""

from __future__ import annotations

from typing import Any

from screenbridge.connectors.base import BaseLLMConnector


class OllamaConnector(BaseLLMConnector):
    """Ollama connector for fully local operation.

    Supports any model available via Ollama (Llama, Mistral, Phi, etc.).
    """

    def __init__(self, model: str = "llama3.2", host: str = "http://localhost:11434") -> None:
        self.model = model
        self.host = host
        self._client: Any = None

    async def initialize(self) -> None:
        """Initialize Ollama client."""
        # TODO: Import and initialize ollama.AsyncClient
        pass

    async def cleanup(self) -> None:
        """Cleanup Ollama resources."""
        pass

    async def send_message(
        self,
        summary: dict[str, Any],
        task: str,
        history: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Send to Ollama and receive actions."""
        # TODO: Implement Ollama API call
        return {"actions": []}

    @property
    def name(self) -> str:
        return f"Ollama({self.model})"
