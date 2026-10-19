"""
Security and tenant-isolation test suite for Reconstructed Phase 2 Group 9:
Analytics & Reporting domain.
"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
import pytest
from fastapi import HTTPException

from app.api.dependencies.tenant import resolve_tenant_context
from app.api.v1.reports import (
    generate_report as api_generate_report,
    get_dashboard_summary as api_get_dashboard_summary,
    get_report as api_get_report,
    list_reports as api_list_reports,
)
from app.core.context import TenantContext
from app.core.database import AsyncSessionLocal
from app.core.uow import UnitOfWork
from app.db.models import Project, User
from app.domains.analytics.models import APILog, Report
from app.domains.analytics.repository import APILogRepository, ReportRepository
from app.domains.analytics.schemas import ReportGenerate
from app.domains.analytics.service import AnalyticsService
from app.domains.customers.models import CustomerProfile
from app.domains.integrations.models import Integration, IntegrationStatus
from app.domains.messages.models import Message, MessageDirection
from app.domains.orders.models import Order, OrderStatus
from app.services.report_generator import ReportGenerator, generate_report

pytestmark = pytest.mark.asyncio


async def setup_test_analytics_environment():
    """Seed two isolated tenants with orders, messages, integrations, reports, and API logs."""
    async with AsyncSessionLocal() as db:
        now = datetime.utcnow()
        user_a = User(id=uuid4(), email=f"user_an_a_{uuid4()}@example.com", password_hash="hash")
        user_b = User(id=uuid4(), email=f"user_an_b_{uuid4()}@example.com", password_hash="hash")

        proj_a = Project(
            id=uuid4(),
            name="Analytics Project A",
            owner_id=user_a.id,
            project_code=str(uuid4())[:8],
        )
        proj_b = Project(
            id=uuid4(),
            name="Analytics Project B",
            owner_id=user_b.id,
            project_code=str(uuid4())[:8],
        )

        cust_a = CustomerProfile(
            id=uuid4(), project_id=proj_a.id, customer_id=f"ca-{uuid4()}", name="Alice A"
        )
        cust_b = CustomerProfile(
            id=uuid4(), project_id=proj_b.id, customer_id=f"cb-{uuid4()}", name="Bob B"
        )
        db.add_all([user_a, user_b, proj_a, proj_b, cust_a, cust_b])
        await db.flush()

        order_a = Order(
            id=uuid4(),
            project_id=proj_a.id,
            external_id=f"ord-a-{uuid4()}",
            provider="shopify",
            status=OrderStatus.FULFILLED.value,
            total=150.0,
            currency="USD",
            customer={"name": "Alice A", "email": "alice@a.com"},
            items=[{"sku": "SKU-A", "qty": 1}],
            order_date=now,
        )
        order_b = Order(
            id=uuid4(),
            project_id=proj_b.id,
            external_id=f"ord-b-{uuid4()}",
            provider="shopify",
            status=OrderStatus.FULFILLED.value,
            total=9999.0,
            currency="USD",
            customer={"name": "Secret B", "email": "secret@b.com"},
            items=[{"sku": "SKU-B", "qty": 10}],
            order_date=now,
        )
        db.add_all([order_a, order_b])

        msg_a = Message(
            id=uuid4(),
            project_id=proj_a.id,
            customer_id=cust_a.id,
            provider="whatsapp",
            platform="whatsapp",
            direction=MessageDirection.OUTBOUND,
            content="Order confirmed A",
            ai_generated=True,
            extra_data={"is_escalation": True, "response_time": 1.5, "ai_generated": True},
            created_at=now,
        )
        msg_b = Message(
            id=uuid4(),
            project_id=proj_b.id,
            customer_id=cust_b.id,
            provider="whatsapp",
            platform="whatsapp",
            direction=MessageDirection.OUTBOUND,
            content="Confidential message B",
            ai_generated=True,
            extra_data={"is_escalation": True, "response_time": 5.0, "ai_generated": True},
            created_at=now,
        )
        db.add_all([msg_a, msg_b])

        int_fb_a = Integration(
            id=uuid4(),
            project_id=proj_a.id,
            provider="facebook",
            status=IntegrationStatus.CONNECTED,
            config={"page_id": "fb-page-a"},
            extra_data={"page_id": "fb-page-a", "access_token": "secret-fb-token-a"},
        )
        int_ig_a = Integration(
            id=uuid4(),
            project_id=proj_a.id,
            provider="instagram",
            status=IntegrationStatus.CONNECTED,
            config={"page_id": "ig-page-a", "ig_id": "ig-a"},
            extra_data={
                "page_id": "ig-page-a",
                "ig_id": "ig-a",
                "access_token": "secret-ig-token-a",
            },
        )
        int_fb_b = Integration(
            id=uuid4(),
            project_id=proj_b.id,
            provider="facebook",
            status=IntegrationStatus.CONNECTED,
            config={"page_id": "fb-page-b"},
            extra_data={"page_id": "fb-page-b", "access_token": "TOP-SECRET-FB-TOKEN-B"},
        )
        int_ig_b = Integration(
            id=uuid4(),
            project_id=proj_b.id,
            provider="instagram",
            status=IntegrationStatus.CONNECTED,
            config={"page_id": "ig-page-b", "ig_id": "ig-b"},
            extra_data={
                "page_id": "ig-page-b",
                "ig_id": "ig-b",
                "access_token": "TOP-SECRET-IG-TOKEN-B",
            },
        )
        db.add_all([int_fb_a, int_ig_a, int_fb_b, int_ig_b])

        rep_a = Report(
            id=uuid4(),
            project_id=proj_a.id,
            report_type="sales",
            payload={"summary": {"total_revenue": 150.0, "total_orders": 1}},
            summary="Tenant A sales report",
            start_date=now - timedelta(days=7),
            end_date=now,
        )
        rep_b = Report(
            id=uuid4(),
            project_id=proj_b.id,
            report_type="sales",
            payload={"summary": {"total_revenue": 9999.0, "total_orders": 1}},
            summary="Tenant B confidential report",
            start_date=now - timedelta(days=7),
            end_date=now,
        )
        db.add_all([rep_a, rep_b])

        log_a = APILog(
            project_id=proj_a.id,
            method="POST",
            endpoint="/v1/chat/completions",
            status_code=200,
        )
        log_b = APILog(
            project_id=proj_b.id,
            method="POST",
            endpoint="/v1/models/gemini:generateContent",
            status_code=200,
        )
        db.add_all([log_a, log_b])
        await db.flush()
        log_a_id = log_a.id
        log_b_id = log_b.id
        proj_a_id = proj_a.id
        proj_b_id = proj_b.id
        user_a_id = user_a.id
        user_b_id = user_b.id
        rep_a_id = rep_a.id
        rep_b_id = rep_b.id
        order_a_id = order_a.id
        order_b_id = order_b.id
        await db.commit()

        ctx_a = TenantContext(project_id=proj_a_id, user_id=user_a_id, role="owner")
        ctx_b = TenantContext(project_id=proj_b_id, user_id=user_b_id, role="owner")
        ids = {
            "proj_a": proj_a_id,
            "proj_b": proj_b_id,
            "user_a": user_a_id,
            "user_b": user_b_id,
            "rep_a": rep_a_id,
            "rep_b": rep_b_id,
            "log_a": log_a_id,
            "log_b": log_b_id,
            "order_a": order_a_id,
            "order_b": order_b_id,
        }
        return ctx_a, ctx_b, ids


# ============================================================================
# A. Same-tenant positive cases
# ============================================================================


async def test_same_tenant_report_retrieval_succeeds():
    """1. Same-tenant report retrieval and listing succeed via repo, service, and API."""
    ctx_a, _, ids = await setup_test_analytics_environment()
    async with AsyncSessionLocal() as db:
        service = AnalyticsService(UnitOfWork(db), ctx_a)

        fetched = await api_get_report(
            project_id=ids["proj_a"],
            report_id=ids["rep_a"],
            context=ctx_a,
            service=service,
        )
        assert fetched.id == ids["rep_a"]
        assert fetched.project_id == ids["proj_a"]

        listed = await api_list_reports(
            project_id=ids["proj_a"],
            report_type=None,
            page=1,
            page_size=20,
            context=ctx_a,
            service=service,
        )
        assert any(r.id == ids["rep_a"] for r in listed)
        assert all(r.project_id == ids["proj_a"] for r in listed)


async def test_same_tenant_report_generation_succeeds():
    """2. Same-tenant report generation succeeds and persists report under TenantContext."""
    ctx_a, _, ids = await setup_test_analytics_environment()
    now = datetime.utcnow()
    async with AsyncSessionLocal() as db:
        service = AnalyticsService(UnitOfWork(db), ctx_a)
        req = ReportGenerate(
            report_type="orders",
            start_date=now - timedelta(days=7),
            end_date=now + timedelta(minutes=5),
        )
        created = await api_generate_report(
            project_id=ids["proj_a"],
            report_data=req,
            context=ctx_a,
            service=service,
        )
        assert created.project_id == ids["proj_a"]
        assert created.report_type == "orders"
        assert created.payload["summary"]["total_orders"] == 1


async def test_same_tenant_dashboard_summary_succeeds():
    """3. Same-tenant dashboard summary succeeds with accurate period stats."""
    ctx_a, _, ids = await setup_test_analytics_environment()
    async with AsyncSessionLocal() as db:
        service = AnalyticsService(UnitOfWork(db), ctx_a)
        with patch(
            "app.services.integrations.facebook.FacebookClient.get_page_engagement",
            new_callable=AsyncMock,
            return_value=None,
        ), patch(
            "app.services.integrations.instagram.InstagramClient.get_instagram_engagement",
            new_callable=AsyncMock,
            return_value=None,
        ):
            summary = await api_get_dashboard_summary(
                project_id=ids["proj_a"],
                context=ctx_a,
                service=service,
            )
            assert summary["today"]["orders"] == 1
            assert summary["today"]["revenue"] == 150.0
            assert summary["today"]["messages"] == 1
            assert summary["today"]["escalations"] == 1


async def test_same_tenant_external_provider_call_allowed_when_authorized():
    """4. Authorized tenant can invoke external providers (Facebook, Instagram, AI) with its own context."""
    ctx_a, _, ids = await setup_test_analytics_environment()
    async with AsyncSessionLocal() as db:
        service = AnalyticsService(UnitOfWork(db), ctx_a)
        with patch(
            "app.services.integrations.facebook.FacebookClient.get_page_engagement",
            new_callable=AsyncMock,
            return_value={"name": "Page A", "followers_count": 500, "fan_count": 450},
        ) as mock_fb, patch(
            "app.services.integrations.instagram.InstagramClient.get_instagram_engagement",
            new_callable=AsyncMock,
            return_value={
                "name": "IG A",
                "username": "iga",
                "followers_count": 1200,
                "media_count": 42,
            },
        ) as mock_ig:
            summary = await service.get_dashboard_summary(context=ctx_a, project_id=ids["proj_a"])
            assert mock_fb.call_count == 1
            assert mock_ig.call_count == 1
            assert summary["social_engagement"]["facebook"]["name"] == "Page A"
            assert summary["social_engagement"]["instagram"]["username"] == "iga"


# ============================================================================
# B. Cross-tenant isolation
# ============================================================================


async def test_cross_tenant_get_report_by_report_id_returns_404():
    """5. Cross-tenant get report by report_id returns 404."""
    ctx_a, _, ids = await setup_test_analytics_environment()
    async with AsyncSessionLocal() as db:
        service = AnalyticsService(UnitOfWork(db), ctx_a)
        with pytest.raises(HTTPException) as exc:
            await api_get_report(
                project_id=ids["proj_a"],
                report_id=ids["rep_b"],
                context=ctx_a,
                service=service,
            )
        assert exc.value.status_code == 404


async def test_cross_tenant_get_analytics_resource_by_id_denied():
    """6. Cross-tenant get analytics resource (Report and APILog) by ID is denied at SQL level."""
    ctx_a, ctx_b, ids = await setup_test_analytics_environment()
    async with AsyncSessionLocal() as db:
        rep_repo_a = ReportRepository(db, ctx_a)
        log_repo_a = APILogRepository(db, ctx_a)

        assert await rep_repo_a.get_by_context(ids["rep_b"], ctx_a) is None
        assert await rep_repo_a.get(ids["rep_b"], ctx_a) is None
        assert await log_repo_a.get_by_context(ids["log_b"], ctx_a) is None
        assert await log_repo_a.get(ids["log_b"], ctx_a) is None

        # Tenant B can still read its own resources
        assert await ReportRepository(db, ctx_b).get_by_context(ids["rep_b"], ctx_b) is not None
        assert await APILogRepository(db, ctx_b).get_by_context(ids["log_b"], ctx_b) is not None


async def test_forged_project_id_mismatching_tenant_context_rejected():
    """7. Forged project_id mismatching TenantContext is rejected across repo, service, generator, and API."""
    ctx_a, _, ids = await setup_test_analytics_environment()
    async with AsyncSessionLocal() as db:
        rep_repo = ReportRepository(db, ctx_a)
        log_repo = APILogRepository(db, ctx_a)
        service = AnalyticsService(UnitOfWork(db), ctx_a)

        with pytest.raises(PermissionError):
            await rep_repo.get_by_project(ids["proj_b"], ctx_a)

        with pytest.raises(PermissionError):
            await log_repo.get_by_project(ids["proj_b"], ctx_a)

        with pytest.raises(PermissionError):
            ReportGenerator(db, project_id=ids["proj_b"], context=ctx_a)

        with pytest.raises(PermissionError):
            await service.list_reports(context=ctx_a, project_id=ids["proj_b"])

        with pytest.raises(HTTPException) as exc:
            await resolve_tenant_context(ids["proj_b"], ids["user_a"], db)
        assert exc.value.status_code == 404


async def test_cross_tenant_dashboard_summary_blocked():
    """8. Cross-tenant dashboard-summary request is blocked before reading any Tenant B data."""
    ctx_a, _, ids = await setup_test_analytics_environment()
    async with AsyncSessionLocal() as db:
        service = AnalyticsService(UnitOfWork(db), ctx_a)
        with pytest.raises(HTTPException) as exc:
            await api_get_dashboard_summary(
                project_id=ids["proj_b"],
                context=ctx_a,
                service=service,
            )
        assert exc.value.status_code in (403, 404)


async def test_cross_tenant_report_generate_blocked():
    """9. Cross-tenant report generate request is blocked."""
    ctx_a, _, ids = await setup_test_analytics_environment()
    now = datetime.utcnow()
    async with AsyncSessionLocal() as db:
        service = AnalyticsService(UnitOfWork(db), ctx_a)
        req = ReportGenerate(
            report_type="sales",
            start_date=now - timedelta(days=7),
            end_date=now,
        )
        with pytest.raises(HTTPException) as exc:
            await api_generate_report(
                project_id=ids["proj_b"],
                report_data=req,
                context=ctx_a,
                service=service,
            )
        assert exc.value.status_code in (403, 404)


# ============================================================================
# C. External side-effect suppression
# ============================================================================


async def test_unauthorized_dashboard_summary_makes_zero_facebook_calls():
    """10. Unauthorized/cross-tenant dashboard-summary makes 0 Facebook API calls."""
    ctx_a, _, ids = await setup_test_analytics_environment()
    async with AsyncSessionLocal() as db:
        service = AnalyticsService(UnitOfWork(db), ctx_a)
        with patch("app.domains.analytics.service.FacebookClient") as mock_fb_cls, patch(
            "app.services.integrations.facebook.FacebookClient.get_page_engagement",
            new_callable=AsyncMock,
        ) as mock_fb_method:
            with pytest.raises(HTTPException) as exc:
                await api_get_dashboard_summary(
                    project_id=ids["proj_b"],
                    context=ctx_a,
                    service=service,
                )
            assert exc.value.status_code in (403, 404)
            mock_fb_cls.assert_not_called()
            mock_fb_method.assert_not_called()


async def test_unauthorized_dashboard_summary_makes_zero_instagram_calls():
    """11. Unauthorized/cross-tenant dashboard-summary makes 0 Instagram API calls."""
    ctx_a, _, ids = await setup_test_analytics_environment()
    async with AsyncSessionLocal() as db:
        service = AnalyticsService(UnitOfWork(db), ctx_a)
        with patch("app.domains.analytics.service.InstagramClient") as mock_ig_cls, patch(
            "app.services.integrations.instagram.InstagramClient.get_instagram_engagement",
            new_callable=AsyncMock,
        ) as mock_ig_method:
            with pytest.raises(HTTPException) as exc:
                await api_get_dashboard_summary(
                    project_id=ids["proj_b"],
                    context=ctx_a,
                    service=service,
                )
            assert exc.value.status_code in (403, 404)
            mock_ig_cls.assert_not_called()
            mock_ig_method.assert_not_called()


async def test_unauthorized_report_generation_makes_zero_ai_calls():
    """12. Unauthorized/cross-tenant report generation makes 0 Gemini/AI calls."""
    ctx_a, _, ids = await setup_test_analytics_environment()
    now = datetime.utcnow()
    async with AsyncSessionLocal() as db:
        mock_ai = MagicMock()
        mock_ai.generate_response = AsyncMock()
        with patch("app.services.report_generator.get_ai_provider", return_value=mock_ai) as mock_factory:
            with pytest.raises(PermissionError):
                await generate_report(
                    db=db,
                    project_id=ids["proj_b"],
                    report_type="sales",
                    context=ctx_a,
                )
            mock_factory.assert_not_called()
            mock_ai.generate_response.assert_not_called()

            with pytest.raises(PermissionError):
                await generate_report(
                    db=db,
                    project_id=ids["proj_a"],
                    report_type="sales",
                    context=None,
                )
            mock_factory.assert_not_called()
            mock_ai.generate_response.assert_not_called()


# ============================================================================
# D. Credential isolation
# ============================================================================


async def test_tenant_a_cannot_access_tenant_b_integration_oauth_credentials():
    """13. Tenant A never accesses Tenant B's Integration.extra_data OAuth credentials."""
    ctx_a, _, ids = await setup_test_analytics_environment()
    async with AsyncSessionLocal() as db:
        repo_a = ReportRepository(db, ctx_a)
        integrations_a = await repo_a.get_tenant_integrations(ctx_a)
        assert len(integrations_a) == 2
        for integration in integrations_a:
            assert integration.project_id == ids["proj_a"]
            token = (integration.extra_data or {}).get("access_token", "")
            assert "TOP-SECRET" not in token

        captured_fb_configs = []
        captured_ig_configs = []

        class SpyFacebookClient:
            def __init__(self, config):
                captured_fb_configs.append(config)

            async def get_page_engagement(self):
                return {"name": "FB A", "followers_count": 10, "fan_count": 10}

        class SpyInstagramClient:
            def __init__(self, config):
                captured_ig_configs.append(config)

            async def get_instagram_engagement(self):
                return {"name": "IG A", "username": "iga", "followers_count": 20, "media_count": 5}

        service = AnalyticsService(UnitOfWork(db), ctx_a)
        with patch("app.domains.analytics.service.FacebookClient", SpyFacebookClient), patch(
            "app.domains.analytics.service.InstagramClient", SpyInstagramClient
        ):
            await service.get_dashboard_summary(context=ctx_a)

        assert len(captured_fb_configs) == 1
        assert captured_fb_configs[0].get("access_token") == "secret-fb-token-a"
        assert len(captured_ig_configs) == 1
        assert captured_ig_configs[0].get("access_token") == "secret-ig-token-a"


