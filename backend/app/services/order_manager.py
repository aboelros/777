"""
Automatic Order Tracking and Management System.
Handles order synchronization, status updates, and automated notifications.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from uuid import UUID
import structlog
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.orders.models import Order, OrderStatus
from app.domains.messages.models import Message, MessageDirection
from app.domains.integrations.models import Integration
from app.domains.ai.providers.gemini import gemini_client

logger = structlog.get_logger(__name__)


class OrderManager:
    """Manages automatic order tracking and updates."""
    
    def __init__(self, db: AsyncSession, project_id: UUID):
        self.db = db
        self.project_id = project_id
    
    async def sync_order_from_shopify(
        self,
        shopify_order: Dict[str, Any],
        integration_id: UUID
    ) -> Order:
        """
        Sync an order from Shopify into the database.
        
        Args:
            shopify_order: Order data from Shopify API
            integration_id: Integration ID for tracking
            
        Returns:
            Created or updated Order object
        """
        logger.info("Syncing Shopify order", order_id=shopify_order.get('id'))
        
        external_id = str(shopify_order['id'])
        
        # Check if order already exists
        result = await self.db.execute(
            select(Order).where(
                and_(
                    Order.project_id == self.project_id,
                    Order.external_id == external_id,
                    Order.provider == 'shopify'
                )
            )
        )
        existing_order = result.scalar_one_or_none()
        
        # Parse order data
        customer = shopify_order.get('customer', {})
        line_items = shopify_order.get('line_items', [])
        
        order_data = {
            "project_id": self.project_id,
            "integration_id": integration_id,
            "external_id": external_id,
            "provider": "shopify",
            "customer_name": customer.get('first_name', '') + ' ' + customer.get('last_name', ''),
            "customer_email": customer.get('email'),
            "customer_phone": customer.get('phone'),
            "total": float(shopify_order.get('total_price', 0)),
            "currency": shopify_order.get('currency', 'USD'),
            "status": self._map_shopify_status(shopify_order.get('financial_status', 'pending')),
            "line_items": line_items,
            "shipping_address": shopify_order.get('shipping_address', {}),
            "billing_address": shopify_order.get('billing_address', {}),
            "order_date": datetime.fromisoformat(shopify_order['created_at'].replace('Z', '+00:00')),
            "extra_data": {
                "shopify_order_number": shopify_order.get('order_number'),
                "fulfillment_status": shopify_order.get('fulfillment_status'),
                "tags": shopify_order.get('tags', '').split(',') if shopify_order.get('tags') else []
            }
        }
        
        if existing_order:
            # Update existing order
            for key, value in order_data.items():
                if key not in ['id', 'created_at', 'project_id']:
                    setattr(existing_order, key, value)
            existing_order.updated_at = datetime.utcnow()
            await self.db.commit()
            await self.db.refresh(existing_order)
            logger.info("Order updated", order_id=str(existing_order.id))
            return existing_order
        else:
            # Create new order
            order = Order(**order_data)
            self.db.add(order)
            await self.db.commit()
            await self.db.refresh(order)
            logger.info("New order created", order_id=str(order.id))
            
            # Send notification to customer
            await self._send_order_confirmation(order)
            
            return order
    
    async def update_order_status(
        self,
        order_id: UUID,
        new_status: OrderStatus,
        note: Optional[str] = None,
        notify_customer: bool = True
    ) -> Order:
        """
        Update order status and optionally notify customer.
        
        Args:
            order_id: Order ID
            new_status: New status
            note: Optional note about the change
            notify_customer: Whether to send notification
            
        Returns:
            Updated Order object
        """
        logger.info("Updating order status", order_id=str(order_id), new_status=new_status.value)
        
        # Fetch order
        result = await self.db.execute(
            select(Order).where(
                and_(
                    Order.id == order_id,
                    Order.project_id == self.project_id
                )
            )
        )
        order = result.scalar_one_or_none()
        
        if not order:
            raise ValueError(f"Order {order_id} not found")
        
        old_status = order.status
        order.status = new_status
        order.updated_at = datetime.utcnow()
        
        # Add note to extra_data
        if note:
            if not order.extra_data:
                order.extra_data = {}
            if 'status_history' not in order.extra_data:
                order.extra_data['status_history'] = []
            order.extra_data['status_history'].append({
                "from": old_status.value,
                "to": new_status.value,
                "note": note,
                "timestamp": datetime.utcnow().isoformat()
            })
        
        await self.db.commit()
        await self.db.refresh(order)
        
        # Notify customer
        if notify_customer:
            await self._send_status_update(order, old_status, new_status)
        
        logger.info("Order status updated successfully", order_id=str(order_id))
        return order
    
    async def track_order(self, order_id: UUID) -> Dict[str, Any]:
        """
        Get comprehensive tracking information for an order.
        
        Args:
            order_id: Order ID
            
        Returns:
            Detailed tracking information
        """
        logger.info("Tracking order", order_id=str(order_id))
        
        # Fetch order
        result = await self.db.execute(
            select(Order).where(
                and_(
                    Order.id == order_id,
                    Order.project_id == self.project_id
                )
            )
        )
        order = result.scalar_one_or_none()
        
        if not order:
            raise ValueError(f"Order {order_id} not found")
        
        # Get related messages
        messages_result = await self.db.execute(
            select(Message).where(
                Message.order_id == order_id
            ).order_by(Message.created_at.desc())
        )
        messages = messages_result.scalars().all()
        
        # Build tracking info
        tracking_info = {
            "order_id": str(order.id),
            "external_id": order.external_id,
            "status": order.status.value,
            "customer": {
                "name": order.customer_name,
                "email": order.customer_email,
                "phone": order.customer_phone
            },
            "order_details": {
                "total": order.total,
                "currency": order.currency,
                "items_count": len(order.line_items),
                "order_date": order.order_date.isoformat()
            },
            "status_history": order.extra_data.get('status_history', []) if order.extra_data else [],
            "recent_communications": [
                {
                    "direction": msg.direction.value,
                    "content": msg.content[:100] + "..." if len(msg.content) > 100 else msg.content,
                    "channel": msg.channel,
                    "sent_at": msg.created_at.isoformat()
                }
                for msg in messages[:5]
            ],
            "estimated_delivery": self._estimate_delivery_date(order),
            "updated_at": order.updated_at.isoformat()
        }
        
        return tracking_info
    
    async def process_order_automatically(self, order: Order) -> Dict[str, Any]:
        """
        Use AI to automatically process and respond to order-related queries.
        
        Args:
            order: Order object
            
        Returns:
            AI processing results with actions taken
        """
        logger.info("Auto-processing order with AI", order_id=str(order.id))
        
        # Build context for AI
        context = {
            "order": {
                "id": str(order.id),
                "external_id": order.external_id,
                "status": order.status.value,
                "customer": order.customer_name,
                "total": order.total,
                "currency": order.currency,
                "items": len(order.line_items)
            }
        }
        
        # Determine action based on order status
        if order.status == OrderStatus.PENDING:
            prompt = f"New order received. Should we send a confirmation message to {order.customer_name}? Order total: {order.currency} {order.total}"
        elif order.status == OrderStatus.PROCESSING:
            prompt = f"Order is now being processed. Generate an update message for {order.customer_name}"
        elif order.status == OrderStatus.FULFILLED:
            prompt = f"Order has been fulfilled and shipped. Create a delivery notification and request feedback from {order.customer_name}"
        else:
            prompt = f"Order status is {order.status.value}. Determine if any customer communication is needed"
        
        # Get AI response
        response = await gemini_client.generate_response(
            prompt=prompt,
            context=context,
            use_functions=True
        )
        
        # Execute function calls if any
        actions_taken = []
        if response.get('function_calls'):
            for func_call in response['function_calls']:
                action_result = await self._execute_ai_action(func_call, order)
                actions_taken.append(action_result)
        
        return {
            "ai_response": response.get('text', ''),
            "actions_taken": actions_taken,
            "function_calls": response.get('function_calls', [])
        }
    
    async def _send_order_confirmation(self, order: Order):
        """Send order confirmation message to customer."""
        logger.info("Sending order confirmation", order_id=str(order.id))
        
        # Use AI to generate personalized message
        prompt = f"""Generate a friendly order confirmation message for:
