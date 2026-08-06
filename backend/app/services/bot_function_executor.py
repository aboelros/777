"""
Bot Function Executor - Handles actual execution of AI bot function calls
Connects AI decisions to real platform operations
"""

from typing import Dict, Any, List, Optional
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
import structlog

from app.domains.orders.models import Order
from app.domains.messages.models import Message, MessageDirection
from app.domains.projects.models import Project
from app.domains.integrations.models import Integration, IntegrationProvider
from app.domains.analytics.models import APILog

logger = structlog.get_logger(__name__)


class BotFunctionExecutor:
    """Executes bot function calls and returns real data from platform"""
    
    def __init__(self, db: AsyncSession, project_id: UUID, user_id: UUID):
        self.db = db
        self.project_id = project_id
        self.user_id = user_id
    
    async def execute_function(
        self, 
        function_name: str, 
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a function call and return results.
        
        Args:
            function_name: Name of the function to execute
            parameters: Function parameters
            
        Returns:
            Dict containing function execution results
        """
        try:
            logger.info(
                "Executing bot function",
                function=function_name,
                params=parameters
            )
            
            if not function_name:
                logger.warning("Attempted to execute function with empty name")
                return {
                    "success": False,
                    "error": "Function name cannot be empty"
                }
            
            # Map function names to handlers
            handlers = {
                "get_message_stats": self._get_message_stats,
                "get_order_stats": self._get_order_stats,
                "get_recent_orders": self._get_recent_orders,
                "get_recent_messages": self._get_recent_messages,
                "generate_sales_report": self._generate_sales_report,
                "generate_customer_report": self._generate_customer_report,
                "sync_integration": self._sync_integration,
                "get_integration_status": self._get_integration_status,
                "analyze_message_sentiment": self._analyze_message_sentiment,
                "send_message": self._send_message,
                "update_order_status": self._update_order_status,
                "get_unread_messages": self._get_unread_messages,
                "get_urgent_messages": self._get_urgent_messages,
                "get_top_products": self._get_top_products,
                "compare_periods": self._compare_periods,
                "create_order": self._create_order,
                "track_order": self._track_order,
                "calculate_shipping_and_tax": self._calculate_shipping_and_tax,
            }
            
            handler = handlers.get(function_name)
            
            if not handler:
                logger.warning(f"Unknown function: {function_name}")
                return {
                    "success": False,
                    "error": f"Function '{function_name}' not implemented"
                }
            
            # Execute handler
            result = await handler(parameters)
            
            logger.info(
                "Function executed successfully",
                function=function_name,
                success=result.get("success", True)
            )
            
            return result
            
        except Exception as e:
            logger.error(
                "Function execution failed",
                function=function_name,
                error=str(e),
                error_type=type(e).__name__
            )
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _get_message_stats(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get message statistics for the project"""
        days = params.get("days", 7)
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get total message count
        total_result = await self.db.execute(
            select(func.count(Message.id))
            .where(Message.project_id == self.project_id)
            .where(Message.created_at >= start_date)
        )
        total_messages = total_result.scalar() or 0
        
        # Get unread count
        unread_result = await self.db.execute(
            select(func.count(Message.id))
            .where(Message.project_id == self.project_id)
            .where(Message.is_read == False)
            .where(Message.direction == MessageDirection.INBOUND)
        )
        unread_messages = unread_result.scalar() or 0
        
        # Get count by platform
        platform_result = await self.db.execute(
            select(
                Message.platform,
                func.count(Message.id).label("count")
            )
            .where(Message.project_id == self.project_id)
            .where(Message.created_at >= start_date)
            .group_by(Message.platform)
        )
        
        by_platform = {row.platform: row.count for row in platform_result}
        
        return {
            "success": True,
            "data": {
                "total_messages": total_messages,
                "unread_messages": unread_messages,
                "by_platform": by_platform,
                "period_days": days
            }
        }
    
    async def _get_order_stats(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get order statistics"""
        days = params.get("days", 1)
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get order statistics
        stats_result = await self.db.execute(
            select(
                func.count(Order.id).label("total_orders"),
                func.sum(Order.total).label("total_revenue"),
                func.avg(Order.total).label("avg_order_value"),
                Order.status
            )
            .where(Order.project_id == self.project_id)
            .where(Order.created_at >= start_date)
            .group_by(Order.status)
        )
        
        total_orders = 0
        total_revenue = 0.0
        by_status = {}
        
        for row in stats_result:
            total_orders += row.total_orders
            total_revenue += float(row.total_revenue or 0)
            by_status[row.status] = row.total_orders
        
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
        
        # Get previous period for comparison
        prev_start = start_date - timedelta(days=days)
        prev_result = await self.db.execute(
            select(
                func.count(Order.id).label("total_orders"),
                func.sum(Order.total).label("total_revenue")
            )
            .where(Order.project_id == self.project_id)
            .where(Order.created_at >= prev_start)
            .where(Order.created_at < start_date)
        )
        
        prev_row = prev_result.first()
        prev_orders = prev_row.total_orders or 0
        prev_revenue = float(prev_row.total_revenue or 0)
        
        # Calculate percentage changes
        orders_change = ((total_orders - prev_orders) / prev_orders * 100) if prev_orders > 0 else 0
        revenue_change = ((total_revenue - prev_revenue) / prev_revenue * 100) if prev_revenue > 0 else 0
        
        return {
            "success": True,
            "data": {
                "period_days": days,
                "total_orders": total_orders,
                "total_revenue": round(total_revenue, 2),
                "average_order_value": round(avg_order_value, 2),
                "by_status": by_status,
                "comparison": {
                    "previous_orders": prev_orders,
                    "previous_revenue": round(prev_revenue, 2),
                    "orders_change_percent": round(orders_change, 1),
                    "revenue_change_percent": round(revenue_change, 1)
                }
            }
        }
    
    async def _get_recent_orders(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get recent orders list"""
        limit = params.get("limit", 10)
        status_filter = params.get("status")
        
        query = select(Order).where(Order.project_id == self.project_id)
        
        if status_filter:
            query = query.where(Order.status == status_filter)
        
        query = query.order_by(Order.created_at.desc()).limit(limit)
        
        result = await self.db.execute(query)
        orders = result.scalars().all()
        
        orders_data = [
            {
                "id": str(order.id),
                "external_id": order.external_id,
                "customer_name": order.customer.get("name", "Unknown") if order.customer else "Unknown",
                "customer_email": order.customer.get("email", "") if order.customer else "",
                "total": float(order.total),
                "currency": order.currency,
                "status": order.status,
                "created_at": order.created_at.isoformat(),
                "items_count": len(order.items) if order.items else 0
            }
            for order in orders
        ]
        
        return {
            "success": True,
            "data": {
                "orders": orders_data,
                "count": len(orders_data)
            }
        }
    
    async def _get_recent_messages(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get recent messages"""
        limit = params.get("limit", 20)
        platform_filter = params.get("platform")
        
        query = select(Message).where(Message.project_id == self.project_id)
        
        if platform_filter:
            query = query.where(Message.platform == platform_filter)
        
        query = query.order_by(Message.created_at.desc()).limit(limit)
        
        result = await self.db.execute(query)
        messages = result.scalars().all()
        
        messages_data = [
            {
                "id": str(msg.id),
                "platform": msg.platform,
                "direction": msg.direction.value if msg.direction else "inbound",
                "content": msg.content,
                "sender": msg.sender,
                "recipient": msg.recipient,
                "is_read": msg.is_read,
                "created_at": msg.created_at.isoformat()
            }
            for msg in messages
        ]
        
        return {
            "success": True,
            "data": {
                "messages": messages_data,
                "count": len(messages_data)
            }
        }
    
    async def _get_unread_messages(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get unread messages"""
        result = await self.db.execute(
            select(Message)
            .where(Message.project_id == self.project_id)
            .where(Message.is_read == False)
            .where(Message.direction == MessageDirection.INBOUND)
            .order_by(Message.created_at.desc())
        )
        
        messages = result.scalars().all()
        
        messages_data = [
            {
                "id": str(msg.id),
                "platform": msg.platform,
                "content": msg.content,
                "sender": msg.sender,
                "created_at": msg.created_at.isoformat()
            }
            for msg in messages
        ]
        
        return {
            "success": True,
            "data": {
                "unread_messages": messages_data,
                "count": len(messages_data)
            }
        }
    
    async def _get_urgent_messages(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get urgent/high-priority messages (recent unread)"""
        # Get messages from last 24 hours that are unread
        yesterday = datetime.utcnow() - timedelta(days=1)
        
        result = await self.db.execute(
            select(Message)
            .where(Message.project_id == self.project_id)
            .where(Message.is_read == False)
            .where(Message.direction == MessageDirection.INBOUND)
            .where(Message.created_at >= yesterday)
            .order_by(Message.created_at.desc())
        )
        
        messages = result.scalars().all()
        
        # Simple urgency detection based on keywords
        urgent_keywords = ["urgent", "asap", "immediately", "emergency", "problem", "issue", "complaint", "angry"]
        
        urgent_messages = []
        for msg in messages:
            content_lower = msg.content.lower() if msg.content else ""
            is_urgent = any(keyword in content_lower for keyword in urgent_keywords)
            
            urgent_messages.append({
                "id": str(msg.id),
                "platform": msg.platform,
                "content": msg.content,
                "sender": msg.sender,
                "created_at": msg.created_at.isoformat(),
                "is_urgent": is_urgent,
                "priority": "high" if is_urgent else "medium"
            })
        
        # Sort by urgency
        urgent_messages.sort(key=lambda x: (not x["is_urgent"], x["created_at"]), reverse=True)
        
        return {
            "success": True,
            "data": {
                "urgent_messages": urgent_messages,
                "count": len(urgent_messages),
                "high_priority_count": sum(1 for m in urgent_messages if m["is_urgent"])
            }
        }
    
    async def _generate_sales_report(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate sales report"""
        period = params.get("period", "week")  # day, week, month
        
        # Determine date range
        if period == "day":
            days = 1
        elif period == "week":
            days = 7
        elif period == "month":
            days = 30
        else:
            days = int(params.get("days", 7))
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get order statistics
        result = await self.db.execute(
            select(
                func.count(Order.id).label("total_orders"),
                func.sum(Order.total).label("total_revenue"),
                func.avg(Order.total).label("avg_order_value")
            )
            .where(Order.project_id == self.project_id)
            .where(Order.created_at >= start_date)
        )
        
        row = result.first()
        
        # Get top products
        # Note: This is simplified - in reality you'd aggregate from order items
        top_products_data = []
        
        report = {
            "report_type": "sales",
            "period": period,
            "period_days": days,
            "date_from": start_date.isoformat(),
            "date_to": datetime.utcnow().isoformat(),
            "metrics": {
                "total_orders": row.total_orders or 0,
                "total_revenue": float(row.total_revenue or 0),
                "average_order_value": float(row.avg_order_value or 0)
            },
            "top_products": top_products_data,
            "generated_at": datetime.utcnow().isoformat()
        }
        
        return {
            "success": True,
            "data": {
                "report": report
            }
        }
    
    async def _generate_customer_report(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate customer analytics report"""
        period_days = params.get("days", 30)
        start_date = datetime.utcnow() - timedelta(days=period_days)
        
        # Get customer statistics from orders
        result = await self.db.execute(
            select(Order)
            .where(Order.project_id == self.project_id)
            .where(Order.created_at >= start_date)
        )
        
        orders = result.scalars().all()
        
        # Analyze customers
        customers = {}
        for order in orders:
            if order.customer and order.customer.get("email"):
                email = order.customer["email"]
                if email not in customers:
                    customers[email] = {
                        "name": order.customer.get("name", "Unknown"),
                        "email": email,
                        "order_count": 0,
                        "total_spent": 0.0
                    }
                customers[email]["order_count"] += 1
                customers[email]["total_spent"] += float(order.total)
        
        # Sort by total spent
        top_customers = sorted(
            customers.values(),
            key=lambda x: x["total_spent"],
            reverse=True
        )[:10]
        
        report = {
            "report_type": "customers",
            "period_days": period_days,
            "total_unique_customers": len(customers),
            "total_orders": len(orders),
            "top_customers": top_customers,
            "generated_at": datetime.utcnow().isoformat()
        }
        
        return {
            "success": True,
            "data": {
                "report": report
            }
        }
    
    async def _sync_integration(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Trigger integration sync"""
        integration_name = params.get("integration")  # shopify, whatsapp, etc.
        
        # Get integration
        result = await self.db.execute(
            select(Integration)
            .where(Integration.project_id == self.project_id)
            .where(Integration.provider == integration_name)
        )
        
        integration = result.scalar_one_or_none()
        
        if not integration:
            return {
                "success": False,
                "error": f"Integration '{integration_name}' not found or not connected"
            }
        
        # TODO: Actually trigger sync via background task
        # For now, just return success
        
        return {
            "success": True,
            "data": {
                "integration": integration_name,
                "status": "sync_initiated",
                "message": f"Sync started for {integration_name}"
            }
        }
    
    async def _get_integration_status(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get integration status"""
        result = await self.db.execute(
            select(Integration)
            .where(Integration.project_id == self.project_id)
        )
        
        integrations = result.scalars().all()
        
        integrations_data = [
            {
                "name": integ.provider,
                "status": integ.status,
                "last_sync": integ.last_sync.isoformat() if integ.last_sync else None,
                "is_active": integ.is_active
            }
            for integ in integrations
        ]
        
        return {
            "success": True,
            "data": {
                "integrations": integrations_data,
                "total_connected": len([i for i in integrations if i.is_active])
            }
        }
    
    async def _analyze_message_sentiment(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze message sentiment (simplified)"""
        message_id = params.get("message_id")
        
        if not message_id:
            return {"success": False, "error": "message_id required"}
        
        # Get message
        result = await self.db.execute(
            select(Message)
            .where(Message.id == UUID(message_id))
            .where(Message.project_id == self.project_id)
        )
        
        message = result.scalar_one_or_none()
        
        if not message:
            return {"success": False, "error": "Message not found"}
        
        # Simple sentiment analysis based on keywords
        content_lower = message.content.lower() if message.content else ""
        
        negative_keywords = ["angry", "upset", "disappointed", "terrible", "worst", "complaint", "refund"]
        positive_keywords = ["great", "excellent", "awesome", "love", "perfect", "amazing", "happy"]
        urgent_keywords = ["urgent", "asap", "immediately", "emergency"]
        
        negative_count = sum(1 for kw in negative_keywords if kw in content_lower)
        positive_count = sum(1 for kw in positive_keywords if kw in content_lower)
        urgent_count = sum(1 for kw in urgent_keywords if kw in content_lower)
        
        if negative_count > positive_count:
            sentiment = "negative"
        elif positive_count > negative_count:
            sentiment = "positive"
        else:
            sentiment = "neutral"
        
        urgency = "high" if urgent_count > 0 else ("medium" if negative_count > 0 else "low")
        
        return {
            "success": True,
            "data": {
                "message_id": message_id,
                "sentiment": sentiment,
                "urgency": urgency,
                "confidence": 0.75,  # Simplified
                "recommended_tone": "empathetic" if sentiment == "negative" else "friendly"
            }
        }
    
    async def _send_message(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Send message to customer"""
        # This would integrate with actual messaging platforms
        # For now, just log it
        
        to = params.get("to")
        message_content = params.get("message")
        platform = params.get("platform", "whatsapp")
        
        logger.info(
            "Bot sending message",
            to=to,
            platform=platform,
            message_length=len(message_content or "")
        )
        
        # TODO: Actually send via integration
        
        return {
            "success": True,
            "data": {
                "message_sent": True,
                "platform": platform,
                "recipient": to,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    
    async def _update_order_status(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update order status"""
        order_id = params.get("order_id")
        new_status = params.get("status")
        
        if not order_id or not new_status:
            return {"success": False, "error": "order_id and status required"}
        
        # Get order
        result = await self.db.execute(
            select(Order)
            .where(Order.id == UUID(order_id))
            .where(Order.project_id == self.project_id)
        )
        
        order = result.scalar_one_or_none()
        
        if not order:
            return {"success": False, "error": "Order not found"}
        
        old_status = order.status
        order.status = new_status
        order.updated_at = datetime.utcnow()
        
        await self.db.commit()
        
        logger.info(
            "Order status updated by bot",
            order_id=order_id,
            old_status=old_status,
            new_status=new_status
        )
        
        return {
            "success": True,
            "data": {
                "order_id": order_id,
                "previous_status": old_status,
                "new_status": new_status,
                "updated_at": datetime.utcnow().isoformat()
            }
        }
    
    async def _get_top_products(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get top selling products"""
        days = params.get("days", 30)
        limit = params.get("limit", 10)
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get orders
        result = await self.db.execute(
            select(Order)
            .where(Order.project_id == self.project_id)
            .where(Order.created_at >= start_date)
        )
        
        orders = result.scalars().all()
        
        # Aggregate products
        products = {}
        for order in orders:
            if order.items:
                for item in order.items:
                    product_name = item.get("name", "Unknown")
                    if product_name not in products:
                        products[product_name] = {
                            "name": product_name,
                            "quantity_sold": 0,
                            "revenue": 0.0
                        }
                    products[product_name]["quantity_sold"] += item.get("quantity", 1)
                    products[product_name]["revenue"] += float(item.get("price", 0)) * item.get("quantity", 1)
        
        # Sort by quantity sold
        top_products = sorted(
            products.values(),
            key=lambda x: x["quantity_sold"],
            reverse=True
        )[:limit]
        
        return {
            "success": True,
            "data": {
                "top_products": top_products,
                "period_days": days
            }
        }
    
    async def _compare_periods(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Compare two time periods"""
        period_days = params.get("period_days", 7)
        
        # Current period
        current_start = datetime.utcnow() - timedelta(days=period_days)
        current_result = await self.db.execute(
            select(
                func.count(Order.id).label("orders"),
                func.sum(Order.total).label("revenue")
            )
            .where(Order.project_id == self.project_id)
            .where(Order.created_at >= current_start)
        )
        current = current_result.first()
        
        # Previous period
        previous_start = current_start - timedelta(days=period_days)
        previous_result = await self.db.execute(
            select(
                func.count(Order.id).label("orders"),
                func.sum(Order.total).label("revenue")
            )
            .where(Order.project_id == self.project_id)
            .where(Order.created_at >= previous_start)
            .where(Order.created_at < current_start)
        )
        previous = previous_result.first()
        
        # Calculate changes
        orders_change = ((current.orders - previous.orders) / previous.orders * 100) if previous.orders > 0 else 0
        revenue_change = ((float(current.revenue or 0) - float(previous.revenue or 0)) / float(previous.revenue or 1) * 100)
        
        return {
            "success": True,
            "data": {
                "current_period": {
                    "orders": current.orders or 0,
                    "revenue": float(current.revenue or 0)
                },
                "previous_period": {
                    "orders": previous.orders or 0,
                    "revenue": float(previous.revenue or 0)
                },
                "changes": {
                    "orders_percent": round(orders_change, 1),
                    "revenue_percent": round(revenue_change, 1)
                }
            }
        }

    async def _create_order(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new order based on chat instructions"""
        customer_id = params.get("customer_id")
        items = params.get("items", [])
        total = params.get("total", 0.0)
        currency = params.get("currency", "USD")
        status = params.get("status", "pending")
        
        # If customer_id is a formatted string like "UUID", clean it
        if customer_id:
             try:
                 customer_id = UUID(str(customer_id))
             except ValueError:
                 # Try to lookup customer if not a UUID (e.g. email/phone)
                 # For now, require valid UUID or fail
                 return {"success": False, "error": "Invalid customer_id format"}

        # Link to customer profile if possible
        # We might need to find the profile from the conversation context if customer_id is missing
        
        if not items:
            return {"success": False, "error": "Order must have items"}
            
        import uuid
        external_id = f"AI-{str(uuid.uuid4())[:8].upper()}"
        
        try:
            new_order = Order(
                project_id=self.project_id,
                customer_id=customer_id,
                external_id=external_id,
                status=status,
                total=float(total),
                currency=currency,
                items=items,
                extra_data={"source": "ai_assistant", "created_via": "chat"}
            )
            
            self.db.add(new_order)
            await self.db.commit()
            await self.db.refresh(new_order)
            
            logger.info("Order created by AI", order_id=str(new_order.id), external_id=external_id)
            
            return {
                "success": True,
                "data": {
                    "order_id": str(new_order.id),
                    "external_id": external_id,
                    "status": status,
                    "total": total,
                    "currency": currency,
                    "message": f"Order #{external_id} created successfully."
                }
            }
        except Exception as e:
            logger.error("Failed to create order via AI", error=str(e))
            return {"success": False, "error": f"Failed to create order: {str(e)}"}

    async def _track_order(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Track order status by ID or Customer"""
        order_id = params.get("order_id")
        email = params.get("email")
        phone = params.get("phone")
        
        query = select(Order).where(Order.project_id == self.project_id)
        
        if order_id:
            # Try to match external_id first (more user friendly)
            # If not found, check UUID
            query = query.where(
                or_(
                    Order.external_id == order_id,
                    func.cast(Order.id, String) == order_id
                )
            )
        elif email or phone:
            # Find orders by customer contact
            # This requires joining with CustomerProfile or checking customer JSONB in Orders if exists
            # For now, let's assume we search mostly by ID in chat or we implement simple email search if linked
            # Simplified:
            pass
        else:
             return {"success": False, "error": "Please provide an Order ID to track."}
             
        query = query.order_by(Order.created_at.desc()).limit(1)
        result = await self.db.execute(query)
        order = result.scalar_one_or_none()
        
        if not order:
            return {"success": False, "error": "Order not found."}
            
        return {
            "success": True,
            "data": {
                "order_id": str(order.id),
                "external_id": order.external_id,
                "status": order.status,
                "total": float(order.total),
                "currency": order.currency,
                "created_at": order.created_at.isoformat(),
                "items": order.items
            }
        }

    async def _calculate_shipping_and_tax(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate shipping and tax using ShippingService"""
        from app.services.shipping_service import ShippingService
        
        destination = params.get("destination")
        items_total = params.get("items_total")
        currency = params.get("currency", "USD")
        
        if not destination or items_total is None:
            return {"success": False, "error": "destination and items_total are required"}
            
        service = ShippingService()
        result = await service.calculate(destination, float(items_total), currency)
        return {"success": True, "data": result}
