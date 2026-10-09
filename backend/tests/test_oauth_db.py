import pytest
import uuid
import asyncio
from datetime import datetime, timedelta, timezone

from app.domains.integrations.models import OAuthState
from app.domains.integrations.oauth_state_service import OAuthStateService
from app.core.database import AsyncSessionLocal

@pytest.mark.asyncio
async def test_oauth_db():
    async with AsyncSessionLocal() as db:
        project_id = uuid.uuid4()
        user_id = uuid.uuid4()
        token = await OAuthStateService.create_state(db, project_id, user_id, "facebook")
        print("CREATED TOKEN", token)
        
    async with AsyncSessionLocal() as db2:
        consumed = await OAuthStateService.consume_state(db2, token, "facebook")
        print("CONSUMED", consumed)
