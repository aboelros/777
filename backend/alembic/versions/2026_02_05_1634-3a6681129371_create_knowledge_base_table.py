"""create_knowledge_base_table

Revision ID: 3a6681129371
Revises: increase_avatar_len
Create Date: 2026-02-05 16:34:44.164762

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '3a6681129371'
down_revision: Union[str, None] = 'increase_avatar_len'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Ensure ProjectRole enum exists
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'projectrole') THEN
                CREATE TYPE projectrole AS ENUM ('OWNER', 'ADMIN', 'MODERATOR', 'WORKER');
            END IF;
        END$$;
    """)

    # 2. Create project_members table
    op.create_table(
        'project_members',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('project_id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('role', postgresql.ENUM('OWNER', 'ADMIN', 'MODERATOR', 'WORKER', name='projectrole', create_type=False), nullable=False, server_default='WORKER'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('project_id', 'user_id', name='idx_member_project_user')
    )
    op.create_index('ix_member_role', 'project_members', ['role'], unique=False)

    # 3. Create knowledge_base table
    op.create_table(
        'knowledge_base',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('project_id', sa.UUID(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('source_type', sa.String(length=50), nullable=True, server_default='text'),
        sa.Column('source_url', sa.String(length=500), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('tags', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='[]'),
        sa.Column('metadata_info', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_kb_project', 'knowledge_base', ['project_id'], unique=False)
    op.create_index('idx_kb_active', 'knowledge_base', ['is_active'], unique=False)


def downgrade() -> None:
    op.drop_index('idx_kb_active', table_name='knowledge_base')
    op.drop_index('idx_kb_project', table_name='knowledge_base')
    op.drop_table('knowledge_base')
    op.drop_index('ix_member_role', table_name='project_members')
    op.drop_table('project_members')
    # Custom type removal (careful in production)
    # op.execute("DROP TYPE projectrole")
