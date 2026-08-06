import structlog
from typing import Dict, Any, Optional, List
from uuid import UUID

from app.core.uow import UnitOfWork
from app.domains.products.repository import ProductRepository
from app.domains.orders.repository import OrderRepository

logger = structlog.get_logger(__name__)

class ToolExecutor:
    """
    Executes functions requested by LLMs (OpenAI, Gemini).
    Decouples LLM tool definitions from actual business logic execution.
    """
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def execute_tool(self, project_id: UUID, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Route tool calls to specific implementations."""
        logger.info(f"Executing tool: {tool_name}", project_id=str(project_id), args=arguments)
        
        tool_map = {
            "search_products": self.search_products,
            "get_order_status": self.get_order_status,
            "check_inventory": self.check_inventory
        }
        
        handler = tool_map.get(tool_name)
        if not handler:
            return {"error": f"Tool '{tool_name}' not recognized."}
            
        try:
            return await handler(project_id, **arguments)
        except Exception as e:
            logger.error(f"Tool execution failed: {tool_name}", error=str(e))
            return {"error": f"Failed to execute {tool_name}: {str(e)}"}

    async def search_products(self, project_id: UUID, query: str = "", limit: int = 5) -> Dict[str, Any]:
        """Tool: Search for products in the store."""
        async with self.uow as uow:
            repo = ProductRepository(uow.session)
            products = await repo.search(project_id=project_id, query=query, limit=limit)
            return {
                "results": [
                    {"id": str(p.id), "name": p.name, "price": p.price, "stock": p.stock_quantity} 
                    for p in products
                ],
                "count": len(products)
            }

    async def get_order_status(self, project_id: UUID, order_number: str) -> Dict[str, Any]:
        """Tool: Get the status of an order."""
        async with self.uow as uow:
            repo = OrderRepository(uow.session)
            order = await repo.get_by_number(project_id, order_number)
            if not order:
                return {"error": "Order not found."}
            
            return {
                "order_number": order.order_number,
                "status": order.status,
                "total": str(order.total_amount),
                "created_at": order.created_at.isoformat() if order.created_at else None
            }
            
    async def check_inventory(self, project_id: UUID, product_id: str) -> Dict[str, Any]:
        """Tool: Check specific inventory for a product."""
        async with self.uow as uow:
            repo = ProductRepository(uow.session)
            product = await repo.get(UUID(product_id))
            if not product or product.project_id != project_id:
                return {"error": "Product not found."}
                
            return {
                "name": product.name,
                "in_stock": product.stock_quantity > 0,
                "quantity": product.stock_quantity
            }
