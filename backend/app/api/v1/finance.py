from typing import Any, Dict, List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Body, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.context import TenantContext
from app.api.dependencies.tenant import get_tenant_context
from app.domains.finance.schemas import (
    FinancialOverviewResponse,
    ScenarioSimulationConfig,
    ValuationSummary,
    MarketOpportunityRegion,
    UnitEconomicsBreakdown
)
from app.domains.finance.service import FinanceService
from app.domains.finance.scenario_engine import ScenarioEngine
from app.domains.finance.market_engine import MarketOpportunityEngine

router = APIRouter()


@router.get("/{project_id}/overview", response_model=FinancialOverviewResponse)
async def get_financial_overview(
    project_id: UUID,
    tenant: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get executive financial command center overview.
    Combines actual historical revenue with 36-month baseline projections and valuation.
    """
    if tenant.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: cannot view financial data of another project"
        )
    
    service = FinanceService(db=db)
    return await service.get_comprehensive_overview(project_id=project_id)


@router.post("/{project_id}/simulate", response_model=FinancialOverviewResponse)
async def simulate_scenario(
    project_id: UUID,
    config: ScenarioSimulationConfig = Body(...),
    tenant: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Execute real-time interactive financial simulation with custom user parameters.
    Re-computes all 36-month statements, unit economics, and valuation in milliseconds.
    """
    if tenant.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: cannot simulate financial data for another project"
        )

    service = FinanceService(db=db)
    return await service.get_comprehensive_overview(project_id=project_id, config_override=config)


@router.get("/{project_id}/scenarios", response_model=Dict[str, Any])
async def get_scenario_comparison(
    project_id: UUID,
    tenant: TenantContext = Depends(get_tenant_context),
    months: int = 36
) -> Any:
    """
    Get side-by-side comparison of Conservative, Base Case, and Aggressive scenarios.
    """
    if tenant.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: cannot view financial data of another project"
        )

    return ScenarioEngine.compare_scenarios(months=months)


@router.get("/{project_id}/valuation", response_model=ValuationSummary)
async def get_company_valuation(
    project_id: UUID,
    tenant: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get independent 5-method company valuation with EV, Equity Value, and DCF.
    """
    if tenant.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: cannot view valuation data of another project"
        )

    service = FinanceService(db=db)
    overview = await service.get_comprehensive_overview(project_id=project_id)
    return overview.valuation


@router.get("/{project_id}/market-opportunity", response_model=List[MarketOpportunityRegion])
async def get_market_opportunity(
    project_id: UUID,
    tenant: TenantContext = Depends(get_tenant_context)
) -> Any:
    """
    Get global market TAM / SAM / SOM across Egypt, Saudi Arabia, UAE, GCC, US, UK, and EU.
    """
    if tenant.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: cannot access market data for another project"
        )

    return MarketOpportunityEngine.calculate_regional_opportunities()


@router.get("/{project_id}/unit-economics", response_model=UnitEconomicsBreakdown)
async def get_unit_economics(
    project_id: UUID,
    tenant: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get per-customer contribution margin, CAC payback, and break-even customer targets.
    """
    if tenant.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: cannot view economics data of another project"
        )

    service = FinanceService(db=db)
    overview = await service.get_comprehensive_overview(project_id=project_id)
    return overview.unit_economics
