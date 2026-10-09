import secrets
import string
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.integrations.models import OAuthState

class OAuthStateService:
    @staticmethod
    def _generate_token() -> str:
        # Generate 32 bytes of entropy, resulting in a 43-character url-safe base64 string
        return secrets.token_urlsafe(32)

    @staticmethod
    async def create_state(
        db: AsyncSession,
        project_id: UUID,
        user_id: UUID,
        provider: str,
        redirect_uri: Optional[str] = None,
        expire_minutes: int = 15
    ) -> str:
        token = OAuthStateService._generate_token()
        
        state_obj = OAuthState(
            project_id=project_id,
            user_id=user_id,
            provider=provider,
            state_token=token,
            redirect_uri=redirect_uri,
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)
        )
        db.add(state_obj)
        await db.commit()
        return token

    @staticmethod
    async def consume_state(
        db: AsyncSession,
        state_token: str,
        provider: str
    ) -> Optional[OAuthState]:
        stmt = (
            delete(OAuthState)
            .where(OAuthState.state_token == state_token)
            .where(OAuthState.provider == provider)
            .where(OAuthState.expires_at > datetime.now(timezone.utc))
            .returning(OAuthState)
        )
        result = await db.execute(stmt)
        await db.commit()
        return result.scalar_one_or_none()

