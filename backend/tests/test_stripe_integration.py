"""
Integration tests for Stripe live billing, fallback mock generation, and webhook reconciliation.
"""
import pytest
import hmac
import hashlib
import json
import time
from uuid import uuid4
from unittest.mock import MagicMock, patch
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.core.database import AsyncSessionLocal
from app.core.context import TenantContext
from app.domains.projects.models import Project
from app.domains.auth.models import User
from app.domains.billing.models import Invoice, PaymentLink
from app.services.payment_service import PaymentService
from app.services.stripe_service import StripePaymentProvider


@pytest.mark.asyncio
async def test_stripe_fallback_when_unconfigured():
    """Verify that payment link generation safely falls back to mock URL when STRIPE_SECRET_KEY is unset."""
    async with AsyncSessionLocal() as session:
        user = User(
            id=uuid4(),
            email=f"stripetest_{uuid4().hex[:8]}@example.com",
            password_hash="pw",
            name="Stripe Tester",
            is_active=True,
        )
        session.add(user)
        project = Project(
            id=uuid4(),
            owner_id=user.id,
            name="Stripe Fallback Project",
            project_code=f"PRJ-{uuid4().hex[:8]}",
        )
        session.add(project)
        await session.commit()

        context = TenantContext(user_id=user.id, project_id=project.id, roles=["owner"])
        service = PaymentService(session, context)

        # Ensure STRIPE_SECRET_KEY is empty
        with patch.object(StripePaymentProvider, "is_configured", return_value=False):
            link = await service.create_payment_link(amount=49.99, description="Fallback Test")
            assert link.id is not None
            assert link.project_id == project.id
            assert "buy.stripe.com/test_" in link.url
            assert link.status == "active"
            assert link.amount == 49.99


@pytest.mark.asyncio
async def test_stripe_checkout_session_live_path_mocked():
    """Verify that when configured, Stripe SDK creates checkout session and records session ID."""
    async with AsyncSessionLocal() as session:
        user = User(
            id=uuid4(),
            email=f"stripelive_{uuid4().hex[:8]}@example.com",
            password_hash="pw",
            name="Stripe Live Tester",
            is_active=True,
        )
        session.add(user)
        project = Project(
            id=uuid4(),
            owner_id=user.id,
            name="Stripe Live Project",
            project_code=f"PRJ-{uuid4().hex[:8]}",
        )
        session.add(project)
        await session.commit()

        context = TenantContext(user_id=user.id, project_id=project.id, roles=["owner"])
        service = PaymentService(session, context)

        mock_session_obj = MagicMock()
        mock_session_obj.id = "cs_live_123456789"
        mock_session_obj.url = "https://checkout.stripe.com/c/pay/cs_live_123456789"

        mock_stripe = MagicMock()
        mock_stripe.checkout.Session.create.return_value = mock_session_obj

        with patch("app.core.config.settings.STRIPE_SECRET_KEY", "sk_test_fake_key_123"), \
             patch.dict("sys.modules", {"stripe": mock_stripe}):
            link = await service.create_payment_link(amount=120.00, description="Live Pro Plan")
            assert link.stripe_payment_link_id == "cs_live_123456789"
            assert link.url == "https://checkout.stripe.com/c/pay/cs_live_123456789"
            assert link.status == "active"


@pytest.mark.asyncio
async def test_stripe_webhook_invalid_signature_rejected():
    """Verify that Stripe webhook rejects missing or invalid signatures with HTTP 400."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Missing signature header
        res1 = await client.post("/api/v1/payments/webhooks/stripe", content=b"{}")
        assert res1.status_code == 400

        # Invalid signature header
        headers = {"stripe-signature": "t=12345,v1=invalidsignature"}
        res2 = await client.post("/api/v1/payments/webhooks/stripe", content=b"{}", headers=headers)
        assert res2.status_code == 400


@pytest.mark.asyncio
async def test_stripe_webhook_checkout_completed_reconciliation():
    """Verify that checkout.session.completed webhook marks PaymentLink and Invoice as paid."""
    async with AsyncSessionLocal() as session:
        user = User(
            id=uuid4(),
            email=f"stripe_reconcile_{uuid4().hex[:8]}@example.com",
            password_hash="pw",
            name="Reconcile User",
            is_active=True,
        )
        session.add(user)
        project = Project(
            id=uuid4(),
            owner_id=user.id,
            name="Reconcile Project",
            project_code=f"PRJ-{uuid4().hex[:8]}",
        )
        session.add(project)
        await session.flush()

        test_session_id = f"cs_test_hook_{uuid4().hex[:12]}"
        invoice = Invoice(
            project_id=project.id,
            invoice_number="INV-RECONCILE-001",
            amount=250.0,
            total_amount=250.0,
            status="draft",
        )
        session.add(invoice)
        await session.flush()

        link = PaymentLink(
            project_id=project.id,
            invoice_id=invoice.id,
            url="https://checkout.stripe.com/test",
            stripe_payment_link_id=test_session_id,
            amount=250.0,
            status="active",
        )
        session.add(link)
        await session.commit()

        # Construct signed Stripe webhook payload
        payload_dict = {
            "id": f"evt_{uuid4().hex[:12]}",
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": test_session_id,
                    "metadata": {
                        "project_id": str(project.id),
                        "invoice_id": str(invoice.id),
                    },
                }
            },
        }
        payload_bytes = json.dumps(payload_dict).encode("utf-8")
        webhook_secret = "whsec_test_secret_for_reconciliation"
        timestamp = str(int(time.time()))
        signed_body = f"{timestamp}.".encode("utf-8") + payload_bytes
        signature = hmac.new(webhook_secret.encode("utf-8"), signed_body, hashlib.sha256).hexdigest()
        sig_header = f"t={timestamp},v1={signature}"

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            with patch("app.core.config.settings.STRIPE_WEBHOOK_SECRET", webhook_secret):
                response = await client.post(
                    "/api/v1/payments/webhooks/stripe",
                    content=payload_bytes,
                    headers={"stripe-signature": sig_header, "Content-Type": "application/json"},
                )
                assert response.status_code == 200
                data = response.json()
                assert data.get("status") == "reconciled"

        # Verify DB updates
        await session.refresh(link)
        await session.refresh(invoice)
        assert link.status == "paid"
        assert invoice.status == "paid"
        assert invoice.paid_at is not None
