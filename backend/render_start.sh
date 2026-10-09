#!/bin/bash
set -e

echo "=== Render Startup ==="
echo "PORT: ${PORT:-8000}"

# Validate required env vars
if [ -z "$AUTH_DATABASE_URL" ]; then
    echo "ERROR: AUTH_DATABASE_URL is not set!"
    exit 1
fi

if [ -z "$APP_DATABASE_URL" ]; then
    echo "ERROR: APP_DATABASE_URL is not set!"
    exit 1
fi

echo "Running database migrations..."
if ! python -m alembic upgrade head; then
    echo "WARNING: Migration failed. Attempting to fix by stamping current head..."
    python -m alembic stamp head || true
    echo "Retrying migration..."
    python -m alembic upgrade head || echo "WARNING: Migrations still failed. Continuing startup anyway..."
fi
echo "Migrations step complete."

echo "Seeding Admin Account..."
python scripts/create_arnold_admin.py || true

echo "Starting Celery worker in background..."
celery -A app.workers.celery_app worker --loglevel=warning --concurrency=1 &
echo "Celery PID: $!"

echo "Starting FastAPI server on port ${PORT:-8000}..."
exec python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1
