/**
 * Webhook dispatcher for WhatsApp Baileys Gateway
 */

const crypto = require('crypto');

async function sendWebhook(backendUrl, endpoint, payload, secret, logger) {
    if (!backendUrl) return;

    try {
        const timestamp = Math.floor(Date.now() / 1000).toString();
        const payloadStr = JSON.stringify(payload);
        const signature = crypto.createHmac('sha256', secret || '').update(timestamp + '.' + payloadStr).digest('hex');

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
