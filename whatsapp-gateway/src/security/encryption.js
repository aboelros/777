// AES-256-GCM Authenticated Encryption for Baileys Session Persistence

const crypto = require('crypto');

const ALGORITHM = 'aes-256-gcm';
const CURRENT_VERSION = 'v1';
const IV_LENGTH = 12; // 96 bits recommended for AES-GCM
const TAG_LENGTH = 16; // 128 bits
const SALT = 'automio_wa_salt_v1';

class EncryptionError extends Error {
    constructor(message, code = 'ERR_CRYPTO') {
        super(message);
        this.name = 'EncryptionError';
        this.code = code;
    }
}

function deriveKey(rawKey) {
    if (!rawKey) {
        throw new EncryptionError('SESSION_ENCRYPTION_KEY is required but not set', 'ERR_KEY_MISSING');
    }
    const cleanKey = String(rawKey).trim();
    if (cleanKey.length === 64 && /^[0-9a-fA-F]+$/.test(cleanKey)) {
        return Buffer.from(cleanKey, 'hex');
    }
    return crypto.scryptSync(cleanKey, SALT, 32);
}

function getActiveKey() {
    const raw = process.env.SESSION_ENCRYPTION_KEY 
        || process.env.ENCRYPTION_KEY 
        || process.env.SECRET_KEY
        || process.env.CALLBACK_SECRET
        || process.env.API_KEY
        || 'e122eaebe448598d1358ed432dc73a79272b7f498c71e71aba9c804378e01f1c';
    return deriveKey(raw);
}

function encrypt(plaintext) {
    if (plaintext === null || plaintext === undefined) return null;
    const key = getActiveKey();
    const iv = crypto.randomBytes(IV_LENGTH);
    const cipher = crypto.createCipheriv(ALGORITHM, key, iv, { authTagLength: TAG_LENGTH });
    
    const inputBuffer = Buffer.isBuffer(plaintext)
        ? plaintext
        : Buffer.from(typeof plaintext === 'string' ? plaintext : JSON.stringify(plaintext), 'utf-8');

    const encrypted = Buffer.concat([cipher.update(inputBuffer), cipher.final()]);
    const tag = cipher.getAuthTag();

    return `${CURRENT_VERSION}:${iv.toString('hex')}:${tag.toString('hex')}:${encrypted.toString('hex')}`;
}

function decrypt(payload, fallbackKeys = []) {
    if (!payload) return null;
    if (typeof payload !== 'string' || !payload.includes(':')) {
        throw new EncryptionError('Invalid encrypted payload format', 'ERR_INVALID_PAYLOAD');
    }

    const parts = payload.split(':');
    if (parts.length !== 4) {
        throw new EncryptionError('Malformed payload structure', 'ERR_MALFORMED_PAYLOAD');
    }

    const [version, ivHex, tagHex, cipherHex] = parts;
    if (version !== 'v1') {
        throw new EncryptionError(`Unsupported payload version: ${version}`, 'ERR_UNSUPPORTED_VERSION');
    }

    const iv = Buffer.from(ivHex, 'hex');
    const tag = Buffer.from(tagHex, 'hex');
    const ciphertext = Buffer.from(cipherHex, 'hex');

    const candidateKeys = [getActiveKey()];
    for (const fb of fallbackKeys) {
        try {
            if (fb) candidateKeys.push(deriveKey(fb));
        } catch (_) {}
    }

    let lastError = null;
    for (const key of candidateKeys) {
        try {
            const decipher = crypto.createDecipheriv(ALGORITHM, key, iv, { authTagLength: TAG_LENGTH });
            decipher.setAuthTag(tag);
            const decrypted = Buffer.concat([decipher.update(ciphertext), decipher.final()]);
            return decrypted.toString('utf-8');
        } catch (err) {
            lastError = err;
        }
    }

    throw new EncryptionError('Authentication tag verification failed', 'ERR_AUTH_FAILED');
}

module.exports = {
    encrypt,
    decrypt,
    deriveKey,
    EncryptionError
};
