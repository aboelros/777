"""add_bot_settings_to_projects

Revision ID: 5c7194f18a33
Revises: 4b7194f18a22
Create Date: 2026-02-05 20:45:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '5c7194f18a33'
down_revision = '4b7194f18a22'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Add bot settings columns to projects table if they don't exist
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='projects' AND column_name='bot_name') THEN
                ALTER TABLE projects ADD COLUMN bot_name VARCHAR(100) DEFAULT 'Alex';
            END IF;
            
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='projects' AND column_name='bot_tone') THEN
                ALTER TABLE projects ADD COLUMN bot_tone VARCHAR(50) DEFAULT 'Professional';
            END IF;
            
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='projects' AND column_name='personality_prompt') THEN
                ALTER TABLE projects ADD COLUMN personality_prompt TEXT;
            END IF;
        END$$;
    """)

def downgrade() -> None:
    # Remove added columns
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='projects' AND column_name='personality_prompt') THEN
                ALTER TABLE projects DROP COLUMN personality_prompt;
            END IF;
            
            IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='projects' AND column_name='bot_tone') THEN
                ALTER TABLE projects DROP COLUMN bot_tone;
            END IF;
            
            IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='projects' AND column_name='bot_name') THEN
                ALTER TABLE projects DROP COLUMN bot_name;
            END IF;
        END$$;
    """)
