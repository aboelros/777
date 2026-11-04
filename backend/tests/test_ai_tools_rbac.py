"""
Unit and regression tests for AI Controlled Tools, RBAC, and IDOR protection.
Verifies server-side argument validation, tenant isolation, and customer resource checks.
"""

import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock
from app.core.context import TenantContext
from app.domains.ai.tools.schemas import ToolRiskLevel
from app.domains.ai.tools.registry import tool_registry, ToolDefinition
from app.domains.ai.tools.guard import ToolAuthorizationGuard
from app.domains.ai.tools.executor import SecureToolExecutor


def test_tool_registry_spec_and_allowlist():
    assert tool_registry.is_allowed("search_products") is True
    assert tool_registry.is_allowed("check_inventory") is True
    assert tool_registry.is_allowed("get_order_status") is True
    assert tool_registry.is_allowed("unapproved_hack_tool") is False

    declarations = tool_registry.get_declarations_for_llm()
    assert len(declarations) >= 5
    tool_names = [d["name"] for d in declarations]
    assert "search_products" in tool_names
    assert "get_order_status" in tool_names


def test_tool_authorization_guard_idor_protection():
    proj_a = uuid4()
    proj_b = uuid4()
    cust_alice = uuid4()
    cust_bob = uuid4()

    ctx_tenant_a = TenantContext(project_id=proj_a, roles=["customer"])

    # IDOR Test 1: Customer Alice tries to access Customer Bob's order in Tenant A -> DENIED
    denied = ToolAuthorizationGuard.validate_order_ownership(
        order_project_id=proj_a,
        order_customer_id=cust_bob,
        context=ctx_tenant_a,
        caller_customer_id=cust_alice,
        caller_role="customer"
    )
    assert denied is False

    # IDOR Test 2: Customer Alice accesses her own order in Tenant A -> ALLOWED
    allowed = ToolAuthorizationGuard.validate_order_ownership(
        order_project_id=proj_a,
        order_customer_id=cust_alice,
        context=ctx_tenant_a,
        caller_customer_id=cust_alice,
        caller_role="customer"
    )
    assert allowed is True

    # IDOR Test 3: Cross-tenant access: Alice tries to access order belonging to Tenant B -> DENIED
    cross_denied = ToolAuthorizationGuard.validate_order_ownership(
        order_project_id=proj_b,
        order_customer_id=cust_alice,
        context=ctx_tenant_a,
        caller_customer_id=cust_alice,
        caller_role="customer"
    )
    assert cross_denied is False

    # IDOR Test 4: Store owner/staff in Tenant A can query any order in Tenant A -> ALLOWED
    ctx_owner = TenantContext(project_id=proj_a, roles=["owner"])
    staff_allowed = ToolAuthorizationGuard.validate_order_ownership(
        order_project_id=proj_a,
        order_customer_id=cust_bob,
        context=ctx_owner,
        caller_customer_id=None,
        caller_role="owner"
    )
    assert staff_allowed is True


@pytest.mark.asyncio
async def test_secure_tool_executor_validation_and_unauthorized():
    executor = SecureToolExecutor(uow=None)
    proj_id = uuid4()
    ctx = TenantContext(project_id=proj_id, roles=["customer"])

    # 1. Unregistered tool is rejected safely
    outcome_unreg = await executor.execute(
        tool_name="drop_database",
        arguments={},
        context=ctx
    )
    assert outcome_unreg.status == "error"
    assert "Unrecognized" in outcome_unreg.error

    # 2. Invalid arguments fail Pydantic validation (e.g. limit < 1)
    outcome_invalid = await executor.execute(
        tool_name="search_products",
        arguments={"limit": -5},
        context=ctx
    )
    assert outcome_invalid.status == "error"
    assert "Invalid arguments" in outcome_invalid.error

    # 3. Valid arguments pass schema validation
    outcome_policy = await executor.execute(
        tool_name="get_store_policy",
        arguments={"policy_type": "return"},
        context=ctx
    )
    assert outcome_policy.status == "success"
    assert outcome_policy.data.get("policy_type") == "return"
