"""add_unique_constraint_to_messages

Revision ID: 2e1430bfa5b2
Revises: add_project_code
Create Date: 2025-11-28 23:29:52.617607

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2e1430bfa5b2'
down_revision: Union[str, None] = 'add_project_code'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Clean up duplicate messages before adding constraint
    # Keep the oldest message (based on created_at) for each unique combination
    op.execute("""
        DELETE FROM messages
        WHERE id IN (
            SELECT id
            FROM (
                SELECT id,
                       ROW_NUMBER() OVER (
                           PARTITION BY project_id, provider, external_id
                           ORDER BY created_at ASC
                       ) as rnum
                FROM messages
                WHERE external_id IS NOT NULL
            ) t
            WHERE t.rnum > 1
        )
    """)

    # Create a unique constraint on project_id, provider, and external_id
    # This prevents duplicate messages from being inserted
    op.create_unique_constraint(
        'uq_messages_project_provider_external_id',
        'messages',
        ['project_id', 'provider', 'external_id']
    )


def downgrade() -> None:
    op.drop_constraint('uq_messages_project_provider_external_id', 'messages', type_='unique')
