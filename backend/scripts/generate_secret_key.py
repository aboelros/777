#!/usr/bin/env python
"""
Generate a secure SECRET_KEY for JWT tokens.
Run with: python scripts/generate_secret_key.py
"""

import secrets

def generate_secret_key(length=64):
    """Generate a cryptographically secure secret key."""
    return secrets.token_urlsafe(length)


if __name__ == "__main__":
    secret_key = generate_secret_key()
    
    print("=" * 70)
    print("Generated SECRET_KEY for JWT Authentication")
    print("=" * 70)
    print()
    print("Add this to your .env file:")
    print()
    print(f"SECRET_KEY={secret_key}")
    print()
    print("=" * 70)
    print()
    print("⚠️  IMPORTANT:")
    print("   - Keep this secret secure")
    print("   - Never commit it to version control")
    print("   - Use different keys for dev/staging/prod")
    print("   - Rotate keys periodically")
    print()
