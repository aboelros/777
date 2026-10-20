BEGIN;

-- Running upgrade d8f3a1e5c2b4 -> f3a2b1c4e5d6

DROP INDEX IF EXISTS ix_subscription_user;

DROP INDEX IF EXISTS idx_subscription_user;

ALTER TABLE public.alembic_version ENABLE ROW LEVEL SECURITY;

REVOKE ALL ON TABLE public.alembic_version FROM anon, authenticated;

ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;

REVOKE ALL ON TABLE public.users FROM anon, authenticated;

ALTER TABLE public.refresh_tokens ENABLE ROW LEVEL SECURITY;

REVOKE ALL ON TABLE public.refresh_tokens FROM anon, authenticated;

ALTER TABLE public.subscriptions ENABLE ROW LEVEL SECURITY;

REVOKE ALL ON TABLE public.subscriptions FROM anon, authenticated;

ALTER TABLE public.projects ENABLE ROW LEVEL SECURITY;

REVOKE ALL ON TABLE public.projects FROM anon, authenticated;

ALTER TABLE public.project_members ENABLE ROW LEVEL SECURITY;

REVOKE ALL ON TABLE public.project_members FROM anon, authenticated;

ALTER TABLE public.customer_profiles ENABLE ROW LEVEL SECURITY;

REVOKE ALL ON TABLE public.customer_profiles FROM anon, authenticated;

ALTER TABLE public.deals ENABLE ROW LEVEL SECURITY;

REVOKE ALL ON TABLE public.deals FROM anon, authenticated;

ALTER TABLE public.pipeline_stages ENABLE ROW LEVEL SECURITY;

REVOKE ALL ON TABLE public.pipeline_stages FROM anon, authenticated;

ALTER TABLE public.orders ENABLE ROW LEVEL SECURITY;

REVOKE ALL ON TABLE public.orders FROM anon, authenticated;

ALTER TABLE public.invoices ENABLE ROW LEVEL SECURITY;

REVOKE ALL ON TABLE public.invoices FROM anon, authenticated;

ALTER TABLE public.payment_links ENABLE ROW LEVEL SECURITY;

REVOKE ALL ON TABLE public.payment_links FROM anon, authenticated;

ALTER TABLE public.products ENABLE ROW LEVEL SECURITY;

REVOKE ALL ON TABLE public.products FROM anon, authenticated;

ALTER TABLE public.knowledge_base ENABLE ROW LEVEL SECURITY;

REVOKE ALL ON TABLE public.knowledge_base FROM anon, authenticated;

ALTER TABLE public.integrations ENABLE ROW LEVEL SECURITY;

REVOKE ALL ON TABLE public.integrations FROM anon, authenticated;

ALTER TABLE public.drip_campaigns ENABLE ROW LEVEL SECURITY;

REVOKE ALL ON TABLE public.drip_campaigns FROM anon, authenticated;

ALTER TABLE public.drip_steps ENABLE ROW LEVEL SECURITY;

REVOKE ALL ON TABLE public.drip_steps FROM anon, authenticated;

ALTER TABLE public.campaign_enrollments ENABLE ROW LEVEL SECURITY;

REVOKE ALL ON TABLE public.campaign_enrollments FROM anon, authenticated;

ALTER TABLE public.auto_response_templates ENABLE ROW LEVEL SECURITY;

REVOKE ALL ON TABLE public.auto_response_templates FROM anon, authenticated;

ALTER TABLE public.bot_instructions ENABLE ROW LEVEL SECURITY;

REVOKE ALL ON TABLE public.bot_instructions FROM anon, authenticated;

ALTER TABLE public.model_trainings ENABLE ROW LEVEL SECURITY;

REVOKE ALL ON TABLE public.model_trainings FROM anon, authenticated;

ALTER TABLE public.reports ENABLE ROW LEVEL SECURITY;

REVOKE ALL ON TABLE public.reports FROM anon, authenticated;

ALTER TABLE public.oauth_states ENABLE ROW LEVEL SECURITY;

REVOKE ALL ON TABLE public.oauth_states FROM anon, authenticated;

ALTER TABLE public.usage_tracking ENABLE ROW LEVEL SECURITY;

REVOKE ALL ON TABLE public.usage_tracking FROM anon, authenticated;

ALTER TABLE public.api_logs ENABLE ROW LEVEL SECURITY;

REVOKE ALL ON TABLE public.api_logs FROM anon, authenticated;

ALTER TABLE public.messages ENABLE ROW LEVEL SECURITY;

REVOKE ALL ON TABLE public.messages FROM anon, authenticated;

ALTER TABLE public.conversation_history ENABLE ROW LEVEL SECURITY;

REVOKE ALL ON TABLE public.conversation_history FROM anon, authenticated;

ALTER TABLE public.bot_activities ENABLE ROW LEVEL SECURITY;

REVOKE ALL ON TABLE public.bot_activities FROM anon, authenticated;

ALTER TABLE public.social_media_comments ENABLE ROW LEVEL SECURITY;

REVOKE ALL ON TABLE public.social_media_comments FROM anon, authenticated;

ALTER TABLE public.social_media_posts ENABLE ROW LEVEL SECURITY;

REVOKE ALL ON TABLE public.social_media_posts FROM anon, authenticated;

REVOKE ALL ON TABLE public.business_context FROM anon, authenticated;

REVOKE ALL ON TABLE public.product_images FROM anon, authenticated;

REVOKE ALL ON ALL SEQUENCES IN SCHEMA public FROM anon, authenticated;

ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE ALL ON TABLES FROM anon, authenticated;

ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE ALL ON SEQUENCES FROM anon, authenticated;

UPDATE alembic_version SET version_num='f3a2b1c4e5d6' WHERE alembic_version.version_num = 'd8f3a1e5c2b4';

COMMIT;
