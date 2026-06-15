"""Add storage fields to products

Revision ID: add_product_storage_fields
Revises: add_usage_tracking
Create Date: 2025-11-20 18:30:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "add_product_storage_fields"
down_revision = "add_usage_tracking"
branch_labels = None
depends_on = None


PRODUCT_TABLE = "products"


def _column_exists(inspector, table_name: str, column_name: str) -> bool:
    columns = [col["name"] for col in inspector.get_columns(table_name)]
    return column_name in columns


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if inspector.has_table(PRODUCT_TABLE):
        if not _column_exists(inspector, PRODUCT_TABLE, "storage_locations"):
            op.add_column(
                PRODUCT_TABLE,
                sa.Column(
                    "storage_locations",
                    postgresql.JSONB(astext_type=sa.Text()),
                    nullable=False,
                    server_default=sa.text("'[]'::jsonb"),
                ),
            )

        if not _column_exists(inspector, PRODUCT_TABLE, "reorder_point"):
            op.add_column(
                PRODUCT_TABLE,
                sa.Column("reorder_point", sa.Integer(), nullable=False, server_default="0"),
            )

        if not _column_exists(inspector, PRODUCT_TABLE, "safety_stock"):
            op.add_column(
                PRODUCT_TABLE,
                sa.Column("safety_stock", sa.Integer(), nullable=False, server_default="0"),
            )

        if not _column_exists(inspector, PRODUCT_TABLE, "storage_notes"):
            op.add_column(
                PRODUCT_TABLE,
                sa.Column("storage_notes", sa.Text(), nullable=True),
            )

        if not _column_exists(inspector, PRODUCT_TABLE, "storage_attachments"):
            op.add_column(
                PRODUCT_TABLE,
                sa.Column(
                    "storage_attachments",
                    postgresql.JSONB(astext_type=sa.Text()),
                    nullable=False,
                    server_default=sa.text("'[]'::jsonb"),
                ),
            )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if inspector.has_table(PRODUCT_TABLE):
        for column in [
            "storage_attachments",
            "storage_notes",
            "safety_stock",
            "reorder_point",
            "storage_locations",
        ]:
            if _column_exists(inspector, PRODUCT_TABLE, column):
                op.drop_column(PRODUCT_TABLE, column)
