// WhatsApp Connection Status Webhook Dispatcher

const { sendWebhook, resolveBackendUrl } = require('../webhook');

async function dispatchSessionStatus(sessionId, metadata, status, logger) {
    await sendWebhook(
        resolveBackendUrl(),
        '/api/v1/webhooks/wa_gateway',
        {
            session_id: sessionId,
            event: 'connection.update',
            status,
            metadata: metadata || {}
        },
        process.env.CALLBACK_SECRET,
        logger
    );
}

module.exports = {
    dispatchSessionStatus
};
