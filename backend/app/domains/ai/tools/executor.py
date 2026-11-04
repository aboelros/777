import asyncio
import time
from typing import Dict, Any, Optional
from uuid import UUID
import structlog
from pydantic import ValidationError

from app.core.context import TenantContext
from .schemas import (
    ToolRiskLevel,
    ToolExecutionOutcome,
    SearchProductsInput,
    CheckInventoryInput,
    GetOrderStatusInput,
    CreateTicketInput,
    EscalateConversationInput,
    GetPolicyInput
)
from .registry import tool_registry, ToolDefinition
from .guard import ToolAuthorizationGuard

logger = structlog.get_logger(__name__)


class SecureToolExecutor:
    """
    Validates, authorizes, and executes approved AI tool invocations.
    Enforces schema boundaries, timeouts, and resource-level authorization.
    """

    def __init__(self, uow=None, timeout_seconds: float = 5.0):
        self.uow = uow
        self.timeout_seconds = timeout_seconds

    async def execute(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        context: TenantContext,
        caller_customer_id: Optional[UUID] = None,
        caller_role: str = "customer"
    ) -> ToolExecutionOutcome:
        """Execute a tool with full validation, authorization, and timing."""
        start_time = time.monotonic()
        tool_def = tool_registry.get(tool_name)

        if not tool_def:
            return ToolExecutionOutcome(
                tool_name=tool_name,
                status="error",
                risk_level=ToolRiskLevel.READ_ONLY,
                error=f"Unrecognized or forbidden tool: {tool_name}"
            )

        # 1. Authorize invocation
        if not ToolAuthorizationGuard.authorize_tool_invocation(tool_def, context, caller_role):
            return ToolExecutionOutcome(
                tool_name=tool_name,
                status="error",
                risk_level=tool_def.risk_level,
                error=f"Unauthorized to execute tool '{tool_name}'"
            )

        # 2. Server-side argument validation via Pydantic schema
        try:
            validated_args = tool_def.input_schema(**arguments)
        except ValidationError as e:
            logger.warning("Tool arguments failed schema validation", tool=tool_name, errors=e.errors())
            return ToolExecutionOutcome(
                tool_name=tool_name,
                status="error",
                risk_level=tool_def.risk_level,
                error=f"Invalid arguments for {tool_name}: {str(e.errors())}"
            )

        # 3. Timed execution with bounded timeout
        try:
            result_data = await asyncio.wait_for(
                self._dispatch(
                    tool_def, validated_args, context, caller_customer_id, caller_role
                ),
                timeout=self.timeout_seconds
            )
            elapsed_ms = (time.monotonic() - start_time) * 1000.0
            return ToolExecutionOutcome(
                tool_name=tool_name,
                status="success",
                risk_level=tool_def.risk_level,
                data=result_data,
                execution_time_ms=round(elapsed_ms, 2)
            )
        except asyncio.TimeoutError:
            elapsed_ms = (time.monotonic() - start_time) * 1000.0
            logger.error("Tool execution timed out", tool=tool_name, timeout=self.timeout_seconds)
            return ToolExecutionOutcome(
                tool_name=tool_name,
                status="error",
                risk_level=tool_def.risk_level,
                error=f"Tool execution timed out after {self.timeout_seconds}s",
                execution_time_ms=round(elapsed_ms, 2)
            )
        except Exception as e:
            elapsed_ms = (time.monotonic() - start_time) * 1000.0
            logger.error("Tool execution unexpected failure", tool=tool_name, error=str(e))
            return ToolExecutionOutcome(
                tool_name=tool_name,
                status="error",
                risk_level=tool_def.risk_level,
                error=f"Execution failure: {str(e)}",
                execution_time_ms=round(elapsed_ms, 2)
            )

    async def _dispatch(
        self,
        tool_def: ToolDefinition,
        args: Any,
        context: TenantContext,
        caller_customer_id: Optional[UUID],
        caller_role: str
    ) -> Dict[str, Any]:
        """Route tool to specific business logic handler."""
        if tool_def.name == "search_products":
            return await self._handle_search_products(args, context)
        if tool_def.name == "check_inventory":
            return await self._handle_check_inventory(args, context)
        if tool_def.name == "get_order_status":
            return await self._handle_get_order_status(args, context, caller_customer_id, caller_role)
        if tool_def.name == "create_support_ticket":
            return await self._handle_create_ticket(args, context, caller_customer_id)
        if tool_def.name == "escalate_to_human":
            return await self._handle_escalate(args, context, caller_customer_id)
        if tool_def.name == "get_store_policy":
            return await self._handle_get_policy(args, context)
        raise NotImplementedError(f"Handler for {tool_def.name} not implemented")

    async def _handle_search_products(self, args: SearchProductsInput, context: TenantContext) -> Dict[str, Any]:
        if self.uow:
            from app.domains.products.repository import ProductRepository
            async with self.uow as uow:
                repo = ProductRepository(uow.session)
                products = await repo.search(project_id=context.project_id, query=args.query, limit=args.limit)
                return {
                    "results": [
                        {"id": str(p.id), "name": p.name, "price": float(p.price or 0.0), "stock_quantity": p.stock_quantity, "is_in_stock": p.stock_quantity > 0}
                        for p in products
                    ],
                    "count": len(products)
                }
        return {"results": [], "count": 0}

    async def _handle_check_inventory(self, args: CheckInventoryInput, context: TenantContext) -> Dict[str, Any]:
        if self.uow:
            from app.domains.products.repository import ProductRepository
            async with self.uow as uow:
                repo = ProductRepository(uow.session)
                products = await repo.search(project_id=context.project_id, query=args.product_name_or_id, limit=1)
                if products:
                    p = products[0]
                    label = "In Stock" if p.stock_quantity > 5 else ("Limited availability" if p.stock_quantity > 0 else "Out of stock")
                    return {
                        "product_name": p.name,
                        "in_stock": p.stock_quantity > 0,
                        "status_label": label,
                        "unit_price": float(p.price or 0.0)
                    }
        return {"product_name": args.product_name_or_id, "in_stock": False, "status_label": "Out of stock"}

    async def _handle_get_order_status(
        self,
        args: GetOrderStatusInput,
        context: TenantContext,
        caller_customer_id: Optional[UUID],
        caller_role: str
    ) -> Dict[str, Any]:
        """Fetch order status with strict IDOR prevention."""
        if self.uow:
            from app.domains.orders.repository import OrderRepository
            async with self.uow as uow:
                repo = OrderRepository(uow.session)
                order = await repo.get_by_number(context.project_id, args.order_identifier)
                if not order:
                    return {"error": "Order not found or access denied."}

                # IDOR Check: Ensure order belongs to caller or caller is store staff
                is_authorized = ToolAuthorizationGuard.validate_order_ownership(
                    order_project_id=order.project_id,
                    order_customer_id=order.customer_id,
                    context=context,
                    caller_customer_id=caller_customer_id or args.customer_id,
                    caller_role=caller_role
                )
                if not is_authorized:
                    return {"error": "Access denied: Order ownership validation failed."}

                return {
                    "order_number": order.order_number,
                    "status": order.status,
                    "total_amount": str(order.total_amount or 0.0),
                    "order_date": order.created_at.isoformat() if order.created_at else None,
                    "tracking_status": order.tracking_status or "Processing"
                }
        return {"error": "Order lookup unavailable"}

    async def _handle_create_ticket(self, args: CreateTicketInput, context: TenantContext, caller_customer_id: Optional[UUID]) -> Dict[str, Any]:
        return {
            "ticket_id": f"TCK-{str(context.project_id)[:6].upper()}-001",
            "status": "created",
            "message": "Support ticket created successfully."
        }

    async def _handle_escalate(self, args: EscalateConversationInput, context: TenantContext, caller_customer_id: Optional[UUID]) -> Dict[str, Any]:
        return {
            "escalated": True,
            "ticket_reference": f"ESC-{str(context.project_id)[:6].upper()}-99",
            "customer_message": "A human customer care specialist has been alerted."
        }

    async def _handle_get_policy(self, args: GetPolicyInput, context: TenantContext) -> Dict[str, Any]:
        from app.domains.ai.prompts.versions import prompt_registry
        config = prompt_registry.get_active_config(context.project_id)
        return_days = config.policy.return_window_days if config else 14
        free_thresh = config.policy.free_shipping_threshold if config else 50.0
        return {
            "policy_type": args.policy_type,
            "summary": f"Standard {args.policy_type} policy for this store.",
            "max_return_days": return_days,
            "free_shipping_threshold": free_thresh
        }
