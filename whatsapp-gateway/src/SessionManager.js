/**
 * Session Manager - Handles WhatsApp session lifecycle
 */

const { default: makeWASocket, DisconnectReason, useMultiFileAuthState, fetchLatestBaileysVersion } = require('@whiskeysockets/baileys');
const pino = require('pino');
const fs = require('fs');
const path = require('path');
const QRCode = require('qrcode');
const { v4: uuidv4 } = require('uuid');

class SessionManager {
    constructor(sessionDir = './sessions') {
        this.sessions = new Map();
        this.sessionDir = sessionDir;
        this.logger = pino({ level: process.env.LOG_LEVEL || 'info' });

        // Ensure session directory exists
        if (!fs.existsSync(sessionDir)) {
            fs.mkdirSync(sessionDir, { recursive: true });
        }
    }

    /**
     * Create a new WhatsApp session
     */
    async createSession(sessionId, metadata = {}) {
        // If session already exists, close it first
        if (this.sessions.has(sessionId)) {
            this.logger.warn({ sessionId }, 'Session already exists, closing it before creating new one');
            try {
                await this.closeSession(sessionId);
            } catch (error) {
                this.logger.error({ sessionId, error: error.message }, 'Failed to close existing session, will try to recreate anyway');
            }
        }

        const sessionPath = path.join(this.sessionDir, sessionId);

        // Create session directory
        if (!fs.existsSync(sessionPath)) {
            fs.mkdirSync(sessionPath, { recursive: true });
        }

        const { state, saveCreds } = await useMultiFileAuthState(sessionPath);
        const { version } = await fetchLatestBaileysVersion();

        const session = {
            id: sessionId,
            metadata,
            status: 'connecting',
            qr: null,
            socket: null,
            createdAt: new Date(),
            lastActivity: new Date()
        };

        // Create a promise to wait for QR code
        let qrResolve, qrReject;
        const qrPromise = new Promise((resolve, reject) => {
            qrResolve = resolve;
            qrReject = reject;
        });

        // Timeout after 5 minutes (enough time for user to enter pairing code)
        const timeout = setTimeout(() => {
            qrReject(new Error('QR code generation timeout'));
        }, 300000);

        // Create socket
        const sock = makeWASocket({
            version,
            auth: state,
            printQRInTerminal: false,
            logger: pino({ level: 'silent' }),
            browser: ['Chrome (Linux)', '', ''],
            connectTimeoutMs: 60000,
            retryRequestDelayMs: 5000,
            markOnlineOnConnect: false,
        });

        session.socket = sock;
        let pairingRequested = false;

        // Handle QR code
        sock.ev.on('connection.update', async (update) => {
            const { connection, lastDisconnect, qr } = update;

            if (qr) {
                // Extract phone number from either key (robustness fix)
                const rawPhoneNumber = metadata.phoneNumber || metadata.phone_number;

                this.logger.info({ sessionId, metadata, rawPhoneNumber }, 'Connection update received');

                // If pairing code is requested, don't generate QR
                if (metadata.usePairingCode && rawPhoneNumber) {
                    if (pairingRequested) return; // Prevent multiple requests
                    pairingRequested = true;

                    try {
                        // Sanitize phone number (remove + and non-digits)
                        const cleanPhoneNumber = rawPhoneNumber.replace(/\D/g, '');

                        this.logger.info({ sessionId, phoneNumber: cleanPhoneNumber }, 'Requesting pairing code from WhatsApp...');

                        // Request code
                        const code = await sock.requestPairingCode(cleanPhoneNumber);

                        session.pairingCode = code;
                        session.status = 'pairing_code_ready';
                        this.logger.info({ sessionId, code }, 'Pairing code generated successfully');

                        clearTimeout(timeout);
                        qrResolve();
                        return;
                    } catch (error) {
                        this.logger.error({ sessionId, error: error.message }, 'Failed to request pairing code');
                        qrReject(error);
                        return;
                    }
                }

                try {
                    // Generate QR code as data URL
                    const qrDataURL = await QRCode.toDataURL(qr);
                    session.qr = qrDataURL;
                    session.status = 'qr_ready';
                    this.logger.info({ sessionId }, 'QR code generated');

                    // Resolve the promise
                    clearTimeout(timeout);
                    qrResolve();
                } catch (error) {
                    this.logger.error({ sessionId, error: error.message }, 'Failed to generate QR code');
                    qrReject(error);
                }
            }

            if (connection === 'close') {
                const statusCode = lastDisconnect?.error?.output?.statusCode;
                const shouldReconnect = statusCode !== DisconnectReason.loggedOut;

                this.logger.warn({
                    sessionId,
                    shouldReconnect,
                    statusCode,
                    error: lastDisconnect?.error?.message
                }, 'Connection closed');

                if (!shouldReconnect) {
                    session.status = 'disconnected';
                    this.sessions.delete(sessionId);

                    // Clean up session files
                    this.cleanupSessionFiles(sessionId);
                } else {
                    session.status = 'connecting';
                }
            } else if (connection === 'open') {
                session.status = 'connected';
                session.qr = null;
                this.logger.info({ sessionId }, 'Connection opened successfully');
            }
        });

        // Wrap saveCreds to handle race conditions during cleanup
        const safeSaveCreds = async (creds) => {
            try {
                // Check if session directory still exists
                if (fs.existsSync(sessionPath)) {
                    await saveCreds(creds);
                }
            } catch (error) {
                // Ignore ENOENT errors during cleanup
                if (error.code !== 'ENOENT') {
                    this.logger.error({ sessionId, error: error.message }, 'Failed to save credentials');
                }
            }
        };

        // Save credentials on update
        sock.ev.on('creds.update', safeSaveCreds);

        // Handle incoming messages
        sock.ev.on('messages.upsert', async ({ messages, type }) => {
            if (type === 'notify') {
                for (const msg of messages) {
                    if (!msg.key.fromMe && msg.message) {
                        await this.handleIncomingMessage(sessionId, msg);
                    }
                }
            }
        });

        this.sessions.set(sessionId, session);
        this.logger.info({ sessionId }, 'Session created, waiting for QR code...');

        // Wait for QR code or pairing code to be generated
        try {
            await qrPromise;
        } catch (error) {
            // Only clean up if we didn't successfully generate a pairing code
            // If pairing code was generated, keep the session alive for user to enter it
            if (!session.pairingCode) {
                this.sessions.delete(sessionId);
                this.cleanupSessionFiles(sessionId);
            } else {
                this.logger.warn({ sessionId }, 'Error after pairing code generation, keeping session alive');
            }
            throw error;
        }

        return {
            session_id: sessionId,
            status: session.status,
            qr_code: session.qr,
            pairing_code: session.pairingCode,
            created_at: session.createdAt
        };
    }

