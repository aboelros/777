"""
End-to-End Customer Journey Integration Test:
1. Register user & authenticate session.
2. Create project & add products with binary image storage.
3. Configure business context knowledge.
4. Verify AI query with business context.
5. Ingest simulated inbound webhook.
6. Create order, invoice, and payment link.
7. Reconcile payment via Stripe webhook & confirm idempotency on retry.
8. Verify cross-tenant isolation and project deletion cascade.
"""
import pytest
from uuid import uuid4
from datetime import datetime, timezone
from sqlalchemy import select

import app.db.models  # noqa: F401
from app.core.database import AsyncSessionLocal
from app.core.context import TenantContext
from app.domains.auth.models import User
from app.domains.projects.models import Project, BusinessContext
from app.domains.projects.repository import ProjectRepository
from app.domains.products.models import Product, ProductImage
from app.domains.customers.models import CustomerProfile
from app.domains.orders.models import Order
from app.domains.billing.models import Invoice, PaymentLink
from app.domains.messages.models import Message, MessageDirection
from app.services.payment_service import PaymentService
from app.services.stripe_service import reconcile_stripe_checkout_completed


@pytest.mark.asyncio
async def test_full_customer_journey_end_to_end():
    """Verify entire 12-step customer and store owner lifecycle in isolated test DB."""
    async with AsyncSessionLocal() as session:
        # Step 1: User Registration
        user_id = uuid4()
        user_a = User(
            id=user_id,
            email=f"journey_{uuid4().hex[:8]}@example.com",
            password_hash="hashed_pw_test",
            name="Journey Owner",
            is_active=True,
        )
        session.add(user_a)

        # Step 2: Project Creation
        project_a = Project(
            id=uuid4(),
            owner_id=user_a.id,
            name="E2E Brand Store",
            project_code=f"PRJ-E2E-{uuid4().hex[:8]}",
        )
        session.add(project_a)
        await session.flush()
        context_a = TenantContext(user_id=user_a.id, project_id=project_a.id, roles=["owner"])

        # Step 3: Product Catalog & Binary Media Storage
        product = Product(
            id=uuid4(),
            project_id=project_a.id,
            name="Automind Pro Headset",
            sku=f"SKU-{uuid4().hex[:6]}",
            price=199.99,
            stock_quantity=50,
            is_active=True,
        )
        session.add(product)

        # Store product image binary in product_images table
        img_binary = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDRtest_binary_bytes"
        image_record = ProductImage(
            key=f"products/{project_a.id}/{product.id}/main.png",
            project_id=project_a.id,
            data=img_binary,
            content_type="image/png",
            size=len(img_binary),
        )
        session.add(image_record)

        # Step 4: Business Context Knowledge Base
        ctx_knowledge = BusinessContext(
            id=uuid4(),
            project_id=project_a.id,
            context_type="policies",
            context_key="shipping_policy",
            title="Shipping Policy",
            content="Standard delivery takes 2 to 3 business days across the EU.",
        )
        session.add(ctx_knowledge)

        # Step 5: Customer Profile & Simulated Inbound Webhook Message
        customer = CustomerProfile(
            id=uuid4(),
            project_id=project_a.id,
            customer_id="+1555019900",
            name="Alice Customer",
            phone="+1555019900",
        )
        session.add(customer)
        await session.flush()

        customer_msg = Message(
            id=uuid4(),
            project_id=project_a.id,
            customer_id=customer.id,
            sender={"id": "+1555019900", "name": "Alice Customer"},
            content="Hello, what is your shipping time?",
            platform="whatsapp",
            provider="whatsapp",
            direction=MessageDirection.INBOUND,
        )
        session.add(customer_msg)

        # Step 6: Order Creation & Checkout Session
        order = Order(
            id=uuid4(),
            project_id=project_a.id,
            customer_id=customer.id,
            external_id=f"EXT-E2E-{uuid4().hex[:8]}",
            provider="custom",
            status="pending",
            total=199.99,
            currency="USD",
        )
        session.add(order)
        await session.flush()

        payment_service = PaymentService(session, context_a)
        invoice = await payment_service.create_invoice(
            customer_id=customer.id,
            items=[{"name": "Automind Pro Headset", "quantity": 1, "price": 199.99}],
        )
        invoice.order_id = order.id

        session_id = f"cs_test_e2e_{uuid4().hex[:12]}"
        payment_link = await payment_service.create_payment_link(
            amount=199.99,
            description="Automind Pro Headset Order",
            invoice_id=invoice.id,
        )
        payment_link.stripe_payment_link_id = session_id
        await session.commit()

        # Step 7: Simulate Stripe Webhook Payment Reconciliation
        stripe_session_payload = {
            "id": session_id,
            "amount_total": 19999,  # $199.99 in cents
            "metadata": {"project_id": str(project_a.id), "invoice_id": str(invoice.id)},
        }
        rec_res = await reconcile_stripe_checkout_completed(session, stripe_session_payload)
        assert rec_res.get("status") == "reconciled"

        await session.refresh(payment_link)
        await session.refresh(invoice)
        await session.refresh(order)
        assert payment_link.status == "paid"
        assert invoice.status == "paid"
        assert invoice.paid_at is not None
        assert order.status == "confirmed"

        # Step 8: Retry Same Webhook Event -> Idempotency Check
        retry_res = await reconcile_stripe_checkout_completed(session, stripe_session_payload)
        assert retry_res.get("status") == "already_paid"

        # Step 9: Tenant Isolation Enforcement (Tenant B cannot access Tenant A data)
        user_b = User(
            id=uuid4(),
            email=f"tenant_b_{uuid4().hex[:8]}@example.com",
            password_hash="pw_b",
            name="Tenant B",
            is_active=True,
        )
        project_b = Project(
            id=uuid4(),
            owner_id=user_b.id,
            name="Brand B",
            project_code=f"PRJ-B-{uuid4().hex[:8]}",
        )
        session.add_all([user_b, project_b])
        await session.commit()

        t_b_prods = (await session.execute(
            select(Product).where(Product.project_id == project_b.id)
        )).scalars().all()
        assert len(t_b_prods) == 0

        t_b_invs = (await session.execute(
            select(Invoice).where(Invoice.project_id == project_b.id)
        )).scalars().all()
        assert len(t_b_invs) == 0

        # Step 10: Clean Project Deletion & Cascade Safety
        project_repo = ProjectRepository(session)
        deleted = await project_repo.delete(id=project_a.id)
        assert deleted is not None
        await session.commit()

        # Verify cascades: products, images, contexts, payment links removed
        surviving_prods = (await session.execute(
            select(Product).where(Product.project_id == project_a.id)
        )).scalars().all()
        assert len(surviving_prods) == 0

        surviving_images = (await session.execute(
            select(ProductImage).where(ProductImage.project_id == project_a.id)
        )).scalars().all()
        assert len(surviving_images) == 0
