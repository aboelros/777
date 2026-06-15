"""Add usage_tracking table

Revision ID: add_usage_tracking
Revises: add_new_features
Create Date: 2025-11-14 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_usage_tracking'
down_revision = 'add_new_features'
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    # Ensure subscriptions table exists (new deployments may not have it yet)
    # Ensure enum types exist (idempotent)
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_type t
                JOIN pg_namespace n ON n.oid = t.typnamespace
                WHERE t.typname = 'subscriptiontier' AND n.nspname = 'public'
            ) THEN
                CREATE TYPE subscriptiontier AS ENUM ('FREE', 'BASIC', 'PRO', 'ENTERPRISE');
            END IF;
        END$$;
    """)

    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_type t
                JOIN pg_namespace n ON n.oid = t.typnamespace
                WHERE t.typname = 'subscriptionstatus' AND n.nspname = 'public'
            ) THEN
                CREATE TYPE subscriptionstatus AS ENUM ('ACTIVE', 'INACTIVE', 'CANCELLED', 'PAST_DUE');
            END IF;
        END$$;
    """)

    subscription_tier_enum = postgresql.ENUM('FREE', 'BASIC', 'PRO', 'ENTERPRISE', name='subscriptiontier', create_type=False)
    subscription_status_enum = postgresql.ENUM('ACTIVE', 'INACTIVE', 'CANCELLED', 'PAST_DUE', name='subscriptionstatus', create_type=False)

    if not inspector.has_table('subscriptions'):
        op.create_table(
            'subscriptions',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
            sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True),
            sa.Column('tier', subscription_tier_enum, nullable=False, server_default='FREE'),
            sa.Column('status', subscription_status_enum, nullable=False, server_default='ACTIVE'),
            sa.Column('price_monthly', sa.Float(), nullable=False, server_default='0'),
            sa.Column('price_annually', sa.Float(), nullable=False, server_default='0'),
            sa.Column('billing_cycle', sa.String(length=50), nullable=False, server_default='monthly'),
            sa.Column('currency', sa.String(length=10), nullable=False, server_default='USD'),
            sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('trial_ends_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('cancelled_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('next_billing_date', sa.DateTime(timezone=True), nullable=True),
            sa.Column('stripe_customer_id', sa.String(length=255), nullable=True),
            sa.Column('stripe_subscription_id', sa.String(length=255), nullable=True),
            sa.Column('stripe_payment_method_id', sa.String(length=255), nullable=True),
            sa.Column('limit_messages', sa.Integer(), nullable=False, server_default='100'),
            sa.Column('limit_orders', sa.Integer(), nullable=False, server_default='10'),
            sa.Column('limit_ai_requests', sa.Integer(), nullable=False, server_default='1000'),
            sa.Column('limit_projects', sa.Integer(), nullable=False, server_default='1'),
            sa.Column('limit_integrations', sa.Integer(), nullable=False, server_default='2'),
            sa.Column('limit_storage_gb', sa.Float(), nullable=False, server_default='1'),
            sa.Column('limit_team_members', sa.Integer(), nullable=False, server_default='1'),
            sa.Column('features', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
            sa.Column('total_paid', sa.Float(), nullable=False, server_default='0'),
            sa.Column('invoices', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
            sa.Column('extra_data', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True, server_default=sa.func.now(), onupdate=sa.func.now())
        )
        op.create_index('ix_subscription_user', 'subscriptions', ['user_id'], unique=True)
        op.create_index('ix_subscription_tier', 'subscriptions', ['tier'], unique=False)
        op.create_index('ix_subscription_status', 'subscriptions', ['status'], unique=False)
        op.create_index('ix_subscription_expires', 'subscriptions', ['expires_at'], unique=False)

    # Create usage_tracking table
    if not inspector.has_table('usage_tracking'):
        op.create_table(
            'usage_tracking',
            sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('subscription_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('period_start', sa.DateTime(timezone=True), nullable=False),
            sa.Column('period_end', sa.DateTime(timezone=True), nullable=False),
            sa.Column('messages_sent', sa.Integer(), nullable=True, server_default='0'),
            sa.Column('messages_received', sa.Integer(), nullable=True, server_default='0'),
            sa.Column('orders_created', sa.Integer(), nullable=True, server_default='0'),
            sa.Column('ai_requests', sa.Integer(), nullable=True, server_default='0'),
            sa.Column('ai_tokens_used', sa.Integer(), nullable=True, server_default='0'),
            sa.Column('storage_used_gb', sa.Float(), nullable=True, server_default='0'),
            sa.Column('ai_cost', sa.Float(), nullable=True, server_default='0'),
            sa.Column('storage_cost', sa.Float(), nullable=True, server_default='0'),
            sa.Column('total_cost', sa.Float(), nullable=True, server_default='0'),
            sa.Column('limits_exceeded', postgresql.JSON(), nullable=True),
            sa.Column('overage_charges', sa.Float(), nullable=True, server_default='0'),
            sa.Column('extra_data', postgresql.JSON(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(['subscription_id'], ['subscriptions.id']),
            sa.ForeignKeyConstraint(['user_id'], ['users.id']),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_usage_tracking_subscription_id'), 'usage_tracking', ['subscription_id'], unique=False)
        op.create_index(op.f('ix_usage_tracking_user_id'), 'usage_tracking', ['user_id'], unique=False)
        op.create_index(op.f('ix_usage_tracking_period_start'), 'usage_tracking', ['period_start'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_usage_tracking_period_start'), table_name='usage_tracking')
    op.drop_index(op.f('ix_usage_tracking_user_id'), table_name='usage_tracking')
    op.drop_index(op.f('ix_usage_tracking_subscription_id'), table_name='usage_tracking')
    op.drop_table('usage_tracking')
