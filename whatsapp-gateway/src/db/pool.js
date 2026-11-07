// Database Connection Pool for WhatsApp Gateway (PostgreSQL / Supabase)

const { Pool } = require('pg');
const pino = require('pino');

const logger = pino({ level: process.env.LOG_LEVEL || 'info' });

let poolInstance = null;

function sanitizeUrl(rawUrl) {
    if (!rawUrl) return null;
    let url = String(rawUrl).trim();
    if (url.startsWith('postgresql+asyncpg://')) {
        url = url.replace('postgresql+asyncpg://', 'postgresql://');
    } else if (url.startsWith('postgres+asyncpg://')) {
        url = url.replace('postgres+asyncpg://', 'postgresql://');
    }
    return url;
}

function resolveConnectionString() {
    return (
        sanitizeUrl(process.env.DATABASE_URL) ||
        sanitizeUrl(process.env.SUPABASE_DATABASE_URL) ||
        sanitizeUrl(process.env.APP_DATABASE_URL) ||
        sanitizeUrl('postgresql://postgres.ccejhzadokkjssjiwmxt:n01012012Noran@aws-1-eu-north-1.pooler.supabase.com:5432/postgres')
    );
}

function getPool() {
    if (poolInstance) return poolInstance;

    const connectionString = resolveConnectionString();
    if (!connectionString) {
        throw new Error('DATABASE_URL or SUPABASE_DATABASE_URL is required for gateway persistence');
    }

    const isRemote = !connectionString.includes('localhost') && !connectionString.includes('127.0.0.1');

    poolInstance = new Pool({
        connectionString,
        max: parseInt(process.env.DB_POOL_MAX || '10', 10),
        idleTimeoutMillis: 30000,
        connectionTimeoutMillis: 10000,
        ssl: isRemote ? { rejectUnauthorized: false } : false
    });

    poolInstance.on('error', (err) => {
        logger.error({ error: err.message }, 'Unexpected idle client error in PostgreSQL pool');
    });

    return poolInstance;
}

async function query(text, params = []) {
    const pool = getPool();
    const start = Date.now();
    try {
        const result = await pool.query(text, params);
        const duration = Date.now() - start;
        if (duration > 1500) {
            logger.warn({ duration, queryPreview: text.slice(0, 50) }, 'Slow PostgreSQL query executed');
        }
        return result;
    } catch (err) {
        logger.error({ error: err.message, queryPreview: text.slice(0, 50) }, 'PostgreSQL query failed');
        throw err;
    }
}

async function getClient() {
    const pool = getPool();
    const client = await pool.connect();
    return client;
}

async function healthCheck() {
    try {
        const res = await query('SELECT 1 as healthy');
        return res.rows[0]?.healthy === 1;
    } catch (err) {
        return false;
    }
}

async function closePool() {
    if (poolInstance) {
        await poolInstance.end();
        poolInstance = null;
        logger.info('PostgreSQL pool closed successfully');
    }
}

module.exports = {
    getPool,
    query,
    getClient,
    healthCheck,
    closePool
};
