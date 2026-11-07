// Distributed Advisory Locking for WhatsApp Gateway Integrations

const crypto = require('crypto');
const os = require('os');
const { getClient, query } = require('./pool');
const pino = require('pino');

const logger = pino({ level: process.env.LOG_LEVEL || 'info' });

class LockAcquisitionError extends Error {
    constructor(message, integrationId) {
        super(message);
        this.name = 'LockAcquisitionError';
        this.integrationId = integrationId;
    }
}

function hashIntegrationIdToBigInt(integrationId) {
    const hash = crypto.createHash('sha256').update(String(integrationId)).digest();
    return hash.readBigInt64BE(0).toString();
}

class DistributedLock {
    constructor(integrationId) {
        this.integrationId = integrationId;
        this.lockKey = hashIntegrationIdToBigInt(integrationId);
        this.client = null;
        this.holderId = `${os.hostname()}:${process.pid}:${Date.now()}`;
        this.isAcquired = false;
    }

    async acquire() {
        if (this.isAcquired) return true;

        this.client = await getClient();
        try {
            const res = await this.client.query('SELECT pg_try_advisory_lock($1::bigint) as acquired', [this.lockKey]);
            const acquired = res.rows[0]?.acquired === true;

            if (!acquired) {
                this.client.release();
                this.client = null;
                logger.warn({ integrationId: this.integrationId }, 'Distributed lock busy: another instance holds socket lock');
                return false;
            }

            this.isAcquired = true;
            await query(
                'UPDATE whatsapp_gateway_sessions SET session_status = $1, updated_at = NOW() WHERE integration_id = $2',
                ['connecting', this.integrationId]
            ).catch(() => {});

            logger.info({ integrationId: this.integrationId, lockKey: this.lockKey }, 'Distributed lock acquired successfully');
            return true;
        } catch (err) {
            if (this.client) {
                this.client.release();
                this.client = null;
            }
            logger.error({ integrationId: this.integrationId, error: err.message }, 'Failed during lock acquisition');
            throw new LockAcquisitionError(err.message, this.integrationId);
        }
    }

    async release() {
        if (!this.isAcquired || !this.client) return;

        try {
            await this.client.query('SELECT pg_advisory_unlock($1::bigint)', [this.lockKey]);
            logger.info({ integrationId: this.integrationId }, 'Distributed lock released');
        } catch (err) {
            logger.warn({ integrationId: this.integrationId, error: err.message }, 'Error releasing advisory lock');
        } finally {
            this.isAcquired = false;
            this.client.release();
            this.client = null;
        }
    }
}

module.exports = {
    DistributedLock,
    LockAcquisitionError,
    hashIntegrationIdToBigInt
};
