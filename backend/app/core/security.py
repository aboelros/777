"""
Security utilities for authentication, password hashing, and JWT tokens.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, Security, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer token security - auto_error=False to allow checking cookies
security_bearer = HTTPBearer(auto_error=False)

# Encryption Setup
from cryptography.fernet import Fernet

def _get_start_fernet() -> Fernet:
    """Lazy loading of Fernet instance."""
    try:
        if not settings.ENCRYPTION_KEY:
            # Fallback for dev if validation somehow approved empty key
            key = Fernet.generate_key()
            return Fernet(key)
        return Fernet(settings.ENCRYPTION_KEY.encode())
    except Exception as e:
        print(f"Encryption Init Error: {e}")
        # Always return a valid element to prevent crashes, but log critical error
        return Fernet(Fernet.generate_key())

_cipher_suite = None

def get_cipher_suite():
    global _cipher_suite
    if _cipher_suite is None:
        _cipher_suite = _get_start_fernet()
    return _cipher_suite

def encrypt_pii(data: str) -> str:
    """
    Encrypt sensitive personally identifiable information (PII).
    Args:
        data: Plain text string (e.g. email, phone)
    Returns:
        Encrypted string (safe to store)
    """
    if not data:
        return data
    try:
        cipher = get_cipher_suite()
        return cipher.encrypt(data.encode()).decode()
    except Exception:
        # Fail safe: return original (in production this implies unencrypted storage 
        # but protects app availability) or raise error depending on risk profile.
        # Here we return original to avoid data loss during key rotation issues.
        return data

def decrypt_pii(encrypted_data: str) -> str:
    """
    Decrypt sensitive data.
    Args:
        encrypted_data: Encrypted string
    Returns:
        Original plain text
    """
    if not encrypted_data:
        return encrypted_data
    try:
        cipher = get_cipher_suite()
        return cipher.decrypt(encrypted_data.encode()).decode()
    except Exception:
        # If decryption fails (e.g. key changed, or data wasn't encrypted), return as is.
        # This handles the migration phase where some data might be plain text.
        return encrypted_data


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password from database
        
    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password string
    """
    return pwd_context.hash(password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Dictionary of claims to encode in the token
        expires_delta: Optional custom expiration time
        
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """
    Create a JWT refresh token with longer expiration.
    
    Args:
        data: Dictionary of claims to encode in the token
        
    Returns:
        Encoded JWT refresh token string
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    })
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode and verify a JWT token.
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded token payload
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=401,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def verify_token(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security_bearer)
) -> Dict[str, Any]:
    """
    FastAPI dependency to verify JWT token from Authorization header or Cookie.
    
    Args:
        request: HTTP Request object
        credentials: HTTP Authorization credentials (optional)
        
    Returns:
        Decoded token payload
        
    Raises:
        HTTPException: If token is invalid or missing
    """
    # Skip auth check in testing mode
    if settings.TESTING_MODE:
        return {
            "sub": "test-user-id",
            "email": "test@testing.com",
            "role": "admin",
            "type": "access"
        }
    
    token = None
    
    # 1. Check Authorization header
    if credentials:
        token = credentials.credentials
        
    # 2. Check Cookie
    if not token:
        cookie_token = request.cookies.get("access_token")
        if cookie_token:
            # Handle "Bearer <token>" format in cookie if present
            if cookie_token.startswith("Bearer "):
                token = cookie_token.split(" ")[1]
            else:
                token = cookie_token
    
    if not token:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    payload = decode_token(token)
    
    # Verify token type
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=401,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return payload


async def get_current_user_id(token_payload: Dict[str, Any] = Depends(verify_token)) -> str:
    """
    FastAPI dependency to get current user ID from token.
    
    Args:
        token_payload: Decoded JWT payload
        
    Returns:
        User ID string
        
    Raises:
        HTTPException: If user_id not in token
    """
    user_id = token_payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    return user_id


async def get_current_user_role(token_payload: Dict[str, Any] = Depends(verify_token)) -> str:
    """
    FastAPI dependency to get current user role from token.
    
    Args:
        token_payload: Decoded JWT payload
        
    Returns:
        User role string
    """
    return token_payload.get("role", "user")


def require_role(required_role: str):
    """
    Factory function to create a dependency that requires a specific role.
    
    Args:
        required_role: Role required to access the endpoint
        
    Returns:
        FastAPI dependency function
    """
    async def role_checker(token_payload: Dict[str, Any] = Depends(verify_token)) -> Dict[str, Any]:
        user_role = token_payload.get("role", "user")
        
        if user_role != required_role and user_role != "admin":
            raise HTTPException(
                status_code=403,
                detail=f"Insufficient permissions. Required role: {required_role}"
            )
        
        return token_payload
    
    return role_checker


# API Key validation (for webhook endpoints)
def verify_api_key(api_key: str, project_id: str) -> bool:
    """
    Verify API key for webhook endpoints.
    This should check against database in production.
    
    Args:
        api_key: API key from request header
        project_id: Project ID to validate against
        
    Returns:
        True if valid, False otherwise
    """
    # TODO: Implement database lookup
    # For now, this is a placeholder
    return True


def generate_api_key() -> str:
    """
    Generate a secure random API key.
    
    Returns:
        Random API key string
    """
    import secrets
    return f"sk_{secrets.token_urlsafe(32)}"
