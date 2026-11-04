from typing import Dict, Any, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field


class UsageRecord(BaseModel):
    project_id: UUID
    input_tokens: int
    output_tokens: int
    estimated_cost_usd: float
    model_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class TokenCostTracker:
    """
    Monitors token consumption and estimated costs per tenant.
    Prevents unexpected budget depletion and flags abnormal traffic spikes.
    """

    # Price per million tokens (USD)
    RATES = {
        "gemini-2.0-flash": {"input": 0.10, "output": 0.40},
        "gemini-1.5-flash": {"input": 0.075, "output": 0.30},
        "gemini-1.5-pro": {"input": 1.25, "output": 5.00},
        "openrouter": {"input": 0.50, "output": 1.50},
    }

    def __init__(self, monthly_budget_usd: float = 50.0):
        # project_id -> list of UsageRecord
        self._usage_ledger: Dict[UUID, list[UsageRecord]] = {}
        self.default_monthly_budget_usd = monthly_budget_usd

    def record_usage(
        self,
        project_id: UUID,
        input_tokens: int,
        output_tokens: int,
        model_name: str = "gemini-2.0-flash"
    ) -> UsageRecord:
        """Record usage and compute cost."""
        rates = self.RATES.get(model_name, self.RATES["gemini-2.0-flash"])
        cost = (
            (input_tokens / 1_000_000.0) * rates["input"] +
            (output_tokens / 1_000_000.0) * rates["output"]
        )

        record = UsageRecord(
            project_id=project_id,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            estimated_cost_usd=round(cost, 6),
            model_name=model_name
        )

        if project_id not in self._usage_ledger:
            self._usage_ledger[project_id] = []
        self._usage_ledger[project_id].append(record)

        return record

    def get_tenant_spend(self, project_id: UUID) -> float:
        """Get aggregate spend in USD for a tenant."""
        records = self._usage_ledger.get(project_id, [])
        return sum(r.estimated_cost_usd for r in records)

    def is_within_budget(self, project_id: UUID) -> bool:
        """Verify tenant has not exceeded their cost ceiling."""
        return self.get_tenant_spend(project_id) < self.default_monthly_budget_usd


# Global tracker instance
token_cost_tracker = TokenCostTracker()
