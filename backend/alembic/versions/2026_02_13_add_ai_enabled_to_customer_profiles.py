"""add_ai_enabled_to_customer_profiles

Revision ID: add_ai_profile_columns
Revises: create_sales_pipeline_tables
Create Date: 2026-02-13 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision: str = 'add_ai_profile_columns'
down_revision: Union[str, None] = 'create_sales_pipeline_tables'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add ai_enabled and other missing columns to customer_profiles table"""
    # Use raw SQL for idempotency (IF NOT EXISTS is cleaner in raw SQL for Postgres)
    
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='customer_profiles' AND column_name='ai_enabled') THEN
                ALTER TABLE customer_profiles ADD COLUMN ai_enabled BOOLEAN DEFAULT TRUE;
            END IF;

            IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='customer_profiles' AND column_name='ai_settings') THEN
                ALTER TABLE customer_profiles ADD COLUMN ai_settings JSONB DEFAULT '{}';
            END IF;

            IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='customer_profiles' AND column_name='extra_data') THEN
                ALTER TABLE customer_profiles ADD COLUMN extra_data JSONB DEFAULT '{}';
            END IF;

            -- Also check for potentially missing columns from previous steps just in case
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='customer_profiles' AND column_name='notes') THEN
                ALTER TABLE customer_profiles ADD COLUMN notes TEXT;
            END IF;
            
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='customer_profiles' AND column_name='special_instructions') THEN
                ALTER TABLE customer_profiles ADD COLUMN special_instructions TEXT;
            END IF;
        END$$;
    """)


def downgrade() -> None:
    """Remove added columns"""
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='customer_profiles' AND column_name='ai_enabled') THEN
                ALTER TABLE customer_profiles DROP COLUMN ai_enabled;
            END IF;

            IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='customer_profiles' AND column_name='ai_settings') THEN
                ALTER TABLE customer_profiles DROP COLUMN ai_settings;
            END IF;

            IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='customer_profiles' AND column_name='extra_data') THEN
                ALTER TABLE customer_profiles DROP COLUMN extra_data;
            END IF;
        END$$;
    """)
