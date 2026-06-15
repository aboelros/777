
"""increase_avatar_url_length

Revision ID: increase_avatar_len
Revises: 4389f273cede
Create Date: 2026-01-31 14:24:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'increase_avatar_len'
down_revision: Union[str, None] = '4389f273cede'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Change String(500) to Text for avatar_url
    op.execute("ALTER TABLE customer_profiles ALTER COLUMN avatar_url TYPE TEXT")

def downgrade() -> None:
    # Change back to String(500) - might truncate data if downgrading
    op.execute("ALTER TABLE customer_profiles ALTER COLUMN avatar_url TYPE VARCHAR(500)")
