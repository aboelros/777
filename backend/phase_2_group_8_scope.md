# Phase 2 Group 8 Scope: Social Media & Campaigns Security Migration

> RECONSTRUCTED GROUP 8 SCOPE — NOT HISTORICALLY VERIFIED

---

## 1. Provenance
* **HISTORICAL GROUP 8 SPECIFICATION: NOT RECOVERABLE**
  The original historical project specification for any group beyond Group 5 is not preserved in any surviving project file, planning record, or git commit. Groups 6 and 7 were deliberate reconstructions based on repository audit findings (`remaining_security_audit.md`).
* **RECONSTRUCTED GROUP 8 SCOPE**
  This scope is a deliberate, evidence-based reconstruction designed to harden the remaining highest-risk unmigrated domain: **Social Media & Campaigns** (`social_media.py`, `drip_campaigns.py`, `domains/social/`, `services/social_media_monitor.py`, `services/drip_engine.py`).
* **Repository Derivation**:
  * `remaining_security_audit.md` explicitly inventories `Social Media / Campaigns` as having 10 routes, 8 direct SQL bypasses, and High External Side Effects.
  * `remaining_security_audit.md` Section 3 Item 5 flags `social_media.py` for primitive caller-supplied IDs.
  * Group 7 scope (`phase_2_group_7_scope.md`) and final evidence (`phase_2_group_7_final_evidence.md`) explicitly recorded `social_media.py` and `drip_campaigns.py` as deferred to a subsequent group.
* **Provenance Rule**:
  This scope is **not** claimed to be an original historical specification. It is a strictly bounded, repository-evidenced reconstruction.

---

## 2. Historical-Status Warning
> **WARNING: RECONSTRUCTED SPECIFICATION**
> No historical document or commit exists defining "Group 8". This document defines a reconstructed implementation contract based solely on static analysis and surviving audit artifacts. Do not treat any sequencing or domain boundaries herein as historical facts.

---

## 3. Exact In-Scope Files

### API Routers (Requires TenantContext & Rule 11 Modularization)
* `backend/app/api/v1/social_media.py` (to be modularized into focused files ≤250 lines)
* `backend/app/api/v1/drip_campaigns.py`
* Extracted router modules:
  * `backend/app/api/v1/social_media_accounts.py` (accounts list, avatar persistence, live feed)
  * `backend/app/api/v1/social_media_replies.py` (AI response generation, platform reply dispatch)
  * `backend/app/api/v1/social_media_schemas.py` (Pydantic request/response schemas)

### Domain Repositories & Services (Requires TenantContext Injection)
* `backend/app/domains/social/models.py` (schemas untouched, models leveraged)
* `backend/app/domains/social/repository.py` (tenant-scoped `SocialMediaCommentRepository` and `SocialMediaPostRepository`)
* `backend/app/domains/social/service.py` (tenant-scoped `SocialMediaService`)
* `backend/app/domains/crm/repository.py` (tenant-scoped `DripCampaignRepository` and campaign enrollments)
* `backend/app/domains/crm/service.py` (tenant-scoped `CRMService`)

### Domain Services (Requires IDOR Elimination & Rule 11 Modularization)
* `backend/app/services/social_media_monitor.py` (to be modularized into focused files ≤250 lines)
* Extracted service modules:
  * `backend/app/services/social_media_auto_responder.py` (auto-reply execution and template personalization)
  * `backend/app/services/social_media_analyzer.py` (AI content analysis, sentiment, and prompt formatting)
* `backend/app/services/drip_engine.py` (tenant validation on enrollments and background execution)

### Dedicated Security Test Suite
* `backend/tests/test_social_security.py`

---

