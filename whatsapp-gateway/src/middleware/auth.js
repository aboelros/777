/**
 * Authentication Middleware
 */

function authMiddleware(req, res, next) {
    const apiKey = req.headers['authorization'];
    const expectedKey = `Bearer ${process.env.API_KEY}`;

    if (!apiKey || apiKey !== expectedKey) {
        return res.status(401).json({
            status: 'error',
            message: 'Unauthorized - Invalid API key'
        });
    }

    next();
}

module.exports = authMiddleware;
