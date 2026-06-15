"""Add subscription fields to users table

Revision ID: add_subscription_fields
Revises: 6cecfbddb1a5
Create Date: 2025-11-11 03:50:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_subscription_fields'
down_revision: Union[str, None] = '6cecfbddb1a5'  # Depends on initial migration
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add MANAGER role to existing UserRole enum
    op.execute("ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'MANAGER'")
    
    # Create subscription ENUM types
    op.execute("CREATE TYPE subscriptiontier AS ENUM ('FREE', 'BASIC', 'PRO', 'ENTERPRISE')")
    op.execute("CREATE TYPE subscriptionstatus AS ENUM ('ACTIVE', 'INACTIVE', 'CANCELLED', 'PAST_DUE')")
    
    # Add subscription columns to users table
    op.add_column('users', sa.Column('subscription_tier', sa.Enum('FREE', 'BASIC', 'PRO', 'ENTERPRISE', name='subscriptiontier'), nullable=False, server_default='FREE'))
    op.add_column('users', sa.Column('subscription_status', sa.Enum('ACTIVE', 'INACTIVE', 'CANCELLED', 'PAST_DUE', name='subscriptionstatus'), nullable=False, server_default='ACTIVE'))
    op.add_column('users', sa.Column('subscription_started_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('users', sa.Column('subscription_expires_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('users', sa.Column('stripe_customer_id', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('stripe_subscription_id', sa.String(length=255), nullable=True))
    
    # Add indexes
    op.create_index(op.f('ix_users_stripe_customer_id'), 'users', ['stripe_customer_id'], unique=True)
    op.create_index(op.f('ix_users_stripe_subscription_id'), 'users', ['stripe_subscription_id'], unique=True)


def downgrade() -> None:
    # Drop indexes
    op.drop_index(op.f('ix_users_stripe_subscription_id'), table_name='users')
    op.drop_index(op.f('ix_users_stripe_customer_id'), table_name='users')
    
    # Drop columns
    op.drop_column('users', 'stripe_subscription_id')
    op.drop_column('users', 'stripe_customer_id')
    op.drop_column('users', 'subscription_expires_at')
    op.drop_column('users', 'subscription_started_at')
    op.drop_column('users', 'subscription_status')
    op.drop_column('users', 'subscription_tier')
    
    # Drop ENUM types
    op.execute('DROP TYPE subscriptionstatus')
    op.execute('DROP TYPE subscriptiontier')
