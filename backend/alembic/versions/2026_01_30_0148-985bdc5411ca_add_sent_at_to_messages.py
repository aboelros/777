"""add_sent_at_to_messages

Revision ID: 985bdc5411ca
Revises: create_social_posts
Create Date: 2026-01-30 01:48:32.634895

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '985bdc5411ca'
down_revision: Union[str, None] = 'create_social_posts'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add sent_at column to messages table
    op.add_column('messages', sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    # Remove sent_at column from messages table
    op.drop_column('messages', 'sent_at')
