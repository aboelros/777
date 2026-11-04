"""
Finance API Endpoints & Authorization Tests.
Verifies REST API contracts, multi-tenant isolation, real-time simulation,
and 403 Forbidden protections.
"""

import pytest
from uuid import uuid4
from decimal import Decimal
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch

from app.main import app
from app.core.context import TenantContext
from app.api.dependencies.tenant import get_tenant_context


@pytest.fixture
def test_project_id():
    return uuid4()


@pytest.fixture
def mock_tenant_context(test_project_id):
    return TenantContext(project_id=test_project_id, roles=["owner"])


@pytest.mark.asyncio
async def test_finance_api_overview_success(test_project_id, mock_tenant_context):
    """Verify GET /api/v1/finance/{project_id}/overview returns full financial statement."""
    app.dependency_overrides[get_tenant_context] = lambda: mock_tenant_context
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get(f"/api/v1/finance/{test_project_id}/overview")
            assert resp.status_code == 200
            data = resp.json()
            assert "current_actual_mrr" in data
            assert len(data["projections_36_months"]) == 36
            assert len(data["annual_summaries"]) == 3
            assert "valuation" in data
            assert "unit_economics" in data
    finally:
        app.dependency_overrides.pop(get_tenant_context, None)


@pytest.mark.asyncio
async def test_finance_api_cross_tenant_forbidden(test_project_id, mock_tenant_context):
    """Verify attempting to access another tenant's financial data returns 403 Forbidden."""
    another_project_id = uuid4()
    app.dependency_overrides[get_tenant_context] = lambda: mock_tenant_context
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get(f"/api/v1/finance/{another_project_id}/overview")
            assert resp.status_code == 403
            assert "forbidden" in resp.json()["detail"].lower()
    finally:
        app.dependency_overrides.pop(get_tenant_context, None)


@pytest.mark.asyncio
async def test_finance_api_simulate_custom_parameters(test_project_id, mock_tenant_context):
    """Verify POST /api/v1/finance/{project_id}/simulate dynamically recomputes statement."""
    app.dependency_overrides[get_tenant_context] = lambda: mock_tenant_context
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            payload = {
                "scenario_name": "High Velocity Scale",
                "starting_customers": 50,
                "monthly_growth_rate_pct": 20.0,
                "monthly_churn_rate_pct": 2.5,
                "average_monthly_plan_usd": 99.0,
                "fixed_opex_monthly_usd": 6000.0,
                "starting_cash_balance_usd": 50000.0
            }
            resp = await client.post(f"/api/v1/finance/{test_project_id}/simulate", json=payload)
            assert resp.status_code == 200
            data = resp.json()
            # Month 1 customers should reflect custom starting base
            m1 = data["projections_36_months"][0]
            assert m1["active_customers"] > 50
    finally:
        app.dependency_overrides.pop(get_tenant_context, None)


@pytest.mark.asyncio
async def test_finance_api_scenarios_and_market_opportunity(test_project_id, mock_tenant_context):
    """Verify scenario comparison and regional market endpoints."""
    app.dependency_overrides[get_tenant_context] = lambda: mock_tenant_context
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Scenarios
            resp_scen = await client.get(f"/api/v1/finance/{test_project_id}/scenarios")
            assert resp_scen.status_code == 200
            scens = resp_scen.json()
            assert "conservative" in scens
            assert "base_case" in scens
            assert "aggressive" in scens

            # Market opportunity
            resp_mkt = await client.get(f"/api/v1/finance/{test_project_id}/market-opportunity")
            assert resp_mkt.status_code == 200
            regions = resp_mkt.json()
            assert len(regions) >= 6
            assert any(r["country"] == "Egypt" for r in regions)
            assert any(r["country"] == "Saudi Arabia" for r in regions)
    finally:
        app.dependency_overrides.pop(get_tenant_context, None)