## 4. Exact Out-of-Scope Files
The following files are strictly **EXCLUDED** from Group 8:
* `backend/app/api/v1/payments_invoicing.py` & `backend/app/services/payment_service.py` (deferred to subsequent migration)
* `backend/app/api/v1/subscriptions.py` & `backend/app/services/subscription_service.py` (user account billing, not project tenant scoped)
* `backend/app/api/v1/reports.py` & `backend/app/services/report_generator.py` (read-only analytics)
* `backend/app/api/v1/deals.py` (internal CRM pipeline)
* `backend/app/api/v1/products.py` (already refactored to ProductService/UoW)
* `backend/app/api/v1/projects.py` (root project CRUD)
* `backend/app/services/integrations/facebook.py` (`FacebookClient` external API wrapper logic untouched)
* `backend/app/services/integrations/instagram.py` (`InstagramClient` external API wrapper logic untouched)
* All previously frozen code in Groups 1 through 7 (`orders`, `assistant`, `knowledge`, `webhooks`, `integrations`, `workers/tasks/core.py`, `workers/tasks/ai_tasks.py`).

---

## 5. Route Inventory

| HTTP Method | Path | Handler Name | Caller-Supplied IDs | `project_id` Source | Current Auth | DB Resources Accessed | Repo/Service Used | External Provider Invoked | Provider Invoked Timing | Expected Status | Current Security Weakness |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `GET` | `/{project_id}/comments` | `list_comments` | `project_id` (path) | Path param | `verify_project_access` | `SocialMediaComment` | None (raw SQL) | None | N/A | 200 OK | Bypasses repository layer; raw SQL in router; uses legacy `verify_project_access`. |
| `GET` | `/{project_id}/accounts` | `get_social_accounts` | `project_id` (path) | Path param | `verify_project_access` | `Integration` | `WebhookProcessor` (for avatar persist) | Meta CDN (HTTP GET for avatars) | After `verify_project_access`, but mutates DB on GET | 200 OK | Direct SQL reads raw OAuth tokens; mutates DB (`extra_data`) during HTTP GET request; bypasses `IntegrationRepository`. |
| `GET` | `/{project_id}/feed` | `get_live_feed` | `project_id` (path) | Path param | `verify_project_access` | `Integration` | `FacebookClient`, `InstagramClient` | Meta Graph API (`get_feed`, `get_media`) | During GET, using raw tokens from SQL | 200 OK | Direct SQL reads credentials; triggers live external Graph API calls synchronously; no repository abstraction. |
| `POST` | `/{project_id}/comments` | `create_comment` | `project_id` (path), `external_id`, `post_id` (body) | Path param | `verify_project_access` | `SocialMediaComment` | `gemini_client` | Gemini AI (`analyze_sentiment`) | Before DB insert, after `verify_project_access` | 200 OK | Raw SQL in router; `post_id` in body is not validated for tenant ownership (untrusted primitive ID). |
| `POST` | `/{project_id}/comments/{comment_id}/generate-response` | `generate_comment_response` | `project_id` (path), `comment_id` (path) | Path param | `verify_project_access` | `SocialMediaComment`, `Product`, `BotInstruction` | `gemini_client` | Gemini AI (`generate_response`) | After DB reads | 200 OK | Executes 3 raw SQL queries in router; bypasses repositories for comments, products, and bot instructions; prompt logic in router. |
| `POST` | `/{project_id}/comments/{comment_id}/send-response` | `send_comment_response` | `project_id` (path), `comment_id` (path) | Path param | `verify_project_access` | `SocialMediaComment`, `Integration` | `FacebookClient`, `InstagramClient` | Meta Graph API (`reply_to_comment`) | After raw SQL lookups | 200 OK | High-risk external side effect executed in router; raw SQL reads integration access tokens; mutates comment even if external API fails. |
| `GET` | `/{project_id}/stats` | `get_comment_stats` | `project_id` (path) | Path param | `verify_project_access` | `SocialMediaComment` | None (raw SQL) | None | N/A | 200 OK | 3 raw SQL aggregate queries in router; bypasses repository layer. |
| `GET` | `/{project_id}/campaigns` | `get_campaigns` | `project_id` (path) | Path param | `verify_project_access` | `DripCampaign`, `DripStep` | None (raw SQL) | None | N/A | 200 OK | Raw SQL with `selectinload` in router; bypasses repository layer; uses legacy `verify_project_access`. |
| `POST` | `/{project_id}/campaigns` | `create_campaign` | `project_id` (path), `name` (query) | Path param | `verify_project_access` | `DripCampaign` | None (direct ORM `db.add`) | None | N/A | 200 OK | Direct ORM mutation in router; bypasses repository layer; uses legacy `verify_project_access`. |
| `POST` | `/{project_id}/campaigns/{campaign_id}/steps` | `add_step` | `project_id` (path), `campaign_id` (path) | Path param | `verify_project_access` | `DripCampaign`, `DripStep` | None (direct ORM `db.get` + `db.add`) | None | N/A | 200 OK | `db.get` loads campaign globally, checks project in Python; direct ORM in router; legacy `verify_project_access`. |

