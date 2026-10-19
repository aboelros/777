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

if [ -z "$IMAGE_STORAGE_DATABASE_URL" ]; then
    echo "INFO: IMAGE_STORAGE_DATABASE_URL is not set; defaulting to APP_DATABASE_URL"
    export IMAGE_STORAGE_DATABASE_URL="$APP_DATABASE_URL"
fi

# Migration Governance Gate
# Production policy: Application startup must not automatically apply schema migrations under any circumstances.
# Schema migrations must be applied through authorized release pipelines or operator commands.
ENVIRONMENT_LOWER=$(echo "${ENVIRONMENT:-development}" | tr '[:upper:]' '[:lower:]' | xargs)

if [ "$ENVIRONMENT_LOWER" = "production" ] || [ "$ENVIRONMENT_LOWER" = "prod" ]; then
    if [ "${RUN_MIGRATIONS_ON_STARTUP:-false}" = "true" ]; then
        echo "[MIGRATION GOVERNANCE] WARNING: RUN_MIGRATIONS_ON_STARTUP=true was requested, but automatic startup migrations are strictly PROHIBITED in production."
    fi
    echo "[MIGRATION GOVERNANCE] NOTICE: Automatic migrations on startup are DISABLED in production environment."
    echo "[MIGRATION GOVERNANCE] Schema migrations must be applied via authorized release pipelines or operator command:"
    echo "[MIGRATION GOVERNANCE]   python -m alembic upgrade head"
elif [ "$ENVIRONMENT_LOWER" = "staging" ] || [ "$ENVIRONMENT_LOWER" = "stage" ]; then
    if [ "${RUN_MIGRATIONS_ON_STARTUP:-false}" = "true" ]; then
        echo "[MIGRATION GOVERNANCE] Explicit RUN_MIGRATIONS_ON_STARTUP=true detected for staging. Running migrations..."
        if ! python -m alembic upgrade head; then
            echo "CRITICAL ERROR: Migration failed during startup. Halting to protect database consistency."
            exit 1
        fi
        echo "[MIGRATION GOVERNANCE] Migrations completed successfully."
    else
        echo "[MIGRATION GOVERNANCE] NOTICE: Automatic migrations on startup are DISABLED by default in staging."
        echo "[MIGRATION GOVERNANCE] To enable in staging, set RUN_MIGRATIONS_ON_STARTUP=true, or run manually:"
        echo "[MIGRATION GOVERNANCE]   python -m alembic upgrade head"
    fi
else
    # Non-production (development, test, local)
    if [ "${RUN_MIGRATIONS_ON_STARTUP:-true}" = "false" ]; then
        echo "[MIGRATION GOVERNANCE] Startup migrations explicitly disabled via RUN_MIGRATIONS_ON_STARTUP=false."
    else
        echo "[MIGRATION GOVERNANCE] Running database migrations for $ENVIRONMENT_LOWER environment..."
        if ! python -m alembic upgrade head; then
            echo "CRITICAL ERROR: Migration failed during startup. Halting."
            exit 1
        fi
        echo "[MIGRATION GOVERNANCE] Migrations completed successfully."
    fi
fi

# Admin Account Seeding Gate
if [ "$ENVIRONMENT_LOWER" != "production" ]; then
    echo "Seeding Admin Account for $ENVIRONMENT_LOWER..."
    python scripts/create_arnold_admin.py || true
else
    echo "Skipping default admin seeding in production."
fi

echo "Starting Celery worker in background..."
celery -A app.workers.celery_app worker --loglevel=warning --concurrency=1 &
echo "Celery PID: $!"

echo "Starting FastAPI server on port ${PORT:-8000}..."
exec python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1
