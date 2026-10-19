"""
Google Gemini AI client using direct API.
Implements function-calling pattern for autonomous actions.
Supports multiple API keys with automatic rotation for rate limit management.
"""

from typing import List, Dict, Any, Optional
from uuid import UUID
import json
import structlog
import google.generativeai as genai
from google.ai import generativelanguage as glm
from app.core.config import settings
from app.core.ai_personas import (
    get_web_assistant_prompt,
    AI_SALER_BASE_PROMPT,
    AI_SALER_CLOSING_RULES,
)
import random
import aiohttp
import tempfile
import os
import asyncio

logger = structlog.get_logger(__name__)


WEB_ASSISTANT_BEHAVIOR_RULES = """You are an AI Business Management Assistant for business owners using AI Sales Commander platform.

**YOUR ROLE:**
You help BUSINESS OWNERS manage their e-commerce business. You are NOT talking to customers - you're talking to the store owner/manager.

**COMPANY IDENTITY:**
- Platform: AI Sales Commander
- Owned by: Nexora Company
- Founder: Mahmoud Abo Elros

**LANGUAGE SUPPORT:**
- ALWAYS respond in the SAME LANGUAGE as the user's message
- Supported languages: English, Arabic (العربية), Spanish (Español), French (Français)
- Detect the language and respond accordingly
- NEVER mix languages

**YOUR CAPABILITIES - HELP BUSINESS OWNERS:**

1. **Analytics & Insights**
   - Show sales performance, revenue, trends
   - Analyze customer behavior and patterns
   - Identify top products and best customers
   - Compare time periods (today vs yesterday, this month vs last month)

2. **Order Management**
   - List recent orders and their status
   - Show pending, fulfilled, or cancelled orders
   - Track order details and customer information
   - Monitor order fulfillment

3. **Customer Communication**
   - Show unread messages from customers
   - Highlight urgent customer requests
   - Summarize customer conversations
   - Help draft responses to customers

4. **Business Reports**
   - Generate sales reports (daily, weekly, monthly)
   - Create customer analytics reports
   - Show product performance reports
   - Provide actionable business insights

5. **Integration Management**
   - Check integration status (WhatsApp, Shopify, etc.)
   - Trigger data syncs
   - Monitor integration health

**AVAILABLE FUNCTIONS (USE THESE!):**
- get_message_stats(days) - Message statistics
- get_order_stats(days) - Sales metrics  
- get_recent_orders(limit, status) - List orders
- get_recent_messages(limit, platform) - List messages
- get_unread_messages() - Unread customer messages
- get_urgent_messages() - High-priority messages
- generate_sales_report(period) - Sales report
- generate_customer_report(days) - Customer analytics
- get_top_products(days, limit) - Best sellers
- compare_periods(period_days) - Period comparison
- sync_integration(integration) - Sync data
- get_integration_status() - Integration health

**BEHAVIOR RULES:**

1. **BE PROACTIVE & INSIGHTFUL**
   - Offer business insights and recommendations
   - Suggest actions to improve sales
   - Highlight opportunities and trends
   - Provide strategic advice

2. **JUST DO IT - NO EXPLANATIONS**
   - User asks "show me sales" → Call get_order_stats() immediately
   - User asks "how to" → Give 3-5 simple steps
   - NEVER apologize or explain what you're doing
   - Just show results

3. **BE EXTREMELY SIMPLE**
   - Use 1-2 sentence responses when possible
   - No technical jargon
   - Format: Action → Result → Insight

4. **PROVIDE ACTIONABLE INSIGHTS**
   - Don't just show data - explain what it means
   - Suggest next steps
   - Highlight what needs attention

**RESPONSE EXAMPLES:**

✅ GOOD: "📊 Today's Performance:
• 23 orders ($3,450)
• ↑ 15% from yesterday
• Top product: Blue T-Shirt (8 sales)

💡 Insight: Sales spike at 2-4 PM. Consider running ads during this time."

✅ GOOD: "🔔 5 Unread Messages:
• 3 product inquiries
• 1 order status question
• 1 complaint (needs urgent attention)

⚠️ Priority: Customer #1234 waiting 2 hours for response."

✅ GOOD: "📈 This Month vs Last Month:
• Revenue: $45K → $52K (+15%)
• Orders: 340 → 390 (+14%)
• Avg Order: $132 → $133 (+1%)

🎯 Recommendation: Focus on customer retention - repeat rate is down 3%."

**NEVER:**
- Apologize or explain technical issues
- Mix languages
- Talk like you're selling to customers (you're helping the business owner!)

**ALWAYS:**
- Be direct and actionable
- Provide business insights
- Show results immediately
- Respond in the SAME language as the user
- Focus on helping the business owner succeed"""


