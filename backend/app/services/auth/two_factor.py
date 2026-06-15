"""
Two-Factor Authentication Service
Implements TOTP-based 2FA with QR code generation and backup codes.
"""
import pyotp
import qrcode
import io
import base64
from typing import Dict, List, Optional
from datetime import datetime
import secrets
from cryptography.fernet import Fernet
from app.core.config import settings


class TwoFactorAuth:
    """
    Handles two-factor authentication setup and verification.
    """
    
    def __init__(self):
        self.cipher = Fernet(settings.ENCRYPTION_KEY.encode() if isinstance(settings.ENCRYPTION_KEY, str) else settings.ENCRYPTION_KEY)
    
    def setup_2fa(self, user_email: str, user_id: str) -> Dict[str, any]:
        """
        Set up 2FA for a user.
        
        Args:
            user_email: User's email address
            user_id: User's unique identifier
            
        Returns:
            Dictionary with QR code, secret, and backup codes
        """
        # Generate secret
        secret = pyotp.random_base32()
        
        # Create TOTP instance
        totp = pyotp.TOTP(secret)
        
        # Generate provisioning URI for QR code
        provisioning_uri = totp.provisioning_uri(
            name=user_email,
            issuer_name=settings.APP_NAME or "AI Business Platform"
        )
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        # Generate backup codes
        backup_codes = self._generate_backup_codes()
        
        return {
            'secret': secret,
            'qr_code': f'data:image/png;base64,{qr_code_base64}',
            'backup_codes': backup_codes,
            'provisioning_uri': provisioning_uri
        }
    
    def verify_2fa_token(self, secret: str, token: str) -> bool:
        """
        Verify a 2FA token.
        
        Args:
            secret: User's TOTP secret
            token: 6-digit token from authenticator app
            
        Returns:
            True if token is valid, False otherwise
        """
        try:
            totp = pyotp.TOTP(secret)
            # Allow 1 window before and after for clock skew
            return totp.verify(token, valid_window=1)
        except Exception:
            return False
    
    def verify_backup_code(self, stored_codes: List[str], provided_code: str) -> tuple[bool, List[str]]:
        """
        Verify a backup code and remove it from the list.
        
        Args:
            stored_codes: List of encrypted backup codes
            provided_code: Code provided by user
            
        Returns:
            Tuple of (is_valid, remaining_codes)
        """
        # Decrypt stored codes
        decrypted_codes = [self._decrypt(code) for code in stored_codes]
        
        if provided_code in decrypted_codes:
            # Remove used code
            decrypted_codes.remove(provided_code)
            # Re-encrypt remaining codes
            remaining_codes = [self._encrypt(code) for code in decrypted_codes]
            return True, remaining_codes
        
        return False, stored_codes
    
    def _generate_backup_codes(self, count: int = 10) -> List[str]:
        """Generate backup codes for 2FA recovery."""
        codes = []
        for _ in range(count):
            # Generate 8-character alphanumeric code
            code = ''.join(secrets.choice('ABCDEFGHJKLMNPQRSTUVWXYZ23456789') for _ in range(8))
            # Format as XXXX-XXXX
            formatted_code = f"{code[:4]}-{code[4:]}"
            codes.append(formatted_code)
        return codes
    
    def _encrypt(self, value: str) -> str:
        """Encrypt a value."""
        return self.cipher.encrypt(value.encode()).decode()
    
    def _decrypt(self, encrypted_value: str) -> str:
        """Decrypt a value."""
        return self.cipher.decrypt(encrypted_value.encode()).decode()
    
    def encrypt_secret(self, secret: str) -> str:
        """Encrypt TOTP secret for storage."""
        return self._encrypt(secret)
    
    def decrypt_secret(self, encrypted_secret: str) -> str:
        """Decrypt TOTP secret from storage."""
        return self._decrypt(encrypted_secret)


class SSOProvider:
    """
    Handles Single Sign-On integration with various providers.
    """
    
    SUPPORTED_PROVIDERS = ['google', 'microsoft', 'github']
    
    def __init__(self):
        self.providers = {}
    
    def get_authorization_url(self, provider: str, redirect_uri: str, state: str) -> str:
        """
        Get OAuth authorization URL for a provider.
        
        Args:
            provider: Provider name (google, microsoft, github)
            redirect_uri: Callback URL
            state: CSRF protection state
            
        Returns:
            Authorization URL
        """
        if provider == 'google':
            return self._get_google_auth_url(redirect_uri, state)
        elif provider == 'microsoft':
            return self._get_microsoft_auth_url(redirect_uri, state)
        elif provider == 'github':
            return self._get_github_auth_url(redirect_uri, state)
        else:
            raise ValueError(f"Unsupported SSO provider: {provider}")
    
    def _get_google_auth_url(self, redirect_uri: str, state: str) -> str:
        """Generate Google OAuth URL."""
        base_url = "https://accounts.google.com/o/oauth2/v2/auth"
        params = {
            'client_id': settings.GOOGLE_CLIENT_ID,
            'redirect_uri': redirect_uri,
            'response_type': 'code',
            'scope': 'openid email profile',
            'state': state,
            'access_type': 'offline',
            'prompt': 'consent'
        }
        query_string = '&'.join(f"{k}={v}" for k, v in params.items())
        return f"{base_url}?{query_string}"
    
    def _get_microsoft_auth_url(self, redirect_uri: str, state: str) -> str:
        """Generate Microsoft OAuth URL."""
        tenant = getattr(settings, 'MICROSOFT_TENANT_ID', 'common')
        base_url = f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/authorize"
        params = {
            'client_id': settings.MICROSOFT_CLIENT_ID,
            'redirect_uri': redirect_uri,
            'response_type': 'code',
            'scope': 'openid email profile',
            'state': state,
            'response_mode': 'query'
        }
        query_string = '&'.join(f"{k}={v}" for k, v in params.items())
        return f"{base_url}?{query_string}"
    
    def _get_github_auth_url(self, redirect_uri: str, state: str) -> str:
        """Generate GitHub OAuth URL."""
        base_url = "https://github.com/login/oauth/authorize"
        params = {
            'client_id': settings.GITHUB_CLIENT_ID,
            'redirect_uri': redirect_uri,
            'scope': 'user:email',
            'state': state
        }
        query_string = '&'.join(f"{k}={v}" for k, v in params.items())
        return f"{base_url}?{query_string}"
