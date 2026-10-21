"""
Meta App Review test account datasets coordinator.
Aggregates modular account datasets for seeding.
"""

from typing import List, Dict, Any
from .meta_review_data_fashion import FASHION_AND_GOURMET_ACCOUNTS
from .meta_review_data_tech import TECH_AND_WELLNESS_ACCOUNTS

META_TEST_ACCOUNTS: List[Dict[str, Any]] = (
    FASHION_AND_GOURMET_ACCOUNTS + TECH_AND_WELLNESS_ACCOUNTS
)
