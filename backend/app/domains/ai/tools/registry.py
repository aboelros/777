from typing import Dict, Any, List, Optional, Type
from pydantic import BaseModel
from .schemas import (
    ToolRiskLevel,
    SearchProductsInput,
    CheckInventoryInput,
    GetOrderStatusInput,
    CreateTicketInput,
    EscalateConversationInput,
    GetPolicyInput
)


class ToolDefinition(BaseModel):
    """Specification of an approved AI tool."""
    name: str
    description: str
    risk_level: ToolRiskLevel
    input_schema: Type[BaseModel]
    requires_human_confirmation: bool = False
    allowed_for_customers: bool = True


class ToolRegistry:
    """
    Catalog of strictly authorized tools.
    Disallows dynamic discovery of arbitrary Python code.
    """

    def __init__(self):
        self._tools: Dict[str, ToolDefinition] = {}
        self._register_default_tools()

    def register(self, tool_def: ToolDefinition):
        """Register an approved tool definition."""
        self._tools[tool_def.name] = tool_def

    def get(self, tool_name: str) -> Optional[ToolDefinition]:
        """Fetch tool definition if present in allowlist."""
        return self._tools.get(tool_name)

    def is_allowed(self, tool_name: str) -> bool:
        """Check if tool exists in the approved allowlist."""
        return tool_name in self._tools

    def get_declarations_for_llm(self) -> List[Dict[str, Any]]:
        """Export function calling declarations compatible with LLM providers."""
        declarations = []
        for name, tool_def in self._tools.items():
            schema = tool_def.input_schema.model_json_schema()
            declarations.append({
                "name": name,
                "description": tool_def.description,
                "parameters": {
                    "type": "object",
                    "properties": schema.get("properties", {}),
                    "required": schema.get("required", [])
                }
            })
        return declarations

    def _register_default_tools(self):
        """Initialize the standard production toolset."""
        self.register(ToolDefinition(
            name="search_products",
            description="Search the store product catalog by keyword or view all available items.",
            risk_level=ToolRiskLevel.READ_ONLY,
            input_schema=SearchProductsInput,
            allowed_for_customers=True
        ))
        self.register(ToolDefinition(
            name="check_inventory",
            description="Verify real-time stock availability and unit price for a specific product.",
            risk_level=ToolRiskLevel.READ_ONLY,
            input_schema=CheckInventoryInput,
            allowed_for_customers=True
        ))
        self.register(ToolDefinition(
            name="get_order_status",
            description="Retrieve status and tracking updates for a customer order by order number.",
            risk_level=ToolRiskLevel.READ_ONLY,
            input_schema=GetOrderStatusInput,
            allowed_for_customers=True
        ))
        self.register(ToolDefinition(
            name="create_support_ticket",
            description="Create a customer service ticket when an issue requires staff assistance.",
            risk_level=ToolRiskLevel.STATE_CHANGING,
            input_schema=CreateTicketInput,
            allowed_for_customers=True
        ))
        self.register(ToolDefinition(
            name="escalate_to_human",
            description="Escalate the active conversation to a live human representative.",
            risk_level=ToolRiskLevel.STATE_CHANGING,
            input_schema=EscalateConversationInput,
            allowed_for_customers=True
        ))
        self.register(ToolDefinition(
            name="get_store_policy",
            description="Retrieve verified return, shipping, or payment policy terms for this store.",
            risk_level=ToolRiskLevel.READ_ONLY,
            input_schema=GetPolicyInput,
            allowed_for_customers=True
        ))


# Global singleton tool registry
tool_registry = ToolRegistry()