    /**
     * Get session status
     */
    getSessionStatus(sessionId) {
        const session = this.sessions.get(sessionId);

        if (!session) {
            return {
                status: 'not_found',
                message: 'Session does not exist'
            };
        }

        return {
            status: session.status,
            qr_code: session.qr,
            pairing_code: session.pairingCode,
            created_at: session.createdAt,
            last_activity: session.lastActivity,
            metadata: session.metadata
        };
    }

    /**
     * Send a message
     */
    async sendMessage(sessionId, to, message, messageType = 'text') {
        const session = this.sessions.get(sessionId);

        if (!session) {
            throw new Error('Session not found');
        }

        if (session.status !== 'connected') {
            throw new Error(`Session is ${session.status}, not connected`);
        }

        const sock = session.socket;

        // Format phone number for WhatsApp
        const jid = to.includes('@') ? to : `${to}@s.whatsapp.net`;

        let result;

        if (messageType === 'text') {
            result = await sock.sendMessage(jid, { text: message });
        } else {
            throw new Error(`Unsupported message type: ${messageType}`);
        }

        session.lastActivity = new Date();
        this.logger.info({ sessionId, to }, 'Message sent');

        return {
            message_id: result.key.id,
            status: 'sent',
            timestamp: new Date()
        };
    }

    /**
     * Close a session
     */
    async closeSession(sessionId) {
        const session = this.sessions.get(sessionId);

        if (!session) {
            throw new Error('Session not found');
        }

        if (session.socket) {
            await session.socket.logout();
        }

        this.sessions.delete(sessionId);
        this.cleanupSessionFiles(sessionId);

        this.logger.info({ sessionId }, 'Session closed');

        return {
            status: 'closed',
            session_id: sessionId
        };
    }

    /**
     * Handle incoming message
     */
    async handleIncomingMessage(sessionId, msg) {
        const session = this.sessions.get(sessionId);
        if (!session) return;

        const webhookData = {
            session_id: sessionId,
            message: msg,
            metadata: session.metadata
        };

        // Send to backend webhook
        if (process.env.BACKEND_URL) {
            try {
                const crypto = require('crypto');
                const timestamp = Math.floor(Date.now() / 1000).toString();
                const payloadStr = JSON.stringify(webhookData);
                const secret = process.env.CALLBACK_SECRET || '';
                const signature = crypto.createHmac('sha256', secret).update(timestamp + '.' + payloadStr).digest('hex');

                const fetch = (await import('node-fetch')).default;
                await fetch(`${process.env.BACKEND_URL}/api/v1/webhooks/wa_gateway`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-WA-Signature': signature,
                        'X-WA-Timestamp': timestamp
                    },
                    body: payloadStr
                });

                this.logger.info({ sessionId }, 'Webhook sent to backend');
            } catch (error) {
                this.logger.error({ sessionId, error: error.message }, 'Failed to send webhook');
            }
        }

        session.lastActivity = new Date();
    }

    /**
     * Clean up session files
     */
    cleanupSessionFiles(sessionId) {
        const sessionPath = path.join(this.sessionDir, sessionId);

        if (fs.existsSync(sessionPath)) {
            fs.rmSync(sessionPath, { recursive: true, force: true });
            this.logger.info({ sessionId }, 'Session files cleaned up');
        }
    }

    /**
     * Get all sessions
     */
    getAllSessions() {
        const sessions = [];

        for (const [id, session] of this.sessions.entries()) {
            sessions.push({
                id,
                status: session.status,
                created_at: session.createdAt,
                last_activity: session.lastActivity,
                metadata: session.metadata
            });
        }

        return sessions;
    }
}

module.exports = SessionManager;
