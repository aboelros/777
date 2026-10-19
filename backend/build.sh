#!/usr/bin/env bash
# Render build script for backend

set -o errexit

echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Migration Governance Gate for Build Phase
# Build-time execution of migrations against production databases is strictly prohibited.
# Build artifacts must be immutable; schema changes belong to the release/deployment phase.
ENVIRONMENT_LOWER=$(echo "${ENVIRONMENT:-development}" | tr '[:upper:]' '[:lower:]' | xargs)

if [ "$ENVIRONMENT_LOWER" = "production" ] || [ "$ENVIRONMENT_LOWER" = "prod" ]; then
    if [ "${RUN_MIGRATIONS_ON_BUILD:-false}" = "true" ]; then
        echo "[BUILD GOVERNANCE] WARNING: RUN_MIGRATIONS_ON_BUILD=true was requested, but database migrations during build are strictly PROHIBITED in production."
    fi
    echo "[BUILD GOVERNANCE] Skipping database migrations during build in production. Schema changes must occur in the release phase."
elif [ "$ENVIRONMENT_LOWER" = "staging" ] || [ "$ENVIRONMENT_LOWER" = "stage" ]; then
    if [ "${RUN_MIGRATIONS_ON_BUILD:-false}" = "true" ]; then
        echo "[BUILD GOVERNANCE] Explicit RUN_MIGRATIONS_ON_BUILD=true detected for staging build. Running migrations..."
        alembic upgrade head
    else
        echo "[BUILD GOVERNANCE] Skipping database migrations during build in staging."
    fi
else
    # Non-production (development, local, test)
    if [ "${RUN_MIGRATIONS_ON_BUILD:-false}" = "true" ]; then
        echo "[BUILD GOVERNANCE] Running database migrations during build..."
        alembic upgrade head
    else
        echo "[BUILD GOVERNANCE] Skipping database migrations during build."
    fi
fi

echo "Build complete!"
