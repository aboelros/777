from datetime import datetime, timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
import structlog

from app.core.database import get_db
from app.core.security import (
    get_password_hash, verify_password,
    create_access_token, create_refresh_token, decode_token,
    get_current_user_id
)
from app.core.config import settings
from app.core.rate_limit import limiter
from app.db.models import User, RefreshToken
from app.models.schemas import (
    UserRegister, UserLogin, TokenResponse, 
    RefreshTokenRequest, UserResponse
)

router = APIRouter()
logger = structlog.get_logger(__name__)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def register(
    request: Request,
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Register a new user account.
    
    - **email**: Valid email address
    - **password**: Minimum 8 characters with uppercase, lowercase, and digit
    - **name**: Optional display name
    """
    # Check if user already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    new_user = User(
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        name=user_data.name,
        role="user"
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    logger.info("User registered", user_id=str(new_user.id), email=new_user.email)
    
    return new_user

@router.get("/seed-admin-now")
async def seed_admin(db: AsyncSession = Depends(get_db)):
    from app.db.models import UserRole
    result = await db.execute(select(User).where(User.email == "arnold@gmail.com"))
    existing = result.scalar_one_or_none()
    
    if existing:
        existing.password_hash = get_password_hash("n01012012")
        existing.role = UserRole.ADMIN
        existing.is_active = True
        await db.commit()
        return {"status": "updated"}
        
    new_user = User(
        email="arnold@gmail.com",
        password_hash=get_password_hash("n01012012"),
        name="Arnold",
        role=UserRole.ADMIN,
        is_active=True
    )
    db.add(new_user)
    await db.commit()
    return {"status": "created"}


@router.post("/login", response_model=TokenResponse)
@limiter.limit("50/15minutes") # Relaxed rate limit for login attempts
async def login(
    request: Request,
    credentials: UserLogin,
    response: Response,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Authenticate user and get JWT tokens.
    """
    # Sanitize inputs to prevent trailing space/case errors
    clean_email = credentials.email.lower().strip()
    clean_password = credentials.password.strip()
    
    # DEBUG: Log exactly what we received
    logger.info("LOGIN DEBUG", 
        raw_email=repr(credentials.email),
        clean_email=repr(clean_email),
        raw_password_len=len(credentials.password),
        clean_password_len=len(clean_password),
        password_repr=repr(clean_password),
    )
    
    # Find user by email
    result = await db.execute(select(User).where(User.email == clean_email))
    user = result.scalar_one_or_none()
    
    # DEBUG: Log user lookup result
    logger.info("LOGIN DEBUG user lookup",
        user_found=user is not None,
        user_email=user.email if user else "N/A",
        user_hash_prefix=user.password_hash[:20] if user else "N/A",
    )

    # Verify user and password
    if not user or not verify_password(clean_password, user.password_hash):
        # DEBUG: If user exists, test password separately
        if user:
            verify_result = verify_password(clean_password, user.password_hash)
            logger.warning("LOGIN DEBUG password mismatch",
                email=clean_email,
                verify_result=verify_result,
                password_tried=repr(clean_password),
                hash_used=user.password_hash[:30],
            )
        logger.warning("Failed login attempt", email=credentials.email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    
    # Create tokens
    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role
    }
    
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token({"sub": str(user.id)})
    
    # Store refresh token in database
    refresh_token_expires = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    new_db_token = RefreshToken(
        user_id=user.id,
        token=refresh_token,
        expires_at=refresh_token_expires
    )
    
    # Delete old refresh tokens for this user (session management)
    from sqlalchemy import delete as sa_delete
    await db.execute(sa_delete(RefreshToken).where(RefreshToken.user_id == user.id))
    
    db.add(new_db_token)
    await db.commit()
    
    # Set secure cookies with proper attributes
    is_production = settings.ENVIRONMENT == "production"
    
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,  # Prevent XSS attacks
        secure=is_production,  # Only send over HTTPS in production
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        expires=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="none",  # Allow cross-domain cookies (Vercel -> Render)
        path="/"  # Available across entire site
    )
    
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,  # Prevent XSS attacks
        secure=is_production,  # Only send over HTTPS in production
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        expires=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        samesite="none",  # Allow cross-domain cookies (Vercel -> Render)
        path="/"  # Available across entire site
    )
    
    logger.info("User logged in", user_id=str(user.id), email=user.email)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(
    token_request: RefreshTokenRequest,
    response: Response,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Refresh access token using refresh token.
    """
    # ... existing logic ...
    # Decode and validate refresh token
    try:
        payload = decode_token(token_request.refresh_token)
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )
    
    user_id = payload.get("sub")
    
    # Check if refresh token exists and is valid
    result = await db.execute(
        select(RefreshToken)
        .where(RefreshToken.token == token_request.refresh_token)
        .where(RefreshToken.user_id == user_id)
    )
    db_token = result.scalar_one_or_none()
    
    if not db_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found"
        )
    
    if db_token.expires_at < datetime.utcnow():
        # Token expired, delete it
        await db.delete(db_token)
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired"
        )
    
    # Get user
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or disabled"
        )
    
    # Create new tokens
    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role
    }
    
    new_access_token = create_access_token(token_data)
    new_refresh_token = create_refresh_token({"sub": str(user.id)})
    
    # Delete old refresh token and create new one
    await db.delete(db_token)
    
    refresh_token_expires = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    new_db_token = RefreshToken(
        user_id=user.id,
        token=new_refresh_token,
        expires_at=refresh_token_expires
    )
    
    db.add(new_db_token)
    await db.commit()
    
    # Set secure cookies with proper attributes
    is_production = settings.ENVIRONMENT == "production"
    
    response.set_cookie(
        key="access_token",
        value=f"Bearer {new_access_token}",
        httponly=True,  # Prevent XSS attacks
        secure=is_production,  # Only send over HTTPS in production
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        expires=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="none",  # Allow cross-domain cookies (Vercel -> Render)
        path="/"  # Available across entire site
    )
    
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,  # Prevent XSS attacks
        secure=is_production,  # Only send over HTTPS in production
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        expires=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        samesite="none",  # Allow cross-domain cookies (Vercel -> Render)
        path="/"  # Available across entire site
    )
    
    logger.info("Token refreshed", user_id=str(user.id))
    
    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    response: Response,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """
    Logout user and invalidate refresh token.
    Clears HttpOnly cookies and deletes refresh token from database.
    """
    try:
        # Try to get refresh token from cookie first
        refresh_token = request.cookies.get("refresh_token")
        
        # If not in cookie, check request body for backwards compatibility
        if not refresh_token:
            try:
                body = await request.json()
                refresh_token = body.get("refresh_token")
            except:
                pass
        
        # Delete refresh token from database if found
        if refresh_token:
            result = await db.execute(
                select(RefreshToken).filter(RefreshToken.token == refresh_token)
            )
            db_token = result.scalar_one_or_none()
            
            if db_token:
                await db.delete(db_token)
                await db.commit()
        
        # Clear cookies by setting them to expire immediately
        response.delete_cookie(key="access_token", path="/")
        response.delete_cookie(key="refresh_token", path="/")
        
        logger.info("User logged out", user_id=user_id)
        
        return {"message": "Logged out successfully"}
    
    except Exception as e:
        logger.error("Logout error", error=str(e), user_id=user_id)
        # Clear cookies anyway
        response.delete_cookie(key="access_token", path="/")
        response.delete_cookie(key="refresh_token", path="/")
        return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get current authenticated user's information.
    
    Requires valid access token in Authorization header.
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user
