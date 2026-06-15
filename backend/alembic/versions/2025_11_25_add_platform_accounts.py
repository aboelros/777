"""Add platform_accounts to customer_profiles

Revision ID: add_platform_accounts
Revises: add_customer_id_column
Create Date: 2025-11-25 20:25:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'add_platform_accounts'
down_revision = 'add_customer_id_column'
branch_labels = None
depends_on = None


def upgrade():
    # Add platform_accounts column
    op.add_column('customer_profiles', 
        sa.Column('platform_accounts', postgresql.JSONB(astext_type=sa.Text()), nullable=True)
    )
    
    # Set default value for existing rows
    op.execute("UPDATE customer_profiles SET platform_accounts = '{}' WHERE platform_accounts IS NULL")


def downgrade():
    op.drop_column('customer_profiles', 'platform_accounts')
