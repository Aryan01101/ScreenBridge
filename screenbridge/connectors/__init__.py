"""
Connectors module - LLM-specific adapters.

Provides connectors for:
- Claude (Anthropic SDK)
- OpenAI (GPT-4)
- Gemini (Google Generative AI)
- Ollama (Local LLMs)

All connectors implement the BaseLLMConnector interface.
"""

from screenbridge.connectors.base import BaseLLMConnector
from screenbridge.connectors.claude import ClaudeConnector
from screenbridge.connectors.openai import OpenAIConnector
from screenbridge.connectors.gemini import GeminiConnector
from screenbridge.connectors.ollama import OllamaConnector

__all__ = [
    "BaseLLMConnector",
    "ClaudeConnector",
    "OpenAIConnector",
    "GeminiConnector",
    "OllamaConnector",
]
