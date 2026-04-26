"""
Core ScreenBridge orchestrator and configuration.

This module provides the main ScreenBridge class that coordinates all
subsystems: capture, processing, safety checks, LLM communication, and
action execution.
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from screenbridge.capture import CaptureManager
from screenbridge.processor import ScreenProcessor
from screenbridge.sentinel import SentinelLayer
from screenbridge.transport import LLMBridge
from screenbridge.executor import ActionExecutor
from screenbridge.security import SecurityManager


class Config(BaseModel):
    """ScreenBridge configuration.

    Attributes:
        privacy_tier: Privacy level (summarised, full, redacted, offline)
        max_steps: Maximum steps in agentic loop
        screenshot_format: Storage format for screenshots (jpeg, png, webp)
        retention_days: Days to keep session data
        rate_limit_actions_per_sec: Max actions per second
        rate_limit_actions_per_task: Max actions per task
        confirmation_required: Actions requiring user confirmation
        debug: Enable debug mode (verbose logs, visualizations)
        storage_path: Path to ScreenBridge storage directory
    """

    privacy_tier: str = Field(default="summarised", pattern="^(summarised|full|redacted|offline)$")
    max_steps: int = Field(default=10, ge=1, le=1000)
    screenshot_format: str = Field(default="jpeg", pattern="^(jpeg|png|webp)$")
    retention_days: int = Field(default=7, ge=1, le=365)
    rate_limit_actions_per_sec: int = Field(default=2, ge=1, le=100)
    rate_limit_actions_per_task: int = Field(default=50, ge=1, le=1000)
    confirmation_required: list[str] = Field(
        default_factory=lambda: [
            "delete_file",
            "send_message",
            "submit_form",
            "close_window",
            "execute_code",
        ]
    )
    debug: bool = False
    storage_path: Path = Field(default_factory=lambda: Path.home() / ".screenbridge")

    class Config:
        frozen = True  # Immutable config


class ScreenBridge:
    """Main ScreenBridge orchestrator.

    Coordinates all subsystems to provide LLMs with desktop vision and control
    while maintaining privacy and safety guarantees.

    Example:
        >>> async with ScreenBridge(llm=ClaudeConnector(api_key="...")) as bridge:
        ...     result = await bridge.run("Open Spotify")
        ...     print(result.success)
    """

    def __init__(
        self,
        llm: Any,  # LLMConnector type (imported dynamically to avoid circular deps)
        config: Optional[Config] = None,
    ) -> None:
        """Initialize ScreenBridge.

        Args:
            llm: LLM connector instance (ClaudeConnector, OpenAIConnector, etc.)
            config: Optional configuration override
        """
        self.config = config or Config()
        self._llm = llm

        # Initialize subsystems (will be created in __aenter__)
        self._capture: Optional[CaptureManager] = None
        self._processor: Optional[ScreenProcessor] = None
        self._sentinel: Optional[SentinelLayer] = None
        self._transport: Optional[LLMBridge] = None
        self._executor: Optional[ActionExecutor] = None
        self._security: Optional[SecurityManager] = None

        self._session_id: Optional[str] = None
        self._initialized = False

    async def __aenter__(self) -> ScreenBridge:
        """Async context manager entry - initialize all subsystems."""
        await self._initialize()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit - cleanup resources."""
        await self._cleanup()

    async def _initialize(self) -> None:
        """Initialize all subsystems and create session."""
        if self._initialized:
            return

        # Create session ID
        self._session_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        session_path = self.config.storage_path / "sessions" / self._session_id
        session_path.mkdir(parents=True, exist_ok=True)

        # Initialize subsystems
        self._capture = CaptureManager(config=self.config, session_path=session_path)
        self._processor = ScreenProcessor(config=self.config)
        self._sentinel = SentinelLayer(config=self.config)
        self._executor = ActionExecutor(config=self.config)
        self._security = SecurityManager(config=self.config, session_path=session_path)
        self._transport = LLMBridge(
            llm_connector=self._llm,
            config=self.config,
        )

        # Initialize each subsystem
        await self._capture.initialize()
        await self._processor.initialize()
        await self._sentinel.initialize()
        await self._executor.initialize()
        await self._security.initialize()
        await self._transport.initialize()

        self._initialized = True

    async def _cleanup(self) -> None:
        """Cleanup resources and save session data."""
        if not self._initialized:
            return

        # Cleanup subsystems in reverse order
        if self._transport:
            await self._transport.cleanup()
        if self._security:
            await self._security.cleanup()
        if self._executor:
            await self._executor.cleanup()
        if self._sentinel:
            await self._sentinel.cleanup()
        if self._processor:
            await self._processor.cleanup()
        if self._capture:
            await self._capture.cleanup()

        self._initialized = False

    async def run(self, task: str) -> dict[str, Any]:
        """Execute a task using the agentic loop.

        Args:
            task: Natural language task description

        Returns:
            Result dictionary with success status, steps taken, and outcome

        Raises:
            RuntimeError: If ScreenBridge not initialized
        """
        if not self._initialized:
            raise RuntimeError("ScreenBridge not initialized. Use 'async with' context manager.")

        # This will be implemented in the agentic loop module
        # For now, return a placeholder
        return {
            "success": False,
            "error": "Agentic loop not yet implemented",
            "task": task,
            "session_id": self._session_id,
        }
