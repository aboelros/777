// Supabase PostgreSQL Authentication State Adapter for Baileys v6.6.0

const { BufferJSON, initAuthCreds, proto } = require('@whiskeysockets/baileys');
const { query, getClient } = require('../db/pool');
const { encrypt, decrypt } = require('../security/encryption');
const pino = require('pino');

const logger = pino({ level: process.env.LOG_LEVEL || 'info' });

async function useSupabaseAuthState(integrationId, projectId = null) {
    let sessionRecord = null;

    const findOrCreateSession = async () => {
        const res = await query(
            'SELECT * FROM whatsapp_gateway_sessions WHERE integration_id = $1',
            [integrationId]
        );
        if (res.rows.length > 0) {
            return res.rows[0];
        }

        const freshCreds = initAuthCreds();
        const encrypted = encrypt(JSON.stringify(freshCreds, BufferJSON.replacer));
        const resolvedProj = projectId || integrationId;

        const insertRes = await query(
            `INSERT INTO whatsapp_gateway_sessions 
             (integration_id, project_id, credentials_encrypted, session_status, auth_valid)
             VALUES ($1, $2, $3, $4, $5)
             ON CONFLICT (integration_id) DO UPDATE 
             SET updated_at = NOW() 
             RETURNING *`,
            [integrationId, resolvedProj, encrypted, 'connecting', true]
        );
        return insertRes.rows[0];
    };

    sessionRecord = await findOrCreateSession();

    let creds;
    try {
        const decryptedJson = decrypt(sessionRecord.credentials_encrypted);
        creds = JSON.parse(decryptedJson, BufferJSON.reviver);
    } catch (err) {
        logger.warn({ integrationId, error: err.message }, 'Failed decrypting creds, initializing fresh keys');
        creds = initAuthCreds();
    }

    const keys = {
        get: async (type, ids) => {
            const data = {};
            if (!ids || ids.length === 0) return data;

            try {
                const res = await query(
                    `SELECT key_id, key_data_encrypted 
                     FROM whatsapp_gateway_keys 
                     WHERE session_id = $1 AND key_type = $2 AND key_id = ANY($3)`,
                    [sessionRecord.id, type, ids]
                );

                for (const row of res.rows) {
                    try {
                        const decrypted = decrypt(row.key_data_encrypted);
                        let val = JSON.parse(decrypted, BufferJSON.reviver);
                        if (type === 'app-state-sync-key' && val) {
                            val = proto.Message.AppStateSyncKeyData.fromObject(val);
                        }
                        data[row.key_id] = val;
                    } catch (decErr) {
                        logger.error({ keyId: row.key_id, error: decErr.message }, 'Error decrypting signal key');
                    }
                }
            } catch (queryErr) {
                logger.error({ type, idsCount: ids.length, error: queryErr.message }, 'Failed fetching signal keys');
            }

            for (const id of ids) {
                if (data[id] === undefined) data[id] = null;
            }
            return data;
        },

        set: async (data) => {
            const client = await getClient();
            try {
                await client.query('BEGIN');
                for (const category in data) {
                    for (const id in data[category]) {
                        const value = data[category][id];
                        if (value) {
                            const serialized = JSON.stringify(value, BufferJSON.replacer);
                            const encryptedVal = encrypt(serialized);
                            await client.query(
                                `INSERT INTO whatsapp_gateway_keys 
                                 (session_id, integration_id, key_type, key_id, key_data_encrypted, key_version, updated_at)
                                 VALUES ($1, $2, $3, $4, $5, 1, NOW())
                                 ON CONFLICT (session_id, key_type, key_id) 
                                 DO UPDATE SET 
                                    key_data_encrypted = EXCLUDED.key_data_encrypted,
                                    key_version = whatsapp_gateway_keys.key_version + 1,
                                    updated_at = NOW()`,
                                [sessionRecord.id, integrationId, category, id, encryptedVal]
                            );
                        } else {
                            await client.query(
                                `DELETE FROM whatsapp_gateway_keys 
                                 WHERE session_id = $1 AND key_type = $2 AND key_id = $3`,
                                [sessionRecord.id, category, id]
                            );
                        }
                    }
                }
                await client.query('COMMIT');
            } catch (err) {
                await client.query('ROLLBACK');
                logger.error({ error: err.message }, 'Failed atomic signal keys mutation');
                throw err;
            } finally {
                client.release();
            }
        }
    };

    const saveCreds = async () => {
        try {
            const serialized = JSON.stringify(creds, BufferJSON.replacer);
            const encrypted = encrypt(serialized);
            await query(
                `UPDATE whatsapp_gateway_sessions 
                 SET credentials_encrypted = $1, 
                     auth_valid = TRUE,
                     version = version + 1,
                     updated_at = NOW()
                 WHERE id = $2`,
                [encrypted, sessionRecord.id]
            );
        } catch (err) {
            logger.error({ integrationId, error: err.message }, 'Failed persisting updated credentials');
            throw err;
        }
    };

    const markSessionStatus = async (status, phoneNumber = null) => {
        const updates = ['session_status = $1', 'updated_at = NOW()'];
        const params = [status, sessionRecord.id];
        let pIndex = 3;

        if (status === 'connected') {
            updates.push('last_connected_at = NOW()');
        } else if (status === 'disconnected') {
            updates.push('last_disconnected_at = NOW()');
        }

        if (phoneNumber) {
            updates.push(`phone_number = $${pIndex}`);
            params.push(phoneNumber);
            pIndex++;
        }

        await query(
            `UPDATE whatsapp_gateway_sessions SET ${updates.join(', ')} WHERE id = $2`,
            params
        ).catch((e) => logger.warn({ error: e.message }, 'Status update warning'));
    };

    const invalidateAuth = async () => {
        await query(
            `UPDATE whatsapp_gateway_sessions 
             SET auth_valid = FALSE, session_status = 'disconnected', updated_at = NOW() 
             WHERE id = $1`,
            [sessionRecord.id]
        );
        await query(
            'DELETE FROM whatsapp_gateway_keys WHERE session_id = $1',
            [sessionRecord.id]
        );
        logger.info({ integrationId }, 'Session auth invalidated on explicit logout');
    };

    return {
        state: { creds, keys },
        saveCreds,
        markSessionStatus,
        invalidateAuth,
        sessionId: sessionRecord.id,
        isAuthValid: () => Boolean(sessionRecord.auth_valid)
    };
}

module.exports = {
    useSupabaseAuthState
};