# ============================================================================
# E. Fail-closed
# ============================================================================


async def test_missing_tenant_context_raises_permission_error_in_report_repository():
    """14. Missing TenantContext raises PermissionError in ReportRepository."""
    _, _, ids = await setup_test_analytics_environment()
    now = datetime.utcnow()
    async with AsyncSessionLocal() as db:
        repo = ReportRepository(db, None)
        with pytest.raises(PermissionError):
            await repo.get(ids["rep_a"])
        with pytest.raises(PermissionError):
            await repo.get_by_context(ids["rep_a"])
        with pytest.raises(PermissionError):
            await repo.list_by_context()
        with pytest.raises(PermissionError):
            await repo.get_range_orders(now - timedelta(days=1), now)
        with pytest.raises(PermissionError):
            await repo.get_range_messages(now - timedelta(days=1), now)
        with pytest.raises(PermissionError):
            await repo.get_period_summary_stats(now - timedelta(days=1), now)
        with pytest.raises(PermissionError):
            await repo.get_tenant_integrations()


async def test_missing_tenant_context_raises_permission_error_in_apilog_repository():
    """15. Missing TenantContext raises PermissionError in APILogRepository."""
    _, _, ids = await setup_test_analytics_environment()
    async with AsyncSessionLocal() as db:
        repo = APILogRepository(db, None)
        with pytest.raises(PermissionError):
            await repo.get(ids["log_a"])
        with pytest.raises(PermissionError):
            await repo.get_by_context(ids["log_a"])
        with pytest.raises(PermissionError):
            await repo.list_by_context()
        with pytest.raises(PermissionError):
            await repo.get_by_project(ids["proj_a"])


