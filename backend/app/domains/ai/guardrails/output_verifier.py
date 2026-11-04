import re
from typing import List, Tuple, Optional
from pydantic import BaseModel, Field


class OutputVerificationResult(BaseModel):
    is_safe: bool = True
    cleaned_output: str
    violations: List[str] = Field(default_factory=list)
    suggested_safe_fallback: Optional[str] = None


class OutputVerifier:
    """
    Validates model generation before delivery to the customer.
    Intercepts credential leaks, system prompt disclosures, and unauthorized policy promises.
    """

    SECRET_PATTERNS = [
        (r"(?i)\b(?:sk|pk|rk)_[a-zA-Z0-9_\-]{20,}\b", "api_key_leak"),
        (r"(?i)\bsk-proj-[a-zA-Z0-9_\-]{20,}\b", "openai_key_leak"),
        (r"(?i)\bAIza[0-9A-Za-z-_]{30,40}\b", "google_api_key_leak"),
        (r"\beyJ[a-zA-Z0-9_-]{10,}\.eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\b", "jwt_token_leak"),
        (r"(?i)postgres(?:ql)?:\/\/[^\s]+", "database_url_leak"),
    ]

    PROMPT_LEAK_PATTERNS = [
        (r"(?i)<SYSTEM_INSTRUCTIONS>", "system_prompt_tag_leak"),
        (r"(?i)<BRAND_IDENTITY", "brand_identity_tag_leak"),
        (r"(?i)<OPERATIONAL_BOUNDARIES>", "boundaries_tag_leak"),
        (r"(?i)GROUNDING MANDATE: Answer strictly based", "core_rules_leak"),
    ]

    @classmethod
    def verify(
        cls,
        model_output: str,
        max_allowed_discount_percent: float = 0.0,
        customer_language: str = "English"
    ) -> OutputVerificationResult:
        """Scan and verify AI generated response before sending to user."""
        if not model_output:
            return OutputVerificationResult(is_safe=True, cleaned_output="")

        violations = []
        cleaned = model_output

        # 1. Check for secret leaks
        for pattern, leak_type in cls.SECRET_PATTERNS:
            if re.search(pattern, cleaned):
                violations.append(leak_type)
                cleaned = re.sub(pattern, "[REDACTED_SECRET]", cleaned)

        # 2. Check for system prompt leaks
        for pattern, leak_type in cls.PROMPT_LEAK_PATTERNS:
            if re.search(pattern, cleaned):
                violations.append(leak_type)
                cleaned = re.sub(pattern, "", cleaned)

        # 3. Check for unauthorized discount promises
        discount_matches = re.findall(r"(?:(\d{1,2})%\s*(?:discount|خصم|off)|(?:discount|خصم|off)\s*(\d{1,2})%)", model_output, re.IGNORECASE)
        for d1, d2 in discount_matches:
            disc_str = d1 if d1 else d2
            val = float(disc_str)
            if val > max_allowed_discount_percent:
                violations.append(f"unauthorized_discount_exceeded_{val}%")

        if violations:
            is_critical = any("leak" in v or "unauthorized_discount" in v for v in violations)
            if is_critical:
                safe_fallback = (
                    "يسعدنا خدمتك دائماً! للاستفسار عن العروض والأسعار الحالية، يرجى مراجعة صفحة المنتجات أو التواصل مع فريق المبيعات."
                    if customer_language.lower() == "arabic"
                    else "I'm happy to help you with our verified products and services! Please check our catalog or contact support for current special terms."
                )
                return OutputVerificationResult(
                    is_safe=False,
                    cleaned_output=cleaned,
                    violations=violations,
                    suggested_safe_fallback=safe_fallback
                )

        return OutputVerificationResult(
            is_safe=True,
            cleaned_output=cleaned.strip(),
            violations=[]
        )
