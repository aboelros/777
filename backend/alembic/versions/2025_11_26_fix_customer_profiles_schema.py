"""Fix customer_profiles schema completely

Revision ID: fix_customer_profiles_schema
Revises: add_platform_accounts
Create Date: 2025-11-26 10:45:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'fix_customer_profiles_schema'
down_revision = 'add_platform_accounts'
branch_labels = None
depends_on = None


def upgrade():
    # Rename phone_number to phone (if it exists)
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'customer_profiles' AND column_name = 'phone_number'
            ) THEN
                ALTER TABLE customer_profiles RENAME COLUMN phone_number TO phone;
            END IF;
        END $$;
    """)
    
    # Add phone column if it doesn't exist (in case table was created differently)
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'customer_profiles' AND column_name = 'phone'
            ) THEN
                ALTER TABLE customer_profiles ADD COLUMN phone VARCHAR(50);
            END IF;
        END $$;
    """)
    
    # Add all missing columns
    columns_to_add = [
        ("preferred_language", "VARCHAR(10) DEFAULT 'en'"),
        ("preferred_platform", "VARCHAR(50)"),
        ("communication_style", "VARCHAR(50)"),
        ("interaction_count", "INTEGER DEFAULT 0"),
        ("last_interaction", "TIMESTAMP WITH TIME ZONE"),
        ("first_interaction", "TIMESTAMP WITH TIME ZONE"),
        ("total_orders", "INTEGER DEFAULT 0"),
        ("total_spent", "FLOAT DEFAULT 0.0"),
        ("average_order_value", "FLOAT"),
        ("favorite_products", "JSONB DEFAULT '[]'"),
        ("overall_sentiment", "VARCHAR(50)"),
        ("satisfaction_score", "FLOAT"),
        ("customer_type", "VARCHAR(50)"),
        ("tags", "JSONB DEFAULT '[]'"),
        ("interests", "JSONB DEFAULT '[]'"),
        ("purchase_patterns", "JSONB DEFAULT '{}'"),
        ("lifetime_value_estimate", "FLOAT"),
        ("notes", "TEXT"),
        ("special_instructions", "TEXT"),
        ("is_vip", "BOOLEAN DEFAULT FALSE"),
        ("is_blocked", "BOOLEAN DEFAULT FALSE"),
        ("requires_special_attention", "BOOLEAN DEFAULT FALSE"),
        ("extra_data", "JSONB DEFAULT '{}'"),
    ]
    
    for column_name, column_type in columns_to_add:
        op.execute(f"""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'customer_profiles' AND column_name = '{column_name}'
                ) THEN
                    ALTER TABLE customer_profiles ADD COLUMN {column_name} {column_type};
                END IF;
            END $$;
        """)
    
    # Update index from phone_number to phone
    op.execute("DROP INDEX IF EXISTS idx_customer_profiles_phone_number")
    op.execute("CREATE INDEX IF NOT EXISTS idx_customer_profiles_phone ON customer_profiles(phone)")


def downgrade():
    # Rename phone back to phone_number
    op.execute("ALTER TABLE customer_profiles RENAME COLUMN phone TO phone_number")
    
    # Drop added columns
    columns_to_drop = [
        "preferred_language", "preferred_platform", "communication_style",
        "interaction_count", "last_interaction", "first_interaction",
        "total_orders", "total_spent", "average_order_value", "favorite_products",
        "overall_sentiment", "satisfaction_score", "customer_type", "tags",
        "interests", "purchase_patterns", "lifetime_value_estimate",
        "notes", "special_instructions", "is_vip", "is_blocked",
        "requires_special_attention", "extra_data"
    ]
    
    for column in columns_to_drop:
        op.execute(f"ALTER TABLE customer_profiles DROP COLUMN IF EXISTS {column}")
    
    # Restore old index
    op.execute("DROP INDEX IF EXISTS idx_customer_profiles_phone")
    op.execute("CREATE INDEX IF NOT EXISTS idx_customer_profiles_phone_number ON customer_profiles(phone_number)")
