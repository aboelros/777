"""create social media posts table

Revision ID: create_social_posts
Revises: add_new_features
Create Date: 2025-12-17 00:40:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'create_social_posts'
down_revision = '1d8209bbfdc5'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('social_media_posts',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('platform', sa.String(length=50), nullable=False),
        sa.Column('external_id', sa.String(length=255), nullable=False),
        sa.Column('post_url', sa.String(length=500), nullable=True),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('media_type', sa.String(length=50), nullable=True),
        sa.Column('media_urls', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('author_username', sa.String(length=255), nullable=True),
        sa.Column('author_id', sa.String(length=255), nullable=True),
        sa.Column('likes_count', sa.Integer(), nullable=True),
        sa.Column('comments_count', sa.Integer(), nullable=True),
        sa.Column('shares_count', sa.Integer(), nullable=True),
        sa.Column('views_count', sa.Integer(), nullable=True),
        sa.Column('ai_analyzed', sa.Boolean(), nullable=True),
        sa.Column('sentiment', sa.String(length=50), nullable=True),
        sa.Column('topics', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('keywords', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('ai_summary', sa.Text(), nullable=True),
        sa.Column('last_comment_check', sa.DateTime(timezone=True), nullable=True),
        sa.Column('unresponded_comments', sa.Integer(), nullable=True),
        sa.Column('engagement_rate', sa.Float(), nullable=True),
        sa.Column('best_performing', sa.Boolean(), nullable=True),
        sa.Column('hashtags', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('mentions', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('extra_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('posted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('external_id')
    )
    op.create_index('idx_social_post_project', 'social_media_posts', ['project_id'], unique=False)
    op.create_index('idx_social_post_platform_external', 'social_media_posts', ['platform', 'external_id'], unique=False)
    op.create_index('idx_social_post_engagement', 'social_media_posts', ['engagement_rate'], unique=False)
    op.create_index('idx_social_post_posted_at', 'social_media_posts', ['posted_at'], unique=False)


def downgrade():
    op.drop_index('idx_social_post_posted_at', table_name='social_media_posts')
    op.drop_index('idx_social_post_engagement', table_name='social_media_posts')
    op.drop_index('idx_social_post_platform_external', table_name='social_media_posts')
    op.drop_index('idx_social_post_project', table_name='social_media_posts')
    op.drop_table('social_media_posts')
