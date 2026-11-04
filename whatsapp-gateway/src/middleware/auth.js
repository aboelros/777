/**
 * Authentication Middleware
 */

function authMiddleware(req, res, next) {
    const configuredKey = process.env.API_KEY;

    // If no API_KEY configured in gateway environment, allow request
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
    if (token !== configuredKey.trim()) {
        return res.status(401).json({
            status: 'error',
            message: 'Unauthorized - Invalid API key'
        });
    }

    next();
}

module.exports = authMiddleware;
