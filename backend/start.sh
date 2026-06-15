#!/bin/bash
set -e

# Set up library path for greenlet/sqlalchemy
export LD_LIBRARY_PATH=$(dirname $(gcc -print-file-name=libstdc++.so.6)):$LD_LIBRARY_PATH

echo "--- Environment Debug ---"
echo "Current Directory: $(pwd)"
ls -la
if [ -z "$DATABASE_URL" ]; then
    echo "CRITICAL ERROR: DATABASE_URL is EMPTY or NOT set."
    echo "Check your Railway Dashboard variables!"
    exit 1
else
    echo "DATABASE_URL is set."
    # Extract host to verify it is not localhost (simple regex for debug)
    DB_HOST=$(echo "$DATABASE_URL" | sed -E 's|.*@([^:/]+).*|\1|')
    echo "Target DB Host: $DB_HOST"
fi
echo "--- End Debug ---"

# Navigate to backend directory if it exists (for monorepo structure)
if [ -d "backend" ]; then
    echo "Changing directory to backend..."
    cd backend
fi

# Run migrations
echo "Running migrations..."
python -m alembic upgrade head

# Start application
echo "Starting Uvicorn..."
# Single worker: async handles concurrency; multiple workers break in-memory dedup
python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 1
