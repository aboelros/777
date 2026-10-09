import httpx
from typing import Dict, Any, Optional
from app.core.config import settings

class MetaOAuthService:
    """Service for handling Meta (Facebook) OAuth flow."""
    
    API_VERSION = "v18.0"
    BASE_URL = "https://graph.facebook.com"
    
    def __init__(self, app_id: str, app_secret: str, redirect_uri: str):
        self.app_id = app_id
        self.app_secret = app_secret
        self.redirect_uri = redirect_uri
        
    def get_auth_url(self, state: str, scope: str = "email,public_profile") -> str:
        """Generate the Facebook Login URL."""
        return (
            f"https://www.facebook.com/{self.API_VERSION}/dialog/oauth?"
            f"client_id={self.app_id}&"
            f"redirect_uri={self.redirect_uri}&"
            f"state={state}&"
            f"scope={scope}&"
            f"response_type=code"
        )
        
    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/{self.API_VERSION}/oauth/access_token",
                params={
                    "client_id": self.app_id,
                    "redirect_uri": self.redirect_uri,
                    "client_secret": self.app_secret,
                    "code": code
                }
            )
            
            if response.is_error:
                import structlog
                logger = structlog.get_logger(__name__)
                logger.error("Meta OAuth Error", status=response.status_code, body=response.text)
                
            response.raise_for_status()
            return response.json()
            
    async def get_long_lived_token(self, short_lived_token: str) -> Dict[str, Any]:
        """Exchange short-lived token for long-lived token."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/{self.API_VERSION}/oauth/access_token",
                params={
                    "grant_type": "fb_exchange_token",
                    "client_id": self.app_id,
                    "client_secret": self.app_secret,
                    "fb_exchange_token": short_lived_token
                }
            )
            response.raise_for_status()
            return response.json()

    async def get_user_pages(self, access_token: str) -> Dict[str, Any]:
        """Get list of pages the user manages."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/{self.API_VERSION}/me/accounts",
                params={
                    "access_token": access_token,
                    "fields": "id,name,access_token,instagram_business_account{id,username,name}"
                }
            )
            response.raise_for_status()
            return response.json()

    async def get_whatsapp_accounts(self, access_token: str) -> Dict[str, Any]:
        """Get list of WhatsApp Business Accounts and Phone Numbers."""
        async with httpx.AsyncClient() as client:
            # 1. Get Businesses
            businesses_resp = await client.get(
                f"{self.BASE_URL}/{self.API_VERSION}/me/businesses",
                params={"access_token": access_token}
            )
            
            # If no businesses or error (e.g. no permission), return empty
            if businesses_resp.status_code != 200:
                return {"data": []}
                
            businesses = businesses_resp.json().get("data", [])
            all_numbers = []
            
            for business in businesses:
                biz_id = business.get("id")
                # 2. Get WABAs for this business
                wabas_resp = await client.get(
                    f"{self.BASE_URL}/{self.API_VERSION}/{biz_id}/client_whatsapp_business_accounts",
                    params={"access_token": access_token}
                )
                if wabas_resp.status_code != 200:
                    continue
                    
                wabas = wabas_resp.json().get("data", [])
                
                for waba in wabas:
                    waba_id = waba.get("id")
                    waba_name = waba.get("name")
                    
                    # 3. Get Phone Numbers for this WABA
                    numbers_resp = await client.get(
                        f"{self.BASE_URL}/{self.API_VERSION}/{waba_id}/phone_numbers",
                        params={"access_token": access_token}
                    )
                    if numbers_resp.status_code != 200:
                        continue
                        
                    numbers = numbers_resp.json().get("data", [])
                    for num in numbers:
                        all_numbers.append({
                            "id": num.get("id"),
                            "display_phone_number": num.get("display_phone_number"),
                            "verified_name": num.get("verified_name"),
                            "waba_id": waba_id,
                            "waba_name": waba_name,
                            "business_id": biz_id,
                            "business_name": business.get("name")
                        })
                        
            return {"data": all_numbers}
