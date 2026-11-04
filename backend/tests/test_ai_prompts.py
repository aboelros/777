"""
Unit tests for AI prompt models, versioning registry, and XML builder.
Verifies tenant isolation, version hashing, and operational boundaries.
"""

import pytest
from uuid import uuid4
from app.domains.ai.prompts.models import (
    BrandProfile,
    SalesPolicy,
    ChannelConfig,
    TenantPromptConfig,
)
from app.domains.ai.prompts.versions import PromptRegistry
from app.domains.ai.prompts.builder import PromptBuilder


def test_tenant_prompt_config_defaults():
    project_id = uuid4()
    brand = BrandProfile(store_name="Cairo Sneaker Hub", bot_name="Kareem")
    policy = SalesPolicy(max_discount_percent=15.0, return_window_days=30)
    config = TenantPromptConfig(project_id=project_id, brand=brand, policy=policy)

    assert config.project_id == project_id
    assert config.brand.store_name == "Cairo Sneaker Hub"
    assert config.policy.max_discount_percent == 15.0
    assert config.policy.return_window_days == 30
    assert config.version == "1.0.0"


def test_prompt_registry_versioning_and_rollback():
    registry = PromptRegistry()
    project_id = uuid4()

    # Register v1
    cfg_v1 = TenantPromptConfig(
        project_id=project_id,
        brand=BrandProfile(store_name="Store Alpha"),
        version="1.0.0"
    )
    v1_info = registry.register_version(cfg_v1, activate=True)
    assert v1_info.is_active is True
    assert len(v1_info.sha256_hash) == 64

    # Register v2
    cfg_v2 = TenantPromptConfig(
        project_id=project_id,
        brand=BrandProfile(store_name="Store Alpha Super"),
        version="1.1.0"
    )
    v2_info = registry.register_version(cfg_v2, activate=True)
    assert v2_info.is_active is True

    # Active config is v2
    active = registry.get_active_config(project_id)
    assert active is not None
    assert active.version == "1.1.0"
    assert active.brand.store_name == "Store Alpha Super"

    # Roll back to v1
    rollback_info = registry.rollback(project_id, "1.0.0")
    assert rollback_info is not None
    assert rollback_info.version == "1.0.0"
    assert rollback_info.is_active is True

    # Active config is now v1 again
    active_now = registry.get_active_config(project_id)
    assert active_now is not None
    assert active_now.version == "1.0.0"
    assert active_now.brand.store_name == "Store Alpha"


def test_prompt_builder_strict_delimiters_and_isolation():
    proj_a = uuid4()
    proj_b = uuid4()

    cfg_a = TenantPromptConfig(
        project_id=proj_a,
        brand=BrandProfile(store_name="Store A"),
        policy=SalesPolicy(max_discount_percent=5.0)
    )
    cfg_b = TenantPromptConfig(
        project_id=proj_b,
        brand=BrandProfile(store_name="Store B"),
        policy=SalesPolicy(max_discount_percent=25.0)
    )

    prompt_a = PromptBuilder.build_system_prompt(cfg_a)
    prompt_b = PromptBuilder.build_system_prompt(cfg_b)

    # Delimiters present
    assert "<SYSTEM_INSTRUCTIONS" in prompt_a
    assert "<BRAND_IDENTITY" in prompt_a
    assert "<OPERATIONAL_BOUNDARIES>" in prompt_a

    # Tenant isolation: Store B info not in Store A
    assert "Store A" in prompt_a
    assert "Store B" not in prompt_a
    assert "5.0%" in prompt_a
    assert "25.0%" not in prompt_a

    # User turn assembly
    turn = PromptBuilder.assemble_user_turn(
        customer_message="Do you have size 42?",
        retrieved_evidence="Size 42 in stock.",
        conversation_history=[{"role": "assistant", "content": "Welcome!"}]
    )
    assert "<RETRIEVED_EVIDENCE>" in turn
    assert "Size 42 in stock." in turn
    assert "<CONVERSATION_HISTORY>" in turn
    assert "<UNTRUSTED_CUSTOMER_INPUT>" in turn
    assert "Do you have size 42?" in turn
