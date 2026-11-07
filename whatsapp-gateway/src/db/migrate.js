// Idempotent Database Migrations for WhatsApp Gateway Session Persistence

const { getClient } = require('./pool');
const pino = require('pino');

const logger = pino({ level: process.env.LOG_LEVEL || 'info' });

const UP_SQL = `
CREATE TABLE IF NOT EXISTS whatsapp_gateway_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    integration_id UUID UNIQUE NOT NULL,
    project_id UUID NOT NULL,
    credentials_encrypted TEXT NOT NULL,
    session_status VARCHAR(50) DEFAULT 'disconnected',
    auth_valid BOOLEAN DEFAULT TRUE,
    phone_number VARCHAR(50),
    platform VARCHAR(50) DEFAULT 'baileys',
    version INTEGER DEFAULT 1,
    last_connected_at TIMESTAMPTZ,
    last_disconnected_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS whatsapp_gateway_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES whatsapp_gateway_sessions(id) ON DELETE CASCADE,
    integration_id UUID NOT NULL,
    key_type VARCHAR(100) NOT NULL,
    key_id VARCHAR(255) NOT NULL,
    key_data_encrypted TEXT NOT NULL,
    key_version INTEGER DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT uq_wa_gateway_key UNIQUE (session_id, key_type, key_id)
);

CREATE INDEX IF NOT EXISTS idx_wa_sessions_integration ON whatsapp_gateway_sessions (integration_id);
CREATE INDEX IF NOT EXISTS idx_wa_sessions_project ON whatsapp_gateway_sessions (project_id);
CREATE INDEX IF NOT EXISTS idx_wa_keys_lookup ON whatsapp_gateway_keys (session_id, key_type, key_id);
CREATE INDEX IF NOT EXISTS idx_wa_keys_integration ON whatsapp_gateway_keys (integration_id);
`;

const DOWN_SQL = `
DROP TABLE IF EXISTS whatsapp_gateway_keys CASCADE;
DROP TABLE IF EXISTS whatsapp_gateway_sessions CASCADE;
`;

async function runMigrations() {
    const client = await getClient();
    try {
        await client.query('BEGIN');
        await client.query(UP_SQL);
        await client.query('COMMIT');
        logger.info('WhatsApp gateway database migrations applied successfully');
        return true;
    } catch (err) {
        await client.query('ROLLBACK');
        logger.error({ error: err.message }, 'Failed applying WhatsApp gateway database migrations');
        throw err;
    } finally {
        client.release();
    }
}

async function rollbackMigrations() {
    const client = await getClient();
    try {
        await client.query('BEGIN');
        await client.query(DOWN_SQL);
        await client.query('COMMIT');
        logger.info('WhatsApp gateway database tables dropped successfully');
        return true;
    } catch (err) {
        await client.query('ROLLBACK');
        logger.error({ error: err.message }, 'Failed rolling back WhatsApp gateway database migrations');
        throw err;
    } finally {
        client.release();
    }
}

module.exports = {
    runMigrations,
    rollbackMigrations
};
