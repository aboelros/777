"""
Security and isolation test suite for Social Media & Campaigns domain (Group 8).
Validates tenant boundaries across repositories, services, monitors, drip engine, and side effects.
"""

import pytest
from uuid import uuid4
from datetime import datetime
from unittest.mock import AsyncMock, patch
from fastapi import HTTPException

from app.core.database import AsyncSessionLocal
from app.core.context import TenantContext
from app.db.models import User, Project
from app.domains.social.models import SocialMediaPost, SocialMediaComment
from app.domains.social.repository import SocialMediaPostRepository, SocialMediaCommentRepository
from app.domains.social.service import SocialMediaService
from app.domains.crm.models import DripCampaign, DripStep, CampaignEnrollment
from app.domains.crm.repository import DripCampaignRepository
from app.domains.customers.models import CustomerProfile
from app.domains.integrations.models import Integration, IntegrationStatus
from app.services.social_media_monitor import SocialMediaMonitor
from app.services.drip_engine import DripEngine
from app.api.dependencies.tenant import resolve_tenant_context

pytestmark = pytest.mark.asyncio


async def setup_test_social_environment():
    async with AsyncSessionLocal() as db:
        user_a = User(id=uuid4(), email=f"user_soc_a_{uuid4()}@example.com", password_hash="hash")
        user_b = User(id=uuid4(), email=f"user_soc_b_{uuid4()}@example.com", password_hash="hash")
        db.add_all([user_a, user_b])
        await db.flush()

        proj_a = Project(id=uuid4(), name="Project Social A", owner_id=user_a.id, project_code=str(uuid4())[:8])
        proj_b = Project(id=uuid4(), name="Project Social B", owner_id=user_b.id, project_code=str(uuid4())[:8])
        db.add_all([proj_a, proj_b])
        await db.flush()

        # Posts
        post_a = SocialMediaPost(
            id=uuid4(), project_id=proj_a.id, platform="facebook", external_id=f"fb-post-a-{uuid4()}",
            content="Post A content", likes_count=100, comments_count=10, engagement_rate=12.0
        )
        post_b = SocialMediaPost(
            id=uuid4(), project_id=proj_b.id, platform="facebook", external_id=f"fb-post-b-{uuid4()}",
            content="Post B secret content", likes_count=200, comments_count=20, engagement_rate=15.0
        )
        db.add_all([post_a, post_b])

        # Comments
        comm_a = SocialMediaComment(
            id=uuid4(), project_id=proj_a.id, platform="facebook", external_id=f"fb-comm-a-{uuid4()}",
            post_id=post_a.external_id, content="Comment on Post A", responded=False
        )
        comm_b = SocialMediaComment(
            id=uuid4(), project_id=proj_b.id, platform="facebook", external_id=f"fb-comm-b-{uuid4()}",
            post_id=post_b.external_id, content="Confidential Comment B", responded=False
        )
        db.add_all([comm_a, comm_b])

        # Integrations
        int_a = Integration(
            id=uuid4(), project_id=proj_a.id, provider="facebook", status=IntegrationStatus.CONNECTED,
            config={"page_id": "page-a", "access_token": "token-a"}
        )
        int_b = Integration(
            id=uuid4(), project_id=proj_b.id, provider="facebook", status=IntegrationStatus.CONNECTED,
            config={"page_id": "page-b", "access_token": "token-b"}
        )
        db.add_all([int_a, int_b])

        # Customers
        cust_a = CustomerProfile(id=uuid4(), project_id=proj_a.id, customer_id=f"cust-a-{uuid4()}", name="Customer A")
        cust_b = CustomerProfile(id=uuid4(), project_id=proj_b.id, customer_id=f"cust-b-{uuid4()}", name="Customer B")
        db.add_all([cust_a, cust_b])

        # Drip Campaigns
        camp_a = DripCampaign(id=uuid4(), project_id=proj_a.id, name="Campaign A", trigger_type="manual")
        camp_b = DripCampaign(id=uuid4(), project_id=proj_b.id, name="Campaign B", trigger_type="manual")
        db.add_all([camp_a, camp_b])
        await db.flush()

        step_a = DripStep(id=uuid4(), campaign_id=camp_a.id, step_order=1, content_template="Hello {{name}} from A", delay_hours=1)
        step_b = DripStep(id=uuid4(), campaign_id=camp_b.id, step_order=1, content_template="Secret step B", delay_hours=1)
        db.add_all([step_a, step_b])

        await db.commit()

        ctx_a = TenantContext(project_id=proj_a.id, user_id=user_a.id, role="owner")
        ctx_b = TenantContext(project_id=proj_b.id, user_id=user_b.id, role="owner")

        ids = {
            "proj_a": proj_a.id, "proj_b": proj_b.id,
            "user_a": user_a.id, "user_b": user_b.id,
            "post_a": post_a.id, "post_b": post_b.id,
            "comm_a": comm_a.id, "comm_b": comm_b.id,
            "int_a": int_a.id, "int_b": int_b.id,
            "cust_a": cust_a.id, "cust_b": cust_b.id,
            "camp_a": camp_a.id, "camp_b": camp_b.id,
        }
        return ctx_a, ctx_b, ids


