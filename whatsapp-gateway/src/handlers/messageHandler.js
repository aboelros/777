// WhatsApp Message Handler - Normalization, sending, and dispatching

const { sendWebhook, resolveBackendUrl } = require('../webhook');

function normalizeJid(to) {
    const cleanTo = String(to || '').trim();
    if (cleanTo.includes('@')) {
        return cleanTo;
    }
    const digits = cleanTo.replace(/\D/g, '');
    if (digits.length >= 15) {
        return `${digits}@lid`;
    }
    return `${digits}@s.whatsapp.net`;
}

async function sendSessionMessage(socket, to, message, messageType = 'text') {
    if (!socket) {
        throw new Error('Socket not initialized');
    }
    if (messageType !== 'text') {
        throw new Error(`Unsupported message type: ${messageType}`);
    }

    const jid = normalizeJid(to);
    const result = await socket.sendMessage(jid, { text: message });
    return {
        message_id: result.key.id,
        status: 'sent',
        timestamp: new Date()
    };
}

async function handleIncomingMessage(sessionId, metadata, msg, logger) {
    await sendWebhook(
        resolveBackendUrl(),
        '/api/v1/webhooks/wa_gateway',
        { session_id: sessionId, message: msg, metadata: metadata || {} },
        process.env.CALLBACK_SECRET,
        logger
    );
}

module.exports = {
    normalizeJid,
    sendSessionMessage,
    handleIncomingMessage
};
