import re
from typing import Dict, Any
from pydantic import BaseModel


class ModelRoute(BaseModel):
    tier: str  # "fast", "standard", "reasoning"
    model_name: str
    temperature: float
    max_output_tokens: int
    timeout_seconds: float


class ModelRouter:
    """
    Routes customer turns to optimal model tiers based on complexity and risk,
    optimizing latency and cost without compromising transaction safety.
    """

    GREETING_PATTERNS = [
        r"^(hi|hello|hey|good\s+morning|good\s+evening|welcome)$",
        r"^(أهلا|مرحبا|سلام|مساء\s+الخير|صباح\s+الخير|ازيك|ازيكو)$"
    ]

    COMPLEX_PATTERNS = [
        r"(refund|cancel|wrong\s+item|broken|lawsuit|dispute|manager|complaint)",
        r"(استرجاع|استبدال|فلوسي|شكوى|نصب|محامي|تعويض|مسروق)"
    ]

    MODELS = {
        "fast": ModelRoute(
            tier="fast",
            model_name="gemini-2.0-flash",
            temperature=0.3,
            max_output_tokens=300,
            timeout_seconds=4.0
        ),
        "standard": ModelRoute(
            tier="standard",
            model_name="gemini-2.0-flash",
            temperature=0.6,
            max_output_tokens=800,
            timeout_seconds=6.0
        ),
        "reasoning": ModelRoute(
            tier="reasoning",
            model_name="gemini-1.5-pro",
            temperature=0.4,
            max_output_tokens=1500,
            timeout_seconds=10.0
        )
    }

    @classmethod
    def route(cls, message: str) -> ModelRoute:
        """Evaluate complexity and return model configuration."""
        clean = message.strip().lower()

        # Check for simple greeting
        for pat in cls.GREETING_PATTERNS:
            if re.search(pat, clean):
                return cls.MODELS["fast"]

        # Check for complex dispute / complaint
        for pat in cls.COMPLEX_PATTERNS:
            if re.search(pat, clean):
                return cls.MODELS["reasoning"]

        # Standard sales turn
        return cls.MODELS["standard"]