Customer: {order.customer_name}
Order ID: {order.external_id}
Total: {order.currency} {order.total}
Items: {len(order.line_items)} items

Keep it professional, warm, and include:
1. Thank you message
2. Order details
3. What to expect next
4. Support contact info"""
        
        try:
            response = await gemini_client.generate_response(
                prompt=prompt,
                use_functions=False,
                temperature=0.7
            )
            
            message_content = response.get('text', f"Thank you for your order #{order.external_id}! We're processing it now.")
            
            # Create message record
            message = Message(
                project_id=self.project_id,
                order_id=order.id,
                direction=MessageDirection.OUTBOUND,
                content=message_content,
                channel="email",  # Default channel
                extra_data={
                    "ai_generated": True,
                    "type": "order_confirmation"
                }
            )
            self.db.add(message)
            await self.db.commit()
            
            logger.info("Order confirmation sent", order_id=str(order.id))
        
        except Exception as e:
            logger.error("Failed to send order confirmation", error=str(e))
    
    async def _send_status_update(self, order: Order, old_status: OrderStatus, new_status: OrderStatus):
        """Send status update notification to customer."""
        logger.info("Sending status update", order_id=str(order.id), new_status=new_status.value)
        
        status_messages = {
            OrderStatus.PROCESSING: "Your order is now being processed",
            OrderStatus.FULFILLED: "Great news! Your order has been shipped",
            OrderStatus.CANCELLED: "Your order has been cancelled",
            OrderStatus.REFUNDED: "Your refund has been processed"
        }
        
        base_message = status_messages.get(new_status, f"Your order status has been updated to {new_status.value}")
        
        # Use AI to generate personalized message
        prompt = f"""Generate a customer-friendly status update message:
