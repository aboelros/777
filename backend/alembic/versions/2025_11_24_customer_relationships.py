"""Add customer_id to messages and orders

Revision ID: 2025_11_24_customer_relationships
Revises: add_product_storage_fields
Create Date: 2025-11-24 18:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'customer_relationships_2024'
down_revision = 'add_product_storage_fields'  # Fixed to match actual revision ID
branch_labels = None
depends_on = None


def upgrade():
    # Create customer_profiles table if it doesn't exist
    # This ensures the table exists before we add foreign keys to it
    op.execute("""
        CREATE TABLE IF NOT EXISTS customer_profiles (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            project_id UUID NOT NULL,
            phone_number VARCHAR(50),
            email VARCHAR(255),
            name VARCHAR(255),
            platform VARCHAR(50),
            metadata JSONB DEFAULT '{}',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create indexes on customer_profiles if they don't exist
    op.execute("CREATE INDEX IF NOT EXISTS idx_customer_profiles_project_id ON customer_profiles(project_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_customer_profiles_phone_number ON customer_profiles(phone_number)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_customer_profiles_email ON customer_profiles(email)")
    
    # Add customer_id to messages table
    op.add_column('messages', sa.Column('customer_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key(
        'fk_messages_customer_id',
        'messages', 'customer_profiles',
        ['customer_id'], ['id'],
        ondelete='SET NULL'
    )
    op.create_index('idx_messages_customer_id', 'messages', ['customer_id'])
    
    # Add customer_id to orders table
    op.add_column('orders', sa.Column('customer_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key(
        'fk_orders_customer_id',
        'orders', 'customer_profiles',
        ['customer_id'], ['id'],
        ondelete='SET NULL'
    )
    op.create_index('idx_orders_customer_id', 'orders', ['customer_id'])


def downgrade():
    # Remove customer_id from orders
    op.drop_index('idx_orders_customer_id', table_name='orders')
    op.drop_constraint('fk_orders_customer_id', 'orders', type_='foreignkey')
    op.drop_column('orders', 'customer_id')
    
    # Remove customer_id from messages
    op.drop_index('idx_messages_customer_id', table_name='messages')
    op.drop_constraint('fk_messages_customer_id', 'messages', type_='foreignkey')
    op.drop_column('messages', 'customer_id')
    
    # Note: We don't drop customer_profiles table in downgrade
    # as it might have been created by another migration
