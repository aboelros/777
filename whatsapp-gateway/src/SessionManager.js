// WhatsApp Session Manager - Supabase persistence, distributed locking, lifecycle

const { default: makeWASocket, DisconnectReason, fetchLatestBaileysVersion, Browsers } = require('@whiskeysockets/baileys');
const pino = require('pino');
const QRCode = require('qrcode');
const { useSupabaseAuthState } = require('./auth/supabaseAuthState');
const { DistributedLock } = require('./db/lock');
const { migrateFilesystemSession } = require('./auth/migration');
const RestorationQueue = require('./auth/queue');
const { query } = require('./db/pool');
const { sendSessionMessage, handleIncomingMessage } = require('./handlers/messageHandler');
const { dispatchSessionStatus } = require('./handlers/statusDispatcher');

class SessionManager {
    constructor(sessionDir = './sessions') {
        this.sessions = new Map();
        this.sessionDir = sessionDir;
        this.logger = pino({ level: process.env.LOG_LEVEL || 'info' });
        this.restorationQueue = new RestorationQueue({ concurrency: 2, maxRetries: 3 });
    }

    async createSession(sessionId, metadata = {}) {
        if (this.sessions.has(sessionId)) {
            const existing = this.sessions.get(sessionId);
            if (['connected', 'qr_ready', 'connecting'].includes(existing.status)) {
                return { session_id: sessionId, status: existing.status, qr_code: existing.qr, created_at: existing.createdAt };
            }
            if (existing.socket) {
                try { existing.socket.end(new Error('Refreshing socket')); } catch (_) {}
            }
        }

        const lock = new DistributedLock(sessionId);
        const acquired = await lock.acquire();
        if (!acquired) {
            return { session_id: sessionId, status: 'locked', message: 'Socket locked by another gateway instance' };
        }

        await migrateFilesystemSession(this.sessionDir, sessionId, metadata.project_id).catch((err) => {
            this.logger.warn({ sessionId, error: err.message }, 'Filesystem migration check note');
        });

        const session = {
            id: sessionId,
            metadata,
            status: 'connecting',
            qr: null,
            socket: null,
            lock,
            authAdapter: null,
            createdAt: new Date(),
            lastActivity: new Date()
        };
        this.sessions.set(sessionId, session);

        let qrResolve, qrReject;
        const qrPromise = new Promise((res, rej) => { qrResolve = res; qrReject = rej; });
        const timeout = setTimeout(() => qrReject(new Error('QR generation timeout')), 60000);

        await this.startSocket(sessionId, metadata, qrResolve, qrReject, timeout);

        try {
            await qrPromise;
        } catch (error) {
            if (session.status !== 'connected') {
                this.logger.warn({ sessionId, error: error.message }, 'QR wait notice');
            }
        }

        return { session_id: sessionId, status: session.status, qr_code: session.qr, created_at: session.createdAt };
    }

