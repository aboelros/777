from datetime import datetime, timedelta
from typing import Optional, Tuple
from uuid import UUID
from fastapi import HTTPException, status
import structlog

from app.core.uow import UnitOfWork
from app.domains.auth.repository import UserRepository, RefreshTokenRepository
from app.domains.auth.models import User, RefreshToken, UserRole
from app.domains.auth.schemas import UserRegister, UserLogin
from app.core.security import get_password_hash, verify_password, create_access_token, create_refresh_token, decode_token
from app.core.config import settings

logger = structlog.get_logger(__name__)

class AuthService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
        
    async def register_user(self, user_data: UserRegister) -> User:
        async with self.uow as uow:
            user_repo = UserRepository(uow.session)
            
            existing_user = await user_repo.get_by_email(user_data.email)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            
            new_user = User(
                email=user_data.email,
                password_hash=get_password_hash(user_data.password),
                name=user_data.name,
                role=UserRole.USER,
                is_active=True
            )
            
            user_repo.add(new_user)
            await uow.commit()
            
            logger.info("User registered successfully", user_id=str(new_user.id), email=new_user.email)
            return new_user

    async def authenticate_user(self, login_data: UserLogin) -> Tuple[User, str, str]:
        async with self.uow as uow:
            user_repo = UserRepository(uow.session)
            token_repo = RefreshTokenRepository(uow.session)
            
            user = await user_repo.get_by_email(login_data.email)
            if not user or not verify_password(login_data.password, user.password_hash):
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
                
            access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": str(user.id), "role": user.role.value}, 
                expires_delta=access_token_expires
            )
            
            refresh_token = create_refresh_token()
            expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
            
            db_token = RefreshToken(
                token=refresh_token,
                user_id=user.id,
                expires_at=expires_at
            )
            token_repo.add(db_token)
            
            # Update last login
            user.last_login = datetime.utcnow()
            await uow.commit()
            
            return user, access_token, refresh_token

    async def refresh_tokens(self, refresh_token: str) -> Tuple[str, str]:
        async with self.uow as uow:
            token_repo = RefreshTokenRepository(uow.session)
            user_repo = UserRepository(uow.session)
            
            db_token = await token_repo.get_by_token(refresh_token)
            
            if not db_token or db_token.is_revoked or db_token.expires_at < datetime.utcnow():
                if db_token:
                    await token_repo.delete_by_token(refresh_token)
                    await uow.commit()
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired refresh token",
                    headers={"WWW-Authenticate": "Bearer"},
                )
                
            user = await user_repo.get(db_token.user_id)
            if not user or not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found or inactive",
                )
                
            # Rotate refresh token
            await token_repo.delete_by_token(refresh_token)
            
            new_access_token = create_access_token(
                data={"sub": str(user.id), "role": user.role.value},
                expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            )
            
            new_refresh_token = create_refresh_token()
            expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
            
            new_db_token = RefreshToken(
                token=new_refresh_token,
                user_id=user.id,
                expires_at=expires_at
            )
            token_repo.add(new_db_token)
            await uow.commit()
            
            return new_access_token, new_refresh_token

    async def logout_user(self, refresh_token: str) -> None:
        async with self.uow as uow:
            token_repo = RefreshTokenRepository(uow.session)
            await token_repo.delete_by_token(refresh_token)
            await uow.commit()

    async def get_user_profile(self, user_id: str) -> User:
        async with self.uow as uow:
            user_repo = UserRepository(uow.session)
            user = await user_repo.get(UUID(user_id))
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            return user
