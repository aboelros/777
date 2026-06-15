"""add_avatar_url_to_customer_profiles

Revision ID: edbe90bad4fd
Revises: 985bdc5411ca
Create Date: 2026-01-30 22:07:10.141972

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'edbe90bad4fd'
down_revision: Union[str, None] = '985bdc5411ca'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add avatar_url column to customer_profiles table"""
    op.add_column('customer_profiles', sa.Column('avatar_url', sa.String(length=500), nullable=True))


def downgrade() -> None:
    """Remove avatar_url column from customer_profiles table"""
    op.drop_column('customer_profiles', 'avatar_url')