async def test_social_post_cross_tenant_isolation():
    ctx_a, ctx_b, ids = await setup_test_social_environment()
    async with AsyncSessionLocal() as db:
        post_repo = SocialMediaPostRepository(db, ctx_a)

        # Tenant A cannot read Tenant B's post
        assert await post_repo.get_by_context(ids["post_b"], ctx_a) is None

        # Tenant A cannot update Tenant B's post
        post_b = await SocialMediaPostRepository(db, ctx_b).get_by_context(ids["post_b"], ctx_b)
        assert post_b is not None
        with pytest.raises(ValueError):
            await post_repo.update_post(post_b, ctx_a)

        # Tenant B can read its own post
        assert await SocialMediaPostRepository(db, ctx_b).get_by_context(ids["post_b"], ctx_b) is not None


async def test_social_comment_cross_tenant_isolation():
    ctx_a, ctx_b, ids = await setup_test_social_environment()
    async with AsyncSessionLocal() as db:
        comm_repo = SocialMediaCommentRepository(db, ctx_a)

        # Tenant A cannot read Tenant B's comment
        assert await comm_repo.get_by_context(ids["comm_b"], ctx_a) is None

        # Tenant B can read its own comment
        assert await SocialMediaCommentRepository(db, ctx_b).get_by_context(ids["comm_b"], ctx_b) is not None


async def test_social_monitor_analyze_post_idor_blocked():
    ctx_a, _, ids = await setup_test_social_environment()
    async with AsyncSessionLocal() as db:
        monitor = SocialMediaMonitor(db, ctx_a)

        # Cross-tenant post ID must raise ValueError / fail closed
        with pytest.raises(ValueError) as exc:
            await monitor.analyze_post(ids["post_b"])
        assert "not found" in str(exc.value).lower()

        # Same-tenant post analysis works
        res = await monitor.analyze_post(ids["post_a"], fetch_comments=False)
        assert res["post"]["id"] == str(ids["post_a"])


async def test_social_monitor_analyze_post_comments_idor_blocked():
    ctx_a, _, ids = await setup_test_social_environment()
    async with AsyncSessionLocal() as db:
        monitor = SocialMediaMonitor(db, ctx_a)

        with pytest.raises(ValueError) as exc:
            await monitor.analyze_post_comments(ids["post_b"])
        assert "not found" in str(exc.value).lower()


async def test_social_monitor_generate_reply_idor_blocked():
    ctx_a, _, ids = await setup_test_social_environment()
    async with AsyncSessionLocal() as db:
        monitor = SocialMediaMonitor(db, ctx_a)

        with pytest.raises(ValueError) as exc:
            await monitor.generate_comment_reply(ids["comm_b"])
        assert "not found" in str(exc.value).lower()


