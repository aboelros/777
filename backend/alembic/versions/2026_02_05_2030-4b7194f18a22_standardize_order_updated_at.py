"""standardize_order_updated_at

Revision ID: 4b7194f18a22
Revises: 3a6681129371
Create Date: 2026-02-05 20:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '4b7194f18a22'
down_revision = '3a6681129371'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 1. Standardize Order.last_updated -> Order.updated_at
    op.execute("""
        DO $$
        BEGIN
            -- Check if last_updated exists
            IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='orders' AND column_name='last_updated') THEN
                
                -- Check if updated_at already exists (collision case)
                IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='orders' AND column_name='updated_at') THEN
                    -- If updated_at exists, we assume it's the valid one or we prefer it.
                    -- We can migrate data from last_updated if null?
                    -- UPDATE orders SET updated_at = last_updated WHERE updated_at IS NULL;
                    ALTER TABLE orders DROP COLUMN last_updated;
                ELSE
                    -- Rename
                    ALTER TABLE orders RENAME COLUMN last_updated TO updated_at;
                END IF;
            
            -- If last_updated does NOT exist, make sure updated_at DOES
            ELSIF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='orders' AND column_name='updated_at') THEN
                -- Neither exists, create updated_at
                ALTER TABLE orders ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE;
            END IF;
        END$$;
    """)

def downgrade() -> None:
    # Revert updated_at -> last_updated
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='orders' AND column_name='updated_at') THEN
                 ALTER TABLE orders RENAME COLUMN updated_at TO last_updated;
            END IF;
        END$$;
    """)
