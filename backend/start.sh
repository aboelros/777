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

# Start application
echo "Starting Uvicorn..."
# Single worker: async handles concurrency; multiple workers break in-memory dedup
python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 1