async def test_social_monitor_auto_respond_idor_blocked():
    ctx_a, _, ids = await setup_test_social_environment()
    async with AsyncSessionLocal() as db:
        monitor = SocialMediaMonitor(db, ctx_a)

        with pytest.raises(ValueError) as exc:
            await monitor.auto_respond_to_comments(post_id=ids["post_b"])
        assert "not found" in str(exc.value).lower()


async def test_social_monitor_learn_post_performance_idor_blocked():
    ctx_a, _, ids = await setup_test_social_environment()
    async with AsyncSessionLocal() as db:
        monitor = SocialMediaMonitor(db, ctx_a)

        # Attempting to learn from Tenant B's post must be rejected
        with pytest.raises(ValueError) as exc:
            await monitor.learn_from_post_performance(ids["post_b"])
        assert "not found" in str(exc.value).lower()


async def test_drip_campaign_repository_cross_tenant_isolation():
    ctx_a, ctx_b, ids = await setup_test_social_environment()
    async with AsyncSessionLocal() as db:
        camp_repo = DripCampaignRepository(db, ctx_a)

        # Tenant A cannot read Tenant B's campaign
        assert await camp_repo.get_by_context(ids["camp_b"], ctx_a) is None

        # Tenant A cannot add step to Tenant B's campaign
        with pytest.raises(HTTPException) as exc:
            await camp_repo.add_step(ids["camp_b"], 2, "Hacked step", 1, ctx_a)
        assert exc.value.status_code == 404

        # Tenant B can read its campaign
        assert await DripCampaignRepository(db, ctx_b).get_by_context(ids["camp_b"], ctx_b) is not None


async def test_drip_engine_enroll_customer_cross_tenant_blocked():
    ctx_a, _, ids = await setup_test_social_environment()
    async with AsyncSessionLocal() as db:
        engine = DripEngine(db)

        # 1. Tenant A project, Tenant B campaign, Tenant A customer -> DENIED (404)
        with pytest.raises(HTTPException) as exc1:
            await engine.enroll_customer(ids["proj_a"], ids["camp_b"], ids["cust_a"])
        assert exc1.value.status_code == 404

        # 2. Tenant A project, Tenant A campaign, Tenant B customer -> DENIED (404)
        with pytest.raises(HTTPException) as exc2:
            await engine.enroll_customer(ids["proj_a"], ids["camp_a"], ids["cust_b"])
        assert exc2.value.status_code == 404

        # 3. Valid same-tenant enrollment -> ALLOWED
        enrollment = await engine.enroll_customer(ids["proj_a"], ids["camp_a"], ids["cust_a"])
        assert enrollment is not None
        assert enrollment.project_id == ids["proj_a"]


async def test_drip_engine_process_due_steps_tenant_scoped():
    ctx_a, _, ids = await setup_test_social_environment()
    async with AsyncSessionLocal() as db:
        engine = DripEngine(db)
        # Ensure enrollment exists and is due
        enrollment = await engine.enroll_customer(ids["proj_a"], ids["camp_a"], ids["cust_a"])
        enrollment.next_execution_at = datetime.utcnow()
        await db.commit()

        processed = await engine.process_due_steps()
        assert processed >= 1


async def test_api_send_comment_response_external_side_effect_invariant():
    ctx_a, _, ids = await setup_test_social_environment()
    from app.api.v1.social_media_replies import send_comment_response

    async with AsyncSessionLocal() as db:
        with patch("app.services.integrations.facebook.FacebookClient.reply_to_comment", new_callable=AsyncMock) as mock_reply:
            # Tenant A attempts to reply to Tenant B's comment
            with pytest.raises(HTTPException) as exc:
                await send_comment_response(
                    project_id=ids["proj_a"],
                    comment_id=ids["comm_b"],
                    response_text="Hello",
                    context=ctx_a,
                    db=db
                )
            assert exc.value.status_code == 404
            # Non-negotiable invariant: Provider MUST NOT be called!
            mock_reply.assert_not_called()


