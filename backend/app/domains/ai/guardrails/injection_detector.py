import re
from typing import List, Dict, Any
from pydantic import BaseModel, Field


class InjectionScanResult(BaseModel):
    is_injection: bool = False
    risk_score: float = 0.0
    detected_patterns: List[str] = Field(default_factory=list)
    action_recommended: str = "allow"  # "allow", "flag", "block"


class PromptInjectionDetector:
    """
    Multi-lingual rule-based & heuristic prompt injection scanner for sales agents.
    Detects instruction override, role swapping, credential hunting, and authority attacks.
    """

    ADVERSARIAL_PATTERNS = [
        # Instruction Overrides (English)
        (r"(?i)\bignore\s+(all\s+)?(previous|prior|above)\s+instructions\b", "instruction_override"),
        (r"(?i)\bdisregard\s+(your\s+)?(rules|prompts|guidelines)\b", "instruction_override"),
        (r"(?i)\b(?:enable\s+|switch\s+to\s+|you\s+are\s+now\s+(?:in\s+)?|activate\s+)(?:developer|debug|god|unrestricted|dan|jailbreak|root)\s+mode\b", "mode_switch"),
        (r"(?i)\b(reveal|show|print|display|tell\s+me)\s+(your\s+)?(system\s+prompt|initial\s+prompt|hidden\s+instructions)\b", "prompt_exfiltration"),
        (r"(?i)\b(what\s+are\s+your|repeat\s+the)\s+(system\s+instructions|system\s+prompt)\b", "prompt_exfiltration"),
        (r"(?i)\b(pretend|act\s+as\s+if)\s+you\s+have\s+no\s+(rules|restrictions|limits)\b", "jailbreak_dan"),
        (r"(?i)\b(do\s+anything\s+now|system\s+override|sudo\s+mode|bypass\s+restrictions)\b", "jailbreak_dan"),
        
        # Social Engineering & Authority Claims (English)
        (r"(?i)\b(?:i\s+am|i\'?m)\s+(?:the\s+)?(?:store\s+|platform\s+|company\s+)?(?:owner|admin|developer|tester|ceo|founder|creator|boss|supervisor|system\s+administrator)\b", "authority_impersonation"),
        (r"(?i)\bthis\s+is\s+a\s+(test|security\s+audit)\s+from\s+(management|headquarters)\b", "authority_impersonation"),

        # Arabic Attacks (تجاهل الأوامر، انتحال هوية المدير، استخراج التعليمات)
        (r"(تجاهل|انسَ|الغِ)\s+(كل\s+)?(التعليمات|الأوامر|القواعد|التوجيهات)\s*(السابقة)?", "ar_instruction_override"),
        (r"(أظهر|اكشف|ما\s+هو)\s+(البرومبت|التعليمات\s+السرية|نظامك\s+الداخلي)", "ar_prompt_exfiltration"),
        (r"أنا\s+(صاحب\s+المحل|المدير|المطور|الأدمن|المبرمج|رئيس\s+مجلس\s+الإدارة)", "ar_authority_impersonation"),
        (r"(وضع\s+المطور|وضع\s+التصحيح|الوضع\s+المتقدم|تخطي\s+القيود|أنت\s+الآن\s+غير\s+مقيد)", "ar_mode_switch"),
    ]

    @classmethod
    def scan(cls, text: str) -> InjectionScanResult:
        """Scan input string against prompt injection and jailbreak signatures."""
        if not text:
            return InjectionScanResult()

        detected = []
        for pattern, pattern_name in cls.ADVERSARIAL_PATTERNS:
            if re.search(pattern, text):
                detected.append(pattern_name)

        if not detected:
            return InjectionScanResult(
                is_injection=False,
                risk_score=0.0,
                detected_patterns=[],
                action_recommended="allow"
            )

        # Calculate risk based on matches
        score = min(1.0, len(detected) * 0.45)
        is_inj = score >= 0.4
        action = "block" if score >= 0.7 else ("flag" if is_inj else "allow")

        return InjectionScanResult(
            is_injection=is_inj,
            risk_score=round(score, 2),
            detected_patterns=list(set(detected)),
            action_recommended=action
        )
