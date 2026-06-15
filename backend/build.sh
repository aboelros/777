#!/usr/bin/env bash
# Render build script for backend

set -o errexit

echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Running database migrations..."
# Wait for database to be ready
python << END
import time
import asyncpg
import os

async def wait_for_db():
    max_retries = 30
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            conn = await asyncpg.connect(os.environ['DATABASE_URL'])
            await conn.close()
            print("Database is ready!")
            return
        except Exception as e:
            retry_count += 1
            print(f"Waiting for database... ({retry_count}/{max_retries})")
            time.sleep(2)
    
    raise Exception("Database not ready after 60 seconds")

import asyncio
asyncio.run(wait_for_db())
END

# Run migrations
alembic upgrade head

echo "Build complete!"
