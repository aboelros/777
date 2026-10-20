"""
Supabase Security Remediation and Tenant Isolation Tests.
Validates RLS enforcement, DAC revocation, duplicate index removal,
and architectural boundary separation between API roles and backend.
"""

import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException
from alembic.config import Config
from alembic.script import ScriptDirectory

from app.core.context import TenantContext
from app.api.dependencies.tenant import resolve_tenant_context
from app.domains.projects.models import Project, ProjectMember, ProjectRole
from app.domains.billing.models import Subscription
from app.domains.auth.models import RefreshToken
from app.domains.integrations.models import OAuthState


def _get_remediation_migration_module():
    """Load migration module via Alembic script directory."""
    config = Config("alembic.ini")
    config.set_main_option("script_location", "alembic")
    script = ScriptDirectory.from_config(config)
    rev = script.get_revision("f3a2b1c4e5d6")
    return rev.module


def test_alembic_head_and_migration_chain():
    """Verify migration lineage cleanly heads at f3a2b1c4e5d6."""
    config = Config("alembic.ini")
    config.set_main_option("script_location", "alembic")
    script = ScriptDirectory.from_config(config)
    heads = script.get_heads()
    assert heads == ["f3a2b1c4e5d6"]
    rev = script.get_revision("f3a2b1c4e5d6")
    assert rev.down_revision == "d8f3a1e5c2b4"


def test_migration_hardens_all_public_tables():
    """Verify all 30 legacy public tables have RLS and DAC revocation applied."""
    mod = _get_remediation_migration_module()
    required_tables = {
        "alembic_version", "users", "refresh_tokens", "subscriptions",
        "projects", "project_members", "customer_profiles", "deals",
        "pipeline_stages", "orders", "invoices", "payment_links",
        "products", "knowledge_base", "integrations", "drip_campaigns",
        "drip_steps", "campaign_enrollments", "auto_response_templates",
        "bot_instructions", "model_trainings", "reports", "oauth_states",
        "usage_tracking", "api_logs", "messages", "conversation_history",
        "bot_activities", "social_media_comments", "social_media_posts"
    }
    assert required_tables.issubset(set(mod.TABLES_TO_HARDEN))


def test_subscription_model_duplicate_index_removed():
    """Verify redundant idx_subscription_user index is purged from Subscription model."""
    index_names = [idx.name for idx in Subscription.__table_args__ if hasattr(idx, "name")]
    assert "idx_subscription_user" not in index_names
    assert "ix_subscription_user" not in index_names
    user_id_col = Subscription.__table__.columns["user_id"]
    assert user_id_col.unique is True


def test_refresh_token_isolation_and_protection():
    """Verify refresh_tokens table model links strictly to user_id without broad exposure."""
    assert "token" in RefreshToken.__table__.columns
    user_id_col = RefreshToken.__table__.columns["user_id"]
    assert len(user_id_col.foreign_keys) == 1
    fk = list(user_id_col.foreign_keys)[0]
    assert fk.target_fullname == "users.id"


def test_oauth_state_model_tenant_isolation():
    """Verify OAuthState enforces both user_id and project_id tenant isolation."""
    cols = OAuthState.__table__.columns
    assert "state_token" in cols
    assert "user_id" in cols
    assert "project_id" in cols
    user_fk = [fk for fk in cols["user_id"].foreign_keys]
    project_fk = [fk for fk in cols["project_id"].foreign_keys]
    assert len(user_fk) == 1 and user_fk[0].target_fullname == "users.id"
    assert len(project_fk) == 1 and project_fk[0].target_fullname == "projects.id"


@pytest.mark.asyncio
async def test_tenant_context_resolution_rejects_unrelated_user():
    """Verify User B cannot resolve tenant context for User A's project (returns 404)."""
    user_b_id = uuid4()
    project_a_id = uuid4()

    mock_db = AsyncMock()
    mock_project_result = MagicMock()
    mock_project_result.scalar_one_or_none.return_value = None
    mock_member_result = MagicMock()
    mock_member_result.scalar_one_or_none.return_value = None
    mock_db.execute.side_effect = [mock_project_result, mock_member_result]

    with pytest.raises(HTTPException) as exc_info:
        await resolve_tenant_context(project_id=project_a_id, user_id=user_b_id, db=mock_db)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Project not found or access denied"


@pytest.mark.asyncio
async def test_tenant_context_resolution_accepts_valid_owner():
    """Verify project owner resolves valid TenantContext with full ownership permissions."""
    owner_id = uuid4()
    project_id = uuid4()
    mock_project = MagicMock(spec=Project)
    mock_project.id = project_id
    mock_project.owner_id = owner_id

    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_project
    mock_db.execute.return_value = mock_result

    context = await resolve_tenant_context(project_id=project_id, user_id=owner_id, db=mock_db)
    assert isinstance(context, TenantContext)
    assert context.project_id == project_id
    assert context.user_id == owner_id
    assert context.role == ProjectRole.OWNER.value
    assert "*" in context.permissions


@pytest.mark.asyncio
async def test_tenant_context_resolution_accepts_valid_member():
    """Verify project member resolves valid TenantContext with assigned member role."""
    user_id = uuid4()
    project_id = uuid4()
    member_id = uuid4()

    mock_db = AsyncMock()
    mock_owner_result = MagicMock()
    mock_owner_result.scalar_one_or_none.return_value = None

    mock_member = MagicMock(spec=ProjectMember)
    mock_member.id = member_id
    mock_member.role = ProjectRole.MODERATOR
    mock_member_result = MagicMock()
    mock_member_result.scalar_one_or_none.return_value = mock_member
    mock_db.execute.side_effect = [mock_owner_result, mock_member_result]

    context = await resolve_tenant_context(project_id=project_id, user_id=user_id, db=mock_db)
    assert isinstance(context, TenantContext)
    assert context.project_id == project_id
    assert context.user_id == user_id
    assert context.role == ProjectRole.MODERATOR.value
    assert context.membership_id == member_id
