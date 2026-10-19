"""
Application configuration using Pydantic Settings.
Loads environment variables and provides type-safe configuration access.
"""

from functools import lru_cache
import json
from typing import List, Optional

from pydantic import Field, field_validator, validator
from pydantic_settings import (
    BaseSettings,
    DotEnvSettingsSource,
    EnvSettingsSource,
    SettingsConfigDict,
)


def _parse_cors_env_value(value):
    """Return a list of origins from an env value, handling JSON, CSV, and blanks."""
    if value is None:
        return None

    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return []

        if stripped == "*":
            return ["*"]

        try:
            loaded = json.loads(stripped)
            if isinstance(loaded, list):
                return [str(origin).strip() for origin in loaded if str(origin).strip()]
        except json.JSONDecodeError:
            pass

        return [origin.strip() for origin in stripped.split(",") if origin.strip()]

    if isinstance(value, (list, tuple, set)):
        return [str(origin).strip() for origin in value if str(origin).strip()]

    return None


class LenientEnvSettingsSource(EnvSettingsSource):
    def decode_complex_value(self, field_name, field, value):
        if field_name in ("CORS_ORIGINS", "ALLOWED_TEST_DATABASES", "ALLOWED_TEST_DATABASE_URLS", "ALLOWED_TEST_IMAGE_STORAGE_DATABASE_URLS"):
            parsed = _parse_cors_env_value(value)
            if parsed is not None:
                return parsed
        return super().decode_complex_value(field_name, field, value)


