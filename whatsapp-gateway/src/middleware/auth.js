/**
 * Authentication Middleware
 */

const INTERNAL_SECRET = process.env.INTERNAL_SECRET || 'automio_gateway_internal_secret_2026';

function authMiddleware(req, res, next) {
    const internalHeader = req.headers['x-internal-secret'];
    if (internalHeader && internalHeader === INTERNAL_SECRET) {
        return next();
    }

    const configuredKey = process.env.API_KEY;
    if (!configuredKey || configuredKey.trim() === '') {
        return next();
    }

    const authHeader = req.headers['authorization'] || req.headers['x-api-key'];
    if (!authHeader) {
        return res.status(401).json({
            status: 'error',
            message: 'Unauthorized - Missing API key'
        });
    }

    const token = authHeader.startsWith('Bearer ') ? authHeader.slice(7).trim() : authHeader.trim();
    if (token === configuredKey.trim() || token === INTERNAL_SECRET) {
        return next();
    }

    return res.status(401).json({
        status: 'error',
        message: 'Unauthorized - Invalid API key'
    });
}

module.exports = authMiddleware;
