"""SentinelLayer - Privacy and safety guardian."""

from __future__ import annotations

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

from screenbridge.sentinel.pii_redactor import PIIRedactor
from screenbridge.sentinel.context_detector import ContextDetector


class SentinelLayer:
    """Detects sensitive contexts and makes HALT/WARN/SAFE decisions.

    Runs entirely locally before any data reaches LLM.

    Core responsibilities:
    - Detect financial, healthcare, auth screens
    - Redact PII before summaries are sent
    - Make HALT/WARN/SAFE decisions
    - Audit log all decisions
    """

    def __init__(self, config: Any) -> None:
        """Initialize SentinelLayer.

        Args:
            config: ScreenBridge configuration object
        """
        self.config = config
        self._pii_redactor: Optional[PIIRedactor] = None
        self._context_detector: Optional[ContextDetector] = None
        self._audit_log: list[dict[str, Any]] = []
        self._session_path: Optional[Path] = None

    async def initialize(self, session_path: Optional[Path] = None) -> None:
        """Initialize detection patterns and PII redaction rules.

        Args:
            session_path: Path to session directory for audit logs
        """
        self._pii_redactor = PIIRedactor()

        # Get sensitivity level from config
        sensitivity = getattr(
            getattr(self.config, "sentinel", {}),
            "sensitivity_level",
            "balanced"
        )
        self._context_detector = ContextDetector(sensitivity_level=sensitivity)

        self._session_path = session_path

    async def cleanup(self) -> None:
        """Cleanup sentinel resources and save audit log."""
        if self._session_path and self._audit_log:
            await self._save_audit_log()

    async def evaluate(
        self,
        summary: dict[str, Any],
        redact_pii: bool = True
    ) -> dict[str, Any]:
        """Evaluate if screen context is safe to proceed.

        This is the main entry point for SentinelLayer.

        Args:
            summary: Structured summary from ScreenProcessor
            redact_pii: Whether to redact PII (default True)

        Returns:
            Decision dict:
            {
                "status": "SAFE" | "WARN" | "HALT",
                "reason": "Explanation",
                "redacted_summary": {...},  # Summary with PII redacted
                "context_type": "financial" | ...,
                "confidence": 0.0-1.0,
                "pii_found": {...},  # What PII was redacted
                "timestamp": "ISO datetime"
            }
        """
        if not self._pii_redactor or not self._context_detector:
            raise RuntimeError("SentinelLayer not initialized")

        timestamp = datetime.now()

        # Step 1: Detect sensitive context
        context_result = self._context_detector.detect_context(summary)

        # Step 2: Redact PII if enabled
        redacted_summary = summary.copy()
        pii_summary = {}

        if redact_pii:
            # Redact element tree
            if "element_tree" in redacted_summary:
                redacted_tree, tree_log = self._pii_redactor.redact_element_tree(
                    redacted_summary["element_tree"]
                )
                redacted_summary["element_tree"] = redacted_tree

                if tree_log:
                    pii_summary.update(
                        self._pii_redactor.get_redaction_summary(tree_log)
                    )

            # Redact text blocks
            if "text_blocks" in redacted_summary:
                redacted_blocks, blocks_log = self._pii_redactor.redact_text_blocks(
                    redacted_summary["text_blocks"]
                )
                redacted_summary["text_blocks"] = redacted_blocks

                if blocks_log:
                    for pii_type, count in self._pii_redactor.get_redaction_summary(blocks_log).items():
                        pii_summary[pii_type] = pii_summary.get(pii_type, 0) + count

            # Redact full text
            if "full_text" in redacted_summary:
                redacted_text, text_log = self._pii_redactor.redact_text(
                    redacted_summary["full_text"]
                )
                redacted_summary["full_text"] = redacted_text

        # Build result
        result = {
            "status": context_result["decision"],
            "reason": context_result["reason"],
            "redacted_summary": redacted_summary,
            "context_type": context_result.get("context_type"),
            "confidence": context_result["confidence"],
            "pii_found": pii_summary,
            "timestamp": timestamp.isoformat(),
            "matches": context_result.get("matches", [])
        }

        # Log decision to audit trail
        await self._log_decision(result)

        return result

    async def _log_decision(self, decision: dict[str, Any]) -> None:
        """Log decision to audit trail.

        Args:
            decision: Decision dict from evaluate()
        """
        audit_entry = {
            "timestamp": decision["timestamp"],
            "status": decision["status"],
            "context_type": decision["context_type"],
            "confidence": decision["confidence"],
            "reason": decision["reason"],
            "pii_redacted": decision["pii_found"],
        }

        self._audit_log.append(audit_entry)

    async def _save_audit_log(self) -> None:
        """Save audit log to session directory."""
        if not self._session_path:
            return

        audit_path = self._session_path / "sentinel_audit.json"

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: audit_path.write_text(
                json.dumps(self._audit_log, indent=2)
            )
        )

    def get_audit_log(self) -> list[dict[str, Any]]:
        """Get current audit log.

        Returns:
            List of audit entries
        """
        return self._audit_log.copy()

    def get_statistics(self) -> dict[str, Any]:
        """Get SentinelLayer statistics for current session.

        Returns:
            Dict with halt/warn/safe counts, PII redaction counts, etc.
        """
        total = len(self._audit_log)
        if total == 0:
            return {
                "total_evaluations": 0,
                "halts": 0,
                "warnings": 0,
                "safe": 0,
                "pii_redactions": {}
            }

        halts = sum(1 for e in self._audit_log if e["status"] == "HALT")
        warnings = sum(1 for e in self._audit_log if e["status"] == "WARN")
        safe = sum(1 for e in self._audit_log if e["status"] == "SAFE")

        # Aggregate PII redactions
        pii_totals = {}
        for entry in self._audit_log:
            for pii_type, count in entry.get("pii_redacted", {}).items():
                pii_totals[pii_type] = pii_totals.get(pii_type, 0) + count

        return {
            "total_evaluations": total,
            "halts": halts,
            "warnings": warnings,
            "safe": safe,
            "pii_redactions": pii_totals,
            "context_types_detected": list(set(
                e["context_type"] for e in self._audit_log
                if e["context_type"]
            ))
        }


# Add missing Optional import
from typing import Optional
