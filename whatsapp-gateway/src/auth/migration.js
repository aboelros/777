// Filesystem to Supabase Session Migration Helper

const fs = require('fs');
const path = require('path');
const { BufferJSON } = require('@whiskeysockets/baileys');
const { query, getClient } = require('../db/pool');
const { encrypt, decrypt } = require('../security/encryption');
const pino = require('pino');

const logger = pino({ level: process.env.LOG_LEVEL || 'info' });

const KNOWN_KEY_TYPES = [
    'app-state-sync-version',
    'app-state-sync-key',
    'sender-key-memory',
    'sender-key',
    'pre-key',
    'session'
];

function parseKeyFileName(fileName) {
    if (!fileName.endsWith('.json') || fileName === 'creds.json') {
        return null;
    }
    const base = fileName.slice(0, -5);
    for (const keyType of KNOWN_KEY_TYPES) {
        const prefix = `${keyType}-`;
        if (base.startsWith(prefix)) {
            const rawId = base.slice(prefix.length);
            const keyId = rawId.replace(/__/g, '/').replace(/-/g, ':');
            return { keyType, keyId };
        }
    }
    return null;
}

async function migrateFilesystemSession(sessionDir, integrationId, projectId = null) {
    const targetDir = path.join(sessionDir, integrationId);
    const credsPath = path.join(targetDir, 'creds.json');

    if (!fs.existsSync(credsPath)) {
        return { migrated: false, reason: 'no_fs_creds' };
    }

    logger.info({ integrationId }, 'Found local filesystem credentials, preparing migration');

    let credsRaw;
    try {
        credsRaw = fs.readFileSync(credsPath, 'utf-8');
    } catch (err) {
        logger.error({ integrationId, error: err.message }, 'Failed reading creds.json');
        return { migrated: false, error: err.message };
    }

    const encryptedCreds = encrypt(credsRaw);
    const resolvedProj = projectId || integrationId;

    const sessionRes = await query(
        `INSERT INTO whatsapp_gateway_sessions 
         (integration_id, project_id, credentials_encrypted, session_status, auth_valid)
         VALUES ($1, $2, $3, $4, $5)
         ON CONFLICT (integration_id) DO UPDATE 
         SET credentials_encrypted = EXCLUDED.credentials_encrypted,
             auth_valid = TRUE,
             updated_at = NOW()
         RETURNING id`,
        [integrationId, resolvedProj, encryptedCreds, 'connecting', true]
    );

    const sessionId = sessionRes.rows[0].id;

    // Verify decryption of credentials
    try {
        const decryptedCreds = decrypt(encryptedCreds);
        JSON.parse(decryptedCreds, BufferJSON.reviver);
    } catch (verErr) {
        logger.error({ integrationId, error: verErr.message }, 'Migration verification failed on creds decryption');
        throw verErr;
    }

    const files = fs.readdirSync(targetDir);
    let migratedKeys = 0;
    const client = await getClient();

    try {
        await client.query('BEGIN');
        for (const file of files) {
            const parsed = parseKeyFileName(file);
            if (!parsed) continue;

            const filePath = path.join(targetDir, file);
            const content = fs.readFileSync(filePath, 'utf-8');
            const encryptedKey = encrypt(content);

            await client.query(
                `INSERT INTO whatsapp_gateway_keys 
                 (session_id, integration_id, key_type, key_id, key_data_encrypted, key_version, updated_at)
                 VALUES ($1, $2, $3, $4, $5, 1, NOW())
                 ON CONFLICT (session_id, key_type, key_id) 
                 DO UPDATE SET 
                    key_data_encrypted = EXCLUDED.key_data_encrypted,
                    key_version = whatsapp_gateway_keys.key_version + 1,
                    updated_at = NOW()`,
                [sessionId, integrationId, parsed.keyType, parsed.keyId, encryptedKey]
            );
            migratedKeys++;
        }
        await client.query('COMMIT');
    } catch (err) {
        await client.query('ROLLBACK');
        logger.error({ integrationId, error: err.message }, 'Failed migrating key files into database');
        throw err;
    } finally {
        client.release();
    }

    logger.info(
        { integrationId, migratedKeys, localPreserved: true },
        'Filesystem session migrated to Supabase. Local files preserved per safety constraint.'
    );

    return { migrated: true, sessionId, migratedKeys };
}

module.exports = {
    migrateFilesystemSession,
    parseKeyFileName
};
