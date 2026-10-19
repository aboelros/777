import pytest
import uuid
import asyncio
from datetime import datetime, timedelta, timezone

from app.domains.integrations.models import OAuthState
from app.domains.integrations.oauth_state_service import OAuthStateService
from app.core.database import AsyncSessionLocal
from app.db.models import User, Project


@pytest.mark.asyncio
async def test_oauth_db():
    async with AsyncSessionLocal() as db:
        user = User(
            id=uuid.uuid4(),
            email=f"oauth_test_{uuid.uuid4().hex[:8]}@example.com",
            password_hash="hash",
            is_active=True,
        )
        db.add(user)
        await db.flush()

        project = Project(
            id=uuid.uuid4(),
            name="OAuth Test Project",
            owner_id=user.id,
            project_code=uuid.uuid4().hex[:8],
        )
        db.add(project)
        await db.commit()

        token = await OAuthStateService.create_state(db, project.id, user.id, "facebook")
        assert token is not None

    async with AsyncSessionLocal() as db2:
        consumed = await OAuthStateService.consume_state(db2, token, "facebook")
        assert consumed is not None
        assert consumed.project_id == project.id
        assert consumed.user_id == user.id