Customer: {order.customer_name}
Order: #{order.external_id}
Status changed from: {old_status.value} to {new_status.value}

Base message: {base_message}

Make it warm and helpful. Include tracking info if shipped."""
        
        try:
            response = await gemini_client.generate_response(
                prompt=prompt,
                use_functions=False,
                temperature=0.7
            )
            
            message_content = response.get('text', base_message)
            
            # Create message record
            message = Message(
                project_id=self.project_id,
                order_id=order.id,
                direction=MessageDirection.OUTBOUND,
                content=message_content,
                channel="email",
                extra_data={
                    "ai_generated": True,
                    "type": "status_update",
                    "old_status": old_status.value,
                    "new_status": new_status.value
                }
            )
            self.db.add(message)
            await self.db.commit()
            
            logger.info("Status update sent", order_id=str(order.id))
        
        except Exception as e:
            logger.error("Failed to send status update", error=str(e))
    
    def _map_shopify_status(self, shopify_status: str) -> OrderStatus:
        """Map Shopify status to our OrderStatus enum."""
        status_map = {
            "pending": OrderStatus.PENDING,
            "paid": OrderStatus.PROCESSING,
            "fulfilled": OrderStatus.FULFILLED,
            "refunded": OrderStatus.REFUNDED,
            "cancelled": OrderStatus.CANCELLED
        }
        return status_map.get(shopify_status.lower(), OrderStatus.PENDING)
    
    def _estimate_delivery_date(self, order: Order) -> Optional[str]:
        """Estimate delivery date based on order status."""
        if order.status == OrderStatus.FULFILLED:
            # Assume 3-5 business days from fulfillment
            from datetime import timedelta
            estimated_date = order.updated_at + timedelta(days=4)
            return estimated_date.strftime('%Y-%m-%d')
        elif order.status == OrderStatus.PROCESSING:
            from datetime import timedelta
            estimated_date = datetime.utcnow() + timedelta(days=7)
            return estimated_date.strftime('%Y-%m-%d')
        return None
    
    async def _execute_ai_action(self, func_call: Dict[str, Any], order: Order) -> Dict[str, Any]:
        """Execute an AI function call action."""
        function_name = func_call['name']
        parameters = func_call['parameters']
        
        logger.info("Executing AI action", function=function_name, order_id=str(order.id))
        
        if function_name == "send_message":
            # Send message to customer
            message = Message(
                project_id=self.project_id,
                order_id=order.id,
                direction=MessageDirection.OUTBOUND,
                content=parameters['message'],
                channel=parameters.get('channel', 'email'),
                extra_data={
                    "ai_generated": True,
                    "ai_action": function_name
                }
            )
            self.db.add(message)
            await self.db.commit()
            return {"action": "message_sent", "channel": parameters.get('channel')}
        
        elif function_name == "update_order_status":
            # Update order status
            new_status = OrderStatus(parameters['status'])
            await self.update_order_status(
                order.id,
                new_status,
                note=parameters.get('note'),
                notify_customer=True
            )
            return {"action": "status_updated", "new_status": parameters['status']}
        
        elif function_name == "schedule_followup":
            # Schedule follow-up (would integrate with Celery)
            return {
                "action": "followup_scheduled",
                "delay_hours": parameters.get('delay_hours'),
                "message": parameters.get('message')
            }
        
        else:
            logger.warning("Unknown AI action", function=function_name)
            return {"action": "unknown", "function": function_name}


async def sync_all_shopify_orders(
    db: AsyncSession,
    project_id: UUID,
    integration_id: UUID,
    shopify_client
) -> Dict[str, Any]:
    """
    Sync all orders from Shopify for a project.
    
    Args:
        db: Database session
        project_id: Project ID
        integration_id: Shopify integration ID
        shopify_client: Shopify client instance
        
    Returns:
        Sync results summary
    """
    logger.info("Starting Shopify order sync", project_id=str(project_id))
    
    manager = OrderManager(db, project_id)
    
    try:
        # Fetch orders from Shopify
        shopify_orders = await shopify_client.get_orders(limit=50)  # Adjust limit as needed
        
        synced_orders = []
        errors = []
        
        for shopify_order in shopify_orders:
            try:
                order = await manager.sync_order_from_shopify(shopify_order, integration_id)
                synced_orders.append(str(order.id))
            except Exception as e:
                logger.error("Failed to sync order", order_id=shopify_order.get('id'), error=str(e))
                errors.append({"order_id": shopify_order.get('id'), "error": str(e)})
        
        return {
            "success": True,
            "synced_count": len(synced_orders),
            "orders": synced_orders,
            "errors": errors
        }
    
    except Exception as e:
        logger.error("Shopify sync failed", error=str(e))
        return {
            "success": False,
            "error": str(e)
        }
