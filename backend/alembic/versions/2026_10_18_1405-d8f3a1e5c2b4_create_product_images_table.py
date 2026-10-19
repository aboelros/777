"""create_product_images_table

Revision ID: d8f3a1e5c2b4
Revises: b7d41f09e2a1
Create Date: 2026-10-18 14:05:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'd8f3a1e5c2b4'
down_revision: Union[str, None] = 'b7d41f09e2a1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'product_images',
        sa.Column('key', sa.String(length=500), nullable=False),
        sa.Column('project_id', sa.UUID(), nullable=True),
        sa.Column('data', sa.LargeBinary(), nullable=False),
        sa.Column('content_type', sa.String(length=100), nullable=False),
        sa.Column('size', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('key')
    )
    op.create_index('idx_product_images_project_id', 'product_images', ['project_id'], unique=False)

    # Tenant security: Enable RLS to prevent direct API/PostgREST exposure (anon/authenticated default deny).
    # Application backend connects with rolbypassrls=true, so application-level WHERE project_id predicates
    # are strictly required for backend isolation.
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("ALTER TABLE product_images ENABLE ROW LEVEL SECURITY")


def downgrade() -> None:
    op.drop_index('idx_product_images_project_id', table_name='product_images')
    op.drop_table('product_images')