---

## 6. Resource Inventory

| Resource Entity | 1. Contains `project_id`? | 2. Can be accessed via arbitrary ID? | 3. Ownership enforced by repository? | 4. Ownership checked only in router/service? | 5. Path where ownership NOT checked? | 6. Can AI / user ID reach it? | 7. Triggers external side effect? |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `SocialMediaPost` | YES (FK `projects.id`) | YES (in `SocialMediaMonitor`) | NO (repository only has basic `get_by_project`) | NOT checked in `SocialMediaMonitor` | YES (`SocialMediaMonitor.analyze_post`, `analyze_post_comments`, `auto_respond_to_comments`, `learn_from_post_performance`) | YES (caller passes `post_id` UUID) | YES (`auto_respond_to_comments`, `learn_from_post_performance` extracts learnings) |
| `SocialMediaComment` | YES (FK `projects.id`) | YES (in `SocialMediaMonitor.generate_comment_reply`) | NO (repository only has basic `get_by_project`) | Checked in router via raw SQL; NOT in monitor service | YES (`SocialMediaMonitor.generate_comment_reply` queries `where(id == comment_id)`) | YES (caller passes `comment_id` UUID) | YES (`send_comment_response` calls Meta Graph API to reply) |
| `Integration` | YES (FK `projects.id`) | NO (queried by `project_id` + provider) | NO in social router (bypasses `IntegrationRepository`) | Router checks via raw SQL | NO (filtered by path `project_id`), but bypasses repo | NO | YES (OAuth tokens used to call Meta Graph API) |
| `Project` | YES (PK `id`) | NO (root tenant) | N/A | Checked via `verify_project_access` | NO | NO | NO |
| `CustomerProfile` | YES (FK `projects.id`) | YES (in `DripEngine.enroll_customer`) | NO in DripEngine | NOT checked in `DripEngine.enroll_customer` | YES (`enroll_customer` takes `customer_id` without verifying tenant ownership) | YES (caller passes `customer_id`) | YES (drip message dispatch) |
| `DripCampaign` | YES (FK `projects.id`) | YES (in `DripEngine.enroll_customer`) | NO (router uses raw ORM; DripEngine uses raw SQL) | Router checks in Python; DripEngine does NOT check | YES (`DripEngine.enroll_customer` queries steps without verifying campaign project ownership) | YES (caller passes `campaign_id`) | YES (triggers automated drip step execution) |
| `DripStep` | NO (FK `drip_campaigns.id`) | YES (via `campaign_id` + `step_order`) | NO | Indirect through campaign | YES (`_get_step` in DripEngine only checks `campaign_id`) | YES | YES (defines message content and delays) |
| `CampaignEnrollment` | YES (FK `projects.id`) | YES (in `DripEngine.process_due_steps`) | NO | NOT checked in background loop | YES (`process_due_steps` scans globally across all projects without tenant context) | NO | YES (triggers `_execute_step` sending messages) |
| `Product` | YES (FK `projects.id`) | NO (filtered by `project_id` in SQL) | NO in `social_media.py` (bypasses `ProductRepository`) | Router checks via raw SQL | NO | NO | NO |
| `BotInstruction` | YES (FK `projects.id`) | NO (filtered by `project_id` in SQL) | NO in `social_media.py` (bypasses `BotInstructionRepository`) | Router checks via raw SQL | NO | NO | NO |

