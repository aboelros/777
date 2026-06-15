/**
 * Express Server - WhatsApp Baileys Gateway
 */

require('dotenv').config();
const express = require('express');
const cors = require('cors');
const pino = require('pino');
const { v4: uuidv4 } = require('uuid');
const SessionManager = require('./SessionManager');
const authMiddleware = require('./middleware/auth');

const app = express();
const logger = pino({ level: process.env.LOG_LEVEL || 'info' });
const sessionManager = new SessionManager(process.env.SESSION_DIR || './sessions');

// Middleware
app.use(cors());
app.use(express.json());

// Health check
app.get('/health', (req, res) => {
    res.json({
        status: 'ok',
        timestamp: new Date(),
        sessions: sessionManager.getAllSessions().length
    });
});

// Root endpoint
app.get('/', (req, res) => {
    res.json({
        name: 'WhatsApp Baileys Gateway',
        version: '1.0.0',
        status: 'running',
        endpoints: {
            health: '/health',
            sessions: '/sessions',
            documentation: 'See README.md for API documentation'
        }
    });
});

// ============================================================================
// Session Management Endpoints
// ============================================================================

/**
 * Create a new session
 * POST /sessions
 */
app.post('/sessions', authMiddleware, async (req, res) => {
    const startTime = Date.now();
    try {
        const { project_id, integration_id, metadata } = req.body;

        logger.info({ project_id, integration_id }, 'Received session creation request');

        // Generate session ID
        const sessionId = integration_id || uuidv4();

        logger.info({ sessionId }, 'Starting session creation...');

        const sessionData = await sessionManager.createSession(sessionId, {
            project_id,
            integration_id,
            ...metadata
        });

        const duration = Date.now() - startTime;
        logger.info({ sessionId, duration }, 'Session created via API');

        res.json({
            status: 'success',
            ...sessionData
        });
    } catch (error) {
        const duration = Date.now() - startTime;
        logger.error({ error: error.message, stack: error.stack, duration }, 'Failed to create session');
        res.status(500).json({
            status: 'error',
            message: error.message
        });
    }
});

/**
 * Get session status
 * GET /sessions/:sessionId
 */
app.get('/sessions/:sessionId', authMiddleware, (req, res) => {
    try {
        const { sessionId } = req.params;
        const status = sessionManager.getSessionStatus(sessionId);

        res.json({
            status: 'success',
            ...status
        });
    } catch (error) {
        logger.error({ error: error.message }, 'Failed to get session status');
        res.status(500).json({
            status: 'error',
            message: error.message
        });
    }
});

/**
 * Get all sessions
 * GET /sessions
 */
app.get('/sessions', authMiddleware, (req, res) => {
    try {
        const sessions = sessionManager.getAllSessions();

        res.json({
            status: 'success',
            sessions,
            count: sessions.length
        });
    } catch (error) {
        logger.error({ error: error.message }, 'Failed to get sessions');
        res.status(500).json({
            status: 'error',
            message: error.message
        });
    }
});

/**
 * Close a session
 * POST /sessions/:sessionId/close
 */
app.post('/sessions/:sessionId/close', authMiddleware, async (req, res) => {
    try {
        const { sessionId } = req.params;
        const result = await sessionManager.closeSession(sessionId);

        logger.info({ sessionId }, 'Session closed via API');

        res.json({
            status: 'success',
            ...result
        });
    } catch (error) {
        logger.error({ error: error.message }, 'Failed to close session');
        res.status(500).json({
            status: 'error',
            message: error.message
        });
    }
});

// ============================================================================
// Message Endpoints
// ============================================================================

/**
 * Send a message
 * POST /sessions/:sessionId/messages
 */
app.post('/sessions/:sessionId/messages', authMiddleware, async (req, res) => {
    try {
        const { sessionId } = req.params;
        const { to, message, message_type = 'text', extra = {} } = req.body;

        if (!to || !message) {
            return res.status(400).json({
                status: 'error',
                message: 'Missing required fields: to, message'
            });
        }

        const result = await sessionManager.sendMessage(sessionId, to, message, message_type);

        logger.info({ sessionId, to }, 'Message sent via API');

        res.json({
            status: 'success',
            ...result
        });
    } catch (error) {
        logger.error({ error: error.message }, 'Failed to send message');
        res.status(500).json({
            status: 'error',
            message: error.message
        });
    }
});

// ============================================================================
// Error Handling
// ============================================================================

app.use((err, req, res, next) => {
    logger.error({ error: err.message, stack: err.stack }, 'Unhandled error');
    res.status(500).json({
        status: 'error',
        message: 'Internal server error'
    });
});

// ============================================================================
// Start Server
// ============================================================================

// Railway sets PORT automatically, fallback to 3000 for local development
const PORT = process.env.PORT || 3000;

app.listen(PORT, '0.0.0.0', () => {
    logger.info({ port: PORT }, 'WhatsApp Baileys Gateway started');
    console.log(`\n🚀 WhatsApp Baileys Gateway running on port ${PORT}`);
    console.log(`📱 Ready to accept connections\n`);
});

// Graceful shutdown
process.on('SIGINT', async () => {
    logger.info('Shutting down gracefully...');
    process.exit(0);
});

process.on('SIGTERM', async () => {
    logger.info('Shutting down gracefully...');
    process.exit(0);
});