    async startSocket(sessionId, metadata, qrResolve, qrReject, timeout) {
        const session = this.sessions.get(sessionId);
        if (!session) return;

        const authAdapter = await useSupabaseAuthState(sessionId, metadata.project_id);
        session.authAdapter = authAdapter;

        let version = [2, 3000, 1015901307];
        try {
            const vInfo = await fetchLatestBaileysVersion();
            if (vInfo?.version) version = vInfo.version;
        } catch (_) {}

        const sock = makeWASocket({
            version,
            auth: authAdapter.state,
            printQRInTerminal: false,
            logger: pino({ level: 'silent' }),
            browser: Browsers.ubuntu('Chrome'),
            connectTimeoutMs: 60000,
            retryRequestDelayMs: 5000,
            markOnlineOnConnect: false
        });
        session.socket = sock;

        sock.ev.on('connection.update', async (update) => {
            const { connection, lastDisconnect, qr } = update;
            if (qr) {
                try {
                    session.qr = await QRCode.toDataURL(qr);
                    session.status = 'qr_ready';
                    if (timeout) clearTimeout(timeout);
                    if (qrResolve) qrResolve();
                } catch (e) {
                    if (qrReject) qrReject(e);
                }
            }

            if (connection === 'close') {
                const statusCode = lastDisconnect?.error?.output?.statusCode;
                const isLoggedOut = statusCode === DisconnectReason.loggedOut;
                this.logger.warn({ sessionId, isLoggedOut, statusCode }, 'Socket connection closed');

                if (isLoggedOut) {
                    session.status = 'disconnected';
                    await authAdapter.invalidateAuth();
                    if (session.lock) await session.lock.release();
                    this.sessions.delete(sessionId);
                    await dispatchSessionStatus(sessionId, metadata, 'disconnected', this.logger);
                } else {
                    session.status = 'connecting';
                    await authAdapter.markSessionStatus('connecting');
                    const delay = statusCode === DisconnectReason.restartRequired ? 1000 : 3000;
                    setTimeout(() => {
                        if (this.sessions.has(sessionId)) this.startSocket(sessionId, metadata);
                    }, delay);
                }
            } else if (connection === 'open') {
                session.status = 'connected';
                session.qr = null;
                if (timeout) clearTimeout(timeout);
                if (qrResolve) qrResolve();
                const phone = sock.user?.id ? sock.user.id.split(':')[0].split('@')[0] : null;
                await authAdapter.markSessionStatus('connected', phone);
                await dispatchSessionStatus(sessionId, metadata, 'connected', this.logger);
            }
        });

        sock.ev.on('creds.update', async () => {
            await authAdapter.saveCreds().catch((e) => this.logger.error({ error: e.message }, 'Creds save failed'));
        });

        sock.ev.on('messages.upsert', async ({ messages, type }) => {
            if (type === 'notify') {
                for (const msg of messages) {
                    if (!msg.key.fromMe && msg.message) {
                        await handleIncomingMessage(sessionId, session.metadata, msg, this.logger);
                    }
                }
            }
        });
    }

    getSessionStatus(sessionId) {
        const session = this.sessions.get(sessionId);
        if (!session) return { status: 'not_found', message: 'Session does not exist' };
        return {
            status: session.status,
            qr_code: session.qr,
            created_at: session.createdAt,
            last_activity: session.lastActivity,
            metadata: session.metadata
        };
    }

    async sendMessage(sessionId, to, message, messageType = 'text') {
        const session = this.sessions.get(sessionId);
        if (!session) throw new Error('Session not found');
        if (session.status !== 'connected') throw new Error(`Session is ${session.status}, not connected`);
        const result = await sendSessionMessage(session.socket, to, message, messageType);
        session.lastActivity = new Date();
        return result;
    }

    async closeSession(sessionId) {
        const session = this.sessions.get(sessionId);
        if (!session) return { status: 'closed', session_id: sessionId };
        if (session.socket) {
            try { await session.socket.logout(); } catch (_) {}
            try { session.socket.end(new Error('Session closed')); } catch (_) {}
        }
        if (session.authAdapter) await session.authAdapter.invalidateAuth();
        if (session.lock) await session.lock.release();
        this.sessions.delete(sessionId);
        await dispatchSessionStatus(sessionId, session.metadata, 'disconnected', this.logger);
        return { status: 'closed', session_id: sessionId };
    }

    async restoreActiveSessions() {
        try {
            const res = await query(
                `SELECT integration_id, project_id, phone_number 
                 FROM whatsapp_gateway_sessions 
                 WHERE auth_valid = TRUE`
            );
            this.logger.info({ count: res.rows.length }, 'Found active sessions in Supabase to restore');
            for (const row of res.rows) {
                this.restorationQueue.add(async () => {
                    this.logger.info({ integrationId: row.integration_id }, 'Auto-restoring session from Supabase');
                    await this.createSession(row.integration_id, { project_id: row.project_id, auto_restored: true });
                }).catch((err) => {
                    this.logger.error({ integrationId: row.integration_id, error: err.message }, 'Failed auto-restoring session');
                });
            }
        } catch (err) {
            this.logger.error({ error: err.message }, 'Error fetching active sessions for restoration');
        }
    }

    async shutdown() {
        this.logger.info('Shutting down session manager, releasing locks...');
        for (const [sessionId, session] of this.sessions.entries()) {
            if (session.socket) {
                try { session.socket.end(new Error('Gateway shutdown')); } catch (_) {}
            }
            if (session.lock) {
                await session.lock.release().catch(() => {});
            }
        }
        this.sessions.clear();
    }

    getAllSessions() {
        const list = [];
        for (const [id, s] of this.sessions.entries()) {
            list.push({ id, status: s.status, created_at: s.createdAt, last_activity: s.lastActivity });
        }
        return list;
    }
}

module.exports = SessionManager;