---

## 7. Tenant-Boundary Vulnerabilities
1. **Pervasive Raw SQL Bypasses**:
   * `social_media.py` executes 19 raw SQL queries directly in route handlers (`db.execute(select(...))`).
   * `drip_campaigns.py` executes raw SQL and direct ORM calls (`db.add`, `db.get`).
   * None of these routers utilize the context-aware repository pattern established in Groups 1–7.
2. **Legacy `verify_project_access` Dependency**:
   * All 10 routes rely on `verify_project_access(project_id, user_id, db)` rather than `get_tenant_context`.
   * This leaves the door open to parameter tampering where path `project_id` does not match injected `TenantContext`.
3. **Cross-Domain Resource Bypasses**:
   * `social_media.py` directly queries `Product`, `BotInstruction`, and `Integration` tables with raw SQL instead of delegating to `ProductRepository`, `BotInstructionRepository`, and `IntegrationRepository`.
4. **Python-Level Authorization in Drip Steps**:
   * In `add_step`, `db.get(DripCampaign, campaign_id)` performs a global primary-key fetch. Tenant checking occurs in Python (`if campaign.project_id != project_id`) rather than enforcing repository-level SQL predicates (`where(DripCampaign.project_id == context.project_id)`).

---

## 8. External Side-Effect Vulnerabilities
1. **Meta Graph API Reply Execution in Router**:
   * `send_comment_response` directly invokes `FacebookClient.reply_to_comment` and `InstagramClient.reply_to_comment` from within the FastAPI route handler.
   * If a malicious user supplies a valid `comment_id` that is not strictly scoped to the tenant in SQL, or if an unexpected exception occurs, state desynchronization happens (e.g. comment is marked `responded = True` even if the external call threw an exception).
2. **Synchronous Media Downloads on Dashboard Load**:
   * `get_social_accounts` performs synchronous network requests to download and persist external avatar URLs from Meta CDNs inside a GET endpoint, mutating database state (`Integration.extra_data`) during a read operation.
3. **External Feed Fetching Without Caching / Domain Isolation**:
   * `get_live_feed` calls `FacebookClient.get_feed` and `InstagramClient.get_media` directly during the HTTP GET request.
4. **Mandatory Invariant**:
   * Authorization and repository-level ownership validation MUST be proven at the database level BEFORE any external API call is dispatched to Meta, TikTok, or Gemini.

---

## 9. Credential / Integration Boundary
1. **Vulnerability in Credential Access**:
   * In `social_media.py` lines 109–115, 201–207, and 468–474, raw SQL queries fetch `Integration` records to extract sensitive OAuth access tokens (`integration.config.get("access_token")`), page IDs, and shop IDs.
2. **Mandatory Architectural Fix**:
   * All integration lookups MUST use `IntegrationRepository` from Group 3, passing `TenantContext`.
   * An external provider client must NEVER receive credentials or configuration belonging to another tenant project.
   * `IntegrationRepository.get_by_provider(context, provider)` must be the sole mechanism for resolving connected platform accounts.

---

## 10. SocialMediaMonitor Audit
Audit of `backend/app/services/social_media_monitor.py`:

1. `analyze_post(post_id: UUID, fetch_comments: bool)`:
   * **Unconstrained Query**: `select(SocialMediaPost).where(SocialMediaPost.id == post_id)` (line 46).
   * **Flaw**: Omits `SocialMediaPost.project_id == self.project_id`. A caller supplying `post_id` belonging to Tenant B causes Tenant A's monitor to read, analyze with Gemini AI, and mutate Tenant B's post.
2. `analyze_post_comments(post_id: UUID)`:
   * **Unconstrained Query**: `select(SocialMediaPost).where(SocialMediaPost.id == post_id)` (line 109).
   * **Flaw**: Omits `project_id` filter on post lookup.
