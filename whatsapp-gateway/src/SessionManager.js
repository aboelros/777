// Session Manager - Handles WhatsApp session lifecycle and socket events

const { default: makeWASocket, DisconnectReason, useMultiFileAuthState, fetchLatestBaileysVersion, Browsers } = require('@whiskeysockets/baileys');
const pino = require('pino');
const fs = require('fs');
const path = require('path');
const QRCode = require('qrcode');
const { sendWebhook, resolveBackendUrl } = require('./webhook');

class SessionManager {
    constructor(sessionDir = './sessions') {
        this.sessions = new Map();
        this.sessionDir = sessionDir;
        this.logger = pino({ level: process.env.LOG_LEVEL || 'info' });

        if (!fs.existsSync(sessionDir)) fs.mkdirSync(sessionDir, { recursive: true });
    }

    async createSession(sessionId, metadata = {}) {
        if (this.sessions.has(sessionId)) {
            const existing = this.sessions.get(sessionId);
            if (existing.status === 'connected') {
                return { session_id: sessionId, status: 'connected', qr_code: null, pairing_code: null, created_at: existing.createdAt };
            }
            if (existing.status === 'qr_ready' && existing.qr) {
                return { session_id: sessionId, status: 'qr_ready', qr_code: existing.qr, pairing_code: existing.pairingCode, created_at: existing.createdAt };
            }
            if (existing.status === 'connecting') {
                return { session_id: sessionId, status: 'connecting', qr_code: existing.qr, pairing_code: existing.pairingCode, created_at: existing.createdAt };
            }
            if (existing.socket) {
                try { existing.socket.end(new Error('Refreshing socket')); } catch (_) {}
            }
        }

        const session = {
            id: sessionId,
            metadata,
            status: 'connecting',
            qr: null,
            socket: null,
            createdAt: new Date(),
            lastActivity: new Date()
        };
        this.sessions.set(sessionId, session);

        let qrResolve, qrReject;
        const qrPromise = new Promise((resolve, reject) => {
            qrResolve = resolve;
            qrReject = reject;
        });

        const timeout = setTimeout(() => {
            qrReject(new Error('QR code generation timeout'));
        }, 60000);

        await this.startSocket(sessionId, metadata, qrResolve, qrReject, timeout);

        try {
            await qrPromise;
        } catch (error) {
            if (!session.pairingCode && session.status !== 'connected') {
                this.logger.warn({ sessionId, error: error.message }, 'QR wait completed with note');
            }
        }

        return {
            session_id: sessionId,
            status: session.status,
            qr_code: session.qr,
            pairing_code: session.pairingCode,
            created_at: session.createdAt
        };
    }

