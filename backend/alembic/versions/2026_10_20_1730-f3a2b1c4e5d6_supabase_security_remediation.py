"""supabase_security_remediation

Revision ID: f3a2b1c4e5d6
Revises: d8f3a1e5c2b4
Create Date: 2026-10-20 17:30:00.000000

"""
from typing import Sequence, Union
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'f3a2b1c4e5d6'
down_revision: Union[str, None] = 'd8f3a1e5c2b4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Schema public tables created prior to b7d41f09e2a1 requiring RLS and DAC hardening.
# Note: business_context and product_images already enable RLS in their creation migrations.
TABLES_TO_HARDEN = [
    "alembic_version",
    "users",
    "refresh_tokens",
    "subscriptions",
    "projects",
    "project_members",
    "customer_profiles",
    "deals",
    "pipeline_stages",
    "orders",
    "invoices",
    "payment_links",
    "products",
    "knowledge_base",
    "integrations",
    "drip_campaigns",
    "drip_steps",
    "campaign_enrollments",
    "auto_response_templates",
    "bot_instructions",
    "model_trainings",
    "reports",
    "oauth_states",
    "usage_tracking",
    "api_logs",
    "messages",
    "conversation_history",
    "bot_activities",
    "social_media_comments",
    "social_media_posts",
]


def upgrade() -> None:
    bind = op.get_bind()
    is_postgres = bind.dialect.name == "postgresql"

    if is_postgres:
        # 1. Deduplicate subscriptions user_id index
        op.execute("DROP INDEX IF EXISTS ix_subscription_user")
        op.execute("DROP INDEX IF EXISTS idx_subscription_user")

        # 2. Enable Row-Level Security and Revoke discretionary grants from API roles
        for table in TABLES_TO_HARDEN:
            op.execute(f"ALTER TABLE public.{table} ENABLE ROW LEVEL SECURITY")
            op.execute(f"REVOKE ALL ON TABLE public.{table} FROM anon, authenticated")

        # Also ensure business_context and product_images have anon/authenticated grants revoked
        op.execute("REVOKE ALL ON TABLE public.business_context FROM anon, authenticated")
        op.execute("REVOKE ALL ON TABLE public.product_images FROM anon, authenticated")

        # 3. Revoke sequence privileges
        op.execute("REVOKE ALL ON ALL SEQUENCES IN SCHEMA public FROM anon, authenticated")

        # 4. Alter default privileges so future tables and sequences do not grant to API roles
        op.execute(
            "ALTER DEFAULT PRIVILEGES IN SCHEMA public "
            "REVOKE ALL ON TABLES FROM anon, authenticated"
        )
        op.execute(
            "ALTER DEFAULT PRIVILEGES IN SCHEMA public "
            "REVOKE ALL ON SEQUENCES FROM anon, authenticated"
        )


def downgrade() -> None:
    bind = op.get_bind()
    is_postgres = bind.dialect.name == "postgresql"

    if is_postgres:
        # Recreate unique index if needed
        op.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS ix_subscription_user "
            "ON public.subscriptions (user_id)"
        )

        # Disable RLS on application tables
        for table in reversed(TABLES_TO_HARDEN):
            op.execute(f"ALTER TABLE public.{table} DISABLE ROW LEVEL SECURITY")
