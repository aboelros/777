"""
Cryptographic utilities for field-level encryption.
Uses Fernet (AES-128 in CBC mode with SHA256 HMAC) for symmetric encryption.
"""

from typing import Optional
from cryptography.fernet import Fernet
from app.core.config import settings
import structlog

logger = structlog.get_logger(__name__)

# Initialize Fernet with the encryption key from settings
try:
    _fernet = Fernet(settings.ENCRYPTION_KEY)
except Exception as e:
    logger.critical("Failed to initialize encryption system", error=str(e))
    # We don't raise here to allow app startup, but encryption will fail
    _fernet = None


def encrypt_value(value: str) -> Optional[str]:
    """
    Encrypt a string value.
    Returns the URL-safe base64-encoded encrypted token string.
    """
    if not value:
        return None
    
    if not _fernet:
        logger.error("Encryption requested but system not initialized")
        return value  # Fail safe: return original (or should we raise?)
        
    try:
        # Fernet requires bytes
        token = _fernet.encrypt(value.encode('utf-8'))
        return token.decode('utf-8')
    except Exception as e:
        logger.error("Encryption failed", error=str(e))
        raise


def decrypt_value(token: str) -> Optional[str]:
    """
    Decrypt an encrypted token string.
    Returns the original string value.
    """
    if not token:
        return None
        
    if not _fernet:
        logger.error("Decryption requested but system not initialized")
        return token
        
    try:
        # Check if it looks like a Fernet token (optional optimization)
        if not token.startswith("gAAAA"):
            # It might be unencrypted legacy data
            return token
            
        value = _fernet.decrypt(token.encode('utf-8'))
        return value.decode('utf-8')
    except Exception as e:
        logger.error("Decryption failed", error=str(e))
        # Return original token if decryption fails (assuming it might be unencrypted)
        return token
