"""
Sentinel module - Privacy and safety guardian.

Responsible for:
- Detecting sensitive screen contexts (financial, healthcare, auth)
- PII redaction (emails, credit cards, phone numbers, SSN, API keys)
- HALT/WARN/SAFE decision pipeline
- Audit logging of all safety decisions
"""

from screenbridge.sentinel.sentinel_layer import SentinelLayer

__all__ = ["SentinelLayer"]
