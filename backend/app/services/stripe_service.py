"""
Stripe payment processing and webhook reconciliation service.
Handles checkout sessions, signature verification, and invoice status transitions.
Falls back to structured mock generation when credentials are not configured.
"""
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from uuid import UUID, uuid4
import hmac
import hashlib
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.domains.billing.models import Invoice, PaymentLink

logger = structlog.get_logger(__name__)


class StripePaymentProvider:
    """Manages Stripe Checkout Sessions with deterministic fallback."""

    @staticmethod
    def is_configured() -> bool:
        """Check whether live Stripe API keys are configured."""
        return bool(settings.STRIPE_SECRET_KEY and settings.STRIPE_SECRET_KEY.strip())

    @classmethod
    async def create_checkout_session(
        cls,
        project_id: UUID,
        amount: float,
        currency: str = "USD",
        description: str = "",
        metadata: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Create a Stripe Checkout Session or fall back to structured mock.
        Returns dict with keys: url, session_id, provider ('stripe' or 'mock').
        """
        meta = metadata or {}
        meta["project_id"] = str(project_id)

        if cls.is_configured():
            try:
                import stripe

                stripe.api_key = settings.STRIPE_SECRET_KEY
                unit_amount = max(50, int(round(amount * 100)))

                session = stripe.checkout.Session.create(
                    payment_method_types=["card"],
                    line_items=[{
                        "price_data": {
                            "currency": currency.lower(),
                            "product_data": {
                                "name": description or f"Invoice Payment - Project {project_id}",
                            },
                            "unit_amount": unit_amount,
                        },
                        "quantity": 1,
                    }],
                    mode="payment",
                    metadata=meta,
                    success_url=f"https://app.automind.com/projects/{project_id}/billing?session_id={{CHECKOUT_SESSION_ID}}",
                    cancel_url=f"https://app.automind.com/projects/{project_id}/billing?cancelled=true",
                )
                logger.info("Stripe checkout session created", session_id=session.id, project_id=str(project_id))
                return {
                    "url": session.url,
                    "session_id": session.id,
                    "provider": "stripe",
                }
            except Exception as e:
                logger.error("Failed to create live Stripe checkout session, using fallback", error=str(e))

        # Fallback to deterministic mock URL
        mock_id = f"cs_test_mock_{uuid4().hex[:16]}"
        mock_url = f"https://buy.stripe.com/test_{project_id}_{datetime.now().timestamp()}"
        return {
            "url": mock_url,
            "session_id": mock_id,
            "provider": "mock",
        }

    @staticmethod
    def verify_webhook_signature(
        payload: bytes,
        sig_header: Optional[str],
        webhook_secret: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Verify Stripe webhook signature header (stripe-signature).
        Returns decoded event payload dict on success, None on failure.
        """
        secret = webhook_secret or settings.STRIPE_WEBHOOK_SECRET
        if not sig_header or not secret:
            logger.warning("Stripe webhook verification missing header or secret")
            return None

        try:
            import stripe
            event = stripe.Webhook.construct_event(payload, sig_header, secret)
            return dict(event)
        except ImportError:
            # Fallback signature parser for testing environments without stripe SDK
            return StripePaymentProvider._verify_signature_fallback(payload, sig_header, secret)
        except Exception as e:
            logger.warning("Stripe webhook construct_event rejected signature", error=str(e))
            return None

    @staticmethod
    def _verify_signature_fallback(
        payload: bytes,
        sig_header: str,
        secret: str,
    ) -> Optional[Dict[str, Any]]:
        """Fallback HMAC parser for stripe-signature header."""
        try:
            parts = dict(pair.split("=", 1) for pair in sig_header.split(",") if "=" in pair)
            timestamp = parts.get("t")
            v1_sig = parts.get("v1")
            if not timestamp or not v1_sig:
                return None
            signed_payload = f"{timestamp}.".encode("utf-8") + payload
            expected = hmac.new(secret.encode("utf-8"), signed_payload, hashlib.sha256).hexdigest()
            if hmac.compare_digest(expected, v1_sig):
                import json
                return json.loads(payload.decode("utf-8"))
            return None
        except Exception:
            return None


async def reconcile_stripe_checkout_completed(
    db: AsyncSession,
    session_data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Reconcile a completed Stripe checkout session with local PaymentLink, Invoice, and Order records.
    """
    session_id = session_data.get("id")
    metadata = session_data.get("metadata", {})
    invoice_id_str = metadata.get("invoice_id")

    payment_link: Optional[PaymentLink] = None
    if session_id:
        result = await db.execute(
            select(PaymentLink).where(PaymentLink.stripe_payment_link_id == session_id)
        )
        payment_link = result.scalars().first()

    invoice: Optional[Invoice] = None
    if payment_link and payment_link.invoice_id:
        res = await db.execute(select(Invoice).where(Invoice.id == payment_link.invoice_id))
        invoice = res.scalars().first()
    elif invoice_id_str:
        try:
            inv_uuid = UUID(invoice_id_str)
            res = await db.execute(select(Invoice).where(Invoice.id == inv_uuid))
            invoice = res.scalars().first()
        except ValueError:
            pass

    if invoice:
        # 1. Idempotency guard: never overwrite or re-process already paid invoice
        if invoice.status == "paid":
            logger.info("Invoice already paid, idempotent skip", invoice_id=str(invoice.id))
            return {"status": "already_paid", "session_id": session_id, "invoice_id": str(invoice.id)}

        # 2. Server-side amount validation against persisted records
        amount_total = session_data.get("amount_total")
        if amount_total is not None:
            expected_cents = int(round((invoice.total_amount or invoice.amount) * 100))
            if int(amount_total) != expected_cents:
                logger.warning(
                    "Stripe amount mismatch: rejected reconciliation",
                    received_cents=amount_total,
                    expected_cents=expected_cents,
                    invoice_id=str(invoice.id),
                )
                return {"status": "rejected", "reason": "amount_mismatch"}

        # 3. Tenant cross-contamination check
        meta_project = metadata.get("project_id")
        if meta_project and str(invoice.project_id) != str(meta_project):
            logger.warning("Stripe tenant mismatch", expected=str(invoice.project_id), meta=meta_project)
            return {"status": "rejected", "reason": "tenant_mismatch"}

    now = datetime.now(timezone.utc)
    updated = False

    if payment_link:
        payment_link.status = "paid"
        updated = True

    if invoice:
        invoice.status = "paid"
        invoice.paid_at = now
        updated = True
        if invoice.order_id:
            from app.domains.orders.models import Order
            ord_res = await db.execute(select(Order).where(Order.id == invoice.order_id))
            order = ord_res.scalars().first()
            if order:
                order.payment_status = "paid"
                order.status = "confirmed"

    if updated:
        await db.commit()
        logger.info("Stripe payment reconciled", session_id=session_id, invoice_id=str(invoice.id) if invoice else None)
        return {"status": "reconciled", "session_id": session_id}

    return {"status": "ignored", "reason": "no_matching_record"}


async def reconcile_stripe_checkout_failed(
    db: AsyncSession,
    session_data: Dict[str, Any],
) -> Dict[str, Any]:
    """Safely handle expired or failed checkout sessions without downgrading paid records."""
    session_id = session_data.get("id")
    if not session_id:
        return {"status": "ignored"}

    result = await db.execute(
        select(PaymentLink).where(PaymentLink.stripe_payment_link_id == session_id)
    )
    payment_link = result.scalars().first()
    if not payment_link or payment_link.status == "paid":
        return {"status": "ignored", "reason": "already_paid_or_not_found"}

    payment_link.status = "expired"
    await db.commit()
    logger.info("Stripe checkout marked expired", session_id=session_id)
    return {"status": "expired", "session_id": session_id}
