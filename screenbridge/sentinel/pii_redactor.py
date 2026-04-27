"""PII detection and redaction module."""

from __future__ import annotations

import re
from typing import Any, Pattern


class PIIRedactor:
    """Detects and redacts personally identifiable information.

    Patterns for:
    - Email addresses
    - Credit card numbers (Visa, MasterCard, Amex, Discover)
    - Phone numbers (various formats)
    - Social Security Numbers (SSN/Tax IDs)
    - API keys (generic patterns)
    """

    # Regex patterns for PII detection
    PATTERNS: dict[str, Pattern[str]] = {
        "email": re.compile(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            re.IGNORECASE
        ),
        "credit_card": re.compile(
            r'\b(?:\d{4}[\s-]?){3}\d{4}\b'  # 16-digit with optional separators
        ),
        "phone_us": re.compile(
            r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b'
        ),
        "ssn": re.compile(
            r'\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b'  # SSN format XXX-XX-XXXX
        ),
        "api_key_generic": re.compile(
            r'\b[A-Za-z0-9_-]{20,}\b'  # Generic long alphanumeric strings
        ),
        # Specific API key patterns
        "api_key_openai": re.compile(
            r'\bsk-[A-Za-z0-9]{48}\b'  # OpenAI keys
        ),
        "api_key_anthropic": re.compile(
            r'\bsk-ant-[A-Za-z0-9-]{95}\b'  # Anthropic keys
        ),
        "api_key_aws": re.compile(
            r'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b'  # AWS access keys
        ),
    }

    def __init__(self) -> None:
        """Initialize PII redactor."""
        self._redaction_log: list[dict[str, Any]] = []

    def redact_text(
        self,
        text: str,
        types: list[str] | None = None,
        replacement: str = "[REDACTED]"
    ) -> tuple[str, list[dict[str, Any]]]:
        """Redact PII from text.

        Args:
            text: Text to redact
            types: List of PII types to redact (None = all)
            replacement: Replacement string for redacted content

        Returns:
            Tuple of (redacted_text, redaction_log)
            redaction_log contains: [{type, original_value, position, confidence}]
        """
        if types is None:
            types = list(self.PATTERNS.keys())

        redacted = text
        log = []

        for pii_type in types:
            if pii_type not in self.PATTERNS:
                continue

            pattern = self.PATTERNS[pii_type]
            matches = pattern.finditer(redacted)

            for match in matches:
                original = match.group()

                # Validate match (reduce false positives)
                if self._is_valid_pii(pii_type, original):
                    log.append({
                        "type": pii_type,
                        "original_value": original,
                        "position": match.span(),
                        "confidence": self._get_confidence(pii_type, original)
                    })

                    redacted = redacted.replace(original, f"{replacement}:{pii_type.upper()}")

        return redacted, log

    def redact_element_tree(
        self,
        element_tree: dict[str, Any],
        types: list[str] | None = None
    ) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        """Redact PII from element tree labels.

        Args:
            element_tree: Element tree dict
            types: List of PII types to redact (None = all)

        Returns:
            Tuple of (redacted_tree, redaction_log)
        """
        redacted_tree = {}
        all_logs = []

        for element_id, element_data in element_tree.items():
            redacted_element = element_data.copy()

            # Redact label field
            if "label" in redacted_element:
                redacted_label, log = self.redact_text(
                    redacted_element["label"],
                    types=types
                )
                redacted_element["label"] = redacted_label

                if log:
                    for entry in log:
                        entry["element_id"] = element_id
                    all_logs.extend(log)

            redacted_tree[element_id] = redacted_element

        return redacted_tree, all_logs

    def redact_text_blocks(
        self,
        text_blocks: list[dict[str, Any]],
        types: list[str] | None = None
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        """Redact PII from OCR text blocks.

        Args:
            text_blocks: List of OCR text block dicts
            types: List of PII types to redact (None = all)

        Returns:
            Tuple of (redacted_blocks, redaction_log)
        """
        redacted_blocks = []
        all_logs = []

        for block in text_blocks:
            redacted_block = block.copy()

            if "text" in redacted_block:
                redacted_text, log = self.redact_text(
                    redacted_block["text"],
                    types=types
                )
                redacted_block["text"] = redacted_text

                if log:
                    for entry in log:
                        entry["bbox"] = block.get("bbox")
                    all_logs.extend(log)

            redacted_blocks.append(redacted_block)

        return redacted_blocks, all_logs

    def _is_valid_pii(self, pii_type: str, value: str) -> bool:
        """Validate detected PII to reduce false positives.

        Args:
            pii_type: Type of PII
            value: Detected value

        Returns:
            True if likely valid PII, False otherwise
        """
        if pii_type == "credit_card":
            # Luhn algorithm check
            return self._luhn_check(value.replace(" ", "").replace("-", ""))

        elif pii_type == "api_key_generic":
            # Avoid false positives on common patterns
            # Must not be all same character, must have variety
            if len(set(value)) < 8:  # Too repetitive
                return False
            if value.isdigit():  # All numbers (probably not an API key)
                return False

        elif pii_type == "email":
            # Must have valid TLD
            if not re.search(r'\.(com|org|net|edu|gov|io|co|ai|dev|app)$', value, re.I):
                return False

        return True

    def _luhn_check(self, card_number: str) -> bool:
        """Validate credit card number using Luhn algorithm.

        Args:
            card_number: Card number string (digits only)

        Returns:
            True if valid per Luhn algorithm
        """
        if not card_number.isdigit():
            return False

        digits = [int(d) for d in card_number]
        checksum = 0

        # Double every second digit from right
        for i in range(len(digits) - 2, -1, -2):
            digits[i] *= 2
            if digits[i] > 9:
                digits[i] -= 9

        checksum = sum(digits)
        return checksum % 10 == 0

    def _get_confidence(self, pii_type: str, value: str) -> float:
        """Get confidence score for detected PII.

        Args:
            pii_type: Type of PII
            value: Detected value

        Returns:
            Confidence score 0.0-1.0
        """
        # High confidence for specific patterns
        if pii_type in {"api_key_openai", "api_key_anthropic", "api_key_aws"}:
            return 0.95

        # Medium-high for validated credit cards
        if pii_type == "credit_card" and self._luhn_check(value.replace(" ", "").replace("-", "")):
            return 0.90

        # Medium for common patterns
        if pii_type in {"email", "phone_us", "ssn"}:
            return 0.80

        # Lower for generic patterns
        return 0.60

    def get_redaction_summary(self, log: list[dict[str, Any]]) -> dict[str, int]:
        """Get summary of redactions.

        Args:
            log: Redaction log from redact_* methods

        Returns:
            Dict of {pii_type: count}
        """
        summary = {}
        for entry in log:
            pii_type = entry["type"]
            summary[pii_type] = summary.get(pii_type, 0) + 1
        return summary
