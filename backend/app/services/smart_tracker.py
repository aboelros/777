from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, func
import structlog

from app.db.models import Order, Project, Message, MessageDirection, Integration
from app.services.ai_orchestrator import AIOrchestrator

logger = structlog.get_logger()

class SmartTrackerService:
    def __init__(self, db: Session):
        self.db = db
        self.ai = AIOrchestrator(db)

    async def run_checks(self):
        """Run all smart tracking checks."""
        logger.info("Running smart tracker checks")
        
        # Get all projects with AI enabled
        projects = await self._get_active_projects()
        
        for project in projects:
            try:
                # Get tracking rules from project settings
                rules = project.settings.get("smart_tracking", [])
                if not rules:
                    continue
                    
                logger.info(f"Checking rules for project {project.name}", rules_count=len(rules))
                
                for rule in rules:
                    await self._process_rule(project, rule)
                    
            except Exception as e:
                logger.error("Error processing project rules", project_id=str(project.id), error=str(e))

    async def _get_active_projects(self) -> List[Project]:
        """Get projects with active AI subscriptions."""
        stmt = select(Project).where(
            Project.is_active == True,
            # In a real app, check for valid subscription here
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def _process_rule(self, project: Project, rule: Dict[str, Any]):
        """
        Process a single tracking rule.
        
        Rule format:
        {
            "trigger_status": "delivered",  # or "shipped", "pending"
            "delay_hours": 24,
            "message_template": "How is your order? Do you like it?",
            "channel": "whatsapp" # optional, defaults to customer's preferred
        }
        """
        trigger_status = rule.get("trigger_status")
        delay_hours = rule.get("delay_hours", 24)
        
        if not trigger_status:
            return

        # Calculate time window
        # We want orders updated to this status BEFORE (now - delay)
        # But we also don't want to process ancient orders, so let's say (now - delay - 24h)
        cutoff_time = datetime.utcnow() - timedelta(hours=delay_hours)
        window_start = cutoff_time - timedelta(hours=24) 
        
        # specific logic for "pending" might be different (e.g. created_at instad of updated_at)
        
        # Find orders
        # 1. Status matches
        # 2. Updated_at (or created_at) is in the window
        # 3. No follow-up sent yet for THIS rule
        
        stmt = select(Order).where(
            Order.project_id == project.id,
            Order.status == trigger_status,
            Order.updated_at <= cutoff_time,
            Order.updated_at >= window_start
        )
        
        result = await self.db.execute(stmt)
        orders = result.scalars().all()
        
        logger.info(
            "Found orders for rule", 
            project_id=str(project.id), 
            status=trigger_status, 
            count=len(orders)
        )
        
        for order in orders:
            await self._process_order_followup(project, order, rule)

    async def _process_order_followup(self, project: Project, order: Order, rule: Dict[str, Any]):
        """Send follow-up for a specific order."""
        try:
            # Check if we already sent a message for this rule
            # We can check extra_data metadata
            rule_id = rule.get("id", f"{rule['trigger_status']}_{rule['delay_hours']}")
            processed_rules = order.extra_data.get("processed_rules", []) if order.extra_data else []
            
            if rule_id in processed_rules:
                return
            
            logger.info("Sending follow-up", order_id=str(order.id), rule=rule_id)
            
            # Determine channel
            channel = rule.get("channel")
            if not channel:
                # Try to infer from customer or order provider
                channel = order.provider if order.provider in ["whatsapp", "telegram", "messenger"] else "whatsapp"
            
            # Generate message content
            # We'll let the AI personalize it based on the template
            customer_name = order.customer.get("name", "Customer") if order.customer else "Customer"
            items_desc = ", ".join([i.get('name', 'item') for i in order.items]) if order.items else "your items"
            
            prompt = f"""
            You are a helpful customer service AI.
            Send a friendly follow-up message to specific customer.
            
            Context:
            - Customer Name: {customer_name}
            - Order Status: {order.status} (reached {rule['delay_hours']} hours ago)
            - Items: {items_desc}
            - Goal: {rule.get('message_template', 'Check satisfaction')}
            
            Write the message in the language of the customer (default to English).
            Keep it short, friendly, and professional.
            Do not include placeholders like [Name].
            """
            
            # Use AI Orchestrator to generate and send
            # We bypass the normal "incoming message" flow and use _send_message directly
            # But we need to generate the text first.
            
            ai_response = await self.ai.gemini.generate_response(
                prompt=prompt,
                use_functions=False,
                max_tokens=200
            )
            
            message_text = ai_response.get("text", "").strip()
            
            if not message_text:
                logger.warning("Empty AI response for follow-up")
                return

            # Send the message
            # We need to use the AI Orchestrator's sender logic
            send_result = await self.ai._send_message(
                customer_id=order.customer_id,
                message=message_text,
                channel=channel,
                project_id=project.id
            )
            
            if send_result.get("status") == "success":
                # Mark as processed
                new_extra = dict(order.extra_data) if order.extra_data else {}
                current_processed = new_extra.get("processed_rules", [])
                current_processed.append(rule_id)
                new_extra["processed_rules"] = current_processed
                
                order.extra_data = new_extra
                self.db.add(order)
                await self.db.commit()
                
                logger.info("Follow-up sent successfully", order_id=str(order.id))
            
        except Exception as e:
            logger.error("Failed to process order follow-up", order_id=str(order.id), error=str(e))