class GeminiClient:
    """Client for interacting with Google Gemini AI with multi-key support."""

    async def _download_media(self, url: str) -> Optional[str]:
        """Download media from URL to a temporary file."""
        try:
            # Handle local URLs (if needed)
            if url.startswith("/uploads/"):
                # Construct local path - this assumes the server and media are same filesystem
                # If not, we might need to use the full URL
                from app.services.file_storage import UPLOAD_DIR
                local_path = str(UPLOAD_DIR.parent / url.lstrip("/"))
                if os.path.exists(local_path):
                    return local_path
                return None

            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=30) as response:
                    if response.status != 200:
                        logger.error(f"Failed to download media: {response.status}", url=url)
                        return None
                    
                    # Get file extension from content type if possible
                    ext = ".tmp"
                    content_type = response.headers.get("Content-Type", "")
                    if "image" in content_type:
                        ext = f".{content_type.split('/')[-1]}"
                    elif "audio" in content_type:
                        ext = ".mp3"  # Default for audio
                    
                    fd, path = tempfile.mkstemp(suffix=ext)
                    with os.fdopen(fd, 'wb') as tmp:
                        tmp.write(await response.read())
                    
                    return path
        except Exception as e:
            logger.error("Error downloading media", error=str(e), url=url)
            return None
    
    def __init__(self):
        """Initialize Gemini client with multiple API keys."""
        configured_model = settings.GEMINI_MODEL or "gemini-2.5-flash"
        if configured_model in ["gemini-1.5-flash", "gemini-3.6-flash", "gemini-1.5-pro-latest", "gemini-pro"]:
            configured_model = "gemini-2.5-flash"
        self.model_name = configured_model
        
        # Load multiple API keys
        self.api_keys = self._load_api_keys()
        self.current_key_index = 0
        self.api_key = self.api_keys[0] if self.api_keys else None
        
        if self.api_keys:
            # Configure with first key initially
            genai.configure(api_key=self.api_keys[0])
            logger.info(f"Gemini API configured with {len(self.api_keys)} API keys")
        else:
            logger.warning("No GEMINI API keys set - AI features will be limited")
        
        # Define available functions for function calling
        self.available_functions = self._define_functions()
        
        # Subscription and optimizer integration (set externally)
        self.subscription_service = None
        self.ai_optimizer = None
    
    def set_subscription_service(self, service):
        """Set subscription service for usage tracking."""
        self.subscription_service = service
    
    def set_ai_optimizer(self, optimizer):
        """Set AI optimizer for caching and optimization."""
        self.ai_optimizer = optimizer
    
    def _estimate_tokens(self, text: str) -> int:
        """Rough estimate of tokens (1 token ≈ 4 characters)."""
        return len(text) // 4
    
    async def _check_usage_limit(self, user_id: Optional[UUID]) -> bool:
        """Check if user can make AI request."""
        if not user_id or not self.subscription_service:
            return True  # No enforcement if not configured
        
        try:
            # Wrap in try/except to handle potential greenlet/async context issues
            if self.subscription_service:
                result = await self.subscription_service.check_and_enforce_limit(
                    user_id, "ai_requests"
                )
                return result.get("allowed", True)
            return True
        except Exception as e:
            logger.warning(f"Error checking usage limit: {e}")
            return True  # Allow on error to avoid blocking
    
    async def _track_usage(
        self,
        user_id: Optional[UUID],
        prompt: str,
        response: str,
        model: str = "gemini-3.6-flash"
    ):
        """Track AI usage for billing."""
        if not user_id or not self.subscription_service:
            return
        
        try:
            tokens_input = self._estimate_tokens(prompt)
            tokens_output = self._estimate_tokens(response)
            
            await self.subscription_service.track_ai_usage(
                user_id=user_id,
                tokens_input=tokens_input,
                tokens_output=tokens_output,
                model_used=model
            )
            
            logger.debug(
                "AI usage tracked",
                user_id=str(user_id),
                tokens_in=tokens_input,
                tokens_out=tokens_output
            )
        except Exception as e:
            logger.error(f"Error tracking AI usage: {e}")
    
    def _load_api_keys(self) -> List[str]:
        """Load all available API keys from settings (up to 100 keys)."""
        keys = []
        
        # Primary key
        if settings.GEMINI_API_KEY:
            keys.append(settings.GEMINI_API_KEY)
        
        # Additional keys (GEMINI_API_KEY_1 through GEMINI_API_KEY_100)
        for i in range(1, 101):
            key = getattr(settings, f'GEMINI_API_KEY_{i}', None)
            if key:
                keys.append(key)
        
        return keys
    
    def _get_next_api_key(self) -> str:
        """Get next API key using round-robin rotation."""
        if not self.api_keys:
            return None
        
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        key = self.api_keys[self.current_key_index]
        return key
    
    def _configure_next_key(self):
        """Configure Gemini with next API key in rotation."""
        next_key = self._get_next_api_key()
        if next_key:
            genai.configure(api_key=next_key)
            logger.debug(f"Rotated to API key index {self.current_key_index}")
        return next_key
    
    def _define_functions(self) -> List[Dict[str, Any]]:
        """
        Define functions that Gemini can call.
        These are presented to the model as available actions.
        """
        return [
            {
                "name": "get_message_stats",
                "description": "Get statistics about customer messages (total, unread, by platform)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "days": {
                            "type": "integer",
                            "description": "Number of days to look back (default: 7)"
                        }
                    }
                }
            },
            {
                "name": "get_order_stats",
                "description": "Get order statistics and sales metrics",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "days": {
                            "type": "integer",
                            "description": "Number of days to analyze (1 for today, 7 for week, 30 for month)"
                        }
                    }
                }
            },
            {
                "name": "get_recent_orders",
                "description": "Get list of recent orders with details",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of orders to return (default: 10)"
                        },
                        "status": {
                            "type": "string",
                            "enum": ["pending", "processing", "fulfilled", "cancelled"],
                            "description": "Filter by order status (optional)"
                        }
                    }
                }
            },
            {
                "name": "get_recent_messages",
                "description": "Get list of recent customer messages",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of messages to return (default: 20)"
                        },
                        "platform": {
                            "type": "string",
                            "enum": ["whatsapp", "instagram", "facebook", "telegram"],
                            "description": "Filter by platform (optional)"
                        }
                    }
                }
            },
            {
                "name": "get_unread_messages",
                "description": "Get all unread customer messages",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "get_urgent_messages",
                "description": "Get urgent/high-priority messages that need immediate attention",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "generate_sales_report",
                "description": "Generate a comprehensive sales report",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "period": {
                            "type": "string",
                            "enum": ["day", "week", "month"],
                            "description": "Time period for the report"
                        },
                        "days": {
                            "type": "integer",
                            "description": "Custom number of days (optional, overrides period)"
                        }
                    },
                    "required": ["period"]
                }
            },
            {
                "name": "generate_customer_report",
                "description": "Generate customer analytics report",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "days": {
                            "type": "integer",
                            "description": "Number of days to analyze (default: 30)"
                        }
                    }
                }
            },
            {
                "name": "get_top_products",
                "description": "Get top selling products",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "days": {
                            "type": "integer",
                            "description": "Period to analyze (default: 30)"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Number of products to return (default: 10)"
                        }
                    }
                }
            },
            {
                "name": "compare_periods",
                "description": "Compare current period with previous period (sales, orders, etc.)",
                "parameters": {
                    "type": "object",
                    "properties": {
                         "period_days": {
                            "type": "integer",
                            "description": "Number of days in each period (default: 7)"
                        }
                    }
                }
            },
            {
                "name": "create_order",
                "description": "Create a new order for a customer. Collect shipping address, name, and phone before creating.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "string",
                            "description": "The customer's unique identifier (UUID)"
                        },
                        "items": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "product_id": {"type": "string"},
                                    "product_name": {"type": "string"},
                                    "quantity": {"type": "integer"},
                                    "price": {"type": "number"}
                                },
                                "required": ["product_name", "quantity", "price"]
                            },
                            "description": "List of items to order"
                        },
                        "shipping_address": {
                            "type": "string",
                            "description": "Full shipping address (street, city, country)"
                        },
                        "customer_name": {
                            "type": "string",
                            "description": "Customer's full name"
                        },
                        "customer_phone": {
                            "type": "string",
                            "description": "Customer's phone number"
                        },
                        "customer_email": {
                            "type": "string",
                            "description": "Customer's email address (optional)"
                        },
                        "notes": {
                            "type": "string",
                            "description": "Order notes or special instructions"
                        }
                    },
                    "required": ["customer_id", "items", "shipping_address", "customer_name", "customer_phone"]
                }
            },
            {
                "name": "track_order",
                "description": "Check the status of an order. If order_id is not provided, it will check the customer's most recent order.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "order_id": {
                            "type": "string",
                            "description": "Order ID or Order Number. Optional - omit to track latest order."
                        }
                    }
                }
            },
            {
                "name": "sync_integration",
                "description": "Trigger manual sync for an integration (Shopify, WhatsApp, etc.)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "integration": {
                            "type": "string",
                            "enum": ["shopify", "whatsapp", "instagram", "facebook", "telegram"],
                            "description": "Which integration to sync"
                        }
                    },
                    "required": ["integration"]
                }
            },
            {
                "name": "get_integration_status",
                "description": "Get status of all connected integrations",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "analyze_message_sentiment",
                "description": "Analyze sentiment and urgency of a specific message",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "message_id": {
                            "type": "string",
                            "description": "ID of the message to analyze"
                        }
                    },
                    "required": ["message_id"]
                }
            },
            {
                "name": "send_message",
                "description": "Send a message to a customer via their preferred channel",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "string",
                            "description": "The customer's unique identifier"
                        },
                        "message": {
                            "type": "string",
                            "description": "The message content to send"
                        },
                        "channel": {
                            "type": "string",
                            "enum": ["whatsapp", "telegram", "sms", "instagram", "facebook"],
                            "description": "Communication channel to use"
                        }
                    },
                    "required": ["customer_id", "message", "channel"]
                }
            },
            {
                "name": "update_order_status",
                "description": "Update the status of an order",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "order_id": {
                            "type": "string",
                            "description": "The order's unique identifier"
                        },
                        "status": {
                            "type": "string",
                            "enum": ["pending", "processing", "fulfilled", "cancelled", "refunded"],
                            "description": "New status for the order"
                        },
                        "note": {
                            "type": "string",
                            "description": "Optional note about the status change"
                        }
                    },
                    "required": ["order_id", "status"]
                }
            },
            {
                "name": "fetch_order_details",
                "description": "Retrieve detailed information about an order",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "order_id": {
                            "type": "string",
                            "description": "The order's unique identifier"
                        }
                    },
                    "required": ["order_id"]
                }
            },
            {
                "name": "create_support_ticket",
                "description": "Create a support ticket for complex issues",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "string",
                            "description": "The customer's unique identifier"
                        },
                        "subject": {
                            "type": "string",
                            "description": "Ticket subject/title"
                        },
                        "description": {
                            "type": "string",
                            "description": "Detailed description of the issue"
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["low", "medium", "high", "urgent"],
                            "description": "Ticket priority level"
                        }
                    },
                    "required": ["customer_id", "subject", "description"]
                }
            },
            {
                "name": "schedule_followup",
                "description": "Schedule an automated follow-up message",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "string",
                            "description": "The customer's unique identifier"
                        },
                        "message": {
                            "type": "string",
                            "description": "The follow-up message content"
                        },
                        "delay_hours": {
                            "type": "integer",
                            "description": "Hours to wait before sending follow-up"
                        },
                        "channel": {
                            "type": "string",
                            "enum": ["whatsapp", "telegram", "sms", "instagram", "facebook"],
                            "description": "Communication channel to use"
                        }
                    },
                    "required": ["customer_id", "message", "delay_hours", "channel"]
                }
            },
            {
                "name": "generate_report",
                "description": "Generate analytics report for sales, orders, or customer data",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "report_type": {
                            "type": "string",
                            "enum": ["sales", "orders", "customers", "performance", "roi"],
                            "description": "Type of report to generate"
                        },
                        "date_range": {
                            "type": "string",
                            "description": "Date range for the report (e.g., 'last_7_days', 'last_month')"
                        },
                        "metrics": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Specific metrics to include"
                        }
                    },
                    "required": ["report_type", "date_range"]
                }
            },
            {
                "name": "sync_social_media",
                "description": "Sync and fetch messages from social media platforms",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "platforms": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": ["instagram", "facebook", "whatsapp", "telegram"]
                            },
                            "description": "Social media platforms to sync"
                        }
                    },
                    "required": ["platforms"]
                }
            },
            {
                "name": "check_inventory",
                "description": "Check product inventory and details",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Product name or search term"
                        },
                        "product_id": {
                            "type": "string",
                            "description": "Specific product ID (optional)"
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "analyze_customer_sentiment",
                "description": "Analyze customer sentiment from conversations",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "string",
                            "description": "The customer's unique identifier"
                        },
                        "messages": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Recent messages to analyze"
                        }
                    },
                    "required": ["customer_id", "messages"]
                }
            },
            {
                "name": "calculate_shipping_and_tax",
                "description": "Calculate shipping fees and estimated taxes for an order based on destination and value.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "destination": {
                            "type": "string",
                            "description": "The destination address, city, or country."
                        },
                        "items_total": {
                            "type": "number",
                            "description": "The subtotal of items in the order."
                        },
                        "currency": {
                            "type": "string",
                            "description": "Currency code (default: USD)"
                        }
                    },
                    "required": ["destination", "items_total"]
                }
            }
        ]
    
    async def generate_response(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        use_functions: bool = True,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        user_id: Optional[UUID] = None,
        media_url: Optional[str] = None,
        media_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a response from Gemini with optional function calling.
        
        Args:
            prompt: The input prompt/question
            context: Additional context (conversation history, order details, etc.)
            use_functions: Whether to enable function calling
            temperature: Sampling temperature (0.0 - 1.0)
            max_tokens: Maximum tokens to generate
            user_id: User ID for usage tracking (optional)
            
        Returns:
            Dictionary containing response text, function calls, and metadata
        """
        # Check usage limit before generating
        if user_id:
            can_use = await self._check_usage_limit(user_id)
            if not can_use:
                return {
                    "text": "You've reached your AI request limit for this month. Please upgrade your plan to continue using AI features.",
                    "error": "limit_exceeded",
                    "upgrade_required": True
                }
        
        try:
            # Build the full prompt with context
            full_prompt = self._build_prompt(prompt, context)
            
            # Prepare multimodal parts if media is provided
            content_parts = [full_prompt]
            
            if media_url:
                logger.info(f"Processing multimodal input: {media_type} from {media_url[:50]}...")
                tmp_path = await self._download_media(media_url)
                if tmp_path:
                    try:
                        # Upload to Gemini File API
                        # Configure API key first (since generate_response doesn't do it before this point)
                        genai.configure(api_key=self.api_keys[self.current_key_index])
                        
                        media_file = genai.upload_file(path=tmp_path)
                        content_parts.append(media_file)
                        
                        # Add a hint about the media to help the model focus
                        if media_type == "image":
                            content_parts.append("\n[This is an image from the customer. Please analyze it and respond.]")
                        elif media_type in ["audio", "voice", "voice_record"]:
                            content_parts.append("\n[This is a voice message from the customer. Please transcribe and respond to it.]")
                        elif media_type == "video":
                            content_parts.append("\n[This is a video from the customer. Please analyze it and respond.]")
                            
                    except Exception as media_err:
                        logger.error("Failed to upload media to Gemini", error=str(media_err))
                        content_parts.append(f"\n[Error processing customer media: {media_type}]")
                    finally:
                        # Cleanup temp file (only if we created a temporary one)
                        if tmp_path and os.path.exists(tmp_path) and not media_url.startswith("/uploads/"):
                            try:
                                os.remove(tmp_path)
                            except: pass
                else:
                    logger.warning(f"Could not download or find media for multimodal processing: {media_url}")
                    content_parts.append(f"\n[Note: Customer sent {media_type} but it could not be retrieved.]")

            # Prepare generation config
            generation_config = {
                "temperature": temperature or settings.GEMINI_TEMPERATURE,
                "max_output_tokens": max_tokens or settings.GEMINI_MAX_TOKENS,
                "top_p": 0.95,
                "top_k": 40
            }
            
            # Use model from settings (allows user to switch between 1.5-flash, 2.0-flash, etc.)
            model_name = settings.GEMINI_MODEL or "gemini-flash-latest"
            
            # Initialize tools variable
            tools = None

            # Initialize model with tools if enabled
            try:
                if use_functions:

                    # Filter functions to only essential ones to avoid schema errors
                    essential_tools = [
                        "check_inventory", 
                        "create_order", 
                        "track_order", 
                        "fetch_order_details",
                        "schedule_followup",
                        "create_support_ticket",
                        # "update_order_status", # Disabled for security (Admin only)
                        "calculate_shipping_and_tax"
                    ]
                    
                    filtered_functions = [
                        f for f in self.available_functions 
                        if f["name"] in essential_tools
                    ]
                    
                    logger.info("Initializing model with essential tools", 
                                count=len(filtered_functions), 
                                tools=[f["name"] for f in filtered_functions])
                    
                    # Convert function dicts to proper genai format
                    # The SDK needs protos-style declarations, not raw JSON dicts
                    try:
                        def _convert_schema_to_proto(schema_dict):
                            """Recursively convert JSON schema dict to genai.protos.Schema"""
                            type_str = schema_dict.get("type", "STRING").upper()
                            
                            type_map = {
                                "STRING": glm.Type.STRING,
                                "INTEGER": glm.Type.INTEGER,
                                "NUMBER": glm.Type.NUMBER,
                                "BOOLEAN": glm.Type.BOOLEAN,
                                "ARRAY": glm.Type.ARRAY,
                                "OBJECT": glm.Type.OBJECT,
                            }
                            gemini_type = type_map.get(type_str, glm.Type.STRING)
                            
                            # Base kwargs
                            schema_kwargs = {
                                "type_": gemini_type,
                                "description": schema_dict.get("description", ""),
                            }
                            
                            # Hande Enum
                            if "enum" in schema_dict:
                                schema_kwargs["enum"] = schema_dict["enum"]
                                
                            # Handle Array items
                            if gemini_type == glm.Type.ARRAY and "items" in schema_dict:
                                schema_kwargs["items"] = _convert_schema_to_proto(schema_dict["items"])
                                
                            # Handle Object properties
                            if gemini_type == glm.Type.OBJECT and "properties" in schema_dict:
                                props = {}
                                for k, v in schema_dict["properties"].items():
                                    props[k] = _convert_schema_to_proto(v)
                                schema_kwargs["properties"] = props
                                if "required" in schema_dict:
                                    schema_kwargs["required"] = schema_dict["required"]

                            return glm.Schema(**schema_kwargs)

                        tool_declarations = []
                        for func in filtered_functions:
                            # Build the top-level parameters schema (always an OBJECT)
                            params_dict = func.get("parameters", {})
                            # Ensure the top-level type is OBJECT
                            if params_dict.get("type", "").upper() != "OBJECT":
                                params_dict["type"] = "OBJECT"
                                
                            proto_schema = _convert_schema_to_proto(params_dict)
                            
                            func_decl = glm.FunctionDeclaration(
                                name=func["name"],
                                description=func.get("description", ""),
                                parameters=proto_schema
                            )
                            tool_declarations.append(func_decl)
                        
                        # The SDK handles a list of FunctionDeclarations directly
                        tools = tool_declarations
                        
                        model = genai.GenerativeModel(
                            model_name=model_name,
                            generation_config=generation_config,
                            tools=tools
                        )
                        logger.info("✅ Model initialized with tools successfully")
                        
                    except Exception as proto_err:
                        logger.error("Failed to build tool declarations", error=repr(proto_err))
                        import traceback
                        traceback.print_exc()
                        # Fall back to no-tools model
                        model = genai.GenerativeModel(
                            model_name=model_name,
                            generation_config=generation_config
                        )
                else:
                    model = genai.GenerativeModel(
                        model_name=model_name,
                        generation_config=generation_config
                    )
            except Exception as e:
                logger.error("Failed to initialize model with tools, falling back to text-only", error=str(e))
                # Fallback to text-only model
                model = genai.GenerativeModel(
                    model_name=model_name,
                    generation_config=generation_config
                )
            
            # Generate response with automatic key rotation on rate limit
            max_retries = len(self.api_keys) if self.api_keys else 1
            last_error = None
            
            for attempt in range(max_retries):
                try:
                    logger.info(
                        "Generating Gemini response", 
                        prompt_length=len(full_prompt), 
                        model=model_name,
                        attempt=attempt + 1,
                        total_keys=len(self.api_keys)
                    )
                    
                    response = model.generate_content(content_parts)
                    
                    # Parse response
                    result = self._parse_response(response)
                    
                    # Track usage for billing
                    if user_id:
                        await self._track_usage(
                            user_id=user_id,
                            prompt=full_prompt,
                            response=result.get("text", ""),
                            model=model_name
                        )
                    
                    logger.info(
                        "Gemini response generated successfully",
                        tokens_used=result.get("tokens_used"),
                        has_function_calls=bool(result.get("function_calls")),
                        function_names=[fc["name"] for fc in result.get("function_calls", [])],
                        key_index=self.current_key_index
                    )
                    
                    return result
                    
                except Exception as attempt_error:
                    last_error = attempt_error
                    error_msg = str(attempt_error).lower()
                    
                    # Check if it's a rate limit error
                    if "rate limit" in error_msg or "quota" in error_msg or "429" in error_msg:
                        logger.warning(
                            f"Rate limit hit on key {self.current_key_index}",
                            model=model_name,
                            attempt=attempt + 1
                        )
                        
                        # KEY ROTATION STRATEGY:
                        # 1. Try to rotate keys first while keeping the same model (e.g. gemini-3.6)
                        # 2. Only fallback to a cheaper model if we are running out of keys/retries
                        
                        # Rotate to next API key
                        if attempt < max_retries - 1:
                            self._configure_next_key()
                            
                            # Check if we should fallback to cheaper model on the LAST few attempts
                            # e.g. if we have 10 keys, try 7 keys with 2.0, then fallback for the last 3
                            should_fallback = False
                            if "gemini-3.6" in model_name and attempt > (max_retries - 3):
                                should_fallback = True
                                logger.warning("⚠️ Gemini 2.0 failing on multiple keys. Fallback to gemini-flash-latest enabled.")
                                model_name = "gemini-flash-latest"

                            # Recreate model with new key (and potentially new model)
                            try:
                                if use_functions and tools:
                                    model = genai.GenerativeModel(
                                        model_name=model_name,
                                        generation_config=generation_config,
                                        tools=tools
                                    )
                                else:
                                    model = genai.GenerativeModel(
                                        model_name=model_name,
                                        generation_config=generation_config
                                    )
                            except Exception as e:
                                # Fallback if tool recreation fails
                                model = genai.GenerativeModel(
                                    model_name=model_name,
                                    generation_config=generation_config
                                )
                            continue
                    
                    # Check for empty response error
                    elif "model output must contain either output text or tool calls" in error_msg:
                        logger.warning("Gemini returned empty response, retrying...")
                        continue

                    elif "not found" in error_msg or "404" in error_msg:
                        candidate_models = ["gemini-2.5-flash", "gemini-flash-latest", "gemini-2.5-pro"]
                        fallback_success = False
                        for cand in candidate_models:
                            if cand == model_name:
                                continue
                            logger.warning(f"Model {model_name} not found (404), retrying with {cand}")
                            model_name = cand
                            try:
                                if use_functions and tools:
                                    model = genai.GenerativeModel(model_name=model_name, generation_config=generation_config, tools=tools)
                                else:
                                    model = genai.GenerativeModel(model_name=model_name, generation_config=generation_config)
                            except Exception:
                                model = genai.GenerativeModel(model_name=model_name, generation_config=generation_config)
                            try:
                                response = model.generate_content(content_parts)
                                result = self._parse_response(response)
                                if user_id:
                                    await self._track_usage(
                                        user_id=user_id,
                                        prompt=full_prompt,
                                        response=result.get("text", ""),
                                        model=model_name
                                    )
                                logger.info("Gemini fallback model succeeded", model=model_name)
                                return result
                            except Exception as cand_err:
                                logger.warning(f"Fallback candidate {cand} failed: {cand_err}")
                                last_error = cand_err
                                continue
                        raise last_error or attempt_error
                        
                    else:
                        # Not a recoverable error, raise immediately
                        raise

            
            # All retries exhausted
            import traceback
            error_details = traceback.format_exc()
            logger.error(
                "All API keys exhausted or Gemini generation failed", 
                error=str(last_error), 
                error_type=type(last_error).__name__,
                attempts=max_retries,
                traceback=error_details
            )
            
            # Return fallback response instead of crashing
            return {
                "text": "I apologize, but I'm experiencing technical difficulties connecting to my brain. Please try again in a moment.",
                "function_calls": [],
                "tokens_used": 0,
                "cost": 0.0,
                "model": model_name,
                "error": str(last_error)
            }
            
        except Exception as e:
            # Catch any other unexpected errors
            import traceback
            error_details = traceback.format_exc()
            logger.error("Unexpected error in generate_response", error=str(e), traceback=error_details)
            
            return {
                "text": "I encountered an unexpected error. Please contact support.",
                "function_calls": [],
                "tokens_used": 0,
                "cost": 0.0,
                "model": model_name,
                "error": str(e)
            }
    
    def _build_prompt(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        persona = (context or {}).get("persona", "web_assistant")
        persona_detail = (context or {}).get("persona_detail")

        if persona == "ai_saler":
            language_name = (context or {}).get("language_name", "English")
            base_prompt = AI_SALER_BASE_PROMPT.format(language_name=language_name)
            system_instructions = f"{base_prompt}\n\n{AI_SALER_CLOSING_RULES}"
        elif persona == "custom":
            # Custom persona - no system instructions, full control to caller
            system_instructions = ""
        else:
            # Default to AI Sales Assistant persona
            assistant_intro = get_web_assistant_prompt()
            system_instructions = f"{assistant_intro}\n\n{WEB_ASSISTANT_BEHAVIOR_RULES}"

        if persona_detail and persona == "ai_saler":
            system_instructions = f"{system_instructions}\n\n{persona_detail}"

        system_instructions += "\n"

        context = context or {}

        context_str = ""
        if context:
            context_str = "\n\nContext:\n"

            if persona == "ai_saler" and context.get("custom_instructions"):
                context_str += "\n**BRAND INSTRUCTIONS (FOLLOW PRECISELY):**\n"
                for instruction in context["custom_instructions"]:
                    context_str += (
                        f"- (Priority {instruction.get('priority', 0)}) "
                        f"[{', '.join(instruction.get('platforms') or ['all'])}] "
                        f"{instruction.get('instruction')}\n"
                    )

            if context.get("intent"):
                context_str += "\nConversation state:\n"
                context_str += f"- Intent: {context['intent'].get('primary_intent')}\n"
                context_str += f"- Urgency: {context['intent'].get('urgency')}\n"
                context_str += f"- Sentiment: {context['intent'].get('sentiment')}\n"

            if context.get("channel"):
                context_str += f"- Channel: {context['channel']}\n"

            if context.get("current_message"):
                context_str += f"- Latest customer message: {context['current_message']}\n"

            if context.get("customer_profile"):
                profile = context["customer_profile"]
                context_str += "\nCustomer profile:\n"
                context_str += f"- Name: {profile.get('name')}\n"
                context_str += f"- Preferred language: {profile.get('preferred_language')}\n"
                context_str += f"- Communication style: {profile.get('communication_style')}\n"

            if context.get("product_catalog"):
                context_str += "\nProduct highlights:\n"
                for product in context["product_catalog"][:10]:
                    context_str += (
                        f"- {product.get('name')} (${product.get('price')} {product.get('currency')}): "
                        f"{product.get('description')}\n"
                    )

            if context.get("conversation_history"):
                context_str += "\nRecent conversation:\n"
                for msg in context["conversation_history"][-5:]:
                    role = msg.get("role")
                    content = msg.get("content")
                    context_str += f"- {role}: {content}\n"

            if context.get("order"):
                order = context["order"]
                context_str += "\nOrder details:\n"
                context_str += f"- Order ID: {order.get('id')}\n"
                context_str += f"- Status: {order.get('status')}\n"
                context_str += f"- Total: {order.get('currency')} {order.get('total')}\n"

        full_prompt = f"""{system_instructions}
{context_str}

---
CUSTOMER MESSAGE:
{prompt}
---

YOUR RESPONSE (as the Sales Agent):"""
        return full_prompt
    
    def _parse_response(self, response) -> Dict[str, Any]:
        """Parse Gemini response including function calls."""
        
        result = {
            "text": "",
            "function_calls": [],
            "tokens_used": 0,
            "cost": 0.0,
            "model": self.model_name
        }
        
        # Extract text response
        try:
            if hasattr(response, 'text') and response.text:
                result["text"] = response.text
        except Exception:
            # response.text raises error if blocked or empty
            pass

        if not result["text"] and hasattr(response, 'candidates') and response.candidates:
            # Try to extract text from candidates if direct text fails
            candidate = response.candidates[0]
            
            # Check for safety finish reason
            if hasattr(candidate, 'finish_reason') and str(candidate.finish_reason) == "SAFETY":
                 result["text"] = "I cannot answer that due to safety guidelines."
                 return result

            if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                for part in candidate.content.parts:
                    if hasattr(part, 'text') and part.text:
                        result["text"] = part.text
                        break
        
        # Fallback: If no text response but we have function calls, provide a default response
        if not result["text"] and result["function_calls"]:
            result["text"] = "I'm processing your request and executing the necessary actions."
        
        # Ultimate fallback: Always provide some response
        if not result["text"]:
            result["text"] = "I understand your request. How can I help you further?"
        
        # Extract function calls
        if hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            
            if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                for part in candidate.content.parts:
                    if hasattr(part, 'function_call'):
                        func_call = part.function_call
                        # Handle None args properly
                        params = {}
                        if func_call.args:
                            try:
                                params = dict(func_call.args)
                            except (TypeError, ValueError):
                                params = {}
                        
                        raw_name = getattr(func_call, 'name', None)
                        func_name = raw_name.strip() if raw_name and isinstance(raw_name, str) else None
                        
                        if not func_name and hasattr(func_call, 'name'):
                             # Sometimes name is a property that needs to be accessed differently or it's in the part text
                             func_name = str(func_call.name).strip()

                        if func_name:
                            result["function_calls"].append({
                                "name": func_name,
                                "parameters": params
                            })
                        else:
                            # Try to extract from parts if name is missing but it's a call
                            # Some models might put the name in the text part before the function call
                            logger.warning(
                                "Gemini returned function call with missing/invalid name", 
                                raw_name=str(raw_name),
                                raw_args=str(func_call.args) if hasattr(func_call, 'args') else "No args"
                            )
        
        # Calculate token usage (approximate)
        if hasattr(response, 'usage_metadata'):
            usage = response.usage_metadata
            result["tokens_used"] = usage.total_token_count
            
            # Rough cost estimation (update with actual Gemini pricing)
            # Example: $0.00025 per 1K tokens for Pro model
            result["cost"] = (result["tokens_used"] / 1000) * 0.00025
        
        return result
    
    async def generate_content(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Simplified method to generate text content from Gemini.
        
        Args:
            prompt: The input prompt
            context: Optional context dictionary
            temperature: Sampling temperature (0.0 - 1.0)
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text response as string
        """
        result = await self.generate_response(
            prompt=prompt,
            context=context,
            use_functions=False,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return result.get("text", "")
    
    async def generate_sales_reply(
        self,
        customer_message: str,
        order_context: Optional[Dict[str, Any]] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Specialized method for generating sales replies.
        
        Args:
            customer_message: The customer's message
            order_context: Related order information
            conversation_history: Previous messages in the conversation
            
        Returns:
            Generated reply with optional function calls
        """
        context = {
            "conversation_history": conversation_history or [],
            "order": order_context
        }
        
        return await self.generate_response(
            prompt=customer_message,
            context=context,
            use_functions=True
        )
    
    async def analyze_sentiment(self, message: str) -> Dict[str, Any]:
        """
        Analyze sentiment of a customer message.
        
        Args:
            message: The message to analyze
            
        Returns:
            Sentiment analysis results
        """
        prompt = f"""Analyze the sentiment of this customer message and provide:
1. Overall sentiment (positive, neutral, negative)
2. Urgency level (low, medium, high, urgent)
3. Key concerns or topics
4. Recommended response tone

Message: {message}

Respond in JSON format."""
        
        response = await self.generate_response(
            prompt=prompt,
            use_functions=False,
            temperature=0.3  # Lower temperature for analysis
        )
        
        try:
            # Attempt to parse JSON response
            analysis = json.loads(response["text"])
            return analysis
        except json.JSONDecodeError:
            return {
                "sentiment": "neutral",
                "urgency": "medium",
                "concerns": [],
                "raw_analysis": response["text"]
            }
    
    async def generate_product_recommendation(
        self,
        customer_profile: Dict[str, Any],
        purchase_history: List[Dict[str, Any]],
        available_products: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Generate personalized product recommendations.
        
        Args:
            customer_profile: Customer information and preferences
            purchase_history: Previous purchases
            available_products: Current product catalog
            
        Returns:
            List of recommended products with explanations
        """
        prompt = f"""Generate product recommendations based on:

Customer Profile:
{json.dumps(customer_profile, indent=2)}

Purchase History:
{json.dumps(purchase_history[-10:], indent=2)}

Available Products:
{json.dumps(available_products[:20], indent=2)}

Provide top 5 recommendations with:
1. Product name and ID
2. Reason for recommendation
3. Confidence score (0-1)

Respond in JSON format as array of recommendations."""
        
        response = await self.generate_response(
            prompt=prompt,
            use_functions=False,
            temperature=0.6
        )
        
        try:
            recommendations = json.loads(response["text"])
            return recommendations
        except json.JSONDecodeError:
            logger.warning("Failed to parse recommendations", response=response["text"])
            return []


    async def transcribe_audio(self, audio_path: str) -> str:
        """
        Transcribe audio file using Gemini 1.5 Flash.
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            Transcribed text
        """
        try:
            # Configure API key
            if not self.api_keys:
                self._load_api_keys()
            
            if not self.api_keys:
                logger.error("No API keys available for transcription")
                return ""
                
            genai.configure(api_key=self.api_keys[self.current_key_index])
            
            # Upload file to Gemini
            logger.info(f"Uploading audio file: {audio_path}")
            
            # Use genai.upload_file (synchronous, but fast enough for small files)
            # Note: In a real async app, we might want to run this in a thread pool
            audio_file = genai.upload_file(path=audio_path)
            
            # Use Gemini Flash Latest for fast transcription
            model = genai.GenerativeModel("gemini-flash-latest")
            
            response = model.generate_content([
                "Please transcribe this audio file exactly as spoken. Return ONLY the text.",
                audio_file
            ])
            
            text = response.text.strip()
            logger.info("Audio transcribed", text_preview=text[:50])
            
            return text
            
        except Exception as e:
            logger.error("Transcription failed", error=str(e))
            # Rotate key and retry once
            try:
                self._configure_next_key()
                genai.configure(api_key=self.api_keys[self.current_key_index])
                
                audio_file = genai.upload_file(path=audio_path)
                model = genai.GenerativeModel("gemini-flash-latest")
                response = model.generate_content([
                    "Please transcribe this audio file exactly as spoken. Return ONLY the text.",
                    audio_file
                ])
                return response.text.strip()
            except Exception as retry_e:
                logger.error("Retry transcription failed", error=str(retry_e))
                return ""

    async def analyze_image(self, image_path: str, prompt: str = "Describe this image in detail.") -> str:
        """
        Analyze image using Gemini 1.5 Flash.
        
        Args:
            image_path: Path to the image file
            prompt: Question or instruction about the image
            
        Returns:
            Image description/analysis
        """
        # Try all available keys
        max_retries = len(self.api_keys) if self.api_keys else 1
        
        for attempt in range(max_retries):
            try:
                # Configure API key
                if not self.api_keys:
                    logger.error("No API keys available for image analysis")
                    return ""
                    
                genai.configure(api_key=self.api_keys[self.current_key_index])
                
                # Upload file to Gemini
                # logger.info(f"Uploading image file: {image_path}")
                image_file = genai.upload_file(path=image_path)
                
                # Use configured model
                model_name = settings.GEMINI_MODEL or "gemini-flash-latest"
                model = genai.GenerativeModel(model_name)
                
                response = model.generate_content([
                    prompt,
                    image_file
                ])
                
                text = response.text.strip()
                logger.info("Image analyzed", text_preview=text[:50], key_index=self.current_key_index)
                
                return text
                
            except Exception as e:
                logger.warning(
                    f"Image analysis failed on key {self.current_key_index}", 
                    error=str(e),
                    attempt=attempt + 1,
                    max_retries=max_retries
                )
                
                # Rotate key for next attempt
                self._configure_next_key()
                
        logger.error("All API keys exhausted for image analysis")
        return ""


# Global client instance
gemini_client = GeminiClient()
