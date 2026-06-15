"""Abstract base classes and data structures for AI providers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ProviderFunctionCall:
    """Structured representation of an AI-initiated function call."""

    name: str
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProviderResponse:
    """Standard return payload for AI provider responses."""

    text: str = ""
    function_calls: List[ProviderFunctionCall] = field(default_factory=list)
    tokens_used: int = 0
    cost: float = 0.0
    model: Optional[str] = None
    raw_response: Optional[Any] = None

    def to_dict(self) -> Dict[str, Any]:
        """Return dictionary with backwards-compatible shape."""
        return {
            "text": self.text,
            "function_calls": [
                {"name": call.name, "parameters": call.parameters}
                for call in self.function_calls
            ],
            "tokens_used": self.tokens_used,
            "cost": self.cost,
            "model": self.model,
            "raw_response": self.raw_response,
        }


class AIProvider(ABC):
    """Common interface every AI provider implementation must satisfy."""

    name: str = "unknown"

    @property
    def available_functions(self) -> List[Dict[str, Any]]:
        """Optional list of tool definitions supported by the provider."""
        return []

    @abstractmethod
    async def generate_response(
        self,
        prompt: str,
        *,
        context: Optional[Dict[str, Any]] = None,
        use_functions: bool = True,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        user_id: Optional[Any] = None,
    ) -> ProviderResponse:
        """Generate a rich response using the provider."""

    async def generate_content(
        self,
        prompt: str,
        *,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Convenience wrapper returning plain text content."""
        response = await self.generate_response(
            prompt,
            context=None,
            use_functions=False,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.text

    async def analyze_sentiment(self, message: str) -> Dict[str, Any]:
        """Optional helper for sentiment analysis; default uses generate_response."""
        response = await self.generate_response(
            prompt=message,
            context=None,
            use_functions=False,
            temperature=0.3,
        )
        return {"text": response.text}
