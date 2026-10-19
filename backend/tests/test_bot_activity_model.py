"""
Unit and regression tests for BotActivity SQLAlchemy ORM model.

Verifies:
1. Declarative table name and metadata registration in Base.metadata.
2. Exact column schema, SQL types, nullability, and primary key definition.
3. Foreign key definitions for project_id and customer_id with ondelete actions.
4. Composite index idx_bot_activity_project matching migration 034157d2ccf7.
5. In-memory model instantiation, repr, and relationship configuration.
"""

import os
from uuid import uuid4
import pytest
from sqlalchemy import String, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB

# Configure safe test environment to permit in-memory schema inspection
os.environ["TESTING"] = "true"
os.environ["TEST_DATABASE_URL"] = "postgresql+asyncpg://mock:mock@localhost:5432/mock_test"
os.environ["APPROVED_TEST_DATABASE_URL"] = "postgresql+asyncpg://mock:mock@localhost:5432/mock_test"
os.environ["REQUIRE_TEST_DB_EXPLICIT_AUTHORIZATION"] = "true"

from app.core.config import get_settings
get_settings.cache_clear()

# Import models via legacy proxy to populate the complete registry in order
import app.db.models
from app.core.database import Base
from app.domains.ai.models import BotActivity
from app.domains.projects.models import Project
from app.domains.customers.models import CustomerProfile


def test_bot_activity_table_name():
    """Verify that BotActivity maps to table 'bot_activities'."""
    assert BotActivity.__tablename__ == "bot_activities"
    assert BotActivity.__table__.name == "bot_activities"
    assert "bot_activities" in Base.metadata.tables


def test_bot_activity_columns_schema():
    """Verify exact column definitions matching migration 034157d2ccf7."""
    columns = BotActivity.__table__.columns

    # Verify column existence
    expected_columns = {
        "id", "project_id", "customer_id",
        "activity_type", "description", "details", "created_at"
    }
    assert set(columns.keys()) == expected_columns

    # Column id
    id_col = columns["id"]
    assert id_col.primary_key is True
    assert isinstance(id_col.type, UUID)
    assert id_col.type.as_uuid is True

    # Column project_id
    proj_col = columns["project_id"]
    assert proj_col.nullable is False
    assert isinstance(proj_col.type, UUID)
    assert proj_col.type.as_uuid is True

    # Column customer_id
    cust_col = columns["customer_id"]
    assert cust_col.nullable is True
    assert isinstance(cust_col.type, UUID)
    assert cust_col.type.as_uuid is True

    # Column activity_type
    act_col = columns["activity_type"]
    assert act_col.nullable is False
    assert isinstance(act_col.type, String)
    assert act_col.type.length == 50

    # Column description
    desc_col = columns["description"]
    assert desc_col.nullable is True
    assert isinstance(desc_col.type, Text)

    # Column details
    det_col = columns["details"]
    assert det_col.nullable is True
    assert isinstance(det_col.type, JSONB)

    # Column created_at
    created_col = columns["created_at"]
    assert created_col.nullable is False
    assert isinstance(created_col.type, DateTime)
    assert created_col.type.timezone is True
    assert created_col.server_default is not None


def test_bot_activity_foreign_keys():
    """Verify foreign key target columns and ondelete behaviors."""
    columns = BotActivity.__table__.columns

    # project_id -> projects.id (CASCADE)
    proj_fks = list(columns["project_id"].foreign_keys)
    assert len(proj_fks) == 1
    assert proj_fks[0].target_fullname == "projects.id"
    assert proj_fks[0].ondelete.upper() == "CASCADE"

    # customer_id -> customer_profiles.id (SET NULL)
    cust_fks = list(columns["customer_id"].foreign_keys)
    assert len(cust_fks) == 1
    assert cust_fks[0].target_fullname == "customer_profiles.id"
    assert cust_fks[0].ondelete.upper() == "SET NULL"


def test_bot_activity_composite_index():
    """Verify composite index idx_bot_activity_project on (project_id, created_at)."""
    indexes = {idx.name: idx for idx in BotActivity.__table__.indexes}
    assert "idx_bot_activity_project" in indexes

    index = indexes["idx_bot_activity_project"]
    indexed_col_names = [col.name for col in index.columns]
    assert indexed_col_names == ["project_id", "created_at"]


def test_bot_activity_import_via_legacy_proxy():
    """Verify backward compatibility import via app.db.models."""
    from app.db.models import BotActivity as ProxiedBotActivity
    assert ProxiedBotActivity is BotActivity


def test_bot_activity_instantiation_and_repr():
    """Verify in-memory model instantiation and string representation."""
    act_id = uuid4()
    proj_id = uuid4()
    activity = BotActivity(
        id=act_id,
        project_id=proj_id,
        activity_type="order_created",
        description="Created test order",
        details={"order_id": "ord-123"},
    )
    assert activity.id == act_id
    assert activity.project_id == proj_id
    assert activity.activity_type == "order_created"
    assert activity.description == "Created test order"
    assert activity.details == {"order_id": "ord-123"}
    assert "order_created" in repr(activity)
    assert str(act_id) in repr(activity)