3. `generate_comment_reply(comment_id: UUID, use_templates: bool, auto_send: bool)`:
   * **Unconstrained Query**: `select(SocialMediaComment).where(SocialMediaComment.id == comment_id)` (line 179).
   * **Flaw**: Omits `SocialMediaComment.project_id == self.project_id`. Tenant A can generate replies and mutate `responded` status on Tenant B's comment.
4. `auto_respond_to_comments(post_id: Optional[UUID], max_responses: int)`:
   * **Unconstrained Query**: `select(SocialMediaPost).where(SocialMediaPost.id == post_id)` (line 252).
   * **Flaw**: Omits `project_id` filter on post lookup.
5. `learn_from_post_performance(post_id: UUID)`:
   * **Unconstrained Query**: `select(SocialMediaPost).where(SocialMediaPost.id == post_id)` (line 299).
   * **Flaw**: Reads post belonging to Tenant B and saves extracted learnings into Tenant A's `BusinessContext(project_id=self.project_id)`. Direct cross-tenant data leakage!

---

## 11. DripEngine Audit
Audit of `backend/app/services/drip_engine.py`:

1. `enroll_customer(project_id: UUID, campaign_id: UUID, customer_id: UUID)`:
   * **Flaw**: Does NOT verify that `campaign_id` belongs to `project_id`.
   * **Flaw**: Does NOT verify that `customer_id` belongs to `project_id`.
   * **Impact**: A caller can enroll Tenant B's customer into Tenant A's campaign, or enroll Tenant A's customer into Tenant B's campaign.
2. `process_due_steps()`:
   * **Global Background Query**: `select(CampaignEnrollment)...where(CampaignEnrollment.status == 'active').where(CampaignEnrollment.next_execution_at <= now)` (line 55).
   * **Flaw**: Global background loop processes enrollments across all projects without constructing a scoped `TenantContext`.
   * **Impact**: When `_execute_step` executes, it invokes messaging logic without tenant boundaries.
3. `_execute_step(enrollment: CampaignEnrollment)`:
   * **Required Fix**: Must construct `TenantContext(project_id=enrollment.project_id, roles=["system"])` before dispatching messages or updating customer state.

---

## 12. Required Architecture
The target implementation must strictly conform to the established 4-layer tenant-security architecture:

```text
FastAPI Router (Depends(get_tenant_context))
        ↓ TenantContext
Domain Service (SocialMediaService / CRMService)
        ↓ TenantContext
Tenant-Scoped Repositories (SocialMediaCommentRepository, SocialMediaPostRepository, DripCampaignRepository)
        ↓ SQL with mandatory WHERE project_id == context.project_id
Database (PostgreSQL / SQLite)
        ↓ Verified Tenant Data
External Side Effect (Meta Graph API / Gemini AI)
```

### Architectural Prohibitions:
* **PROHIBITED**: `router -> raw SQL -> external provider`
* **PROHIBITED**: `service -> select(Resource).where(Resource.id == arbitrary_id)`
* **PROHIBITED**: Using `verify_project_access` anywhere in the migrated boundary.
* **PROHIBITED**: Passing unverified `customer_id`, `post_id`, or `comment_id` across tenant boundaries.

---

## 13. Required Repository Methods

### `SocialMediaCommentRepository` (`app/domains/social/repository.py`):
```python
def __init__(self, session: AsyncSession, context: TenantContext): ...
async def get_by_id(self, comment_id: UUID) -> Optional[SocialMediaComment]: ...
async def list_by_filter(self, platform: Optional[str], responded: Optional[bool], skip: int, limit: int) -> List[SocialMediaComment]: ...
async def count_total(self) -> int: ...
async def count_pending(self) -> int: ...
async def count_by_platform(self) -> Dict[str, int]: ...
async def find_existing(self, platform: str, external_id: str) -> Optional[SocialMediaComment]: ...
async def create(self, comment: SocialMediaComment) -> SocialMediaComment: ...
async def update(self, comment: SocialMediaComment) -> SocialMediaComment: ...
```

