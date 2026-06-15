    async def _send_whatsapp_message(
        self,
        customer_id: UUID,
        message: str,
        project_id: UUID
    ) -> Dict[str, Any]:
        """Send message via WA-Gateway."""
        try:
            # Get customer phone number
            from app.db.models import CustomerProfile
            result = await self.db.execute(
                select(CustomerProfile).where(CustomerProfile.id == customer_id)
            )
            customer = result.scalar_one_or_none()
            
            if not customer or not customer.phone:
                logger.error("Customer or phone not found", customer_id=str(customer_id))
                return {"status": "error", "message": "Customer phone not found"}
            
            # Get WA-Gateway integration
            result = await self.db.execute(
                select(Integration)
                .where(Integration.project_id == project_id)
                .where(Integration.provider == "whatsapp")
                .where(Integration.status == "connected")
            )
            integration = result.scalar_one_or_none()
            
            if not integration:
                logger.error("No connected WhatsApp integration", project_id=str(project_id))
                return {"status": "error", "message": "No WhatsApp integration"}
            
            # Get session ID from integration
            session_id = integration.extra_data.get("session_id") if integration.extra_data else None
            if not session_id:
                logger.error("No session_id in integration", integration_id=str(integration.id))
                return {"status": "error", "message": "No session ID"}
            
            # Send message via WA-Gateway
            from app.services.integrations.whatsapp_gateway_service import WhatsAppGatewayService
            
            gateway = WhatsAppGatewayService(
                base_url=integration.config.get("base_url", ""),
                api_key=integration.config.get("api_key", "")
            )
            
            result = await gateway.send_text_message(
                session_id=session_id,
                to=customer.phone,
                text=message
            )
            
            # Save outbound message to database
            outbound_msg = Message(
                project_id=project_id,
                customer_id=customer_id,
                direction=MessageDirection.OUTBOUND,
                platform="whatsapp",
                provider="wa_gateway",
                content=message,
                metadata={"session_id": session_id}
            )
            self.db.add(outbound_msg)
            await self.db.commit()
            
            logger.info(
                "WhatsApp message sent",
                customer_id=str(customer_id),
                phone=customer.phone
            )
            
            return {"status": "success"}
            
        except Exception as e:
            logger.error(
                "Failed to send WhatsApp message",
                error=str(e),
                customer_id=str(customer_id)
            )
            return {"status": "error", "message": str(e)}
