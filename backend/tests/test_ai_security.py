"""
Security and isolation test suite for AI Assistant / Training domain (Group 7).
Validates tenant boundaries across repositories, services, orchestrator, and background workers.
"""

import pytest
from uuid import uuid4
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from fastapi import HTTPException

from app.core.database import AsyncSessionLocal
from app.core.context import TenantContext
from app.core.uow import UnitOfWork
from app.db.models import User, Project
from app.domains.ai.models import BotInstruction, KnowledgeBase, ModelTraining, ModelTrainingStatus
from app.domains.ai.repository import (
    BotInstructionRepository,
    KnowledgeBaseRepository,
    ModelTrainingRepository,
)
from app.domains.ai.service import AIService
from app.domains.ai.orchestrator import AIOrchestrator
from app.domains.customers.models import CustomerProfile
from app.domains.orders.models import Order, OrderStatus
from app.domains.integrations.models import Integration, IntegrationStatus
from app.domains.messages.models import Message
from app.workers.tasks.ai_tasks import sync_integration_data, auto_respond_to_customer, process_incoming_message
from app.api.dependencies.tenant import resolve_tenant_context

pytestmark = pytest.mark.asyncio


def run_celery_task_sync(task_func, *args, **kwargs):
    with ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(task_func, *args, **kwargs).result()


async def setup_test_ai_environment():
    async with AsyncSessionLocal() as db:
        user_a = User(id=uuid4(), email=f"user_a_{uuid4()}@example.com", password_hash="hash")
        user_b = User(id=uuid4(), email=f"user_b_{uuid4()}@example.com", password_hash="hash")
        db.add_all([user_a, user_b])
        await db.flush()

        proj_a = Project(id=uuid4(), name="Project A", owner_id=user_a.id, project_code=str(uuid4())[:8])
        proj_b = Project(id=uuid4(), name="Project B", owner_id=user_b.id, project_code=str(uuid4())[:8])
        db.add_all([proj_a, proj_b])
        await db.flush()

        inst_b = BotInstruction(id=uuid4(), project_id=proj_b.id, title="Test Inst B", instruction="Secret B", category="general", is_active=True)
        kb_b = KnowledgeBase(id=uuid4(), project_id=proj_b.id, title="KB B", content="Confidential B", is_active=True)
        train_b = ModelTraining(id=uuid4(), project_id=proj_b.id, status=ModelTrainingStatus.COMPLETED)
        cust_b = CustomerProfile(id=uuid4(), project_id=proj_b.id, customer_id="cust-b-1", name="Alice B")
        order_b = Order(
            id=uuid4(), project_id=proj_b.id, customer_id=cust_b.id, customer={"name": "Alice B"},
            total=500.0, status=OrderStatus.PENDING.value, provider="shopify", external_id="ext-b-1",
            order_date=datetime.utcnow(), updated_at=datetime.utcnow()
        )
        int_b = Integration(id=uuid4(), project_id=proj_b.id, provider="shopify", status=IntegrationStatus.CONNECTED, config={})
        msg_b = Message(id=uuid4(), project_id=proj_b.id, provider="whatsapp", status="pending", direction="inbound", content="Order status?")

        db.add_all([inst_b, kb_b, train_b, cust_b, order_b, int_b, msg_b])
        await db.commit()

        ctx_a = TenantContext(project_id=proj_a.id, user_id=user_a.id, role="owner")
        ctx_b = TenantContext(project_id=proj_b.id, user_id=user_b.id, role="owner")

        ids = {
            "proj_a": proj_a.id, "proj_b": proj_b.id, "user_a": user_a.id, "user_b": user_b.id,
            "inst_b": inst_b.id, "kb_b": kb_b.id, "train_b": train_b.id, "cust_b": cust_b.id,
            "order_b": order_b.id, "int_b": int_b.id, "msg_b": msg_b.id,
        }
        return ctx_a, ctx_b, ids


