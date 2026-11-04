from typing import Optional, Dict, Any
from uuid import UUID
import structlog
from app.core.context import TenantContext
from .schemas import ToolRiskLevel
from .registry import ToolDefinition

logger = structlog.get_logger(__name__)


class ToolAuthorizationGuard:
    """
    Enforces authorization, tenant isolation, and resource ownership (IDOR defense)
    prior to executing any AI tool invocation.
    """

    @staticmethod
    def authorize_tool_invocation(
        tool: ToolDefinition,
        context: TenantContext,
        caller_role: str = "customer"
    ) -> bool:
        """Verify caller is authorized to invoke this specific tool."""
        if not context or not context.project_id:
            logger.warning("Tool execution rejected: Missing valid TenantContext")
            return False

        if caller_role == "customer" and not tool.allowed_for_customers:
            logger.warning(
                "Tool execution rejected: Tool not allowed for customer role",
                tool=tool.name,
                caller_role=caller_role
            )
            return False

        return True

    @staticmethod
    def validate_order_ownership(
        order_project_id: UUID,
        order_customer_id: Optional[UUID],
        context: TenantContext,
        caller_customer_id: Optional[UUID],
        caller_role: str = "customer"
    ) -> bool:
        """
        Enforce strict IDOR protection for order queries and operations.
        1. Tenant boundaries: order must belong to active project.
        2. Customer boundaries: if caller is a customer, order must belong to them.
        """
        # Cross-tenant denial
        if order_project_id != context.project_id:
            logger.warning(
                "IDOR Guard Violation: Cross-tenant order access attempted",
                order_project=str(order_project_id),
                context_project=str(context.project_id)
            )
            return False

        # Privileged store staff bypass customer-specific ownership
        is_staff = caller_role in ("owner", "admin", "agent", "system")
        if is_staff:
            return True

        # Customer role must match the order's customer_id
        if caller_customer_id is None:
            logger.warning("IDOR Guard Violation: Anonymous caller attempted to read customer order")
            return False

        if order_customer_id is None or order_customer_id != caller_customer_id:
            logger.warning(
                "IDOR Guard Violation: Customer attempted to access another customer's order",
                caller_customer_id=str(caller_customer_id),
                order_customer_id=str(order_customer_id)
            )
            return False

        return True
