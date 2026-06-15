"""Add customer_id to customer_profiles

Revision ID: add_customer_id_column
Revises: customer_relationships_2024
Create Date: 2025-11-25 19:45:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_customer_id_column'
down_revision = 'customer_relationships_2024'
branch_labels = None
depends_on = None


def upgrade():
    # Add customer_id as nullable first
    op.add_column('customer_profiles', sa.Column('customer_id', sa.String(length=255), nullable=True))
    
    # Populate existing rows with phone_number
    op.execute("UPDATE customer_profiles SET customer_id = phone_number WHERE customer_id IS NULL")
    
    # Make it non-nullable
    op.alter_column('customer_profiles', 'customer_id', nullable=False)
    
    # Create index
    op.create_index('idx_customer_profile_customer_id', 'customer_profiles', ['customer_id'], unique=False)


def downgrade():
    op.drop_index('idx_customer_profile_customer_id', table_name='customer_profiles')
    op.drop_column('customer_profiles', 'customer_id')
