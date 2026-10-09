import asyncio
import uuid
from sqlalchemy import text
from app.core.database import AsyncSessionLocal
from app.domains.integrations.oauth_state_service import OAuthStateService
import app.db.models # Initialize all mappers

async def main():
    async with AsyncSessionLocal() as db:
        res = await db.execute(text("SELECT id FROM projects LIMIT 1"))
        project_id = res.scalar()
        res = await db.execute(text("SELECT owner_id FROM projects WHERE id = :pid"), {"pid": project_id})
        user_id = res.scalar()
        
        state = await OAuthStateService.create_state(db, project_id, user_id, "facebook")
        print("Created:", state)
        
    async with AsyncSessionLocal() as db:
        res1 = await OAuthStateService.consume_state(db, state, "facebook")
        print("First consume:", res1 is not None)
        
    async with AsyncSessionLocal() as db:
        res2 = await OAuthStateService.consume_state(db, state, "facebook")
        print("Second consume:", res2 is not None)

asyncio.run(main())
