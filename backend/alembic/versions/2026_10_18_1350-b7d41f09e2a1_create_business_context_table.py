"""create_business_context_table

Revision ID: b7d41f09e2a1
Revises: c1412562210a
Create Date: 2026-10-18 13:50:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'b7d41f09e2a1'
down_revision: Union[str, None] = 'c1412562210a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'business_context',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('project_id', sa.UUID(), nullable=False),
        sa.Column('context_type', sa.String(length=100), nullable=False),
        sa.Column('context_key', sa.String(length=255), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('tags', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default=sa.text("'[]'::jsonb")),
        sa.Column('relevance_score', sa.Float(), nullable=True, server_default=sa.text('1.0')),
        sa.Column('times_used', sa.Integer(), nullable=True, server_default=sa.text('0')),
        sa.Column('learned_from', sa.String(length=100), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True, server_default=sa.text('0.5')),
        sa.Column('active_for_platforms', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default=sa.text("'[]'::jsonb")),
        sa.Column('examples', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default=sa.text("'[]'::jsonb")),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default=sa.text('true')),
        sa.Column('last_used', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_business_context_project', 'business_context', ['project_id'], unique=False)
    op.create_index('idx_business_context_type', 'business_context', ['context_type'], unique=False)
    op.create_index('idx_business_context_key', 'business_context', ['context_key'], unique=False)
    op.create_index('idx_business_context_used', 'business_context', ['times_used'], unique=False)

    # Tenant security: Enable RLS to prevent direct API/PostgREST exposure (anon/authenticated default deny).
    # Application backend connects with rolbypassrls=true, so application-level WHERE project_id predicates
    # are strictly required for backend isolation.
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("ALTER TABLE business_context ENABLE ROW LEVEL SECURITY")


def downgrade() -> None:
    op.drop_index('idx_business_context_used', table_name='business_context')
    op.drop_index('idx_business_context_key', table_name='business_context')
    op.drop_index('idx_business_context_type', table_name='business_context')
    op.drop_index('idx_business_context_project', table_name='business_context')
    op.drop_table('business_context')
