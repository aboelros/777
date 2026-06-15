# 🔒 Security Guidelines

## Overview

AI Sales Commander implements multiple layers of security to protect your data and ensure safe operations. This document outlines security best practices and recommendations.

## Authentication & Authorization

### JWT Token Strategy

- **Access Tokens**: Short-lived (15 minutes) for API requests
- **Refresh Tokens**: Long-lived (7 days) stored in database for rotation
- **Token Rotation**: Automatic refresh token rotation on use
- **Secure Storage**: Tokens stored in localStorage (frontend) and database (backend)

### Password Requirements

- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit
- Hashed using bcrypt with salt rounds

### Role-Based Access Control (RBAC)

Two primary roles:
- **Admin**: Full system access, user management
- **User**: Access to owned projects and resources

## API Security

### Rate Limiting

Implemented per endpoint to prevent abuse:
- Authentication endpoints: 5 requests/minute
- AI endpoints: 60 requests/minute
- Standard endpoints: 100 requests/minute

**Configuration**: Adjust `RATE_LIMIT_PER_MINUTE` in `.env`

### CORS (Cross-Origin Resource Sharing)

Configure allowed origins in production:

```env
CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
```

**Never use** `*` (wildcard) in production.

### Request Validation

- All inputs validated using Pydantic schemas
- SQL injection prevention via SQLAlchemy ORM
- XSS protection through proper escaping

## Data Protection

### Sensitive Data Handling

1. **API Keys & Secrets**
   - Store in environment variables
   - Never commit to version control
   - Use secrets manager in production (e.g., Google Secret Manager)

2. **Customer PII**
   - Minimize data collection
   - Encrypt sensitive fields
   - Redact PII before logging
   - GDPR compliance utilities available

3. **Database Encryption**
   - Use encrypted connections (SSL/TLS)
   - Enable encryption at rest
   - Regular automated backups

### Environment Variables Security

❌ **Never do this:**
```python
SECRET_KEY = "my-secret-key"  # Hardcoded
```

✅ **Always do this:**
```python
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY or len(SECRET_KEY) < 32:
    raise ValueError("Invalid SECRET_KEY")
```

## AI & Gemini Security

### Prompt Injection Prevention

- Input sanitization before sending to AI
- System prompts separated from user input
- Function calling validation

### PII Protection in AI Requests

```python
# Redact sensitive information
customer_data = {
    "name": "John D.",  # Partial name
    "email": "j***@example.com",  # Masked email
    "phone": "***-***-1234"  # Masked phone
}
```

### Cost Management

- Per-project token quotas
- Usage tracking and billing
- Automated throttling on limits
- Cost estimation before requests

## Infrastructure Security

### Docker Security

1. **Non-root Users**
   ```dockerfile
   USER appuser  # Never run as root
   ```

2. **Image Scanning**
   ```bash
   docker scan aisales-backend:latest
   ```

3. **Secrets Management**
   ```bash
   # Use Docker secrets
   docker secret create db_password ./db_password.txt
   ```

### Network Security

- Private network for service communication
- Exposed ports: Only 80/443 (reverse proxy)
- Firewall rules for database and Redis

### SSL/TLS Certificates

**Production must use HTTPS:**

```nginx
server {
    listen 443 ssl http2;
    ssl_certificate /etc/ssl/certs/cert.pem;
    ssl_certificate_key /etc/ssl/private/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
}
```

Use Let's Encrypt for free certificates:
```bash
certbot --nginx -d yourdomain.com
```

## Third-Party Integration Security

### Webhook Verification

All webhooks must verify authenticity:

**Shopify HMAC Verification:**
```python
def verify_shopify_webhook(data, hmac_header, secret):
    computed_hmac = hmac.new(
        secret.encode('utf-8'),
        data,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(computed_hmac, hmac_header)
```

### OAuth Flow Security

- Use state parameter to prevent CSRF
- Validate redirect URIs
- Store tokens encrypted

### API Key Management

- Rotate keys every 90 days
- Use different keys per environment
- Revoke compromised keys immediately

## Logging & Monitoring

### What to Log

✅ **Log:**
- Authentication attempts (success/failure)
- API endpoint access
- Error messages
- AI usage and costs

❌ **Never log:**
- Passwords or tokens
- Credit card numbers
- Full PII without masking

### Log Security

```python
# Good logging
logger.info("User login", user_id=user.id, ip=request.ip)

# Bad logging
logger.info(f"User {user.email} logged in with password {password}")
```

### Security Monitoring

Set up alerts for:
- Multiple failed login attempts
- Unusual API usage patterns
- High AI costs
- Database connection errors
- Webhook verification failures

## Incident Response

### If Security Breach Occurs

1. **Immediate Actions**
   - Rotate all secrets and API keys
   - Force logout all users
   - Review access logs
   - Disable compromised integrations

2. **Investigation**
   - Check database for unauthorized access
   - Review API logs
   - Identify affected users

3. **Notification**
   - Inform affected users
   - Document the incident
   - Update security measures

## Compliance

### GDPR Compliance

**User Rights:**
- Right to access data
- Right to deletion
- Right to data portability
- Right to rectification

**Implementation:**
```python
# Export user data
@router.get("/api/v1/users/me/export")
async def export_user_data(user_id: str):
    # Return all user data in JSON format
    pass

# Delete user data
@router.delete("/api/v1/users/me")
async def delete_user_account(user_id: str):
    # Permanently delete user and associated data
    pass
```

### Data Retention

- API logs: 90 days
- Messages: Configurable per project
- Orders: Indefinite (or per legal requirements)
- Audit logs: 1 year minimum

## Security Checklist

### Pre-Production

- [ ] All secrets moved to environment variables
- [ ] Strong `SECRET_KEY` generated (min 64 chars)
- [ ] HTTPS/SSL configured
- [ ] CORS properly restricted
- [ ] Rate limiting enabled
- [ ] Database backups automated
- [ ] Error messages don't expose system details
- [ ] Dependency vulnerability scan completed
- [ ] Webhook verification implemented
- [ ] API key rotation schedule set

### Post-Deployment

- [ ] Security monitoring enabled
- [ ] Alerts configured
- [ ] Incident response plan documented
- [ ] Regular security audits scheduled
- [ ] Team security training completed

## Vulnerability Reporting

If you discover a security vulnerability:

1. **DO NOT** open a public issue
2. Email: security@yourdomain.com
3. Include:
   - Description of vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

We aim to respond within 24 hours.

## Security Updates

Stay updated:
- Subscribe to security advisories
- Monitor dependency vulnerabilities
- Apply patches promptly
- Review audit logs regularly

## Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [Google Cloud Security Best Practices](https://cloud.google.com/security/best-practices)
- [GDPR Compliance Guide](https://gdpr.eu/)

---

**Last Updated**: 2025-01-12

For questions about security, contact: security@yourdomain.com
