"""create_bot_activities_table

Revision ID: 034157d2ccf7
Revises: 2e1430bfa5b2
Create Date: 2025-11-28 23:35:26.664265

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '034157d2ccf7'
down_revision: Union[str, None] = '2e1430bfa5b2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

def upgrade() -> None:
    op.create_table(
        'bot_activities',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False),
        sa.Column('customer_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('customer_profiles.id', ondelete='SET NULL'), nullable=True),
        sa.Column('activity_type', sa.String(50), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('details', postgresql.JSONB, default={}),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('idx_bot_activity_project', 'bot_activities', ['project_id', 'created_at'])


def downgrade() -> None:
    op.drop_table('bot_activities')
