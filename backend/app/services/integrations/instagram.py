"""
Instagram integration client for handling Direct Messages.
Uses Instagram Graph API.
"""

from typing import Dict, Any, Optional, List
import aiohttp
import structlog
from uuid import UUID

logger = structlog.get_logger(__name__)


class InstagramClient:
    """Client for Instagram Direct Messages via Graph API."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Instagram client.
        
        Args:
            config: Configuration dict containing:
                - page_id: Instagram business account ID
                - access_token: Instagram Graph API access token
        """
        self.page_id = config.get("page_id") or config.get("instagram_business_account_id")
        self.access_token = config.get("access_token") or config.get("api_key")
        self.api_base = "https://graph.facebook.com/v18.0"
        
        if not self.page_id or not self.access_token:
            raise ValueError(f"Instagram config missing required credentials: page_id={self.page_id}, token={'present' if self.access_token else 'missing'}")
    
    async def send_message(
        self,
        customer_id: str,
        message: str,
        quick_replies: Optional[List[Dict[str, str]]] = None,
        messaging_type: str = "RESPONSE",
        tag: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send a message to a customer via Instagram DM.
        
        Args:
            customer_id: Recipient Instagram ID
            message: Message content
            messaging_type: RESPONSE, MESSAGE_TAG, or HUMAN_AGENT
            tag: Required if messaging_type is MESSAGE_TAG
        """
        message_data = {"text": message}
        if quick_replies:
            message_data["quick_replies"] = [
                {
                    "content_type": "text",
                    "title": str(reply.get("title", ""))[:20],
                    "payload": str(reply.get("payload", ""))
                }
                for reply in quick_replies[:13]
            ]
            
        payload = {
            "recipient": {"id": str(customer_id)},
            "message": message_data,
            "messaging_type": messaging_type
        }
        if tag:
            payload["tag"] = tag
            
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        candidate_urls = [f"{self.api_base}/{self.page_id}/messages", f"{self.api_base}/me/messages"]
        last_error = ""

        try:
            timeout = aiohttp.ClientTimeout(total=15)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                for target_url in candidate_urls:
                    async with session.post(target_url, json=payload, headers=headers) as response:
                        if response.status == 200:
                            data = await response.json()
                            logger.info(
                                "Instagram message sent",
                                customer_id=str(customer_id),
                                message_id=data.get("message_id"),
                                type=messaging_type
                            )
                            return {
                                "status": "success",
                                "id": data.get("message_id"),
                                "platform": "instagram"
                            }
                        last_error = await response.text()
                        logger.warning(
                            "Instagram send attempt failed",
                            url=target_url,
                            status=response.status,
                            error=last_error
                        )

                # If failed and quick_replies were included, retry once with clean text
                if quick_replies:
                    clean_payload = {
                        "recipient": {"id": str(customer_id)},
                        "message": {"text": message},
                        "messaging_type": messaging_type
                    }
                    for target_url in candidate_urls:
                        async with session.post(target_url, json=clean_payload, headers=headers) as retry_resp:
                            if retry_resp.status == 200:
                                retry_data = await retry_resp.json()
                                logger.info("Instagram fallback text-only message sent successfully")
                                return {
                                    "status": "success",
                                    "id": retry_data.get("message_id"),
                                    "platform": "instagram"
                                }

                logger.error("Instagram all send attempts failed", error=last_error)
                return {
                    "status": "error",
                    "message": f"API error: {last_error}",
                    "details": last_error
                }
        except Exception as e:
            logger.error("Instagram exception during send", error=str(e))
            return {"status": "error", "message": str(e)}

    async def send_action(
        self,
        customer_id: str,
        sender_action: str
    ) -> Dict[str, Any]:
        """
        Send a sender action (typing_on, typing_off, mark_seen).
        
        Args:
            customer_id: Recipient Instagram ID
            sender_action: typing_on, typing_off, or mark_seen
        """
        url = f"{self.api_base}/{self.page_id}/messages"
        payload = {
            "recipient": {"id": str(customer_id)},
            "sender_action": sender_action
        }
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        try:
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        return {"status": "success"}
                    else:
                        error_data = await response.text()
                        logger.warning(f"Instagram action {sender_action} failed", status=response.status, error=error_data)
                        return {"status": "error", "message": f"API error: {response.status}"}
        except Exception as e:
            logger.error(f"Instagram action {sender_action} exception", error=str(e))
            return {"status": "error", "message": str(e)}
    
    async def unsend_message(
        self,
        message_id: str
    ) -> Dict[str, Any]:
        """
        Unsend (delete) a message on Instagram.
        Note: This only works for outbound messages sent by the page.
        """
        url = f"{self.api_base}/{message_id}"
        
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.delete(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info("Instagram message unsent", message_id=message_id)
                        return {"status": "success", "data": data}
                    else:
                        error_data = await response.text()
                        logger.warning(
                            "Instagram unsend failed",
                            status=response.status,
                            error=error_data
                        )
                        return {"status": "error", "message": f"API error: {response.status}"}
        except Exception as e:
            logger.error("Instagram unsend exception", error=str(e))
            return {"status": "error", "message": str(e)}
            
    async def get_messages(
        self,
        conversation_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Fetch messages from a conversation.
        
        Args:
            conversation_id: Instagram conversation ID
            limit: Max number of messages to fetch
        
        Returns:
            List of message dicts
        """
        url = f"{self.api_base}/{conversation_id}/messages"
        params = {
            "fields": "id,from,to,message,created_time",
            "limit": limit,
            "access_token": self.access_token
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("data", [])
                    return []
        except Exception as e:
            logger.error("Failed to fetch Instagram messages", error=str(e))
            return []
    
    async def verify_webhook(
        self,
        verify_token: str,
        mode: str,
        challenge: str
    ) -> Optional[str]:
        """
        Verify Instagram webhook.
        
        Args:
            verify_token: Expected token
            mode: Verification mode
            challenge: Challenge string to return
        
        Returns:
            Challenge string if verified, None otherwise
        """
        if mode == "subscribe" and verify_token == self.access_token:
            return challenge
        return None
    
    async def handle_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process incoming Instagram webhook event.
        
        Args:
            payload: Webhook payload
        
        Returns:
            Processed event data
        """
        try:
            entry = payload.get("entry", [])[0]
            messaging = entry.get("messaging", [])[0]
            
            sender_id = messaging.get("sender", {}).get("id")
            message = messaging.get("message", {})
            message_text = message.get("text")
            
            return {
                "platform": "instagram",
                "sender_id": sender_id,
                "message": message_text,
                "timestamp": messaging.get("timestamp"),
                "message_id": message.get("mid")
            }
        except (KeyError, IndexError) as e:
            logger.error("Invalid Instagram webhook payload", error=str(e))
            return {"status": "error", "message": "Invalid payload"}
    
    async def get_profile(self, user_id: str) -> Dict[str, Any]:
        """
        Get Instagram user profile information.
        
        Args:
            user_id: Instagram user ID
        
        Returns:
            User profile dict
        """
        url = f"{self.api_base}/{user_id}"
        params = {
            "fields": "id,username,name,profile_picture_url",
            "access_token": self.access_token
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    return {}
        except Exception as e:
            logger.error("Failed to fetch Instagram profile", error=str(e))
            return {}
    
    async def _find_ig_id(self) -> str:
        """
        Internal helper to find the Instagram Business Account ID.
        Many users provide the Page ID; this discovers the linked IG ID.
        """
        # If the ID already looks like it might be a Page ID, or to be safe,
        # we check the instagram_business_account field.
        url = f"{self.api_base}/{self.page_id}"
        params = {
            "fields": "instagram_business_account",
            "access_token": self.access_token
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        ig_id = data.get("instagram_business_account", {}).get("id")
                        if ig_id:
                            return ig_id
        except Exception:
            pass
        return self.page_id

    async def get_instagram_engagement(self) -> Dict[str, Any]:
        """
        Fetch Instagram account engagement metrics.
        Requires instagram_basic permission.
        """
        target_id = await self._find_ig_id()
        
        url = f"{self.api_base}/{target_id}"
        params = {
            "fields": "followers_count,media_count,name,username",
            "access_token": self.access_token
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info("Fetched Instagram engagement metrics", target_id=target_id, followers=data.get("followers_count"))
                        return data
                    
                    error_data = await response.text()
                    logger.error("Failed to fetch Instagram engagement", status=response.status, target_id=target_id, error=error_data)
                    return {}
        except Exception as e:
            logger.error("Exception fetching Instagram engagement", error=str(e))
            return {}

    async def get_media(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Fetch the Instagram Business Account's media.
        """
        target_id = await self._find_ig_id()
        url = f"{self.api_base}/{target_id}/media"
        params = {
            "fields": "id,caption,media_type,media_url,permalink,timestamp",
            "limit": limit,
            "access_token": self.access_token
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("data", [])
                    return []
        except Exception as e:
            logger.error("Exception fetching IG media", error=str(e))
            return []

    async def get_comments(self, media_id: str) -> List[Dict[str, Any]]:
        """
        Fetch comments for an IG media object.
        """
        url = f"{self.api_base}/{media_id}/comments"
        params = {
            "fields": "id,from,text,timestamp",
            "access_token": self.access_token
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("data", [])
                    return []
        except Exception as e:
            logger.error("Exception fetching IG comments", error=str(e))
            return []

    async def reply_to_comment(self, comment_id: str, message: str) -> Dict[str, Any]:
        """
        Reply to an Instagram comment.
        """
        url = f"{self.api_base}/{comment_id}/replies"
        payload = {"message": message}
        params = {"access_token": self.access_token}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    error_data = await response.text()
                    return {"status": "error", "message": error_data}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def test_connection(self) -> bool:
        """Test if Instagram connection is working."""
        url = f"{self.api_base}/{self.page_id}"
        params = {"access_token": self.access_token}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    return response.status == 200
        except Exception:
            return False
