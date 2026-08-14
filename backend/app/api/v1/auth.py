from datetime import datetime, timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import structlog

from app.core.database import get_db
from app.core.security import (
    get_current_user_id,
    create_access_token,
    create_refresh_token,
    verify_password,
    decode_token,
)
from app.core.uow import UnitOfWork
from app.domains.auth.service import AuthService
from app.core.rate_limit import limiter
from app.domains.auth.schemas import (
    UserRegister, UserLogin, TokenResponse, RefreshTokenRequest, UserResponse
)
from app.domains.auth.models import User, RefreshToken, UserRole
from app.core.config import settings

router = APIRouter()
logger = structlog.get_logger(__name__)


async def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(UnitOfWork(db))


def _set_auth_cookies(response: Response, access_token: str, refresh_token: str):
    """Set secure httpOnly auth cookies on the response."""
    is_production = settings.ENVIRONMENT == "production"
    # SameSite=None requires Secure=True in all browsers.
    # In development we use SameSite=Lax with Secure=False.
    samesite = "none" if is_production else "lax"
    secure = is_production

    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        secure=secure,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        expires=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite=samesite,
        path="/",
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=secure,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        expires=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        samesite=samesite,
        path="/",
    )


# ---------------------------------------------------------------------------
# Register
# ---------------------------------------------------------------------------

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def register(
    request: Request,
    user_data: UserRegister,
    auth_service: AuthService = Depends(get_auth_service),
) -> Any:
    """Register a new user account."""
    new_user = await auth_service.register_user(user_data)
    return new_user


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------

@router.post("/login", response_model=TokenResponse)
@limiter.limit("10/minute")
async def login(
    request: Request,
    response: Response,
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Authenticate user and return JWT tokens.

    Tokens are delivered both in the JSON body (for API clients) and
    as httpOnly cookies (for browser clients).
    """
    # Sanitize inputs
    clean_email = login_data.email.lower().strip()
    clean_password = login_data.password.strip()

    # Find user
    result = await db.execute(select(User).where(User.email == clean_email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(clean_password, user.password_hash):
        logger.warning("Failed login attempt", email=clean_email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )

    # Update last login
    user.last_login = datetime.utcnow()

    # Build token payload — always use .value so JWT contains the string "admin"/"user"
    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role.value if isinstance(user.role, UserRole) else str(user.role),
    }

    access_token = create_access_token(token_data)
    refresh_token_str = create_refresh_token({"sub": str(user.id)})

    # Store refresh token and revoke all previous tokens for this user
    refresh_token_expires = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    new_db_token = RefreshToken(
        user_id=user.id,
        token=refresh_token_str,
        expires_at=refresh_token_expires,
    )
    from sqlalchemy import delete as sa_delete
    await db.execute(sa_delete(RefreshToken).where(RefreshToken.user_id == user.id))
    db.add(new_db_token)
    await db.commit()

    # Set secure cookies
    _set_auth_cookies(response, access_token, refresh_token_str)

    logger.info("User logged in", user_id=str(user.id))

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token_str,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


# ---------------------------------------------------------------------------
# Refresh
# ---------------------------------------------------------------------------

@router.post("/refresh", response_model=TokenResponse)
@limiter.limit("20/minute")
async def refresh_access_token(
    request: Request,
    response: Response,
    body: RefreshTokenRequest = None,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Refresh access token using a valid refresh token."""
    # Accept token from httpOnly cookie first, then request body
    refresh_token_str = request.cookies.get("refresh_token")
    if not refresh_token_str and body:
        refresh_token_str = body.refresh_token

    if not refresh_token_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token required",
        )

    # Validate token signature and type
    try:
        payload = decode_token(refresh_token_str)
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )

    user_id = payload.get("sub")

    # Validate against DB
    result = await db.execute(
        select(RefreshToken)
        .where(RefreshToken.token == refresh_token_str)
        .where(RefreshToken.user_id == user_id)
    )
    db_token = result.scalar_one_or_none()

    if not db_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found or already used",
        )

    if db_token.expires_at < datetime.utcnow():
        await db.delete(db_token)
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired",
        )

    # Get user
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or disabled",
        )

    # Rotate tokens
    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role.value if isinstance(user.role, UserRole) else str(user.role),
    }
    new_access_token = create_access_token(token_data)
    new_refresh_token_str = create_refresh_token({"sub": str(user.id)})

    # Swap DB tokens
    await db.delete(db_token)
    refresh_token_expires = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    new_db_token = RefreshToken(
        user_id=user.id,
        token=new_refresh_token_str,
        expires_at=refresh_token_expires,
    )
    db.add(new_db_token)
    await db.commit()

    _set_auth_cookies(response, new_access_token, new_refresh_token_str)

    logger.info("Token refreshed", user_id=str(user.id))

    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token_str,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


# ---------------------------------------------------------------------------
# Logout
# ---------------------------------------------------------------------------

@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    response: Response,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
) -> Any:
    """Logout user — revoke refresh token and clear auth cookies."""
    try:
        refresh_token_str = request.cookies.get("refresh_token")
        if not refresh_token_str:
            try:
                body = await request.json()
                refresh_token_str = body.get("refresh_token")
            except Exception:
                pass

        if refresh_token_str:
            result = await db.execute(
                select(RefreshToken).where(RefreshToken.token == refresh_token_str)
            )
            db_token = result.scalar_one_or_none()
            if db_token:
                await db.delete(db_token)
                await db.commit()

        response.delete_cookie(key="access_token", path="/")
        response.delete_cookie(key="refresh_token", path="/")
        logger.info("User logged out", user_id=user_id)
        return {"message": "Logged out successfully"}

    except Exception as e:
        logger.error("Logout error", error=str(e), user_id=user_id)
        response.delete_cookie(key="access_token", path="/")
        response.delete_cookie(key="refresh_token", path="/")
        return {"message": "Logged out successfully"}


# ---------------------------------------------------------------------------
# Me
# ---------------------------------------------------------------------------

@router.get("/me", response_model=UserResponse)
async def get_current_user(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Get the currently authenticated user's profile."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user
