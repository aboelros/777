"""
Discord Integration Service
Handles Discord bot integration for customer support.
"""

from typing import Dict, Any, Optional
import structlog
import aiohttp

logger = structlog.get_logger(__name__)


class DiscordIntegration:
    """
    Discord integration for customer support via Discord server.
    
    Features:
    - Receive messages from Discord channels
    - Send automated responses
    - Track customer conversations
    - Support ticket creation
    """
    
    def __init__(self, bot_token: str, guild_id: Optional[str] = None):
        self.bot_token = bot_token
        self.guild_id = guild_id
        self.base_url = "https://discord.com/api/v10"
        self.headers = {
            "Authorization": f"Bot {bot_token}",
            "Content-Type": "application/json"
        }
    
    async def send_message(
        self,
        channel_id: str,
        content: str,
        embed: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Send a message to a Discord channel.
        
        Args:
            channel_id: Discord channel ID
            content: Message content
            embed: Optional embed object for rich messages
            
        Returns:
            Discord API response
        """
        url = f"{self.base_url}/channels/{channel_id}/messages"
        
        payload = {"content": content}
        if embed:
            payload["embeds"] = [embed]
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=self.headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info("Discord message sent", channel_id=channel_id)
                        return result
                    else:
                        error = await response.text()
                        logger.error("Failed to send Discord message", error=error, status=response.status)
                        raise Exception(f"Discord API error: {error}")
        except Exception as e:
            logger.error("Discord send message failed", error=str(e))
            raise
    
    async def send_order_status(
        self,
        channel_id: str,
        order_number: str,
        status: str,
        customer_name: str,
        tracking_number: Optional[str] = None
    ):
        """Send order status update as rich embed."""
        
        # Status color coding
        color_map = {
            "pending": 0xFFA500,      # Orange
            "processing": 0x3498DB,    # Blue
            "shipped": 0x9B59B6,       # Purple
            "fulfilled": 0x2ECC71,     # Green
            "cancelled": 0xE74C3C      # Red
        }
        
        embed = {
            "title": f"📦 Order #{order_number} Status",
            "description": f"Status: **{status.upper()}**",
            "color": color_map.get(status, 0x95A5A6),
            "fields": [
                {"name": "Customer", "value": customer_name, "inline": True}
            ],
            "timestamp": "now",
            "footer": {"text": "AI Sales Commander Bot"}
        }
        
        if tracking_number:
            embed["fields"].append({
                "name": "Tracking Number",
                "value": f"`{tracking_number}`",
                "inline": True
            })
        
        await self.send_message(channel_id, "", embed=embed)
    
    async def get_channel_messages(
        self,
        channel_id: str,
        limit: int = 50
    ) -> list:
        """
        Get recent messages from a Discord channel.
        
        Args:
            channel_id: Discord channel ID
            limit: Number of messages to retrieve
            
        Returns:
            List of messages
        """
        url = f"{self.base_url}/channels/{channel_id}/messages?limit={limit}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        messages = await response.json()
                        return messages
                    else:
                        logger.error("Failed to get Discord messages", status=response.status)
                        return []
        except Exception as e:
            logger.error("Discord get messages failed", error=str(e))
            return []
    
    async def create_support_thread(
        self,
        channel_id: str,
        thread_name: str,
        message: str
    ) -> Optional[str]:
        """Create a support thread in Discord."""
        url = f"{self.base_url}/channels/{channel_id}/threads"
        
        payload = {
            "name": thread_name,
            "type": 11,  # Public thread
            "message": {"content": message}
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=self.headers) as response:
                    if response.status in [200, 201]:
                        thread = await response.json()
                        logger.info("Discord thread created", thread_id=thread.get("id"))
                        return thread.get("id")
                    else:
                        logger.error("Failed to create Discord thread", status=response.status)
                        return None
        except Exception as e:
            logger.error("Discord create thread failed", error=str(e))
            return None
    
    async def verify_connection(self) -> bool:
        """Verify Discord bot connection."""
        url = f"{self.base_url}/users/@me"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        bot_info = await response.json()
                        logger.info("Discord connection verified", bot_name=bot_info.get("username"))
                        return True
                    else:
                        logger.error("Discord connection failed", status=response.status)
                        return False
        except Exception as e:
            logger.error("Discord verification failed", error=str(e))
            return False


def get_discord_client(config: Dict[str, Any]) -> DiscordIntegration:
    """Factory function to create Discord client."""
    bot_token = config.get("bot_token")
    guild_id = config.get("guild_id")
    
    if not bot_token:
        raise ValueError("Discord bot_token is required")
    
    return DiscordIntegration(bot_token=bot_token, guild_id=guild_id)
