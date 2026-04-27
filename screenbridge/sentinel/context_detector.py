"""Sensitive context detection for HALT/WARN/SAFE decisions."""

from __future__ import annotations

import re
from typing import Any, Literal


class ContextDetector:
    """Detects sensitive screen contexts.

    Uses hybrid detection:
    - URL pattern matching (for web browsers)
    - Keyword/phrase detection in OCR text
    - UI element analysis (input field types)
    """

    # Sensitive URL patterns
    URL_PATTERNS: dict[str, list[str]] = {
        "financial": [
            r"checkout", r"cart", r"payment", r"billing",
            r"paypal", r"stripe", r"square",
            r"bank", r"crypto", r"wallet", r"coinbase",
            r"trading", r"invest", r"brokerage"
        ],
        "healthcare": [
            r"patient", r"medical", r"health.*portal",
            r"prescription", r"lab.*results", r"diagnosis"
        ],
        "auth": [
            r"login", r"signin", r"auth", r"2fa",
            r"verify", r"reset.*password", r"forgot.*password"
        ]
    }

    # Sensitive keyword patterns in text
    TEXT_KEYWORDS: dict[str, list[str]] = {
        "financial": [
            "credit card", "card number", "cvv", "expir",
            "account number", "routing number", "bitcoin",
            "payment method", "total amount", "checkout",
            "enter card", "billing address"
        ],
        "healthcare": [
            "patient id", "medical record", "diagnosis",
            "prescription", "health insurance", "provider",
            "ssn", "date of birth", "blood type"
        ],
        "auth": [
            "password", "enter password", "confirm password",
            "security code", "verification code", "2fa",
            "authenticator", "passkey"
        ],
        "personal_docs": [
            "passport", "driver license", "tax return",
            "w-2", "w-4", "1099", "birth certificate",
            "social security card"
        ],
        "password_manager": [
            "1password", "lastpass", "bitwarden", "dashlane",
            "keeper", "master password", "vault"
        ]
    }

    # UI element patterns that indicate sensitive contexts
    ELEMENT_PATTERNS: dict[str, list[str]] = {
        "financial": ["cvv", "card number", "expiration"],
        "auth": ["password", "security code", "pin"],
    }

    def __init__(self, sensitivity_level: str = "balanced") -> None:
        """Initialize context detector.

        Args:
            sensitivity_level: "paranoid", "balanced", or "relaxed"
        """
        self.sensitivity_level = sensitivity_level

        # Thresholds based on sensitivity level
        self.thresholds = {
            "paranoid": {"halt": 0.3, "warn": 0.1},
            "balanced": {"halt": 0.6, "warn": 0.3},
            "relaxed": {"halt": 0.8, "warn": 0.5}
        }[sensitivity_level]

    def detect_context(
        self,
        summary: dict[str, Any]
    ) -> dict[str, Any]:
        """Detect if screen contains sensitive context.

        Args:
            summary: Structured summary from ScreenProcessor

        Returns:
            Detection result:
            {
                "decision": "HALT" | "WARN" | "SAFE",
                "confidence": 0.0-1.0,
                "context_type": "financial" | "healthcare" | ...,
                "reason": "Detected payment page with card input fields",
                "matches": [...] # What triggered detection
            }
        """
        # Check for each context type
        detections = []

        # 1. URL-based detection (if available)
        url_detection = self._detect_from_url(summary)
        if url_detection:
            detections.append(url_detection)

        # 2. Text keyword detection
        text_detection = self._detect_from_text(summary.get("full_text", ""))
        if text_detection:
            detections.append(text_detection)

        # 3. Element-based detection
        element_detection = self._detect_from_elements(summary.get("element_tree", {}))
        if element_detection:
            detections.append(element_detection)

        # No detections = SAFE
        if not detections:
            return {
                "decision": "SAFE",
                "confidence": 1.0,
                "context_type": None,
                "reason": "No sensitive context detected",
                "matches": []
            }

        # Aggregate detections - take highest confidence
        best_detection = max(detections, key=lambda d: d["confidence"])

        # Make HALT/WARN/SAFE decision based on confidence
        if best_detection["confidence"] >= self.thresholds["halt"]:
            decision = "HALT"
        elif best_detection["confidence"] >= self.thresholds["warn"]:
            decision = "WARN"
        else:
            decision = "SAFE"

        return {
            "decision": decision,
            "confidence": best_detection["confidence"],
            "context_type": best_detection["context_type"],
            "reason": best_detection["reason"],
            "matches": best_detection["matches"]
        }

    def _detect_from_url(self, summary: dict[str, Any]) -> dict[str, Any] | None:
        """Detect sensitive context from URL patterns.

        Args:
            summary: Screen summary

        Returns:
            Detection dict or None
        """
        # Try to extract URL from element tree (browser address bar)
        element_tree = summary.get("element_tree", {})

        # Look for URL text in address bar elements
        url_text = None
        for element in element_tree.values():
            elem_type = element.get("type", "")
            elem_label = element.get("label", "").lower()

            if elem_type in {"textfield", "combobox"} and ("http" in elem_label or "www" in elem_label):
                url_text = elem_label
                break

        if not url_text:
            return None

        # Check URL against patterns
        for context_type, patterns in self.URL_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, url_text, re.IGNORECASE):
                    return {
                        "confidence": 0.85,  # High confidence for URL matches
                        "context_type": context_type,
                        "reason": f"URL contains {pattern} pattern",
                        "matches": [{"type": "url", "pattern": pattern, "match": url_text}]
                    }

        return None

    def _detect_from_text(self, full_text: str) -> dict[str, Any] | None:
        """Detect sensitive context from OCR text.

        Args:
            full_text: Full OCR-extracted text

        Returns:
            Detection dict or None
        """
        if not full_text:
            return None

        full_text_lower = full_text.lower()
        best_match = None
        max_matches = 0

        for context_type, keywords in self.TEXT_KEYWORDS.items():
            matches = []
            for keyword in keywords:
                if keyword.lower() in full_text_lower:
                    matches.append(keyword)

            if len(matches) > max_matches:
                max_matches = len(matches)
                best_match = {
                    "confidence": min(0.5 + (len(matches) * 0.1), 0.95),
                    "context_type": context_type,
                    "reason": f"Detected {context_type} keywords: {', '.join(matches[:3])}",
                    "matches": [{"type": "keyword", "keyword": kw} for kw in matches]
                }

        return best_match

    def _detect_from_elements(self, element_tree: dict[str, Any]) -> dict[str, Any] | None:
        """Detect sensitive context from UI elements.

        Args:
            element_tree: Element tree dict

        Returns:
            Detection dict or None
        """
        if not element_tree:
            return None

        # Look for sensitive input fields
        for context_type, patterns in self.ELEMENT_PATTERNS.items():
            matches = []

            for element in element_tree.values():
                elem_type = element.get("type", "")
                elem_label = element.get("label", "").lower()

                # Focus on input fields
                if elem_type in {"textfield", "securetextfield", "passwordfield"}:
                    for pattern in patterns:
                        if pattern in elem_label:
                            matches.append({
                                "element_id": element.get("id"),
                                "label": elem_label,
                                "pattern": pattern
                            })

            if matches:
                return {
                    "confidence": 0.90,  # High confidence for input field matches
                    "context_type": context_type,
                    "reason": f"Detected {context_type} input fields",
                    "matches": [{"type": "element", **m} for m in matches]
                }

        return None

    def is_password_manager(self, element_tree: dict[str, Any]) -> bool:
        """Detect if password manager app is active.

        Args:
            element_tree: Element tree dict

        Returns:
            True if password manager detected
        """
        root = element_tree.get("1", {})
        root_label = root.get("label", "").lower()

        password_managers = ["1password", "lastpass", "bitwarden", "dashlane", "keeper"]

        return any(pm in root_label for pm in password_managers)
