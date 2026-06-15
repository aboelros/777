"""
Enhanced AI Service with conversation memory, business context, and intelligent features.
Handles order extraction, customer profiling, and context-aware responses.
"""

from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_, or_
import structlog
import re
import json

from app.services.gemini_client import GeminiClient
from app.db.models import (
    ConversationHistory, BusinessContext, CustomerProfile,
    SocialMediaPost, SocialMediaComment, Message, Order,
    Product, MessageDirection, OrderStatus
)

logger = structlog.get_logger(__name__)


class EnhancedAIService:
    """
    Enhanced AI service with memory, context, and intelligent automation.
    """
    
    def __init__(self, db: AsyncSession, project_id: UUID):
        self.db = db
        self.project_id = project_id
        self.gemini_client = GeminiClient()
    
    async def get_conversation_history(
        self, 
        customer_id: str, 
        platform: str,
        limit: int = 20
    ) -> List[ConversationHistory]:
        """
        Retrieve conversation history for a customer.
        Returns recent conversations for context.
        """
        result = await self.db.execute(
            select(ConversationHistory)
            .where(
                and_(
                    ConversationHistory.project_id == self.project_id,
                    ConversationHistory.customer_id == customer_id,
                    ConversationHistory.platform == platform
                )
            )
            .order_by(desc(ConversationHistory.created_at))
            .limit(limit)
        )
        return list(reversed(result.scalars().all()))  # Oldest first
    
    async def save_conversation(
        self,
        customer_id: str,
        customer_name: Optional[str],
        platform: str,
        message_content: str,
        direction: MessageDirection,
        intent: Optional[str] = None,
        sentiment: Optional[str] = None,
        entities: Optional[Dict] = None
    ) -> ConversationHistory:
        """
        Save a conversation message for future context.
        """
        # Generate AI summary for quick retrieval
        summary = await self._generate_message_summary(message_content)
        
        conversation = ConversationHistory(
            project_id=self.project_id,
            customer_id=customer_id,
            customer_name=customer_name,
            platform=platform,
            message_content=message_content,
            message_direction=direction,
            intent=intent,
            sentiment=sentiment,
            entities_extracted=entities or {},
            summary=summary
        )
        
        self.db.add(conversation)
        await self.db.commit()
        await self.db.refresh(conversation)
        
        logger.info("Conversation saved", customer_id=customer_id, platform=platform)
        return conversation
    
    async def get_customer_profile(
        self, 
        customer_id: str,
        create_if_not_exists: bool = True
    ) -> Optional[CustomerProfile]:
        """
        Get or create customer profile.
        """
        result = await self.db.execute(
            select(CustomerProfile)
            .where(
                and_(
                    CustomerProfile.project_id == self.project_id,
                    CustomerProfile.customer_id == customer_id
                )
            )
        )
        profile = result.scalar_one_or_none()
        
        if not profile and create_if_not_exists:
            profile = CustomerProfile(
                project_id=self.project_id,
                customer_id=customer_id,
                first_interaction=datetime.utcnow()
            )
            self.db.add(profile)
            await self.db.commit()
            await self.db.refresh(profile)
            logger.info("Customer profile created", customer_id=customer_id)
        
        return profile
    
    async def update_customer_profile(
        self,
        customer_id: str,
        platform: str,
        **updates
    ) -> CustomerProfile:
        """
        Update customer profile with new information.
        """
        profile = await self.get_customer_profile(customer_id)
        
        # Update interaction count and timestamp
        profile.interaction_count += 1
        profile.last_interaction = datetime.utcnow()
        
        # Update platform accounts
        if platform:
            platform_accounts = profile.platform_accounts or {}
            if platform not in platform_accounts:
                platform_accounts[platform] = customer_id
            profile.platform_accounts = platform_accounts
        
        # Apply other updates
        for key, value in updates.items():
            if hasattr(profile, key) and value is not None:
                setattr(profile, key, value)
        
        await self.db.commit()
        await self.db.refresh(profile)
        
        return profile
    
    async def get_business_context(
        self,
        context_type: Optional[str] = None,
        platform: Optional[str] = None,
        limit: int = 50
    ) -> List[BusinessContext]:
        """
        Retrieve relevant business context for AI responses.
        """
        query = select(BusinessContext).where(
            and_(
                BusinessContext.project_id == self.project_id,
                BusinessContext.is_active == True
            )
        )
        
        if context_type:
            query = query.where(BusinessContext.context_type == context_type)
        
        if platform:
            # Get context for specific platform or general context
            query = query.where(
                or_(
                    BusinessContext.active_for_platforms == [],
                    BusinessContext.active_for_platforms.contains([platform])
                )
            )
        
        query = query.order_by(
            desc(BusinessContext.relevance_score),
            desc(BusinessContext.times_used)
        ).limit(limit)
        
        result = await self.db.execute(query)
        contexts = result.scalars().all()
        
        # Update times_used for retrieved contexts
        for context in contexts:
            context.times_used += 1
            context.last_used = datetime.utcnow()
        await self.db.commit()
        
        return contexts
    
    async def extract_order_from_message(
        self,
        message_content: str,
        customer_id: str,
        platform: str
    ) -> Optional[Dict[str, Any]]:
        """
        Extract order information from customer message using AI.
        Detects: product requests, quantities, addresses, payment preferences.
        """
        # Get product catalog for matching
        products = await self._get_products()
        product_info = [
            f"{p.name} - ${p.price} - SKU: {p.sku}" 
            for p in products if p.is_active
        ]
        
        # Create AI prompt for order extraction
        prompt = f"""Analyze this customer message and extract order information.

Customer Message: "{message_content}"

Available Products:
{chr(10).join(product_info[:20])}  

Extract the following if present:
1. Product(s) requested (match with product names above)
2. Quantities
3. Delivery address
4. Special instructions
5. Payment preference
6. Urgency level

Return as JSON:
{{
    "is_order": true/false,
    "products": [{{"name": "", "quantity": 1, "matched_sku": ""}}],
    "delivery_address": "",
    "special_instructions": "",
    "payment_preference": "",
    "urgency": "normal/urgent/not_urgent",
    "confidence": 0.0-1.0
}}

If this is not an order request, set is_order to false."""

        try:
            response = await self.gemini_client.generate_content(
                prompt=prompt,
                temperature=0.3  # Lower temperature for accuracy
            )
            
            # Parse JSON response
            order_data = json.loads(self._extract_json_from_response(response))
            
            if order_data.get("is_order") and order_data.get("confidence", 0) > 0.6:
                logger.info(
                    "Order extracted from message",
                    customer_id=customer_id,
                    products=order_data.get("products")
                )
                return order_data
            
        except Exception as e:
            logger.error("Failed to extract order from message", error=str(e))
        
        return None
    
    async def create_order_from_message(
        self,
        customer_id: str,
        platform: str,
        order_data: Dict[str, Any]
    ) -> Order:
        """
        Create an order from extracted message data.
        """
        # Get customer profile
        profile = await self.get_customer_profile(customer_id)
        
        # Calculate total
        total = 0.0
        items = []
        
        for product_req in order_data.get("products", []):
            # Find product by SKU or name
            result = await self.db.execute(
                select(Product).where(
                    and_(
                        Product.project_id == self.project_id,
                        or_(
                            Product.sku == product_req.get("matched_sku"),
                            Product.name.ilike(f"%{product_req.get('name')}%")
                        )
                    )
                )
            )
            product = result.scalar_one_or_none()
            
            if product:
                quantity = product_req.get("quantity", 1)
                items.append({
                    "product_id": str(product.id),
                    "product_name": product.name,
                    "sku": product.sku,
                    "price": product.price,
                    "quantity": quantity,
                    "subtotal": product.price * quantity
                })
                total += product.price * quantity
        
        # Create order
        order = Order(
            project_id=self.project_id,
            external_id=f"SM-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            provider=platform,
            status=OrderStatus.PENDING.value,
            customer={
                "id": customer_id,
                "name": profile.name if profile else "",
                "email": profile.email if profile else "",
                "phone": profile.phone if profile else "",
                "platform": platform
            },
            items=items,
            total=total,
            currency="USD",
            order_date=datetime.utcnow(),
            extra_data={
                "source": "social_media_message",
                "delivery_address": order_data.get("delivery_address"),
                "special_instructions": order_data.get("special_instructions"),
                "urgency": order_data.get("urgency")
            },
            tags=["social_media", platform, "ai_created"]
        )
        
        self.db.add(order)
        await self.db.commit()
        await self.db.refresh(order)
        
        # Update customer profile
        if profile:
            profile.total_orders += 1
            profile.total_spent += total
            await self.db.commit()
        
        logger.info("Order created from message", order_id=str(order.id), total=total)
        return order
    
    async def generate_context_aware_response(
        self,
        customer_message: str,
        customer_id: str,
        platform: str,
        order_id: Optional[UUID] = None,
        persona: str = "web_assistant"
    ) -> Dict[str, Any]:
        """
        Generate AI response with full context awareness.
        Includes: conversation history, customer profile, business context.
        """
        # Get conversation history
        history = await self.get_conversation_history(customer_id, platform, limit=10)
        
        # Get customer profile
        profile = await self.get_customer_profile(customer_id)
        
        # Get business context
        business_context = await self.get_business_context(platform=platform, limit=20)
        
        # Get order details if provided
        order_info = None
        if order_id:
            result = await self.db.execute(
                select(Order).where(Order.id == order_id)
            )
            order = result.scalar_one_or_none()
            if order:
                order_info = {
                    "id": order.external_id,
                    "status": order.status,
                    "total": order.total,
                    "items": order.items,
                    "order_date": order.order_date.isoformat() if order.order_date else None
                }
        
        # Build context-rich prompt
        context_prompt = self._build_contextual_prompt(
            customer_message=customer_message,
            history=history,
            profile=profile,
            business_context=business_context,
            order_info=order_info,
            platform=platform
        )
        
        # Generate response
        response = await self.gemini_client.generate_content(
            prompt=context_prompt,
            temperature=0.8,
            context={"persona": persona}
        )
        
        # Analyze sentiment and intent
        analysis = await self._analyze_message(customer_message)
        
        # Save conversation
        await self.save_conversation(
            customer_id=customer_id,
            customer_name=profile.name if profile else None,
            platform=platform,
            message_content=customer_message,
            direction=MessageDirection.INBOUND,
            intent=analysis.get("intent"),
            sentiment=analysis.get("sentiment"),
            entities=analysis.get("entities")
        )
        
        await self.save_conversation(
            customer_id=customer_id,
            customer_name=profile.name if profile else None,
            platform=platform,
            message_content=response,
            direction=MessageDirection.OUTBOUND
        )
        
        return {
            "response": response,
            "intent": analysis.get("intent"),
            "sentiment": analysis.get("sentiment"),
            "context_used": {
                "history_messages": len(history),
                "business_contexts": len(business_context),
                "customer_profile": profile is not None,
                "order_context": order_info is not None
            }
        }
    
    def _build_contextual_prompt(
        self,
        customer_message: str,
        history: List[ConversationHistory],
        profile: Optional[CustomerProfile],
        business_context: List[BusinessContext],
        order_info: Optional[Dict],
        platform: str
    ) -> str:
        """
        Build a comprehensive contextual prompt for AI.
        """
        prompt_parts = [
            "You are an intelligent AI assistant for a business. Respond naturally and helpfully.",
            f"\nCurrent Platform: {platform.upper()}",
        ]
        
        # Add business context
        if business_context:
            prompt_parts.append("\n## Business Knowledge:")
            for ctx in business_context[:10]:  # Top 10 most relevant
                prompt_parts.append(f"- {ctx.title}: {ctx.content}")
        
        # Add customer context
        if profile:
            prompt_parts.append(f"\n## Customer Profile:")
            prompt_parts.append(f"- Name: {profile.name or 'Not provided'}")
            prompt_parts.append(f"- Customer Type: {profile.customer_type or 'new'}")
            prompt_parts.append(f"- Total Orders: {profile.total_orders}")
            prompt_parts.append(f"- Communication Style: {profile.communication_style or 'casual'}")
            if profile.special_instructions:
                prompt_parts.append(f"- Special Note: {profile.special_instructions}")
        
        # Add conversation history
        if history:
            prompt_parts.append(f"\n## Recent Conversation History:")
            for msg in history[-5:]:  # Last 5 messages
                direction = "Customer" if msg.message_direction == MessageDirection.INBOUND else "You"
                prompt_parts.append(f"- {direction}: {msg.message_content}")
        
        # Add order context
        if order_info:
            prompt_parts.append(f"\n## Related Order:")
            prompt_parts.append(f"- Order ID: {order_info['id']}")
            prompt_parts.append(f"- Status: {order_info['status']}")
            prompt_parts.append(f"- Total: ${order_info['total']}")
        
        # Add current message
        prompt_parts.append(f"\n## Current Customer Message:")
        prompt_parts.append(f'"{customer_message}"')
        
        prompt_parts.append("\nProvide a helpful, personalized response based on all the context above.")
        prompt_parts.append(f"Keep the tone appropriate for {platform} (professional but friendly).")
        
        return "\n".join(prompt_parts)
    
    async def _analyze_message(self, message: str) -> Dict[str, Any]:
        """
        Analyze message for intent, sentiment, and entities.
        """
        prompt = f"""Analyze this customer message:

"{message}"

Extract:
1. Intent (product_inquiry, order_status, complaint, praise, shipping_question, pricing_question, general_inquiry)
2. Sentiment (positive, negative, neutral, frustrated, excited)
3. Entities (product names, order numbers, locations, dates)

Return as JSON:
{{
    "intent": "",
    "sentiment": "",
    "entities": {{}},
    "requires_urgent_attention": true/false
}}"""

        try:
            response = await self.gemini_client.generate_content(prompt=prompt, temperature=0.2)
            return json.loads(self._extract_json_from_response(response))
        except:
            return {"intent": "general_inquiry", "sentiment": "neutral", "entities": {}}
    
    async def _generate_message_summary(self, message: str) -> str:
        """
        Generate a brief summary of a message for quick context retrieval.
        """
        if len(message) < 100:
            return message
        
        prompt = f"Summarize this message in one sentence (max 100 chars): {message}"
        try:
            return await self.gemini_client.generate_content(prompt=prompt, temperature=0.3)
        except:
            return message[:100] + "..."
    
    def _extract_json_from_response(self, response: str) -> str:
        """
        Extract JSON from AI response that may contain markdown or extra text.
        """
        # Try to find JSON block
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            return json_match.group(0)
        return response
    
    async def _get_products(self) -> List[Product]:
        """
        Get all active products for the project.
        """
        result = await self.db.execute(
            select(Product)
            .where(
                and_(
                    Product.project_id == self.project_id,
                    Product.is_active == True
                )
            )
            .limit(100)
        )
        return result.scalars().all()
