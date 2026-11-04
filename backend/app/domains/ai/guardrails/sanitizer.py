import re
from typing import Tuple


class InputSanitizer:
    """
    Validates and normalizes untrusted incoming customer inputs before
    processing by prompt builders or LLMs.
    """

    MAX_MESSAGE_LENGTH: int = 2000

    @classmethod
    def sanitize(cls, raw_input: str) -> Tuple[bool, str, str]:
        """
        Validate length, strip malicious control characters and prompt delimiter escapes.
        Returns: (is_valid, cleaned_text, reason_if_invalid)
        """
        if not raw_input or not raw_input.strip():
            return False, "", "Empty message received"

        text = raw_input.strip()

        # Enforce max length
        if len(text) > cls.MAX_MESSAGE_LENGTH:
            return False, "", f"Message exceeds maximum allowed length of {cls.MAX_MESSAGE_LENGTH} characters"

        # Strip control characters (except newline, tab)
        cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)

        # Neutralize XML delimiter injection attempts by escaping brackets
        cleaned = cleaned.replace("<SYSTEM_INSTRUCTIONS>", "&lt;SYSTEM_INSTRUCTIONS&gt;")
        cleaned = cleaned.replace("</SYSTEM_INSTRUCTIONS>", "&lt;/SYSTEM_INSTRUCTIONS&gt;")
        cleaned = cleaned.replace("<BRAND_IDENTITY", "&lt;BRAND_IDENTITY")
        cleaned = cleaned.replace("</BRAND_IDENTITY>", "&lt;/BRAND_IDENTITY&gt;")
        cleaned = cleaned.replace("<OPERATIONAL_BOUNDARIES>", "&lt;OPERATIONAL_BOUNDARIES&gt;")
        cleaned = cleaned.replace("</OPERATIONAL_BOUNDARIES>", "&lt;/OPERATIONAL_BOUNDARIES&gt;")
        cleaned = cleaned.replace("<RETRIEVED_EVIDENCE>", "&lt;RETRIEVED_EVIDENCE&gt;")
        cleaned = cleaned.replace("</RETRIEVED_EVIDENCE>", "&lt;/RETRIEVED_EVIDENCE&gt;")

        return True, cleaned, ""
