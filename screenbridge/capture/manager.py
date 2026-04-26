"""Screenshot capture manager with session storage."""

from __future__ import annotations

from pathlib import Path
from typing import Any


class CaptureManager:
    """Manages screenshot capture and local storage.

    Never sends raw screenshots to cloud - all processing happens locally.
    """

    def __init__(self, config: Any, session_path: Path) -> None:
        self.config = config
        self.session_path = session_path
        self.frames_path = session_path / "frames"

    async def initialize(self) -> None:
        """Initialize capture system and create session directories."""
        self.frames_path.mkdir(parents=True, exist_ok=True)

    async def cleanup(self) -> None:
        """Cleanup capture resources."""
        pass

    async def capture_screen(self) -> dict[str, Any]:
        """Capture current screen state.

        Returns:
            Dict with screenshot path and metadata
        """
        # TODO: Implement with mss
        return {"screenshot_path": None, "timestamp": None}
