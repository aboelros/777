"""
Facebook Messenger integration client.
Uses Facebook Graph API for sending/receiving messages.
"""

from typing import Dict, Any, Optional, List
import aiohttp
import structlog
from uuid import UUID

logger = structlog.get_logger(__name__)


class FacebookClient:
    """Client for Facebook Messenger via Graph API."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Facebook Messenger client.
        
        Args:
            config: Configuration dict containing:
                - page_id: Facebook page ID
                - access_token: Page access token
                - app_secret: Facebook app secret (for webhook verification)
        """
        self.page_id = config.get("page_id")
        self.access_token = config.get("access_token")
        self.app_secret = config.get("app_secret")
        self.api_base = "https://graph.facebook.com/v18.0"
        
        if not self.page_id or not self.access_token:
            raise ValueError("Facebook config must include page_id and access_token")
    
    async def send_message(
        self,
        customer_id: str,
        message: str,
        quick_replies: Optional[List[Dict[str, str]]] = None,
        messaging_type: str = "RESPONSE",
        tag: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send a message to a customer via Facebook Messenger.
        
        Args:
            customer_id: Recipient PSID
            message: Message content
            quick_replies: Optional quick reply buttons
            messaging_type: RESPONSE, MESSAGE_TAG, or HUMAN_AGENT
            tag: Required if messaging_type is MESSAGE_TAG
        """
        url = f"{self.api_base}/me/messages"
        
        message_data = {"text": message}
        
        if quick_replies:
            message_data["quick_replies"] = [
                {
                    "content_type": "text",
                    "title": reply["title"],
                    "payload": reply["payload"]
                }
                for reply in quick_replies
            ]
        
        payload = {
            "recipient": {"id": str(customer_id)},
            "message": message_data,
            "messaging_type": messaging_type
        }
        
        if tag:
            payload["tag"] = tag
            
        params = {"access_token": self.access_token}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(
                            "Facebook message sent",
                            customer_id=str(customer_id),
                            message_id=data.get("message_id"),
                            type=messaging_type
                        )
                        return {
                            "status": "success",
                            "id": data.get("message_id"),
                            "platform": "facebook"
                        }
                    else:
                        error_data = await response.text()
                        logger.error(
                            "Facebook send failed",
                            status=response.status,
                            error=error_data
                        )
                        return {
                            "status": "error",
                            "message": f"API error: {response.status}",
                            "details": error_data
                        }
        except Exception as e:
            logger.error("Facebook exception", error=str(e))
            return {"status": "error", "message": str(e)}

    async def send_action(
        self,
        customer_id: str,
        sender_action: str
    ) -> Dict[str, Any]:
        """
        Send a sender action (typing_on, typing_off, mark_seen).
        
        Args:
            customer_id: Recipient PSID
            sender_action: typing_on, typing_off, or mark_seen
        """
        url = f"{self.api_base}/me/messages"
        payload = {
            "recipient": {"id": str(customer_id)},
            "sender_action": sender_action
        }
        params = {"access_token": self.access_token}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, params=params) as response:
                    if response.status == 200:
                        return {"status": "success"}
                    else:
                        error_data = await response.text()
                        logger.warning(f"Facebook action {sender_action} failed", status=response.status, error=error_data)
                        return {"status": "error", "message": f"API error: {response.status}"}
        except Exception as e:
            logger.error(f"Facebook action {sender_action} exception", error=str(e))
            return {"status": "error", "message": str(e)}

    async def unsend_message(
        self,
        message_id: str
    ) -> Dict[str, Any]:
        """
        Unsend (delete) a message on Facebook Messenger.
        Note: This only works for outbound messages sent by the page.
        """
        # Meta Graph API for deleting a message (unsending)
        url = f"{self.api_base}/{message_id}"
        
        params = {"access_token": self.access_token}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.delete(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info("Facebook message unsent", message_id=message_id)
                        return {"status": "success", "data": data}
                    else:
                        error_data = await response.text()
                        logger.warning(
                            "Facebook unsend failed",
                            status=response.status,
                            error=error_data
                        )
                        return {"status": "error", "message": f"API error: {response.status}"}
        except Exception as e:
            logger.error("Facebook unsend exception", error=str(e))
            return {"status": "error", "message": str(e)}

    async def get_page_identity(self) -> Dict[str, Any]:
        """
        Fetch the identity of the entity associated with the access token.
        Returns: { "id": "page_id", "name": "Page Name" }
        """
        url = f"{self.api_base}/me"
        params = {"access_token": self.access_token, "fields": "id,name"}
        timeout = aiohttp.ClientTimeout(total=5)
        try:
             async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    logger.error("Failed to fetch page identity", status=response.status)
                    return {}
        except Exception as e:
            logger.error("Exception fetching page identity", error=str(e))
            return {}

    async def subscribe_app(self) -> Dict[str, Any]:
        """
        Subscribe the App to the Page's events.
        Critical for receiving webhooks.
        """
        # 1. Ensure we have the correct Facebook Page ID (not IG ID)
        identity = await self.get_page_identity()
        target_id = identity.get("id") or self.page_id
        
        logger.info("Subscribing App to Page Events", target_page_id=target_id, configured_id=self.page_id)

        url = f"{self.api_base}/{target_id}/subscribed_apps"
        params = {
            "access_token": self.access_token,
            "subscribed_fields": "messages,messaging_postbacks,messaging_optins,message_deliveries,message_reads,standby"
        }
        
        timeout = aiohttp.ClientTimeout(total=5)
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(url, params=params) as response:
                    data = await response.json()
                    if response.status == 200 and data.get("success"):
                         logger.info("✅ App subscribed to Page events successfully")
                         return {"success": True}
                    
                    logger.error("❌ Failed to subscribe app to page", error=data)
                    return {"success": False, "error": data}
        except Exception as e:
             logger.error("Exception subscribing app", error=str(e))
             return {"success": False, "error": str(e)}
    
    async def send_template(
        self,
        customer_id: UUID,
        template_type: str,
        elements: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Send a template message (e.g., generic template, button template).
        
        Args:
            customer_id: Customer UUID
            template_type: Type of template (generic, button, etc.)
            elements: Template elements
        
        Returns:
            Dict with send status
        """
        url = f"{self.api_base}/me/messages"
        
        payload = {
            "recipient": {"id": str(customer_id)},
            "message": {
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": template_type,
                        "elements": elements
                    }
                }
            }
        }
        
        params = {"access_token": self.access_token}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "status": "success",
                            "id": data.get("message_id")
                        }
                    return {"status": "error", "message": f"Status {response.status}"}
        except Exception as e:
            logger.error("Failed to send template", error=str(e))
            return {"status": "error", "message": str(e)}
    
    async def get_user_profile(self, psid: str, platform: str = "facebook") -> Dict[str, Any]:
        """
        Get Facebook/Instagram user profile information.
        
        Args:
            psid: Page-scoped ID or Instagram-scoped ID of the user
            platform: "facebook" or "instagram"
        
        Returns:
            User profile dict with name, profile_pic, etc.
        """
        # For Instagram, we can fetch name and username specifically
        fields = "first_name,last_name,profile_pic,locale,timezone,gender"
        if platform == "instagram":
             fields = "name,username,profile_pic"

        url = f"{self.api_base}/{psid}"
        params = {
            "fields": fields,
            "access_token": self.access_token
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        name = data.get('name') or f"{data.get('first_name', '')} {data.get('last_name', '')}".strip()
                        username = data.get('username')
                        logger.info(
                            "Fetched Meta Profile", 
                            psid=psid, 
                            platform=platform,
                            name=name,
                            username=username
                        )
                        return data
                    else:
                        error_text = await response.text()
                        logger.warning(
                            "Failed to fetch Meta profile", 
                            status=response.status, 
                            psid=psid, 
                            platform=platform,
                            error=error_text
                        )
                        return {}
        except Exception as e:
            logger.error("Failed to fetch user profile", error=str(e))
            return {}
    
    async def handle_webhook(self, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Process incoming Facebook webhook event.
        
        Args:
            payload: Webhook payload
        
        Returns:
            List of processed messages
        """
        messages = []
        
        try:
            for entry in payload.get("entry", []):
                for messaging_event in entry.get("messaging", []):
                    sender_id = messaging_event.get("sender", {}).get("id")
                    recipient_id = messaging_event.get("recipient", {}).get("id")
                    timestamp = messaging_event.get("timestamp")
                    
                    # Handle message
                    if "message" in messaging_event:
                        message = messaging_event["message"]
                        messages.append({
                            "platform": "facebook",
                            "sender_id": sender_id,
                            "recipient_id": recipient_id,
                            "message": message.get("text"),
                            "timestamp": timestamp,
                            "message_id": message.get("mid"),
                            "attachments": message.get("attachments", [])
                        })
                    
                    # Handle postback (button clicks)
                    elif "postback" in messaging_event:
                        postback = messaging_event["postback"]
                        messages.append({
                            "platform": "facebook",
                            "sender_id": sender_id,
                            "recipient_id": recipient_id,
                            "postback": postback.get("payload"),
                            "title": postback.get("title"),
                            "timestamp": timestamp,
                            "type": "postback"
                        })
            
            # Handle Feed changes (comments)
            for entry in payload.get("entry", []):
                changes = entry.get("changes", [])
                for change in changes:
                    if change.get("field") == "feed":
                        value = change.get("value", {})
                        if value.get("item") == "comment" and value.get("verb") == "add":
                            messages.append({
                                "platform": "facebook",
                                "type": "comment",
                                "post_id": value.get("post_id"),
                                "comment_id": value.get("comment_id"),
                                "sender_id": value.get("from", {}).get("id"),
                                "sender_name": value.get("from", {}).get("name"),
                                "message": value.get("message"),
                                "timestamp": value.get("created_time")
                            })
            
            return messages
            
        except (KeyError, IndexError) as e:
            logger.error("Invalid Facebook webhook payload", error=str(e))
            return []
    
    async def set_get_started_button(self, payload: str = "GET_STARTED") -> bool:
        """
        Configure Get Started button for new conversations.
        
        Args:
            payload: Payload to send when button is clicked
        
        Returns:
            True if successful
        """
        url = f"{self.api_base}/me/messenger_profile"
        
        data = {
            "get_started": {"payload": payload}
        }
        
        params = {"access_token": self.access_token}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data, params=params) as response:
                    return response.status == 200
        except Exception as e:
            logger.error("Failed to set get started button", error=str(e))
            return False
    
    async def set_greeting_text(self, greeting: str) -> bool:
        """
        Set greeting text shown before conversation starts.
        
        Args:
            greeting: Greeting text
        
        Returns:
            True if successful
        """
        url = f"{self.api_base}/me/messenger_profile"
        
        data = {
            "greeting": [
                {
                    "locale": "default",
                    "text": greeting
                }
            ]
        }
        
        params = {"access_token": self.access_token}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data, params=params) as response:
                    return response.status == 200
        except Exception as e:
            logger.error("Failed to set greeting", error=str(e))
            return False
    
    async def get_page_engagement(self) -> Dict[str, Any]:
        """
        Fetch page engagement metrics (followers, fans).
        Supports pages_read_engagement permission.
        """
        url = f"{self.api_base}/{self.page_id}"
        params = {
            "fields": "followers_count,fan_count,name",
            "access_token": self.access_token
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info("Fetched Page engagement metrics", page_id=self.page_id, followers=data.get("followers_count"))
                        return data
                    logger.error("Failed to fetch page engagement", status=response.status)
                    return {}
        except Exception as e:
            logger.error("Exception fetching page engagement", error=str(e))
            return {}

    async def get_feed(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Fetch the Page's feed (posts).
        Supports pages_read_engagement permission.
        """
        url = f"{self.api_base}/{self.page_id}/feed"
        params = {
            "fields": "id,message,created_time,full_picture,permalink_url",
            "limit": limit,
            "access_token": self.access_token
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("data", [])
                    logger.error("Failed to fetch page feed", status=response.status)
                    return []
        except Exception as e:
            logger.error("Exception fetching feed", error=str(e))
            return []

    async def get_comments(self, object_id: str) -> List[Dict[str, Any]]:
        """
        Fetch comments for a post or object.
        """
        url = f"{self.api_base}/{object_id}/comments"
        params = {
            "fields": "id,from,message,created_time,comment_count",
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
            logger.error("Exception fetching comments", error=str(e))
            return []

    async def reply_to_comment(self, comment_id: str, message: str) -> Dict[str, Any]:
        """
        Reply to a comment.
        Supports pages_messaging / pages_manage_metadata.
        """
        url = f"{self.api_base}/{comment_id}/comments"
        payload = {"message": message}
        params = {"access_token": self.access_token}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    error_data = await response.text()
                    logger.error("Failed to reply to comment", status=response.status, error=error_data)
                    return {"status": "error", "message": error_data}
        except Exception as e:
            logger.error("Exception replying to comment", error=str(e))
            return {"status": "error", "message": str(e)}

    async def test_connection(self) -> bool:
        """Test if Facebook connection is working."""
        url = f"{self.api_base}/me"
        params = {"access_token": self.access_token}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    return response.status == 200
        except Exception:
            return False