### `SocialMediaPostRepository` (`app/domains/social/repository.py`):
```python
def __init__(self, session: AsyncSession, context: TenantContext): ...
async def get_by_id(self, post_id: UUID) -> Optional[SocialMediaPost]: ...
async def get_by_external_id(self, platform: str, external_id: str) -> Optional[SocialMediaPost]: ...
async def list_posts(self, skip: int, limit: int) -> List[SocialMediaPost]: ...
async def update(self, post: SocialMediaPost) -> SocialMediaPost: ...
```

### `DripCampaignRepository` (`app/domains/crm/repository.py`):
```python
def __init__(self, session: AsyncSession, context: TenantContext): ...
async def get_by_id(self, campaign_id: UUID) -> Optional[DripCampaign]: ...
async def list_campaigns(self) -> List[DripCampaign]: ...
async def create_campaign(self, name: str, trigger_type: str) -> DripCampaign: ...
async def add_step(self, campaign_id: UUID, step_order: int, content_template: str, delay_hours: int) -> DripStep: ...
async def enroll_customer(self, campaign_id: UUID, customer_id: UUID) -> Optional[CampaignEnrollment]: ...
```

---

## 14. Required Modularization Boundaries (Rule 11 Compliance)

All files modified or created must strictly remain **<= 250 lines**.

### Router Layer Modularization (`backend/app/api/v1/`):
1. `social_media.py` (≤250 lines):
   * Primary router mount.
   * Comment endpoints: `list_comments`, `create_comment`, `get_comment_stats`.
2. `social_media_accounts.py` (≤250 lines):
   * Account endpoints: `get_social_accounts`, `get_live_feed`.
   * Avatar persistence logic cleanly extracted into a dedicated service helper.
3. `social_media_replies.py` (≤250 lines):
   * Reply generation & dispatch: `generate_comment_response`, `send_comment_response`.
4. `social_media_schemas.py` (≤250 lines):
   * Shared Pydantic schemas: `CommentCreate`, `ResponseGenerate`, etc.
5. `drip_campaigns.py` (≤250 lines):
   * Campaign management: `get_campaigns`, `create_campaign`, `add_step`. (Currently 81 lines, complies).

### Service Layer Modularization (`backend/app/services/`):
1. `social_media_monitor.py` (≤250 lines):
   * Core orchestrator: `analyze_post`, `analyze_post_comments`, `learn_from_post_performance`.
2. `social_media_auto_responder.py` (≤250 lines):
   * Automated replying logic: `generate_comment_reply`, `auto_respond_to_comments`, `_find_matching_template`, `_personalize_template`.
3. `social_media_analyzer.py` (≤250 lines):
   * AI helper routines: `_analyze_post_content`, `_analyze_comments_batch`, `_assess_comment_priority`, `_extract_post_learnings`.

---

## 15. Required Security Tests (`backend/tests/test_social_security.py`)

A minimum of 20 distinct security assertions across 5 categories:

### 1. Tenant Isolation
* `test_social_post_cross_tenant_read_blocked`: Tenant A cannot read Tenant B's post.
* `test_social_post_cross_tenant_update_blocked`: Tenant A cannot modify Tenant B's post.
* `test_social_comment_cross_tenant_read_blocked`: Tenant A cannot read Tenant B's comments.
* `test_social_comment_cross_tenant_mutation_blocked`: Tenant A cannot generate response or reply to Tenant B's comment.
* `test_drip_campaign_cross_tenant_read_blocked`: Tenant A cannot list Tenant B's campaigns.
* `test_drip_campaign_cross_tenant_step_blocked`: Tenant A cannot add steps to Tenant B's campaign.

