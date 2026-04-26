"""
Executor module - Action execution on desktop.

Responsible for:
- Element-based actions (click_element, type_into_element)
- Coordinate-based fallback (click, type, scroll, hotkey)
- Auto-upgrade layer (coordinates → elements when possible)
- Rate limiting and safety checks
- Confirmation prompts for destructive actions
"""

from screenbridge.executor.action_executor import ActionExecutor

__all__ = ["ActionExecutor"]
