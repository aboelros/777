"""Add unique constraint for customer profile

Revision ID: ce0292e2228f
Revises: add_ai_profile_columns
Create Date: 2026-10-05 14:33:44.208478

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'ce0292e2228f'
down_revision: Union[str, None] = 'add_ai_profile_columns'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index('idx_customer_profile_project_customer', 'customer_profiles', ['project_id', 'customer_id'], unique=True)

def downgrade() -> None:
    op.drop_index('idx_customer_profile_project_customer', table_name='customer_profiles')
