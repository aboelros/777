"""add_all_missing_customer_profile_columns

Revision ID: 4389f273cede
Revises: edbe90bad4fd
Create Date: 2026-01-30 22:19:05.663687

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4389f273cede'
down_revision: Union[str, None] = 'edbe90bad4fd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add all missing columns to customer_profiles table (idempotent)"""
    from sqlalchemy import inspect
    from sqlalchemy.dialects.postgresql import JSONB
    import sqlalchemy as sa
    
    # Get bind and inspector to check existing columns
    bind = op.get_bind()
    inspector = inspect(bind)
    existing_columns = {col['name'] for col in inspector.get_columns('customer_profiles')}
    
    # Helper function to add column only if it doesn't exist
    def add_column_if_not_exists(column_name, column_obj):
        if column_name not in existing_columns:
            op.add_column('customer_profiles', column_obj)
    
    # Avatar and sync tracking
    add_column_if_not_exists('avatar_url', sa.Column('avatar_url', sa.String(length=500), nullable=True))
    add_column_if_not_exists('last_sync', sa.Column('last_sync', sa.DateTime(timezone=True), nullable=True))
    
    # Preferences
    add_column_if_not_exists('preferred_language', sa.Column('preferred_language', sa.String(length=10), server_default='en', nullable=True))
    add_column_if_not_exists('preferred_platform', sa.Column('preferred_platform', sa.String(length=50), nullable=True))
    add_column_if_not_exists('communication_style', sa.Column('communication_style', sa.String(length=50), nullable=True))
    
    # Behavioral data
    add_column_if_not_exists('interaction_count', sa.Column('interaction_count', sa.Integer(), server_default='0', nullable=True))
    add_column_if_not_exists('last_interaction', sa.Column('last_interaction', sa.DateTime(timezone=True), nullable=True))
    add_column_if_not_exists('first_interaction', sa.Column('first_interaction', sa.DateTime(timezone=True), nullable=True))
    
    # Purchase history
    add_column_if_not_exists('total_orders', sa.Column('total_orders', sa.Integer(), server_default='0', nullable=True))
    add_column_if_not_exists('total_spent', sa.Column('total_spent', sa.Float(), server_default='0.0', nullable=True))
    add_column_if_not_exists('average_order_value', sa.Column('average_order_value', sa.Float(), nullable=True))
    add_column_if_not_exists('favorite_products', sa.Column('favorite_products', JSONB(astext_type=sa.Text()), server_default='[]', nullable=True))
    
    # Sentiment
    add_column_if_not_exists('overall_sentiment', sa.Column('overall_sentiment', sa.String(length=50), nullable=True))
    add_column_if_not_exists('satisfaction_score', sa.Column('satisfaction_score', sa.Float(), nullable=True))
    
    # Customer type
    add_column_if_not_exists('customer_type', sa.Column('customer_type', sa.String(length=50), nullable=True))
    add_column_if_not_exists('tags', sa.Column('tags', JSONB(astext_type=sa.Text()), server_default='[]', nullable=True))
    
    # AI insights
    add_column_if_not_exists('interests', sa.Column('interests', JSONB(astext_type=sa.Text()), server_default='[]', nullable=True))
    add_column_if_not_exists('purchase_patterns', sa.Column('purchase_patterns', JSONB(astext_type=sa.Text()), server_default='{}', nullable=True))
    add_column_if_not_exists('lifetime_value_estimate', sa.Column('lifetime_value_estimate', sa.Float(), nullable=True))
    
    # Notes
    add_column_if_not_exists('notes', sa.Column('notes', sa.Text(), nullable=True))
    add_column_if_not_exists('special_instructions', sa.Column('special_instructions', sa.Text(), nullable=True))
    
    # Flags
    add_column_if_not_exists('is_vip', sa.Column('is_vip', sa.Boolean(), server_default='false', nullable=True))
    add_column_if_not_exists('is_blocked', sa.Column('is_blocked', sa.Boolean(), server_default='false', nullable=True))
    add_column_if_not_exists('requires_special_attention', sa.Column('requires_special_attention', sa.Boolean(), server_default='false', nullable=True))


def downgrade() -> None:
    """Remove all added columns from customer_profiles table"""
    with op.batch_alter_table('customer_profiles', schema=None) as batch_op:
        batch_op.drop_column('requires_special_attention')
        batch_op.drop_column('is_blocked')
        batch_op.drop_column('is_vip')
        batch_op.drop_column('special_instructions')
        batch_op.drop_column('notes')
        batch_op.drop_column('lifetime_value_estimate')
        batch_op.drop_column('purchase_patterns')
        batch_op.drop_column('interests')
        batch_op.drop_column('tags')
        batch_op.drop_column('customer_type')
        batch_op.drop_column('satisfaction_score')
        batch_op.drop_column('overall_sentiment')
        batch_op.drop_column('favorite_products')
        batch_op.drop_column('average_order_value')
        batch_op.drop_column('total_spent')
        batch_op.drop_column('total_orders')
        batch_op.drop_column('first_interaction')
        batch_op.drop_column('last_interaction')
        batch_op.drop_column('interaction_count')
        batch_op.drop_column('communication_style')
        batch_op.drop_column('preferred_platform')
        batch_op.drop_column('preferred_language')
        batch_op.drop_column('last_sync')
        batch_op.drop_column('avatar_url')
