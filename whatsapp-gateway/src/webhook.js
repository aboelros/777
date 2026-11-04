/**
 * Webhook dispatcher for WhatsApp Baileys Gateway
 */

const crypto = require('crypto');
const INTERNAL_SECRET = process.env.CALLBACK_SECRET || 'automio_gateway_internal_secret_2026';

async function sendWebhook(backendUrl, endpoint, payload, secret, logger) {
    if (!backendUrl) return;

    try {
        const timestamp = Math.floor(Date.now() / 1000).toString();
        const payloadStr = JSON.stringify(payload);
        const hmacKey = secret || INTERNAL_SECRET;
        const signature = crypto.createHmac('sha256', hmacKey).update(timestamp + '.' + payloadStr).digest('hex');

        const fetch = (await import('node-fetch')).default;
        const targetUrl = `${backendUrl.replace(/\/+$/, '')}/${endpoint.replace(/^\/+/, '')}`;

        const res = await fetch(targetUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-WA-Signature': signature,
                'X-WA-Timestamp': timestamp
            },
            body: payloadStr
        });

        if (logger) {
            logger.info({ status: res.status, endpoint }, 'Webhook dispatched to backend');
        }
    } catch (error) {
        if (logger) {
            logger.warn({ error: error.message, endpoint }, 'Failed to dispatch webhook');
        }
    }
}

function resolveBackendUrl() {
    const raw = process.env.BACKEND_URL;
    if (raw && !raw.includes('ai-sales-bot-api.onrender.com')) {
        return raw;
    }
    return 'https://ai-sales-bot-api-vdr6.onrender.com';
}

module.exports = {
    sendWebhook,
    resolveBackendUrl
};