async def test_api_generate_comment_response_pre_auth_invariant():
    ctx_a, _, ids = await setup_test_social_environment()
    from app.api.v1.social_media_replies import generate_comment_response

    async with AsyncSessionLocal() as db:
        with patch("app.domains.ai.providers.gemini.gemini_client.generate_response", new_callable=AsyncMock) as mock_ai:
            with pytest.raises(HTTPException) as exc:
                await generate_comment_response(
                    project_id=ids["proj_a"],
                    comment_id=ids["comm_b"],
                    context=ctx_a,
                    db=db
                )
            assert exc.value.status_code == 404
            # Non-negotiable invariant: AI MUST NOT be invoked for cross-tenant comment!
            mock_ai.assert_not_called()


async def test_api_comments_same_tenant_lifecycle():
    ctx_a, _, ids = await setup_test_social_environment()
    from app.api.v1.social_media import list_comments, create_comment, get_comment_stats
    from app.api.v1.social_media_schemas import CommentCreate

    async with AsyncSessionLocal() as db:
        # List comments
        comments_res = await list_comments(project_id=ids["proj_a"], context=ctx_a, db=db)
        assert "comments" in comments_res
        assert comments_res["total"] >= 1

        # Create comment
        new_comm = CommentCreate(
            platform="facebook",
            external_id=f"ext-create-{uuid4()}",
            content="Is this available?",
            author_username="john_doe"
        )
        created_res = await create_comment(project_id=ids["proj_a"], comment=new_comm, context=ctx_a, db=db)
        assert created_res["message"] == "Comment created successfully"

        # Stats
        stats = await get_comment_stats(project_id=ids["proj_a"], context=ctx_a, db=db)
        assert stats["total_comments"] >= 2


async def test_api_forged_project_id_token_mismatch():
    _, _, ids = await setup_test_social_environment()
    async with AsyncSessionLocal() as db:
        # User A attempting to resolve context for Project B must be denied 404
        with pytest.raises(HTTPException) as exc:
            await resolve_tenant_context(ids["proj_b"], ids["user_a"], db)
        assert exc.value.status_code == 404


async def test_api_get_social_accounts_and_feed_tenant_isolation():
    ctx_a, _, ids = await setup_test_social_environment()
    from app.api.v1.social_media_accounts import get_social_accounts, get_live_feed
    from fastapi import Request

    async with AsyncSessionLocal() as db:
        mock_req = AsyncMock(spec=Request)
        mock_req.base_url = "http://testserver"

        accounts_res = await get_social_accounts(
            project_id=ids["proj_a"],
            request=mock_req,
            context=ctx_a,
            db=db
        )
        returned_ids = [a["id"] for a in accounts_res["accounts"]]
        assert ids["int_a"] in returned_ids
        assert ids["int_b"] not in returned_ids  # Tenant B integration NEVER returned!

        with patch("app.services.integrations.facebook.FacebookClient.get_feed", new_callable=AsyncMock) as mock_feed:
            mock_feed.return_value = [{"id": "feed_1", "created_time": "2026-10-07T00:00:00Z"}]
            feed_res = await get_live_feed(
                project_id=ids["proj_a"],
                limit=10,
                context=ctx_a,
                db=db
            )
            assert "data" in feed_res


async def test_missing_tenant_context_fails_closed():
    async with AsyncSessionLocal() as db:
        # Repositories without tenant context must fail closed
        with pytest.raises(ValueError):
            SocialMediaCommentRepository(db, None)._get_context()

        with pytest.raises(ValueError):
            SocialMediaPostRepository(db, None)._get_context()

        with pytest.raises(ValueError):
            DripCampaignRepository(db, None)._get_context()