async def test_missing_tenant_context_raises_permission_error_in_analytics_service():
    """16. Missing TenantContext raises PermissionError in AnalyticsService."""
    _, _, ids = await setup_test_analytics_environment()
    now = datetime.utcnow()
    async with AsyncSessionLocal() as db:
        service = AnalyticsService(UnitOfWork(db), None)
        with pytest.raises(PermissionError):
            await service.list_reports()
        with pytest.raises(PermissionError):
            await service.get_report(ids["rep_a"])
        with pytest.raises(PermissionError):
            await service.generate_project_report("sales", now - timedelta(days=7), now)
        with pytest.raises(PermissionError):
            await service.get_dashboard_summary()


async def test_missing_tenant_context_raises_permission_error_in_report_generator():
    """17. Missing TenantContext raises PermissionError in ReportGenerator and generate_report."""
    _, _, ids = await setup_test_analytics_environment()
    async with AsyncSessionLocal() as db:
        with pytest.raises(PermissionError):
            ReportGenerator(db, project_id=ids["proj_a"], context=None)
        with pytest.raises(PermissionError):
            await generate_report(db, project_id=ids["proj_a"], report_type="sales", context=None)


# ============================================================================
# F. Aggregate isolation
# ============================================================================


async def test_dashboard_summary_aggregates_only_current_tenant_orders_and_messages():
    """18. Dashboard summary aggregates only current tenant's Order and Message rows."""
    ctx_a, ctx_b, _ = await setup_test_analytics_environment()
    async with AsyncSessionLocal() as db:
        with patch(
            "app.services.integrations.facebook.FacebookClient.get_page_engagement",
            new_callable=AsyncMock,
            return_value=None,
        ), patch(
            "app.services.integrations.instagram.InstagramClient.get_instagram_engagement",
            new_callable=AsyncMock,
            return_value=None,
        ):
            summary_a = await AnalyticsService(UnitOfWork(db), ctx_a).get_dashboard_summary(ctx_a)
            summary_b = await AnalyticsService(UnitOfWork(db), ctx_b).get_dashboard_summary(ctx_b)

            # Tenant A has $150 revenue; Tenant B has $9999 revenue. Neither contaminates the other.
            assert summary_a["today"]["orders"] == 1
            assert summary_a["today"]["revenue"] == 150.0
            assert summary_b["today"]["orders"] == 1
            assert summary_b["today"]["revenue"] == 9999.0


