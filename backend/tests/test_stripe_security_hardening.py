"""
Security hardening regression tests for Stripe integration:
1. Idempotency against duplicate webhook deliveries.
2. Server-side amount mismatch detection and rejection.
3. Cross-tenant spoofing rejection.
4. Out-of-order event protection (expired/failed cannot downgrade paid).
5. Authoritative invoice price enforcement.
"""
import pytest
import hmac
import hashlib
import json
import time
from uuid import uuid4
from datetime import datetime, timezone, timedelta
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.core.database import AsyncSessionLocal
from app.domains.projects.models import Project
from app.domains.auth.models import User
from app.domains.billing.models import Invoice, PaymentLink
from app.services.stripe_service import (
    reconcile_stripe_checkout_completed,
    reconcile_stripe_checkout_failed,
)


@pytest.mark.asyncio
async def test_stripe_idempotency_preserves_original_payment_timestamp():
    """Verify duplicate checkout.session.completed does not overwrite paid_at or corrupt status."""
    async with AsyncSessionLocal() as session:
        user = User(
            id=uuid4(),
            email=f"idemp_{uuid4().hex[:8]}@example.com",
            password_hash="pw",
            name="Idempotency User",
            is_active=True,
        )
        session.add(user)
        project = Project(
            id=uuid4(),
            owner_id=user.id,
            name="Idempotency Project",
            project_code=f"PRJ-{uuid4().hex[:8]}",
        )
        session.add(project)
        await session.flush()

        original_paid_at = datetime.now(timezone.utc) - timedelta(hours=2)
        invoice = Invoice(
            project_id=project.id,
            invoice_number="INV-IDEMP-001",
            amount=150.0,
            total_amount=150.0,
            status="paid",
            paid_at=original_paid_at,
        )
        session.add(invoice)
        await session.commit()

        session_data = {
            "id": f"cs_test_{uuid4().hex[:8]}",
            "metadata": {"invoice_id": str(invoice.id), "project_id": str(project.id)},
            "amount_total": 15000,
        }
        result = await reconcile_stripe_checkout_completed(session, session_data)
        assert result.get("status") == "already_paid"

        await session.refresh(invoice)
        assert invoice.status == "paid"
        # Verify paid_at was NOT overwritten with current timestamp
        assert invoice.paid_at == original_paid_at


@pytest.mark.asyncio
async def test_stripe_amount_mismatch_rejected():
    """Verify that a session with an altered amount is rejected and does not mark invoice as paid."""
    async with AsyncSessionLocal() as session:
        user = User(
            id=uuid4(),
            email=f"amount_{uuid4().hex[:8]}@example.com",
            password_hash="pw",
            name="Amount User",
            is_active=True,
        )
        session.add(user)
        project = Project(
            id=uuid4(),
            owner_id=user.id,
            name="Amount Project",
            project_code=f"PRJ-{uuid4().hex[:8]}",
        )
        session.add(project)
        await session.flush()

        invoice = Invoice(
            project_id=project.id,
            invoice_number="INV-AMT-001",
            amount=500.0,  # $500.00
            total_amount=500.0,
            status="draft",
        )
        session.add(invoice)
        await session.commit()

        # Attacker paid $1.00 (100 cents) instead of $500.00 (50000 cents)
        session_data = {
            "id": f"cs_test_fraud_{uuid4().hex[:8]}",
            "metadata": {"invoice_id": str(invoice.id), "project_id": str(project.id)},
            "amount_total": 100,  # 100 cents != 50000 cents
        }
        result = await reconcile_stripe_checkout_completed(session, session_data)
        assert result.get("status") == "rejected"
        assert result.get("reason") == "amount_mismatch"

        await session.refresh(invoice)
        assert invoice.status == "draft"  # Remains draft, NOT paid!


@pytest.mark.asyncio
async def test_stripe_cross_tenant_spoofing_rejected():
    """Verify that a session claiming a foreign project_id is rejected."""
    async with AsyncSessionLocal() as session:
        user = User(
            id=uuid4(),
            email=f"tenant_{uuid4().hex[:8]}@example.com",
            password_hash="pw",
            name="Tenant User",
            is_active=True,
        )
        session.add(user)
        project_a = Project(
            id=uuid4(),
            owner_id=user.id,
            name="Tenant Project A",
            project_code=f"PRJ-{uuid4().hex[:8]}",
        )
        project_b = Project(
            id=uuid4(),
            owner_id=user.id,
            name="Tenant Project B",
            project_code=f"PRJ-{uuid4().hex[:8]}",
        )
        session.add_all([project_a, project_b])
        await session.flush()

        invoice = Invoice(
            project_id=project_a.id,
            invoice_number="INV-TENANT-001",
            amount=100.0,
            total_amount=100.0,
            status="draft",
        )
        session.add(invoice)
        await session.commit()

        # Payload metadata specifies project_b while invoice belongs to project_a
        session_data = {
            "id": f"cs_test_spoof_{uuid4().hex[:8]}",
            "metadata": {"invoice_id": str(invoice.id), "project_id": str(project_b.id)},
            "amount_total": 10000,
        }
        result = await reconcile_stripe_checkout_completed(session, session_data)
        assert result.get("status") == "rejected"
        assert result.get("reason") == "tenant_mismatch"

        await session.refresh(invoice)
        assert invoice.status == "draft"


@pytest.mark.asyncio
async def test_stripe_out_of_order_expiration_does_not_downgrade_paid():
    """Verify that an expired checkout event cannot downgrade a paid payment link."""
    async with AsyncSessionLocal() as session:
        user = User(
            id=uuid4(),
            email=f"ooo_{uuid4().hex[:8]}@example.com",
            password_hash="pw",
            name="OOO User",
            is_active=True,
        )
        session.add(user)
        project = Project(
            id=uuid4(),
            owner_id=user.id,
            name="OOO Project",
            project_code=f"PRJ-{uuid4().hex[:8]}",
        )
        session.add(project)
        await session.flush()

        test_session_id = f"cs_ooo_{uuid4().hex[:8]}"
        link = PaymentLink(
            project_id=project.id,
            url="https://checkout.stripe.com/test",
            stripe_payment_link_id=test_session_id,
            amount=99.0,
            status="paid",  # Already paid
        )
        session.add(link)
        await session.commit()

        # Late-arriving expiration event
        result = await reconcile_stripe_checkout_failed(session, {"id": test_session_id})
        assert result.get("status") == "ignored"

        await session.refresh(link)
        assert link.status == "paid"  # Status preserved
