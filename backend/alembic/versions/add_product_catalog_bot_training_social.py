"""Add product catalog, bot training, and social media tables

Revision ID: add_new_features
Revises: add_subscription_fields
Create Date: 2025-10-15

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_new_features'
down_revision = 'add_subscription_fields'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)

    # Create products table
    if not inspector.has_table('products'):
        op.create_table('products',
            sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('name', sa.String(length=255), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('sku', sa.String(length=100), nullable=True),
            sa.Column('price', sa.Float(), nullable=True),
            sa.Column('currency', sa.String(length=3), nullable=True),
            sa.Column('stock_quantity', sa.Integer(), nullable=True),
            sa.Column('in_stock', sa.Boolean(), nullable=True),
            sa.Column('images', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
            sa.Column('category', sa.String(length=100), nullable=True),
            sa.Column('tags', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
            sa.Column('specifications', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
            sa.Column('faq', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
            sa.Column('keywords', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
            sa.Column('extra_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
            sa.Column('is_active', sa.Boolean(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index('idx_product_project', 'products', ['project_id'], unique=False)
        op.create_index('idx_product_sku', 'products', ['sku'], unique=False)
        op.create_index('idx_product_name', 'products', ['name'], unique=False)

    # Create bot_instructions table
    if not inspector.has_table('bot_instructions'):
        op.create_table('bot_instructions',
            sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('title', sa.String(length=255), nullable=False),
            sa.Column('instruction', sa.Text(), nullable=False),
            sa.Column('category', sa.String(length=100), nullable=True),
            sa.Column('priority', sa.Integer(), nullable=True),
            sa.Column('active_for_platforms', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
            sa.Column('active_for_topics', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
            sa.Column('examples', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
            sa.Column('is_active', sa.Boolean(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index('idx_bot_instruction_project', 'bot_instructions', ['project_id'], unique=False)
        op.create_index('idx_bot_instruction_priority', 'bot_instructions', ['priority'], unique=False)

    # Create social_media_comments table
    if not inspector.has_table('social_media_comments'):
        op.create_table('social_media_comments',
            sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('platform', sa.String(length=50), nullable=False),
            sa.Column('external_id', sa.String(length=255), nullable=False),
            sa.Column('post_id', sa.String(length=255), nullable=True),
            sa.Column('content', sa.Text(), nullable=False),
            sa.Column('author_username', sa.String(length=255), nullable=True),
            sa.Column('author_id', sa.String(length=255), nullable=True),
            sa.Column('responded', sa.Boolean(), nullable=True),
            sa.Column('response_content', sa.Text(), nullable=True),
            sa.Column('response_sent_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('auto_generated', sa.Boolean(), nullable=True),
            sa.Column('sentiment', sa.String(length=50), nullable=True),
            sa.Column('intent', sa.String(length=100), nullable=True),
            sa.Column('requires_human', sa.Boolean(), nullable=True),
            sa.Column('priority', sa.Integer(), nullable=True),
            sa.Column('extra_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index('idx_social_comment_project', 'social_media_comments', ['project_id'], unique=False)
        op.create_index('idx_social_comment_platform_external', 'social_media_comments', ['platform', 'external_id'], unique=False)
        op.create_index('idx_social_comment_responded', 'social_media_comments', ['responded'], unique=False)

    # Create auto_response_templates table
    if not inspector.has_table('auto_response_templates'):
        op.create_table('auto_response_templates',
            sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('name', sa.String(length=255), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('trigger_keywords', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
            sa.Column('trigger_platforms', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
            sa.Column('trigger_intent', sa.String(length=100), nullable=True),
            sa.Column('response_template', sa.Text(), nullable=False),
            sa.Column('variations', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
            sa.Column('use_ai_enhancement', sa.Boolean(), nullable=True),
            sa.Column('requires_approval', sa.Boolean(), nullable=True),
            sa.Column('times_used', sa.Integer(), nullable=True),
            sa.Column('success_rate', sa.Float(), nullable=True),
            sa.Column('is_active', sa.Boolean(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index('idx_auto_response_project', 'auto_response_templates', ['project_id'], unique=False)
        op.create_index('idx_auto_response_active', 'auto_response_templates', ['is_active'], unique=False)

    # Add platform column to messages table if not exists
    message_columns = {col['name'] for col in inspector.get_columns('messages')}
    if 'platform' not in message_columns:
        op.add_column('messages', sa.Column('platform', sa.String(length=50), nullable=True))


def downgrade():
    op.drop_index('idx_auto_response_active', table_name='auto_response_templates')
    op.drop_index('idx_auto_response_project', table_name='auto_response_templates')
    op.drop_table('auto_response_templates')
    
    op.drop_index('idx_social_comment_responded', table_name='social_media_comments')
    op.drop_index('idx_social_comment_platform_external', table_name='social_media_comments')
    op.drop_index('idx_social_comment_project', table_name='social_media_comments')
    op.drop_table('social_media_comments')
    
    op.drop_index('idx_bot_instruction_priority', table_name='bot_instructions')
    op.drop_index('idx_bot_instruction_project', table_name='bot_instructions')
    op.drop_table('bot_instructions')
    
    op.drop_index('idx_product_name', table_name='products')
    op.drop_index('idx_product_sku', table_name='products')
    op.drop_index('idx_product_project', table_name='products')
    op.drop_table('products')
    
    op.drop_column('messages', 'platform')
