#!/bin/bash
set -e

echo "🔧 Creating multiple databases..."

# Create auth database
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE DATABASE aisales_auth;
    GRANT ALL PRIVILEGES ON DATABASE aisales_auth TO $POSTGRES_USER;
EOSQL

# Create application database
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE DATABASE aisales_app;
    GRANT ALL PRIVILEGES ON DATABASE aisales_app TO $POSTGRES_USER;
EOSQL

echo "✅ Databases created successfully!"
echo "   - aisales_auth (users, authentication)"
echo "   - aisales_app (projects, orders, messages, etc.)"