class LenientDotEnvSettingsSource(DotEnvSettingsSource):
    def decode_complex_value(self, field_name, field, value):
        if field_name in ("CORS_ORIGINS", "ALLOWED_TEST_DATABASES", "ALLOWED_TEST_DATABASE_URLS", "ALLOWED_TEST_IMAGE_STORAGE_DATABASE_URLS"):
            parsed = _parse_cors_env_value(value)
            if parsed is not None:
                return parsed
        return super().decode_complex_value(field_name, field, value)


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls,
        init_settings,
        env_settings,
        dotenv_settings,
        file_secret_settings,
    ):
        return (
            init_settings,
            LenientEnvSettingsSource(settings_cls),
            LenientDotEnvSettingsSource(settings_cls),
            file_secret_settings,
        )
    
    # Application
    APP_NAME: str = "AI Sales Commander"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_VERSION: str = "v1"
    TESTING_MODE: bool = False  # Disable for production security
    
    # Test Isolation Guard
    TESTING: bool = False
    TEST_DATABASE_URL: Optional[str] = None
    REQUIRE_TEST_DB_EXPLICIT_AUTHORIZATION: bool = False
    APPROVED_TEST_DATABASE_URL: Optional[str] = None
    ALLOWED_TEST_DATABASE_URLS: List[str] = Field(default_factory=list)
    ALLOWED_TEST_DATABASES: List[str] = Field(default_factory=list)

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Redis
    REDIS_URL: Optional[str] = None
    API_BASE_URL: str = Field(default="")
    
    # Security
    SECRET_KEY: str = Field(default="", min_length=0)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30  # Extended from 7 to 30 days for long-lived sessions
    
    @validator("SECRET_KEY", pre=True, always=True)
    def generate_secret_key_if_missing(cls, v, values):
        """Auto-generate SECRET_KEY if not provided (for development/testing)."""
        is_prod = (values.get("ENVIRONMENT") or "").lower() == "production"
        if not v or len(v) < 32:
            if is_prod:
                raise ValueError("SECRET_KEY must be at least 32 characters in production!")
            import secrets
            import structlog
            logger = structlog.get_logger(__name__)
            
            # Generate a secure random key
            generated_key = secrets.token_urlsafe(32)
            
            logger.warning(
                "SECRET_KEY not set or too short - auto-generated one",
                key_length=len(generated_key),
                note="Set SECRET_KEY in environment variables for production!"
            )
            
            return generated_key
        return v
    
    # Data Encryption
    ENCRYPTION_KEY: str = Field(default="", min_length=0)
    
    @validator("ENCRYPTION_KEY", pre=True, always=True)
    def generate_encryption_key_if_missing(cls, v, values):
        """Auto-generate ENCRYPTION_KEY if not provided (for development/testing)."""
        is_prod = (values.get("ENVIRONMENT") or "").lower() == "production"
        if not v or len(v) < 32:
            if is_prod:
                raise ValueError("ENCRYPTION_KEY is REQUIRED in production! Generate with Fernet.generate_key()")
            
            from cryptography.fernet import Fernet
            import structlog
            logger = structlog.get_logger(__name__)
            
            # Generate a valid Fernet key
            generated_key = Fernet.generate_key().decode()
            
            logger.warning(
                "ENCRYPTION_KEY not set - auto-generated one",
                note="Data encrypted with this key will be lost on restart if not set in .env! Set ENCRYPTION_KEY in environment to persist."
            )
            return generated_key
        return v

    # Database - Single Database (simplified)
    DATABASE_URL: str = Field(default="")
    
    # Dedicated Image Storage Database
    IMAGE_STORAGE_DATABASE_URL: Optional[str] = Field(default=None)
    TEST_IMAGE_STORAGE_DATABASE_URL: Optional[str] = Field(default=None)
    APPROVED_TEST_IMAGE_STORAGE_DATABASE_URL: Optional[str] = Field(default=None)
    ALLOWED_TEST_IMAGE_STORAGE_DATABASE_URLS: List[str] = Field(default_factory=list)

    @validator("IMAGE_STORAGE_DATABASE_URL", "TEST_IMAGE_STORAGE_DATABASE_URL", "APPROVED_TEST_IMAGE_STORAGE_DATABASE_URL", pre=True)
    def convert_image_storage_url(cls, v):
        """Convert postgres:// to postgresql+asyncpg:// for the image database."""
        if not v:
            return v
        
        # Handle Railway/Render/Supabase postgres:// URLs
        if v.startswith("postgres://"):
            v = v.replace("postgres://", "postgresql+asyncpg://", 1)
        elif v.startswith("postgresql://") and "postgresql+asyncpg://" not in v:
            v = v.replace("postgresql://", "postgresql+asyncpg://", 1)
            
        return v
    
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 0
    DB_ECHO: bool = False
    
    @validator("DATABASE_URL", pre=True)
    def convert_database_url(cls, v, values):
        """Convert postgres:// to postgresql+asyncpg:// and handle empty values."""
        if not v:
            import os
            from dotenv import load_dotenv
            load_dotenv()
            # Support both standard and alias names from .env
            v = os.getenv("DATABASE_URL") or os.getenv("APP_DATABASE_URL")
            
        if not v:
            is_prod = (values.get("ENVIRONMENT") or "").lower() == "production"
            if is_prod:
                raise ValueError("DATABASE_URL is REQUIRED in production!")
            return "postgresql+asyncpg://aisales:changeme@localhost:5432/aisales"
        
        # Handle Railway/Render postgres:// URLs
        if v.startswith("postgres://"):
            v = v.replace("postgres://", "postgresql+asyncpg://", 1)
        # Handle standard postgresql:// URLs
        elif v.startswith("postgresql://") and "postgresql+asyncpg://" not in v:
            v = v.replace("postgresql://", "postgresql+asyncpg://", 1)
        # Handle malformed URLs with double protocol
        elif "postgresql+asyncpg:postgresql://" in v:
            v = v.replace("postgresql+asyncpg:postgresql://", "postgresql+asyncpg://", 1)
        
        return v

    @validator("TEST_DATABASE_URL", "APPROVED_TEST_DATABASE_URL", pre=True)
    def convert_test_database_url(cls, v):
        """Convert postgres:// to postgresql+asyncpg:// for the test database."""
        if not v:
            return None
        v = str(v).strip()
        if not v:
            return None
        if v.startswith("postgres://"):
            v = v.replace("postgres://", "postgresql+asyncpg://", 1)
        elif v.startswith("postgresql://") and "postgresql+asyncpg://" not in v:
            v = v.replace("postgresql+asyncpg://", "postgresql+asyncpg://", 1)
        elif "postgresql+asyncpg:postgresql://" in v:
            v = v.replace("postgresql+asyncpg:postgresql://", "postgresql+asyncpg://", 1)
        return v

    @field_validator("ALLOWED_TEST_DATABASES", "ALLOWED_TEST_DATABASE_URLS", "ALLOWED_TEST_IMAGE_STORAGE_DATABASE_URLS", mode="before")
    def parse_allowed_test_lists(cls, v) -> List[str]:
        """Parse comma-separated or JSON list of allowed test database targets."""
        parsed = _parse_cors_env_value(v)
        return parsed if parsed is not None else []
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_PASSWORD: Optional[str] = None
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    
    # Google Gemini AI - Multiple API Keys for load balancing (up to 100 keys!)
    GEMINI_API_KEY: Optional[str] = None
    
    @validator("GEMINI_API_KEY", pre=True, always=True)
    def debug_gemini_key(cls, v):
        import os
        if not v:
            v = os.getenv("GEMINI_API_KEY")
        if v:
            print(f"DEBUG: GEMINI_API_KEY loaded (len={len(v)})")
        else:
            print("DEBUG: GEMINI_API_KEY is missing/empty")
        return v
    # Additional API Keys 1-100: dynamically collected at startup
    # Set GEMINI_API_KEY_1 through GEMINI_API_KEY_100 in environment variables.
    # Use get_all_gemini_keys() property to access all keys.
    GEMINI_MODEL: str = "gemini-3.6-flash"
    GEMINI_MAX_TOKENS: int = 8192
    GEMINI_TEMPERATURE: float = 0.7
    AI_PROVIDER: str = "gemini"
    
    # Groq AI (Fast Inference & Vision)
    GROQ_API_KEY: Optional[str] = None
    
    # OpenRouter AI
    OPENROUTER_API_KEY: Optional[str] = None
    OPENROUTER_MODEL: str = "google/gemini-2.0-flash-001"
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    
    # Google Cloud / Vertex AI (Optional - if not using direct API key)
    GOOGLE_CLOUD_PROJECT: Optional[str] = None
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None
    VERTEX_AI_LOCATION: str = "us-central1"
    
    # Integrations
    SHOPIFY_API_KEY: Optional[str] = None
    SHOPIFY_API_SECRET: Optional[str] = None
    
    # WhatsApp Business API (Official Meta API)
    WHATSAPP_PHONE_NUMBER_ID: Optional[str] = None
    WHATSAPP_BUSINESS_ACCOUNT_ID: Optional[str] = None
    WHATSAPP_ACCESS_TOKEN: Optional[str] = None
    WHATSAPP_VERIFY_TOKEN: Optional[str] = None
    META_VERIFY_TOKEN: Optional[str] = None
    
    # WA-Gateway Configuration (alternative self-hosted gateway)
    WA_GATEWAY_BASE_URL: Optional[str] = None  # e.g., http://localhost:5001
    WA_GATEWAY_API_KEY: Optional[str] = None

    @validator("WA_GATEWAY_API_KEY", pre=True, always=True)
    def fallback_wa_gateway_api_key(cls, v):
        if v:
            return v
        # Fallback to other variable names the user might have set
        import os
        return os.getenv("WHATSAPP_GATEWAY_API_KEY") or os.getenv("WAHA_API_KEY")

    WA_GATEWAY_WEBHOOK_PATH: str = "/api/v1/webhooks/wa-gateway"
    
    # Legacy WhatsApp (deprecated - will be removed)
    WHATSAPP_BUSINESS_ID: Optional[str] = None
    WHATSAPP_GATEWAY_URL: Optional[str] = None
    WHATSAPP_GATEWAY_API_KEY: Optional[str] = None
    WHATSAPP_GATEWAY_CALLBACK_SECRET: Optional[str] = None
    WHATSAPP_LINKED_DEVICE_AUTOMATION_ENABLED: bool = False

    WHATSAPP_LINKED_DEVICE_PROVIDER: str = "baileys"
    WHATSAPP_BAILEYS_URL: Optional[str] = None
    WHATSAPP_BAILEYS_API_KEY: Optional[str] = None
    WHATSAPP_OPENWA_URL: Optional[str] = None
    WHATSAPP_OPENWA_API_KEY: Optional[str] = None
    
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    
    # TikTok
    TIKTOK_APP_KEY: Optional[str] = None
    TIKTOK_APP_SECRET: Optional[str] = None
    
    # Discord
    DISCORD_PUBLIC_KEY: Optional[str] = None
    
    FACEBOOK_APP_ID: Optional[str] = None
    FACEBOOK_APP_SECRET: Optional[str] = None
    FACEBOOK_PAGE_ACCESS_TOKEN: Optional[str] = None
    FACEBOOK_PAGE_ID: Optional[str] = None
    
    # Meta Aliases (matching documentation)
    META_APP_ID: Optional[str] = None
    META_APP_SECRET: Optional[str] = None
    
    @validator("FACEBOOK_APP_ID", pre=True, always=True)
    def fallback_meta_app_id(cls, v, values):
        if v:
            return v
        # Fallback to META_APP_ID if FACEBOOK_APP_ID is missing
        # Note: values contains previously validated fields, but since we are in pre=True, 
        # we might need to check the raw environment or values if they are processed in order.
        # Pydantic v2 validation is different, but for v1/settings:
        import os
        return os.getenv("META_APP_ID")

    @validator("FACEBOOK_APP_SECRET", pre=True, always=True)
    def fallback_meta_app_secret(cls, v, values):
        if v:
            return v
        import os
        return os.getenv("META_APP_SECRET")
    
    # Twilio
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_PHONE_NUMBER: Optional[str] = None
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "https://777-self.vercel.app",
        "https://aisalescommander.com",
        "http://localhost:3000",
        "http://localhost:5173"
    ]
    
    @field_validator("CORS_ORIGINS", mode="before")
    def parse_cors_origins(cls, v) -> List[str]:
        """Parse comma-separated CORS origins or allow wildcard."""
        # Handle None or empty
        if not v:
            return [
                "https://777-self.vercel.app",
                "http://localhost:3000",
                "http://localhost:5173"
            ]
        
        if isinstance(v, str):
            v = v.strip()
            if not v:
                return ["https://777-self.vercel.app", "http://localhost:3000"]
            
            if v == "*":
                return ["*"]
            
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        
        return v if isinstance(v, list) else ["https://777-self.vercel.app"]
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 10  # Stricter default for sensitive routes
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    
    # Storage
    S3_BUCKET_NAME: Optional[str] = None
    S3_REGION: str = "us-east-1"
    S3_ACCESS_KEY: Optional[str] = None
    S3_SECRET_KEY: Optional[str] = None
    S3_ENDPOINT_URL: Optional[str] = None  # Required for Cloudflare R2
    S3_PUBLIC_DOMAIN: Optional[str] = None  # Public URL for accessing files
    
    # Email
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    FROM_EMAIL: str = "noreply@aisalescommander.com"
    
    # Billing
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT.lower() == "development"
    
    @property
    def database_url_sync(self) -> str:
        """Get synchronous database URL (for Alembic migrations)."""
        return self.DATABASE_URL.replace("+asyncpg", "")

    @property
    def all_gemini_keys(self) -> List[str]:
        """Collect all configured Gemini API keys (primary + numbered 1-100)."""
        import os
        keys = []
        if self.GEMINI_API_KEY:
            keys.append(self.GEMINI_API_KEY)
        for i in range(1, 101):
            key = os.getenv(f"GEMINI_API_KEY_{i}")
            if key and key not in keys:
                keys.append(key)
        return keys


@lru_cache()
def get_settings() -> Settings:
    """
    Create and cache settings instance.
    Use this function to get settings throughout the application.
    """
    return Settings()


# Global settings instance
settings = get_settings()
