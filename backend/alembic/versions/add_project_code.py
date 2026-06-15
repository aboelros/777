"""Add project_code to projects table

Revision ID: add_project_code
Revises: fix_customer_profiles_schema
Create Date: 2025-11-28

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_project_code'
down_revision = 'fix_customer_profiles_schema'  # Link to previous migration
branch_labels = None
depends_on = None


def upgrade():
    # Add project_code column (nullable first to allow existing data)
    op.add_column('projects', sa.Column('project_code', sa.String(length=50), nullable=True))
    
    # Generate unique project codes for existing projects
    # Format: PROJ-{sequential_number}
    op.execute("""
        WITH numbered_projects AS (
            SELECT id, ROW_NUMBER() OVER (ORDER BY created_at) as row_num
            FROM projects
        )
        UPDATE projects
        SET project_code = 'PROJ-' || LPAD(numbered_projects.row_num::text, 3, '0')
        FROM numbered_projects
        WHERE projects.id = numbered_projects.id
    """)
    
    # Now make it non-nullable and add unique constraint
    op.alter_column('projects', 'project_code', nullable=False)
    op.create_unique_constraint('uq_projects_project_code', 'projects', ['project_code'])
    op.create_index('ix_projects_project_code', 'projects', ['project_code'])


def downgrade():
    # Remove index, constraint, and column
    op.drop_index('ix_projects_project_code', table_name='projects')
    op.drop_constraint('uq_projects_project_code', 'projects', type_='unique')
    op.drop_column('projects', 'project_code')
