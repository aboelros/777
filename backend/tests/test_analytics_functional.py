"""
Functional correctness, edge-case, numeric accuracy, provider resilience, and API contract
test suite for Reconstructed Phase 2 Group 9: Analytics & Reporting.
"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
import pytest
from fastapi import HTTPException

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
from app.domains.analytics.schemas import ReportGenerate, ReportResponse
from app.domains.analytics.service import AnalyticsService
from app.domains.customers.models import CustomerProfile
from app.domains.integrations.models import Integration, IntegrationStatus
from app.domains.messages.models import Message, MessageDirection
from app.domains.orders.models import Order, OrderStatus
from app.services.report_generator import ReportGenerator, generate_report

pytestmark = pytest.mark.asyncio


async def create_isolated_tenant(db, with_data: bool = True, base_time: datetime = None):
    """Create a fresh tenant project, optionally seeded with deterministic analytics fixtures."""
    now = base_time or datetime.utcnow().replace(microsecond=0)
    user = User(id=uuid4(), email=f"func_an_{uuid4()}@example.com", password_hash="hash")
    proj = Project(
        id=uuid4(),
        name="Functional Analytics Project",
        owner_id=user.id,
        project_code=str(uuid4())[:8],
    )
    db.add_all([user, proj])
    await db.flush()

    ctx = TenantContext(project_id=proj.id, user_id=user.id, role="owner")
    if not with_data:
        await db.commit()
        return ctx, {"proj_id": proj.id, "user_id": user.id, "now": now}

    cust_1 = CustomerProfile(
        id=uuid4(), project_id=proj.id, customer_id=f"c1-{uuid4()}", name="Customer One"
    )
    cust_2 = CustomerProfile(
        id=uuid4(), project_id=proj.id, customer_id=f"c2-{uuid4()}", name="Customer Two"
    )
    db.add_all([cust_1, cust_2])
    await db.flush()

    # Deterministic orders:
    # 1. Fulfilled order ($100.00) 2 days ago
    # 2. Pending order ($50.00) 1 day ago
    # 3. Cancelled order ($25.00) today (1 hour ago)
    o1 = Order(
        id=uuid4(),
        project_id=proj.id,
        external_id=f"o1-{uuid4()}",
        provider="shopify",
        status=OrderStatus.FULFILLED.value,
        total=100.0,
        currency="USD",
        customer={"name": "Customer One", "email": "c1@example.com"},
        items=[{"sku": "A1"}, {"sku": "A2"}],
        order_date=now - timedelta(days=2),
    )
    o2 = Order(
        id=uuid4(),
        project_id=proj.id,
        external_id=f"o2-{uuid4()}",
        provider="woocommerce",
        status=OrderStatus.PENDING.value,
        total=50.0,
        currency="USD",
        customer={"name": "Customer Two", "email": "c2@example.com"},
        items=[{"sku": "B1"}],
        order_date=now - timedelta(days=1),
    )
    o3 = Order(
        id=uuid4(),
        project_id=proj.id,
        external_id=f"o3-{uuid4()}",
        provider="shopify",
        status=OrderStatus.CANCELLED.value,
        total=25.0,
        currency="USD",
        customer={"name": "Customer One", "email": "c1@example.com"},
        items=[],
        order_date=now - timedelta(hours=1),
    )
    db.add_all([o1, o2, o3])

    # Deterministic messages:
    # m1: Inbound from cust_1 (whatsapp)
    # m2: Outbound AI-generated to cust_1 (whatsapp, response_time=2.0, escalation=True)
    # m3: Inbound from cust_2 (instagram)
    # m4: Outbound human to cust_2 (instagram, response_time=4.0, escalation=False)
    m1 = Message(
        id=uuid4(),
        project_id=proj.id,
        customer_id=cust_1.id,
        provider="whatsapp",
        platform="whatsapp",
        direction=MessageDirection.INBOUND,
        content="Where is my order?",
        ai_generated=False,
        extra_data={},
        created_at=now - timedelta(days=2),
    )
    m2 = Message(
        id=uuid4(),
        project_id=proj.id,
        customer_id=cust_1.id,
        provider="whatsapp",
        platform="whatsapp",
        direction=MessageDirection.OUTBOUND,
        content="Your order is on the way",
        ai_generated=True,
        extra_data={"ai_generated": True, "response_time": 2.0, "is_escalation": True},
        created_at=now - timedelta(days=2),
    )
    m3 = Message(
        id=uuid4(),
        project_id=proj.id,
        customer_id=cust_2.id,
        provider="instagram",
        platform="instagram",
        direction=MessageDirection.INBOUND,
        content="Do you ship internationally?",
        ai_generated=False,
        extra_data={},
        created_at=now - timedelta(hours=1),
    )
    m4 = Message(
        id=uuid4(),
        project_id=proj.id,
        customer_id=cust_2.id,
        provider="instagram",
        platform="instagram",
        direction=MessageDirection.OUTBOUND,
        content="Yes we do!",
        ai_generated=False,
        extra_data={"ai_generated": False, "response_time": 4.0, "is_escalation": False},
        created_at=now - timedelta(hours=1),
    )
    db.add_all([m1, m2, m3, m4])

    int_fb = Integration(
        id=uuid4(),
        project_id=proj.id,
        provider="facebook",
        status=IntegrationStatus.CONNECTED,
        config={"page_id": "fb-1"},
        extra_data={"page_id": "fb-1", "access_token": "tok-fb"},
    )
    int_ig = Integration(
        id=uuid4(),
        project_id=proj.id,
        provider="instagram",
        status=IntegrationStatus.ERROR,
        config={"page_id": "ig-1"},
        extra_data={"page_id": "ig-1", "access_token": "tok-ig"},
    )
    db.add_all([int_fb, int_ig])
    await db.commit()

    return ctx, {
        "proj_id": proj.id,
        "user_id": user.id,
        "now": now,
        "o1": o1.id,
        "o2": o2.id,
        "o3": o3.id,
    }


# ============================================================================
# 1. Numeric Correctness Across All 5 Report Types
# ============================================================================


async def test_all_five_report_types_numeric_correctness():
    """Verify exact numeric calculations for sales, orders, customers, performance, and roi."""
    async with AsyncSessionLocal() as db:
        ctx, meta = await create_isolated_tenant(db, with_data=True)
        now = meta["now"]
        start = now - timedelta(days=7)
        end = now + timedelta(minutes=1)

        mock_ai = MagicMock()
        mock_ai.generate_response = AsyncMock(
            return_value=MagicMock(
                text='{"trends": ["steady"], "concerns": [], "recommendations": ["upsell"], "predictions": []}'
            )
        )
        with patch("app.services.report_generator.get_ai_provider", return_value=mock_ai):
            gen = ReportGenerator(db, context=ctx)

            # 1. Sales report: 3 orders ($100 + $50 + $25 = $175), avg = 58.33
            sales = await gen.generate_sales_report(start, end)
            assert sales["summary"]["total_revenue"] == 175.0
            assert sales["summary"]["total_orders"] == 3
            assert sales["summary"]["average_order_value"] == 58.33
            assert sales["status_breakdown"]["fulfilled"] == 1
            assert sales["status_breakdown"]["pending"] == 1
            assert sales["status_breakdown"]["cancelled"] == 1
            assert sales["ai_insights"]["trends"] == ["steady"]

            # 2. Orders report: fulfillment_rate = 33.33%, cancellation_rate = 33.33%
            orders = await gen.generate_order_report(start, end)
            assert orders["summary"]["total_orders"] == 3
            assert orders["summary"]["fulfilled_orders"] == 1
            assert orders["summary"]["pending_orders"] == 1
            assert orders["summary"]["cancelled_orders"] == 1
            assert orders["summary"]["fulfillment_rate"] == 33.33
            assert orders["summary"]["cancellation_rate"] == 33.33
            assert orders["provider_breakdown"] == {"shopify": 2, "woocommerce": 1}
            assert len(orders["orders"]) == 3

            # 3. Customers report: 4 messages (2 inbound, 2 outbound), 2 unique customers, 100% response rate
            customers = await gen.generate_customer_report(start, end)
            assert customers["summary"]["total_messages"] == 4
            assert customers["summary"]["inbound_messages"] == 2
            assert customers["summary"]["outbound_messages"] == 2
            assert customers["summary"]["unique_customers"] == 2
            assert customers["summary"]["response_rate"] == 100.0
            assert customers["summary"]["avg_messages_per_customer"] == 2.0
            assert customers["channel_usage"] == {"whatsapp": 2, "instagram": 2}

            # 4. Performance report: 1 AI message out of 2 outbound = 50.0%, avg response time = (2.0 + 4.0)/2 = 3.0s
            # Integrations: 2 total, 1CONNECTED (active), 1 ERROR (inactive)
            perf = await gen.generate_performance_report(start, end)
            assert perf["ai_performance"]["ai_generated_messages"] == 1
            assert perf["ai_performance"]["total_outbound_messages"] == 2
            assert perf["ai_performance"]["ai_usage_rate"] == 50.0
            assert perf["ai_performance"]["average_response_time_seconds"] == 3.0
            assert perf["integrations"]["total"] == 2
            assert perf["integrations"]["active"] == 1
            assert perf["integrations"]["inactive"] == 1
            assert perf["system_health"]["status"] == "healthy"

            # 5. ROI report: 1 AI message -> 5 mins = 0.0833h -> round(0.08, 2), cost savings = (5/60)*20 = 1.67
            # 3 orders / 2 conversations = 150.0% conversion rate, revenue_per_conversation = 87.5
            roi = await gen.generate_roi_report(start, end)
            assert roi["revenue_impact"]["total_revenue"] == 175.0
            assert roi["revenue_impact"]["orders_processed"] == 3
            assert roi["revenue_impact"]["conversations_handled"] == 2
            assert roi["revenue_impact"]["conversion_rate"] == 150.0
            assert roi["automation_efficiency"]["ai_messages_sent"] == 1
            assert roi["automation_efficiency"]["time_saved_hours"] == 0.08
            assert roi["automation_efficiency"]["estimated_cost_savings"] == 1.67
            assert roi["automation_efficiency"]["automation_rate"] == 25.0
            assert roi["productivity_gains"]["revenue_per_conversation"] == 87.5


# ============================================================================
# 2. Empty Datasets (Zero Orders, Messages, Customers, Integrations)
# ============================================================================


async def test_empty_dataset_reports_and_dashboard_no_division_by_zero():
    """Verify all 5 report types and dashboard-summary handle empty datasets gracefully."""
    async with AsyncSessionLocal() as db:
        ctx, meta = await create_isolated_tenant(db, with_data=False)
        now = meta["now"]
        start = now - timedelta(days=7)
        end = now

        mock_ai = MagicMock()
        mock_ai.generate_response = AsyncMock()
        with patch("app.services.report_generator.get_ai_provider", return_value=mock_ai):
            gen = ReportGenerator(db, context=ctx)

            sales = await gen.generate_sales_report(start, end)
            assert sales["summary"]["total_revenue"] == 0
            assert sales["summary"]["total_orders"] == 0
            assert sales["summary"]["average_order_value"] == 0
            assert sales["summary"]["currency"] == "USD"
            assert "ai_insights" not in sales
            mock_ai.generate_response.assert_not_called()

            orders = await gen.generate_order_report(start, end)
            assert orders["summary"]["total_orders"] == 0
            assert orders["summary"]["fulfillment_rate"] == 0
            assert orders["summary"]["cancellation_rate"] == 0
            assert orders["orders"] == []

            customers = await gen.generate_customer_report(start, end)
            assert customers["summary"]["total_messages"] == 0
            assert customers["summary"]["unique_customers"] == 0
            assert customers["summary"]["response_rate"] == 0
            assert customers["summary"]["avg_messages_per_customer"] == 0
            assert customers["engagement_trend"] == {}

            perf = await gen.generate_performance_report(start, end)
            assert perf["ai_performance"]["ai_usage_rate"] == 0
            assert perf["ai_performance"]["average_response_time_seconds"] == 0
            assert perf["integrations"]["total"] == 0
            assert perf["system_health"]["status"] == "warning"

            roi = await gen.generate_roi_report(start, end)
            assert roi["revenue_impact"]["total_revenue"] == 0
            assert roi["revenue_impact"]["conversion_rate"] == 0
            assert roi["automation_efficiency"]["automation_rate"] == 0
            assert roi["productivity_gains"]["revenue_per_conversation"] == 0

            # Same-day range (start == end) must not divide by zero in messages_per_day / orders_per_day
            same_day_roi = await gen.generate_roi_report(now, now)
            assert same_day_roi["productivity_gains"]["messages_per_day"] == 0

            # Dashboard summary on empty project
            service = AnalyticsService(UnitOfWork(db), ctx)
            dash = await service.get_dashboard_summary(context=ctx)
            for period_key in ("today", "yesterday", "this_week", "last_week", "this_month", "last_month"):
                assert dash[period_key] == {"orders": 0, "revenue": 0.0, "messages": 0, "escalations": 0}
            assert "social_engagement" not in dash


# ============================================================================
# 3. Date Boundary Conditions & Historical Custom Date Ranges
# ============================================================================


async def test_date_boundaries_inclusive_and_historical_short_range():
    """
    Verify exact start/end boundary inclusion and that a short historical range (e.g. 5 days, 60 days ago)
    queries that exact historical window rather than being overwritten by last_7_days from utcnow().
    """
    async with AsyncSessionLocal() as db:
        ctx, _ = await create_isolated_tenant(db, with_data=False)
        hist_start = datetime(2025, 6, 10, 12, 0, 0)
        hist_end = datetime(2025, 6, 15, 12, 0, 0)  # 5-day historical window

        # Order exactly on start_date, order exactly on end_date, and orders 1 second outside
        o_before = Order(
            id=uuid4(),
            project_id=ctx.project_id,
            external_id=f"ob-{uuid4()}",
            provider="shopify",
            status=OrderStatus.FULFILLED.value,
            total=500.0,
            currency="USD",
            order_date=hist_start - timedelta(seconds=1),
        )
        o_on_start = Order(
            id=uuid4(),
            project_id=ctx.project_id,
            external_id=f"os-{uuid4()}",
            provider="shopify",
            status=OrderStatus.FULFILLED.value,
            total=100.0,
            currency="USD",
            order_date=hist_start,
        )
        o_on_end = Order(
            id=uuid4(),
            project_id=ctx.project_id,
            external_id=f"oe-{uuid4()}",
            provider="shopify",
            status=OrderStatus.FULFILLED.value,
            total=200.0,
            currency="USD",
            order_date=hist_end,
        )
        o_after = Order(
            id=uuid4(),
            project_id=ctx.project_id,
            external_id=f"oa-{uuid4()}",
            provider="shopify",
            status=OrderStatus.FULFILLED.value,
            total=900.0,
            currency="USD",
            order_date=hist_end + timedelta(seconds=1),
        )
        db.add_all([o_before, o_on_start, o_on_end, o_after])
        await db.commit()

        service = AnalyticsService(UnitOfWork(db), ctx)
        req = ReportGenerate(
            report_type="orders",
            start_date=hist_start,
            end_date=hist_end,
        )
        report = await api_generate_report(
            project_id=ctx.project_id,
            report_data=req,
            context=ctx,
            service=service,
        )
        # Must include ONLY o_on_start ($100) and o_on_end ($200) -> 2 orders!
        assert report.payload["summary"]["total_orders"] == 2
        assert report.payload["period"]["start"].startswith("2025-06-10")
        assert report.payload["period"]["end"].startswith("2025-06-15")


async def test_inverted_date_range_start_after_end_rejected():
    """Verify start_date > end_date is rejected with 400 Bad Request."""
    async with AsyncSessionLocal() as db:
        ctx, meta = await create_isolated_tenant(db, with_data=False)
        now = meta["now"]
        service = AnalyticsService(UnitOfWork(db), ctx)
        req = ReportGenerate(
            report_type="sales",
            start_date=now,
            end_date=now - timedelta(days=5),
        )
        with pytest.raises(HTTPException) as exc:
            await api_generate_report(
                project_id=ctx.project_id,
                report_data=req,
                context=ctx,
                service=service,
            )
        assert exc.value.status_code in (400, 422)


# ============================================================================
# 4. Persistence, Listing, Filtering, Pagination, and Schema Validation
# ============================================================================


async def test_report_persistence_listing_filtering_and_pagination():
    """Generate multiple reports and verify retrieval, filtering by type, and pagination."""
    async with AsyncSessionLocal() as db:
        ctx, meta = await create_isolated_tenant(db, with_data=True)
        now = meta["now"]
        service = AnalyticsService(UnitOfWork(db), ctx)

        mock_ai = MagicMock()
        mock_ai.generate_response = AsyncMock(return_value=MagicMock(text="Plain text AI summary"))
        with patch("app.services.report_generator.get_ai_provider", return_value=mock_ai):
            r_sales = await api_generate_report(
                project_id=ctx.project_id,
                report_data=ReportGenerate(
                    report_type="sales",
                    start_date=now - timedelta(days=7),
                    end_date=now + timedelta(minutes=1),
                ),
                context=ctx,
                service=service,
            )
            r_perf = await api_generate_report(
                project_id=ctx.project_id,
                report_data=ReportGenerate(
                    report_type="performance",
                    start_date=now - timedelta(days=7),
                    end_date=now + timedelta(minutes=1),
                ),
                context=ctx,
                service=service,
            )

        # Validate Pydantic ReportResponse serialization
        validated_sales = ReportResponse.model_validate(r_sales)
        assert validated_sales.id == r_sales.id
        assert "Generated 3 orders with $175.00 in total revenue." in (validated_sales.summary or "")

        # Retrieve by ID
        fetched = await api_get_report(
            project_id=ctx.project_id,
            report_id=r_perf.id,
            context=ctx,
            service=service,
        )
        assert fetched.id == r_perf.id
        assert fetched.payload == r_perf.payload

        # List with report_type filter
        only_perf = await api_list_reports(
            project_id=ctx.project_id,
            report_type="performance",
            page=1,
            page_size=20,
            context=ctx,
            service=service,
        )
        assert len(only_perf) == 1
        assert only_perf[0].id == r_perf.id

        # Pagination: page_size=1
        page_1 = await api_list_reports(
            project_id=ctx.project_id,
            report_type=None,
            page=1,
            page_size=1,
            context=ctx,
            service=service,
        )
        page_2 = await api_list_reports(
            project_id=ctx.project_id,
            report_type=None,
            page=2,
            page_size=1,
            context=ctx,
            service=service,
        )
        assert len(page_1) == 1
        assert len(page_2) == 1
        assert page_1[0].id != page_2[0].id


# ============================================================================
# 5. External Provider Failure & Partial Failure Resilience
# ============================================================================


async def test_external_provider_failures_and_partial_failure_isolation():
    """
    Verify:
    - If Instagram fails with an exception while Facebook succeeds, Facebook metrics are still returned.
    - If AI provider fails during sales report generation, report still succeeds with fallback error key.
    """
    async with AsyncSessionLocal() as db:
        ctx, meta = await create_isolated_tenant(db, with_data=True)
        now = meta["now"]
        service = AnalyticsService(UnitOfWork(db), ctx)

        # Case 1: Facebook succeeds, Instagram raises RuntimeError
        with patch(
            "app.services.integrations.facebook.FacebookClient.get_page_engagement",
            new_callable=AsyncMock,
            return_value={"name": "Healthy FB Page", "followers_count": 300, "fan_count": 280},
        ), patch(
            "app.services.integrations.instagram.InstagramClient.get_instagram_engagement",
            new_callable=AsyncMock,
            side_effect=RuntimeError("Instagram API timeout"),
        ):
            dash = await service.get_dashboard_summary(context=ctx)
            assert "social_engagement" in dash
            assert dash["social_engagement"]["facebook"]["name"] == "Healthy FB Page"
            assert "instagram" not in dash["social_engagement"]

        # Case 2: AI provider raises RuntimeError during sales report generation
        failing_ai = MagicMock()
        failing_ai.generate_response = AsyncMock(side_effect=RuntimeError("Gemini quota exceeded"))
        with patch("app.services.report_generator.get_ai_provider", return_value=failing_ai):
            gen = ReportGenerator(db, context=ctx)
            sales = await gen.generate_sales_report(now - timedelta(days=7), now + timedelta(minutes=1))
            assert sales["summary"]["total_orders"] == 3
            assert sales["ai_insights"] == {"error": "AI insights unavailable"}


# ============================================================================
# 6. Invalid Input & Unknown Report Type Contract
# ============================================================================


async def test_unknown_report_type_returns_400():
    """Verify unknown report_type raises 400 Bad Request at API boundary."""
    async with AsyncSessionLocal() as db:
        ctx, meta = await create_isolated_tenant(db, with_data=False)
        now = meta["now"]
        service = AnalyticsService(UnitOfWork(db), ctx)
        req = ReportGenerate(
            report_type="non_existent_type",
            start_date=now - timedelta(days=7),
            end_date=now,
        )
        with pytest.raises(HTTPException) as exc:
            await api_generate_report(
                project_id=ctx.project_id,
                report_data=req,
                context=ctx,
                service=service,
            )
        assert exc.value.status_code == 400
        assert "Unknown report type" in exc.value.detail
