"""Screenshot capture manager with session storage."""

from __future__ import annotations

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import mss
from PIL import Image


class CaptureManager:
    """Manages screenshot capture and local storage.

    Never sends raw screenshots to cloud - all processing happens locally.
    Screenshots are stored as JPEG in session-specific folders with configurable
    retention policies.
    """

    def __init__(self, config: Any, session_path: Path) -> None:
        """Initialize capture manager.

        Args:
            config: ScreenBridge configuration object
            session_path: Path to current session directory
        """
        self.config = config
        self.session_path = session_path
        self.frames_path = session_path / "frames"
        self._sct: Optional[mss.mss] = None
        self._frame_count = 0
        self._last_screenshot_path: Optional[Path] = None

    async def initialize(self) -> None:
        """Initialize capture system and create session directories."""
        self.frames_path.mkdir(parents=True, exist_ok=True)

        # Initialize mss in thread pool (it's not async-native)
        loop = asyncio.get_event_loop()
        self._sct = await loop.run_in_executor(None, mss.mss)

    async def cleanup(self) -> None:
        """Cleanup capture resources."""
        if self._sct:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._sct.close)
            self._sct = None

    async def capture_screen(self, monitor: int = 1) -> dict[str, Any]:
        """Capture current screen state and save to session folder.

        Args:
            monitor: Monitor number to capture (1 = primary, 0 = all monitors)

        Returns:
            Dict with screenshot metadata:
                - screenshot_path: Path to saved screenshot
                - timestamp: ISO format timestamp
                - frame_number: Sequential frame number
                - monitor: Monitor that was captured
                - resolution: (width, height) tuple

        Raises:
            RuntimeError: If capture system not initialized
        """
        if not self._sct:
            raise RuntimeError("CaptureManager not initialized. Call initialize() first.")

        loop = asyncio.get_event_loop()

        # Capture screenshot in thread pool
        def _capture() -> Any:
            return self._sct.grab(self._sct.monitors[monitor])

        screenshot = await loop.run_in_executor(None, _capture)

        # Generate frame metadata
        self._frame_count += 1
        timestamp = datetime.now()
        frame_number = self._frame_count

        # Convert to PIL Image and save as JPEG
        screenshot_path = self.frames_path / f"{frame_number:04d}.jpg"

        def _save_image() -> tuple[int, int]:
            img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)

            # Save with configurable quality (from config)
            quality = getattr(self.config, "compression_quality", 85)
            img.save(screenshot_path, "JPEG", quality=quality, optimize=True)

            return screenshot.size

        resolution = await loop.run_in_executor(None, _save_image)

        self._last_screenshot_path = screenshot_path

        # Create metadata JSON
        metadata = {
            "screenshot_path": str(screenshot_path),
            "timestamp": timestamp.isoformat(),
            "frame_number": frame_number,
            "monitor": monitor,
            "resolution": {"width": resolution[0], "height": resolution[1]},
            "format": self.config.screenshot_format,
        }

        # Save metadata alongside screenshot
        metadata_path = self.frames_path / f"{frame_number:04d}.json"
        async with asyncio.get_event_loop().run_in_executor(
            None,
            lambda: open(metadata_path, 'w')
        ) as f:
            await loop.run_in_executor(
                None,
                lambda: json.dump(metadata, open(metadata_path, 'w'), indent=2)
            )

        return metadata

    async def get_last_screenshot(self) -> Optional[Path]:
        """Get path to most recent screenshot.

        Returns:
            Path to last screenshot, or None if no screenshots captured yet
        """
        return self._last_screenshot_path

    def get_frame_count(self) -> int:
        """Get number of frames captured in this session.

        Returns:
            Total frame count
        """
        return self._frame_count
