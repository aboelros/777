"""Create WhatsApp gateway sessions and keys tables for durable Baileys persistence

Revision ID: 2026_11_07_wa_sessions
Revises: add_project_code
Create Date: 2026-11-07
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy.dialects import postgresql

revision = '2026_11_07_wa_sessions'
down_revision = 'c3d4e5f6a7b8'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)

    if not inspector.has_table('whatsapp_gateway_sessions'):
        op.create_table(
            'whatsapp_gateway_sessions',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
            sa.Column('integration_id', postgresql.UUID(as_uuid=True), nullable=False, unique=True),
            sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('credentials_encrypted', sa.Text(), nullable=False),
            sa.Column('session_status', sa.String(length=50), server_default='disconnected'),
            sa.Column('auth_valid', sa.Boolean(), server_default='true'),
            sa.Column('phone_number', sa.String(length=50), nullable=True),
            sa.Column('platform', sa.String(length=50), server_default='baileys'),
            sa.Column('version', sa.Integer(), server_default='1'),
            sa.Column('last_connected_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('last_disconnected_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        )
        op.create_index('idx_wa_sessions_integration', 'whatsapp_gateway_sessions', ['integration_id'], unique=True)
        op.create_index('idx_wa_sessions_project', 'whatsapp_gateway_sessions', ['project_id'], unique=False)

    if not inspector.has_table('whatsapp_gateway_keys'):
        op.create_table(
            'whatsapp_gateway_keys',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
            sa.Column('session_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('whatsapp_gateway_sessions.id', ondelete='CASCADE'), nullable=False),
            sa.Column('integration_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('key_type', sa.String(length=100), nullable=False),
            sa.Column('key_id', sa.String(length=255), nullable=False),
            sa.Column('key_data_encrypted', sa.Text(), nullable=False),
            sa.Column('key_version', sa.Integer(), server_default='1'),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.UniqueConstraint('session_id', 'key_type', 'key_id', name='uq_wa_gateway_key')
        )
        op.create_index('idx_wa_keys_lookup', 'whatsapp_gateway_keys', ['session_id', 'key_type', 'key_id'], unique=False)
        op.create_index('idx_wa_keys_integration', 'whatsapp_gateway_keys', ['integration_id'], unique=False)


def downgrade():
    op.drop_table('whatsapp_gateway_keys')
    op.drop_table('whatsapp_gateway_sessions')
