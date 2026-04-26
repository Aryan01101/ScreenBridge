"""
Security module - Audit logging and permission management.

Responsible for:
- Audit trail of all actions
- User confirmation prompts
- Permission tier enforcement
- Session integrity tracking
"""

from screenbridge.security.security_manager import SecurityManager

__all__ = ["SecurityManager"]
