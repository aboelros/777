import structlog
from typing import Dict, Any, Optional, List
from uuid import UUID

from app.core.uow import UnitOfWork
from app.core.context import TenantContext
from app.domains.products.repository import ProductRepository
from app.domains.orders.repository import OrderRepository
from app.domains.ai.tools.executor import SecureToolExecutor
from app.domains.ai.tools.guard import ToolAuthorizationGuard

logger = structlog.get_logger(__name__)


class ToolExecutor:
    """
    Executes functions requested by LLMs (OpenAI, Gemini).
    Enforces tenant context isolation and IDOR protection on order lookups.
    """

    def __init__(self, uow: UnitOfWork):
        self.uow = uow
        self.secure_executor = SecureToolExecutor(uow=uow)

    async def execute_tool(
        self,
        project_id: UUID,
        tool_name: str,
        arguments: Dict[str, Any],
        customer_id: Optional[UUID] = None,
        caller_role: str = "customer"
    ) -> Dict[str, Any]:
        """Route tool calls through the secure executor with authorization and IDOR guards."""
        logger.info(
            "Executing tool via secure executor",
            project_id=str(project_id),
            tool=tool_name,
            caller_role=caller_role
        )

        context = TenantContext(project_id=project_id, roles=[caller_role])
        outcome = await self.secure_executor.execute(
            tool_name=tool_name,
            arguments=arguments,
            context=context,
            caller_customer_id=customer_id,
            caller_role=caller_role
        )

        if outcome.status == "error":
            return {"error": outcome.error}
        return outcome.data

    async def search_products(
        self,
        project_id: UUID,
        query: str = "",
        limit: int = 5
    ) -> Dict[str, Any]:
        """Tool: Search for products in the store."""
        async with self.uow as uow:
            repo = ProductRepository(uow.session)
            products = await repo.search(project_id=project_id, query=query, limit=limit)
            return {
                "results": [
                    {"id": str(p.id), "name": p.name, "price": float(p.price or 0.0), "stock": p.stock_quantity}
                    for p in products
                ],
                "count": len(products)
            }

    async def get_order_status(
        self,
        project_id: UUID,
        order_number: str,
        customer_id: Optional[UUID] = None,
        caller_role: str = "customer"
    ) -> Dict[str, Any]:
        """Tool: Get order status with server-side customer IDOR verification."""
        async with self.uow as uow:
            repo = OrderRepository(uow.session)
            order = await repo.get_by_number(project_id, order_number)
            if not order:
                return {"error": "Order not found."}

            context = TenantContext(project_id=project_id, roles=[caller_role])
            is_valid = ToolAuthorizationGuard.validate_order_ownership(
                order_project_id=order.project_id,
                order_customer_id=order.customer_id,
                context=context,
                caller_customer_id=customer_id,
                caller_role=caller_role
            )
            if not is_valid:
                return {"error": "Access denied: You are not authorized to view this order."}

            return {
                "order_number": order.order_number,
                "status": order.status,
                "total": str(order.total_amount),
                "created_at": order.created_at.isoformat() if order.created_at else None
            }

    async def check_inventory(
        self,
        project_id: UUID,
        product_id: Optional[str] = None,
        query: Optional[str] = None
    ) -> Dict[str, Any]:
        """Tool: Check specific inventory for a product by id or search query."""
        async with self.uow as uow:
            repo = ProductRepository(uow.session)
            if product_id:
                try:
                    product = await repo.get(UUID(product_id))
                    if product and product.project_id == project_id:
                        return {
                            "name": product.name,
                            "in_stock": product.stock_quantity > 0,
                            "quantity": product.stock_quantity
                        }
                except ValueError:
                    pass

            # Fallback to search by name/query
            search_str = query or product_id or ""
            products = await repo.search(project_id=project_id, query=search_str, limit=1)
            if products:
                p = products[0]
                return {
                    "name": p.name,
                    "in_stock": p.stock_quantity > 0,
                    "quantity": p.stock_quantity
                }

            return {"error": "Product not found."}
