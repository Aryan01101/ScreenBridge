"""
Transport module - LLM communication and agentic loop management.

Responsible for:
- Sending structured summaries to LLMs
- Receiving action instructions from LLMs
- Managing agentic loop state
- Translation between canonical format and LLM-specific formats
"""

from screenbridge.transport.llm_bridge import LLMBridge

__all__ = ["LLMBridge"]
