import re
from typing import Optional


class PIIRedactor:
    """
    Sanitizes log messages and trace records to prevent customer PII
    or authentication secrets from persisting in log drains.
    """

    PATTERNS = [
        # Email Addresses
        (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "[REDACTED_EMAIL]"),
        # Phone Numbers (International and regional formats e.g. +201..., 010..., 011...)
        (r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4,5}", "[REDACTED_PHONE]"),
        (r"\b01[0125]\d{8}\b", "[REDACTED_PHONE]"),  # Egyptian mobile format
        # Credit Card Numbers
        (r"\b(?:\d{4}[-\s]?){3}\d{4}\b", "[REDACTED_CARD]"),
        # Bearer tokens & API Keys
        (r"(?i)bearer\s+[a-zA-Z0-9_\-\.]{15,}", "[REDACTED_BEARER]"),
        (r"(?i)(?:key|token|secret|password)\s*[:=]\s*['\"]?[^\s'\"]+['\"]?", "[REDACTED_SECRET]"),
    ]

    @classmethod
    def redact(cls, text: Optional[str]) -> str:
        """Redact all sensitive PII and secrets in string."""
        if not text:
            return ""
        result = text
        for pattern, replacement in cls.PATTERNS:
            result = re.sub(pattern, replacement, result)
        return result