async def test_ai_repository_cross_tenant_isolation():
    ctx_a, ctx_b, ids = await setup_test_ai_environment()
    async with AsyncSessionLocal() as db:
        inst_repo = BotInstructionRepository(db)
        kb_repo = KnowledgeBaseRepository(db)
        train_repo = ModelTrainingRepository(db)

        # Tenant A attempting to access Tenant B records must return None
        assert await inst_repo.get_by_context(ids["inst_b"], ctx_a) is None
        assert await kb_repo.get_by_context(ids["kb_b"], ctx_a) is None
        assert await train_repo.get_by_context(ids["train_b"], ctx_a) is None

        # Cross-tenant updates and deletes must fail to match any rows
        assert await inst_repo.update_by_context(ids["inst_b"], ctx_a, {"instruction": "Hacked"}) is None
        assert await kb_repo.delete_by_context(ids["kb_b"], ctx_a) is False

        # Tenant B can access its own records
        assert await inst_repo.get_by_context(ids["inst_b"], ctx_b) is not None
        assert await kb_repo.get_by_context(ids["kb_b"], ctx_b) is not None


async def test_ai_service_cross_tenant_denial():
    ctx_a, _, ids = await setup_test_ai_environment()
    async with AsyncSessionLocal() as db:
        uow = UnitOfWork(db)
        ai_service = AIService(uow)

        with pytest.raises(HTTPException) as exc_info:
            await ai_service.get_bot_instruction(ids["inst_b"], ctx_a)
        assert exc_info.value.status_code == 404

        with pytest.raises(HTTPException) as exc_info:
            await ai_service.update_bot_instruction(ids["inst_b"], ctx_a, {"instruction": "Cross-edit"})
        assert exc_info.value.status_code == 404

        with pytest.raises(HTTPException) as exc_info:
            await ai_service.get_knowledge_item(ids["kb_b"], ctx_a)
        assert exc_info.value.status_code == 404

        with pytest.raises(HTTPException) as exc_info:
            await ai_service.delete_knowledge_item(ids["kb_b"], ctx_a)
        assert exc_info.value.status_code == 404


async def test_ai_orchestrator_untrusted_ids_fail_closed():
    ctx_a, _, ids = await setup_test_ai_environment()
    async with AsyncSessionLocal() as db:
        orchestrator = AIOrchestrator(db, context=ctx_a)

        # AI hallucinating or supplying customer_id from Tenant B must yield None
        customer = await orchestrator._get_customer(ids["cust_b"])
        assert customer is None

        # AI attempting to update or fetch order from Tenant B must fail closed immediately
        update_res = await orchestrator._update_order(str(ids["order_b"]), "delivered")
        assert update_res["status"] == "error"
        assert "not found" in update_res["message"].lower() or "denied" in update_res["message"].lower()

        fetch_res = await orchestrator._fetch_order(str(ids["order_b"]), ids["cust_b"])
        assert fetch_res["status"] == "error"
        assert "not found" in fetch_res["message"].lower() or "denied" in fetch_res["message"].lower()


async def test_worker_cross_tenant_task_isolation():
    _, _, ids = await setup_test_ai_environment()
    # 1. sync_integration_data with Project A and Integration B
    res_sync = run_celery_task_sync(sync_integration_data, str(ids["proj_a"]), str(ids["int_b"]))
    assert res_sync is None

    # 2. auto_respond_to_customer with Project A and Customer B
    res_respond = run_celery_task_sync(auto_respond_to_customer, str(ids["cust_b"]), str(ids["proj_a"]), {"message": "Hi"})
    assert res_respond is None

    # 3. process_incoming_message with Project A and Message B
    res_msg = run_celery_task_sync(process_incoming_message, str(ids["msg_b"]), str(ids["proj_a"]))
    assert res_msg is None


async def test_resolve_tenant_context_forged_project():
    _, _, ids = await setup_test_ai_environment()
    async with AsyncSessionLocal() as db:
        # User A attempting to resolve context for Project B must be denied 404
        with pytest.raises(HTTPException) as exc:
            await resolve_tenant_context(ids["proj_b"], ids["user_a"], db)
        assert exc.value.status_code == 404
