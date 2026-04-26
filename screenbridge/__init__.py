"""
ScreenBridge - Privacy-first middleware for LLM desktop control.

ScreenBridge is an open-source SDK that gives any LLM the ability to see and
interact with desktop applications while keeping raw screenshots local.

Core Philosophy:
- Raw screenshots NEVER leave the local machine
- Only structured JSON summaries sent to LLMs
- Built-in safety layer (SentinelLayer) halts on sensitive contexts
- LLM-agnostic design (Claude, GPT-4, Gemini, Ollama)

Example:
    >>> from screenbridge import ScreenBridge
    >>> from screenbridge.connectors import ClaudeConnector
    >>>
    >>> async with ScreenBridge(llm=ClaudeConnector(api_key="...")) as bridge:
    ...     await bridge.run("Open Spotify and play my liked songs")
"""

__version__ = "0.1.0"
__author__ = "ScreenBridge Contributors"
__license__ = "MIT"

from screenbridge.core import ScreenBridge, Config
from screenbridge.connectors import (
    ClaudeConnector,
    OpenAIConnector,
    GeminiConnector,
    OllamaConnector,
)

__all__ = [
    "ScreenBridge",
    "Config",
    "ClaudeConnector",
    "OpenAIConnector",
    "GeminiConnector",
    "OllamaConnector",
]
