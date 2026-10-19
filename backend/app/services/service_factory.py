"""
Service Factory - Initialize and wire services together.
Handles dependency injection between services.
"""

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.services.subscription_service import SubscriptionService
from app.services.ai_optimizer import ai_optimizer
from app.services.ai_providers.base import AIProvider
from app.services.ai_providers.gemini import GeminiProvider
from app.core.config import settings
from app.domains.ai.providers.gemini import GeminiClient

logger = structlog.get_logger(__name__)


class ServiceFactory:
    """Factory for creating and wiring services."""

    _ai_providers: dict[str, AIProvider] = {}

    @classmethod
    def _build_ai_provider(cls, provider_name: str) -> AIProvider:
        provider_name = provider_name.lower()
        if provider_name in cls._ai_providers:
            return cls._ai_providers[provider_name]

        if provider_name in {"gemini", "default"}:
            provider = GeminiProvider()
            provider.set_ai_optimizer(ai_optimizer)
        elif provider_name == "openrouter":
            from app.services.ai_providers.openrouter import OpenRouterProvider
            provider = OpenRouterProvider()
        else:
            raise ValueError(f"Unsupported AI provider: {provider_name}")

        cls._ai_providers[provider_name] = provider
        logger.info("AI provider initialized", provider=provider_name)
        return provider

    @classmethod
    def get_ai_provider(cls, db: AsyncSession | None = None) -> AIProvider:
        provider_name = settings.AI_PROVIDER
        provider = cls._build_ai_provider(provider_name)

        if db is not None and hasattr(provider, "set_subscription_service"):
            subscription_service = SubscriptionService(db)
            provider.set_subscription_service(subscription_service)

        return provider
    
    @classmethod
    def get_gemini_client(cls, db: AsyncSession = None):
        """Temporary backward compatibility helper returning active AI client."""
        provider = cls.get_ai_provider(db)
        if hasattr(provider, "client"):
            return provider.client
        return GeminiClient()

    @classmethod
    def get_subscription_service(cls, db: AsyncSession) -> SubscriptionService:
        """Get subscription service instance."""
        return SubscriptionService(db)
    
    @classmethod
    def get_ai_optimizer(cls):
        """Get AI optimizer singleton."""
        return ai_optimizer

    @classmethod
    def get_whatsapp_business_service(cls):
        """
        Get WhatsApp Business API service (official Meta API).
        Replaces the old gateway client with official WhatsApp Business Cloud API.
        """
        from app.services.integrations.whatsapp_business import WhatsAppBusinessService
        
        try:
            return WhatsAppBusinessService()
        except ValueError as e:
            logger.error(
                "WhatsApp Business API not configured",
                error=str(e),
                hint="Set WHATSAPP_PHONE_NUMBER_ID and WHATSAPP_ACCESS_TOKEN environment variables"
            )
            raise RuntimeError(
                "WhatsApp Business API not configured. "
                "Please set WHATSAPP_PHONE_NUMBER_ID and WHATSAPP_ACCESS_TOKEN."
            ) from e

    @classmethod
    def get_whatsapp_gateway_service(cls, provider: str = "go_whatsapp", base_url: str = None, api_key: str = None):
        """
        Get WhatsApp Gateway service (Go WhatsApp).
        Alternative to WhatsApp Business API using self-hosted gateway.
        """
        from app.core.config import settings
        
        base_url = base_url or settings.WA_GATEWAY_BASE_URL
        api_key = api_key or settings.WA_GATEWAY_API_KEY
        
        if not base_url:
            logger.error(
                "Gateway Base URL not configured",
                hint="Set WA_GATEWAY_BASE_URL environment variable or pass base_url"
            )
            raise RuntimeError(
                "Gateway Base URL not configured. "
                "Please set WA_GATEWAY_BASE_URL environment variable."
            )
            
        if provider == "go_whatsapp":
            from app.services.integrations.go_whatsapp_service import GoWhatsAppService
            return GoWhatsAppService(base_url=base_url, api_key=api_key)
        else:
            raise ValueError(f"Unsupported WhatsApp gateway provider: {provider}. Only 'go_whatsapp' is supported.")


# Convenience functions
def get_ai_provider(db: AsyncSession | None = None) -> AIProvider:
    """Retrieve configured AI provider, wiring optional tracking dependencies."""
    return ServiceFactory.get_ai_provider(db)


def get_gemini_with_tracking(db: AsyncSession) -> GeminiClient:
    """Get Gemini client with usage tracking enabled (legacy helper)."""
    return ServiceFactory.get_gemini_client(db)


def get_gemini_without_tracking() -> GeminiClient:
    """Get Gemini client without usage tracking (legacy helper)."""
    return ServiceFactory.get_gemini_client(None)


def get_whatsapp_business_service():
    """Get WhatsApp Business API service (official Meta API)."""
    return ServiceFactory.get_whatsapp_business_service()


def get_whatsapp_gateway_service(provider: str = "wa_gateway", base_url: str = None, api_key: str = None):
    """Get WA-Gateway service (self-hosted gateway)."""
    return ServiceFactory.get_whatsapp_gateway_service(provider, base_url, api_key)