### 2. Forged IDs Fail-Closed
* `test_forged_post_id_returns_404`: Passing non-existent or cross-tenant `post_id` returns 404.
* `test_forged_comment_id_returns_404`: Passing non-existent or cross-tenant `comment_id` returns 404.
* `test_forged_campaign_id_returns_404`: Passing non-existent or cross-tenant `campaign_id` returns 404.
* `test_forged_customer_enrollment_rejected`: Attempting to enroll Tenant B's customer into Tenant A's campaign fails closed.
* `test_forged_project_id_token_mismatch`: Caller with Tenant A token requesting Tenant B path returns 403.

### 3. External Side Effects Pre-Authorization Invariant
* `test_cross_tenant_comment_reply_suppresses_meta_api`: If comment belongs to Tenant B, `FacebookClient.reply_to_comment` is NEVER called (mock assert_not_called).
* `test_cross_tenant_feed_suppresses_meta_api`: Cross-tenant feed request NEVER retrieves Tenant B's Meta credentials or dispatches Graph API requests.
* `test_cross_tenant_ai_generation_suppresses_gemini`: Cross-tenant comment response generation aborts before Gemini API invocation.
* `test_cross_tenant_drip_step_suppresses_message_dispatch`: Cross-tenant enrollment execution never dispatches messages.

### 4. Same-Tenant Legitimate Access
* `test_same_tenant_comment_lifecycle`: Same tenant can list, create, and view comment statistics.
* `test_same_tenant_campaign_lifecycle`: Same tenant can create campaign and add steps successfully.
* `test_same_tenant_monitor_analysis`: Same tenant post analysis executes successfully with valid credentials.

### 5. Background Execution Safety
* `test_drip_engine_cross_tenant_enrollment_blocked`: Direct invocation of `enroll_customer` with mismatched `project_id` and `customer_id` fails closed.
* `test_drip_engine_process_due_steps_scoped`: Background step processor executes steps within verified tenant boundaries.

---

## 16. Functional Compatibility Requirements
* All existing route paths, HTTP methods, and URL structures must remain unchanged.
* Response payloads for `/comments`, `/accounts`, `/feed`, and `/campaigns` must maintain exact field structures for UI backward compatibility.
* Status codes must adhere to standard patterns (404 for missing/cross-tenant resources, 403 for unauthorized projects).
* Connected account provider mappings (`facebook`, `instagram`, `tiktok`, `whatsapp`) must continue functioning.

---

## 17. Acceptance Criteria
The Group 8 implementation will be approved ONLY if:
1. **Tenant Isolation**: All cross-tenant reads and mutations across comments, posts, and campaigns return 404/403.
2. **Zero Raw SQL in Routers**: All raw SQL queries in `social_media.py` and `drip_campaigns.py` are replaced by tenant-aware repository calls.
3. **Zero `verify_project_access`**: Legacy `verify_project_access` is completely eliminated from the migrated boundary.
4. **Side Effect Invariant**: Meta, Gemini, and messaging side effects are proven to execute only AFTER database ownership verification.
5. **Monitor IDOR Fixed**: All unconstrained `select(Resource).where(Resource.id == id)` queries in `SocialMediaMonitor` enforce `project_id`.
6. **Rule 11 Compliance**: Every modified and newly created Python file is strictly ≤ 250 lines.
7. **Regression Green**: Full regression suite (Groups 1–7: 39 tests + new Group 8 test suite) passes with 100% success rate.

---

## 18. Explicit Non-Goals
* Do NOT implement full Stripe billing in `payments_invoicing.py`.
* Do NOT refactor user-level `subscriptions.py`.
* Do NOT rewrite third-party SDK clients (`FacebookClient`, `InstagramClient`).
* Do NOT modify existing database tables or run destructive database migrations.
* Do NOT alter LLM prompt generation behavior beyond security context filtering.

---

## 19. Evidence Limitations
* Provenance is derived strictly from surviving repository artifacts and code structure.
* No historical document defines a numbered sequence beyond Group 5.
* The grouping of Social Media and Drip Campaigns into Group 8 reflects repository architectural proximity and surviving audit recommendations.

---

GROUP 8 IMPLEMENTATION CONTRACT COMPLETE
