import httpx
import structlog
from typing import Dict, Any, Optional

logger = structlog.get_logger(__name__)

class TikTokOAuthService:
    """Service for handling TikTok Shop OAuth 2.0 flow."""
    
    def __init__(self, app_key: str, app_secret: str, redirect_uri: Optional[str] = None):
        self.app_key = app_key
        self.app_secret = app_secret
        self.redirect_uri = redirect_uri
        self.auth_base_url = "https://services.tiktokshop.com/open/authorize"
        self.token_url = "https://auth.tiktok-shops.com/api/v2/token/get"
        
    def get_auth_url(self, state: str) -> str:
        """
        Generate the authorization URL for TikTok Shop.
        We can also append &redirect_uri={redirect_uri} if necessary,
        but TikTok often uses the one configured in the App Console.
        """
        url = f"{self.auth_base_url}?app_key={self.app_key}&state={state}"
        return url
        
    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """
        Exchange the authorization code for an access token.
        """
        params = {
            "app_key": self.app_key,
            "app_secret": self.app_secret,
            "auth_code": code,
            "grant_type": "authorized_code"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(self.token_url, params=params)
            
            if response.status_code != 200:
                logger.error("TikTok token exchange HTTP error", status=response.status_code, body=response.text)
                raise ValueError(f"HTTP Error {response.status_code} during TikTok token exchange")
                
            data = response.json()
            
            if data.get("code") != 0:
                error_msg = data.get("message", "Unknown error")
                logger.error("TikTok token exchange API error", error=error_msg, raw_data=data)
                raise ValueError(f"TikTok API Error: {error_msg}")
                
            return data.get("data", {})
            
    async def get_authorized_shops(self, access_token: str) -> Dict[str, Any]:
        """
        Fetch the authorized shop details using the access token.
        Endpoint: https://auth.tiktok-shops.com/api/v2/shop/get_authorized_shop
        """
        url = "https://auth.tiktok-shops.com/api/v2/shop/get_authorized_shop"
        params = {
            "app_key": self.app_key,
            "app_secret": self.app_secret,
            "access_token": access_token
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            
            if response.status_code != 200:
                logger.error("TikTok get shops HTTP error", status=response.status_code, body=response.text)
                raise ValueError(f"HTTP Error {response.status_code} during TikTok get shops")
                
            data = response.json()
            if data.get("code") != 0:
                error_msg = data.get("message", "Unknown error")
                logger.error("TikTok get shops API error", error=error_msg, raw_data=data)
                raise ValueError(f"TikTok API Error: {error_msg}")
                
            return data.get("data", {})