    async startSocket(sessionId, metadata, qrResolve, qrReject, timeout) {
        const session = this.sessions.get(sessionId);
        if (!session) return;

        const sessionPath = path.join(this.sessionDir, sessionId);
        if (!fs.existsSync(sessionPath)) fs.mkdirSync(sessionPath, { recursive: true });

        const { state, saveCreds } = await useMultiFileAuthState(sessionPath);
        let version = [2, 3000, 1015901307];
        try {
            const vInfo = await fetchLatestBaileysVersion();
            if (vInfo?.version) version = vInfo.version;
        } catch (_) {}

        const sock = makeWASocket({
            version,
            auth: state,
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
                    this.logger.info({ sessionId }, 'QR code generated');
                    if (timeout) clearTimeout(timeout);
                    if (qrResolve) qrResolve();
                } catch (e) {
                    if (qrReject) qrReject(e);
                }
            }

            if (connection === 'close') {
                const statusCode = lastDisconnect?.error?.output?.statusCode;
                const shouldReconnect = statusCode !== DisconnectReason.loggedOut;

                this.logger.warn({ sessionId, shouldReconnect, statusCode, error: lastDisconnect?.error?.message }, 'Connection closed');

                if (!shouldReconnect) {
                    session.status = 'disconnected';
                    this.sessions.delete(sessionId);
                    this.cleanupSessionFiles(sessionId);
                    this.dispatchStatus(sessionId, 'disconnected');
                } else {
                    session.status = 'connecting';
                    const delay = statusCode === DisconnectReason.restartRequired ? 1000 : 3000;
                    this.logger.info({ sessionId, statusCode, delay }, 'Reconnecting session...');
                    setTimeout(() => {
                        this.startSocket(sessionId, metadata).catch(err => {
                            this.logger.error({ sessionId, error: err.message }, 'Failed reconnecting socket');
                        });
                    }, delay);
                }
            } else if (connection === 'open') {
                session.status = 'connected';
                session.qr = null;
                this.logger.info({ sessionId }, 'WhatsApp connection opened successfully');
                if (timeout) clearTimeout(timeout);
                if (qrResolve) qrResolve();
                this.dispatchStatus(sessionId, 'connected');
            }
        });

        sock.ev.on('creds.update', async (creds) => {
            try {
                if (fs.existsSync(sessionPath)) await saveCreds(creds);
            } catch (err) {
                if (err.code !== 'ENOENT') this.logger.error({ sessionId, error: err.message }, 'Failed saving creds');
            }
        });

        sock.ev.on('messages.upsert', async ({ messages, type }) => {
            if (type === 'notify') {
                for (const msg of messages) {
                    if (!msg.key.fromMe && msg.message) {
                        await this.handleIncomingMessage(sessionId, msg);
                    }
                }
            }
        });
    }
    async dispatchStatus(sessionId, status) {
        const session = this.sessions.get(sessionId);
        await sendWebhook(
            resolveBackendUrl(),
            '/api/v1/webhooks/wa_gateway',
            { session_id: sessionId, event: 'connection.update', status, metadata: session?.metadata || {} },
            process.env.CALLBACK_SECRET,
            this.logger
        );
    }

    getSessionStatus(sessionId) {
        const session = this.sessions.get(sessionId);
        if (!session) return { status: 'not_found', message: 'Session does not exist' };
        return {
            status: session.status,
            qr_code: session.qr,
            pairing_code: session.pairingCode,
            created_at: session.createdAt,
            last_activity: session.lastActivity,
            metadata: session.metadata
        };
    }

    async sendMessage(sessionId, to, message, messageType = 'text') {
        const session = this.sessions.get(sessionId);
        if (!session) throw new Error('Session not found');
        if (session.status !== 'connected') throw new Error(`Session is ${session.status}, not connected`);

        const cleanTo = String(to || '').trim();
        const digits = cleanTo.replace(/\D/g, '');
        const jid = cleanTo.includes("@") ? cleanTo : (digits.length >= 15 ? (digits + "@lid") : (digits + "@s.whatsapp.net"));
        if (messageType !== 'text') throw new Error(`Unsupported message type: ${messageType}`);

        const result = await session.socket.sendMessage(jid, { text: message });
        session.lastActivity = new Date();
        return { message_id: result.key.id, status: 'sent', timestamp: new Date() };
    }

    async closeSession(sessionId) {
        const session = this.sessions.get(sessionId);
        if (!session) {
            this.cleanupSessionFiles(sessionId);
            return { status: 'closed', session_id: sessionId };
        }
        if (session.socket) {
            try { await session.socket.logout(); } catch (_) {}
            try { session.socket.end(new Error('Session closed')); } catch (_) {}
        }
        this.sessions.delete(sessionId);
        this.cleanupSessionFiles(sessionId);
        this.logger.info({ sessionId }, 'Session logged out and files removed');
        return { status: 'closed', session_id: sessionId };
    }

    async handleIncomingMessage(sessionId, msg) {
        const session = this.sessions.get(sessionId);
        if (!session) return;
        await sendWebhook(
            resolveBackendUrl(),
            '/api/v1/webhooks/wa_gateway',
            { session_id: sessionId, message: msg, metadata: session.metadata },
            process.env.CALLBACK_SECRET,
            this.logger
        );
        session.lastActivity = new Date();
    }
    cleanupSessionFiles(sessionId) {
        const sessionPath = path.join(this.sessionDir, sessionId);
        if (fs.existsSync(sessionPath)) {
            fs.rmSync(sessionPath, { recursive: true, force: true });
            this.logger.info({ sessionId }, 'Session directory removed');
        }
    }
    getAllSessions() {
        const sessions = [];
        for (const [id, session] of this.sessions.entries()) {
            sessions.push({ id, status: session.status, created_at: session.createdAt, last_activity: session.lastActivity });
        }
        return sessions;
    }
}

module.exports = SessionManager;
