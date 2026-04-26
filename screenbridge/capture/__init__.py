"""
Capture module - Screenshot capture and local storage management.

Responsible for:
- Taking screenshots via mss (cross-platform)
- Storing raw screenshots locally (NEVER sent to cloud)
- Managing session folders
- Enforcing retention policies
"""

from screenbridge.capture.manager import CaptureManager

__all__ = ["CaptureManager"]
