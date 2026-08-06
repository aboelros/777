"""Gemini AI provider implementation."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.services.ai_providers.base import (
    AIProvider,
    ProviderFunctionCall,
    ProviderResponse,
)
from app.domains.ai.providers.gemini import GeminiClient


class GeminiProvider(AIProvider):
    """Provider wrapper around the legacy GeminiClient implementation."""

    name = "gemini"

    def __init__(self, client: Optional[GeminiClient] = None) -> None:
        self.client = client or GeminiClient()

    @property
    def available_functions(self) -> List[Dict[str, Any]]:  # pragma: no cover - passthrough
        return getattr(self.client, "available_functions", [])

    def set_subscription_service(self, service: Any) -> None:
        if hasattr(self.client, "set_subscription_service"):
            self.client.set_subscription_service(service)

    def set_ai_optimizer(self, optimizer: Any) -> None:
        if hasattr(self.client, "set_ai_optimizer"):
            self.client.set_ai_optimizer(optimizer)

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
        raw = await self.client.generate_response(
            prompt=prompt,
            context=context,
            use_functions=use_functions,
            temperature=temperature,
            max_tokens=max_tokens,
            user_id=user_id,
        )

        function_calls = [
            ProviderFunctionCall(
                name=call.get("name", "unknown"),
                parameters=call.get("parameters", {}) or {},
            )
            for call in raw.get("function_calls", [])
        ]

        return ProviderResponse(
            text=raw.get("text", ""),
            function_calls=function_calls,
            tokens_used=raw.get("tokens_used", 0),
            cost=raw.get("cost", 0.0),
            model=raw.get("model"),
            raw_response=raw,
        )

    async def generate_content(
        self,
        prompt: str,
        *,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        return await self.client.generate_content(
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    async def analyze_sentiment(self, message: str) -> Dict[str, Any]:
        if hasattr(self.client, "analyze_sentiment"):
            return await self.client.analyze_sentiment(message)
        return await super().analyze_sentiment(message)