async def test_generated_reports_aggregate_only_current_tenant_data():
    """19. Generated reports (sales, orders, customers, performance, roi) aggregate only current tenant's data."""
    ctx_a, _, ids = await setup_test_analytics_environment()
    now = datetime.utcnow()
    start = now - timedelta(days=7)
    end = now + timedelta(minutes=5)

    async with AsyncSessionLocal() as db:
        mock_ai = MagicMock()
        mock_ai.generate_response = AsyncMock(
            return_value=MagicMock(text='{"trends": ["up"], "concerns": [], "recommendations": [], "predictions": []}')
        )
        with patch("app.services.report_generator.get_ai_provider", return_value=mock_ai):
            gen_a = ReportGenerator(db, context=ctx_a)

            sales_a = await gen_a.generate_sales_report(start, end)
            assert sales_a["summary"]["total_orders"] == 1
            assert sales_a["summary"]["total_revenue"] == 150.0

            orders_a = await gen_a.generate_order_report(start, end)
            assert orders_a["summary"]["total_orders"] == 1
            order_ids = [o["id"] for o in orders_a["orders"]]
            assert str(ids["order_a"]) in order_ids
            assert str(ids["order_b"]) not in order_ids

            cust_a = await gen_a.generate_customer_report(start, end)
            assert cust_a["summary"]["total_messages"] == 1
            assert cust_a["summary"]["unique_customers"] == 1

            perf_a = await gen_a.generate_performance_report(start, end)
            assert perf_a["ai_performance"]["ai_generated_messages"] == 1
            assert perf_a["integrations"]["total"] == 2

            roi_a = await gen_a.generate_roi_report(start, end)
            assert roi_a["revenue_impact"]["total_revenue"] == 150.0
            assert roi_a["revenue_impact"]["orders_processed"] == 1
