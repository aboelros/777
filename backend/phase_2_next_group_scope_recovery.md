# Phase 2 — Next Security Group Scope Recovery (Post-Group 8 Freeze)

## 1. Executive Conclusion

Following the completion and freeze of Reconstructed Group 8 (**Social Media & Campaigns Security Migration**, documented in `backend/phase_2_group_8_final_evidence.md`), an exhaustive historical and repository-wide security audit was conducted to identify the next security-hardening migration candidate.

1. **Historical Provenance**:
   * **HISTORICAL NEXT GROUP SPECIFICATION: `NOT RECOVERABLE`**
   * No surviving document, git commit, branch, or planning artifact in the repository defines a historical "Group 9" or specifies a numbered migration sequence beyond Group 5 (`Background Integration Workers`).
2. **Repository-Based Recommendation**:
   * **Analytics & Reporting (`reports.py`, `services/report_generator.py`, `domains/analytics/`)** is recommended as the strongest next reconstructed security-migration scope (**`RECONSTRUCTED NEXT-GROUP SCOPE — NOT HISTORICALLY VERIFIED`**).
   * It combines **live external side effects and OAuth credential access** (outbound calls to Meta Graph API using raw `Integration.extra_data` tokens in `reports.py` and outbound calls to Gemini AI in `services/report_generator.py`), **18 raw SQL queries bypassing repositories**, **1 unconstrained primary-key fetch with Python-only tenant filtering** (`AnalyticsService.get_report`), **8 legacy `verify_project_access` occurrences** (including a custom local definition in `reports.py` that ignores `ProjectMember`), **high cross-domain data sensitivity** (revenue, customer PII, AI costs), and **two major Rule 11 monoliths** (`reports.py` at 465 lines and `services/report_generator.py` at 548 lines), while maintaining a **100% clean boundary** with zero overlap with Frozen Groups 1–8.
   * **Documented Near-Tie**: **Product Catalog, Media & File Storage** (`products.py`, `photos.py`, `storage.py`, `domains/products/`, `services/file_storage.py`), **Projects & Tenant Membership** (`projects.py`, `domains/projects/`), and **Payments & Invoicing** (`payments_invoicing.py`, `services/payment_service.py`, `domains/billing/`) also exhibit high-priority tenant-isolation defects and are fully inventoried and ranked below.

---

## 2. Historical Provenance

Every finding in this report is classified under one of the four mandatory provenance categories:

* **`RECOVERED HISTORICAL FACT`**:
  * The original Phase 2 roadmap in commit history terminated its numbered group sequence at `Phase 2 Group 5` (commit `95baef4c9333a90540dba7e72f42e7f5092e7231`: `chore: final verification for Phase 2 Group 5`).
  * `remaining_security_audit.md` (Section 2 & Section 4) cataloged 8 top-level audit domains remaining after Group 1:
    1. `Integrations / Webhooks` (Migrated in Groups 2–5)
    2. `Orders / Commerce` (Migrated in Reconstructed Group 6)
    3. `AI Assistant / Training` (Migrated in Reconstructed Group 7)
    4. `Social Media / Campaigns` (Migrated in Reconstructed Group 8)
    5. `CRM / Messages` (Messages migrated in Group 1; `deals.py` remains unmigrated)
    6. `Subscriptions / Payments` (`payments_invoicing.py` and `subscriptions.py` remain unmigrated; `payments_invoicing.py` was explicitly noted as deferred in `remaining_security_audit.md` Section 6, `phase_2_group_7_scope.md`, and `phase_2_group_8_scope.md`)
    7. `Projects / Settings` (`projects.py`, `products.py`, `photos.py`, `storage.py` remain unmigrated)
    8. `Reporting / Analytics` (`reports.py`, `services/report_generator.py`, `domains/analytics/` remain unmigrated; explicitly deferred in `phase_2_group_8_scope.md`)
* **`REPOSITORY-BASED EVIDENCE`**:
  * Direct static and architectural inspection of all remaining files in `backend/app/api/v1/`, `backend/app/services/`, `backend/app/domains/`, `backend/app/workers/`, and `backend/tests/`.
* **`RECONSTRUCTED NEXT SCOPE`**:
  * The bounded selection of **Analytics & Reporting** as the next security migration scope based on demonstrated repository risk, external side effects, credential exposure, raw SQL bypasses, and clean separation from Frozen Groups 1–8.
* **`INFERENCE`**:
  * Comparative risk prioritization among the remaining unmigrated domains (`Analytics & Reporting`, `Product Catalog & Media Storage`, `Projects & Tenant Membership`, `Payments & Invoicing`, and `CRM Pipeline / Deals`).

```text
HISTORICAL NEXT GROUP SPECIFICATION: NOT RECOVERABLE
```

---

## 3. Evidence Search Performed

The following searches and inspections were executed across the repository:

1. **Git Grep & Commit Log Searches**:
   * `git grep -n -i "Group 9" -- .` → **0 matches**.
   * `git grep -n -i "Phase 2 Group 9" -- .` → **0 matches**.
   * `git log --all --grep="Group 9"` → **0 matches**.
   * `git log --all --grep="Phase 2"` → Matches only `95baef4c9333a90540dba7e72f42e7f5092e7231` (`chore: final verification for Phase 2 Group 5`).
2. **Surviving Audit & Scope Documents Inspected**:
   * `remaining_security_audit.md`
   * `backend/phase_2_group_6_scope_recovery.md`, `backend/phase_2_group_6_scope.md`, `backend/phase_2_group_6_final_evidence.md`
   * `backend/phase_2_group_7_scope.md`, `backend/phase_2_group_7_final_evidence.md`
   * `backend/phase_2_group_8_scope.md`, `backend/phase_2_group_8_final_evidence.md`
3. **Full Codebase Static Scans**:
   * Enumerated all 29 router files in `backend/app/api/v1/`, 51 service files in `backend/app/services/`, 52 domain files in `backend/app/domains/`, and 5 worker files in `backend/app/workers/`.
   * Searched all remaining occurrences of `verify_project_access`, `get_tenant_context`, `TenantContext`, `db.execute(`, `session.execute(`, `select(`, and external client instantiations (`FacebookClient`, `InstagramClient`, `get_ai_provider`, `boto3`, `FileStorageService`).

---

## 4. Remaining-Domain Inventory (Outside Frozen Groups 1–8)

### 4.1 Candidate 1: Analytics & Reporting (`REPOSITORY-BASED EVIDENCE`)
* **Files**:
  * `backend/app/api/v1/reports.py` (465 lines)
  * `backend/app/services/report_generator.py` (548 lines)
  * `backend/app/domains/analytics/models.py` (113 lines)
  * `backend/app/domains/analytics/repository.py` (26 lines)
  * `backend/app/domains/analytics/service.py` (45 lines)
  * `backend/app/domains/analytics/schemas.py` (70 lines)
  * `backend/app/domains/analytics/telemetry.py` (96 lines)
* **API Route Count**: 4 routes in `reports.py`:
  1. `POST /{project_id}/generate` (`generate_report`, line 44)
  2. `GET /{project_id}` (`list_reports`, line 113)
  3. `GET /{project_id}/dashboard-summary` (`get_dashboard_summary`, line 142)
  4. `GET /{project_id}/{report_id}` (`get_report`, line 251)
* **Direct SQL / Unconstrained ORM Queries**:
  * **11 raw SQL queries** in `reports.py` (`lines 28, 128, 167, 176, 185, 213, 264, 297, 347`, plus `db.add`/`db.commit` on lines 99–100).
  * **7 raw SQL queries** in `services/report_generator.py` (`lines 56, 133, 217, 283, 309, 369, 381`).
  * **1 unconstrained primary-key fetch with Python post-filtering** in `domains/analytics/service.py` (`line 41`: `report = await repo.get(UUID(report_id))` followed by `if not report or report.project_id != proj_uuid`).
* **`verify_project_access` Usage**: **8 occurrences**:
  * `reports.py` defines its own custom local `verify_project_access` (`line 26`) that only checks `Project.owner_id == UUID(user_id)` (ignoring `ProjectMember` roles) and calls it at `lines 62, 126, 152, 262`.
  * `domains/analytics/service.py` defines `_verify_project_access` (`line 15`) and calls it at `lines 29, 38`.
* **`TenantContext` / Repository Usage**: **0 `TenantContext` usage**. `reports.py` completely bypasses `AnalyticsService` and `ReportRepository`. `ReportRepository` and `APILogRepository` do not accept `TenantContext`.
* **External Side Effects & Credential Access**: **HIGH**:
  1. **Meta Graph API Calls with Raw Integration Credentials**: In `reports.py` (`get_dashboard_summary`, `lines 211–244`), the endpoint executes raw SQL `select(Integration).where(Integration.project_id == project_id)`, extracts OAuth credentials from `integration.extra_data`, instantiates `FacebookClient(integration.extra_data)` and `InstagramClient(integration.extra_data)`, and dispatches live HTTP requests (`client.get_page_engagement()`, `client.get_instagram_engagement()`) directly from the router without `TenantContext` or `IntegrationRepository`.
  2. **External Gemini AI Calls**: In `services/report_generator.py` (`generate_sales_report` → `_generate_ai_insights`, `lines 28, 108, 465–469`), `ReportGenerator` instantiates `get_ai_provider(db)` and sends aggregated project revenue/sales data to external Gemini AI (`self.ai_provider.generate_response`) without `TenantContext`.
* **Sensitive Data**: Aggregates and returns revenue totals, order lists containing customer PII (`customer_name`, `customer_email`, `external_id`, `total` at `report_generator.py:181–195`), message counts, escalation metrics, AI token costs, and social engagement metrics.
* **Background-Worker Access**: `generate_daily_reports` and `cleanup_old_logs` in `backend/app/workers/tasks/core.py` (`lines 665–747`) query `Project`, `Report`, and `APILog` directly without `TenantContext` (and `generate_daily_reports` uses outdated attribute names `Project.status`, `Report.type`, `Report.data`).
* **Existing Security Tests**: **0 tests**.

---

### 4.2 Candidate 2: Product Catalog, Media & File Storage (`REPOSITORY-BASED EVIDENCE`)
* **Files**:
  * `backend/app/api/v1/products.py` (115 lines)
  * `backend/app/domains/products/service.py` (372 lines)
  * `backend/app/domains/products/repository.py` (54 lines)
  * `backend/app/domains/products/models.py` (96 lines)
  * `backend/app/domains/products/schemas.py` (72 lines)
  * `backend/app/api/v1/photos.py` (223 lines)
  * `backend/app/api/v1/storage.py` (30 lines)
  * `backend/app/services/file_storage.py` (485 lines)
* **API Route Count**: **13 routes**:
  * `products.py` (9 routes): `POST /{project_id}/bulk-upload`, `GET /{project_id}/{product_id}`, `PUT /{project_id}/{product_id}`, `DELETE /{project_id}/{product_id}`, `GET /{project_id}`, `POST /{project_id}`, `POST /{project_id}/{product_id}/images`, `DELETE /{project_id}/{product_id}/images/{image_index}`, `PATCH /{project_id}/{product_id}/images/{image_index}`.
  * `photos.py` (3 routes): `POST /{project_id}/about/photos`, `GET /{project_id}/about/photos`, `DELETE /{project_id}/about/photos`.
  * `storage.py` (1 route): `GET /images/{key:path}`.
* **Direct SQL / Unconstrained ORM Queries**:
  * **6 unconstrained primary-key lookups (`await product_repo.get(prod_uuid)`)** in `domains/products/service.py` (`lines 149, 186, 205, 278, 325, 351`) that load any tenant's `Product` row from PostgreSQL before checking `if not product or product.project_id != proj_uuid` in Python.
  * **1 raw SQL query** in `domains/products/service.py` (`line 97`: `select(Product).where(Product.project_id == proj_uuid)`).
  * **3 raw SQL queries** in `photos.py` (`lines 52, 154, 195`: `select(Project).where(Project.id == project_id).where(Project.owner_id == UUID(user_id))`).
  * **4 raw SQL text queries** in `services/file_storage.py` (`PostgresStorageService`, `lines 177, 204, 219, 251, 270`) accessing `public.product_images` by `key` without a `project_id` column predicate.
* **`verify_project_access` Usage**: **10 occurrences** in `domains/products/service.py` (`_verify_project_access` defined at `line 33` and called at `lines 47, 91, 146, 183, 202, 217, 275, 322, 348`).
* **`TenantContext` / Repository Usage**: **0 `TenantContext` usage**. `ProductRepository` does not accept `TenantContext`.
* **IDOR & Cross-Tenant Write/Delete Vulnerabilities**:
  1. **Python-Only Post-Fetch Tenant Filtering**: All single-product read, update, delete, and image operations fetch `Product` globally by `product_id` before checking `product.project_id` in Python.
  2. **Cross-Tenant Shared File Overwrite & Deletion in `photos.py`**: `upload_about_photos` (`lines 73–75, 100–104`) and `delete_about_photos` (`lines 210–213`) write to and unlink files in a single global `STATIC_DIR` (`backend/static/about/1.jpg..4.jpg`) shared across all projects. Tenant A calling `DELETE /{project_id}/about/photos` deletes the uploaded photos of all other tenants.
  3. **Unauthenticated Binary Image Retrieval in `storage.py`**: `GET /api/v1/storage/images/{key:path}` serves binary image data from `PostgresStorageService` without authentication or tenant verification.
* **External Side Effects & Credential Access**: **HIGH**:
  * `FileStorageService` (`services/file_storage.py`) connects to Cloudflare R2 / AWS S3 using `settings.S3_ACCESS_KEY` and `settings.S3_SECRET_KEY` (`boto3.client('s3')` at `lines 54–60`) to upload (`put_object`), delete (`delete_object`), and presign (`generate_presigned_url`) objects, or connects to an external database via `settings.IMAGE_STORAGE_DATABASE_URL`.
* **Existing Security Tests**: **0 tests**.

---

### 4.3 Candidate 3: Payments & Invoicing (`REPOSITORY-BASED EVIDENCE`)
* **Files**:
  * `backend/app/api/v1/payments_invoicing.py` (56 lines)
  * `backend/app/services/payment_service.py` (70 lines)
  * `backend/app/domains/billing/models.py` (`Invoice`, `PaymentLink` models — 227 lines)
  * `backend/app/domains/billing/repository.py` (`InvoiceRepository`, `PaymentLinkRepository` — 44 lines)
  * `backend/app/domains/billing/service.py` (`BillingService` — 50 lines)
* **API Route Count**: 3 routes in `payments_invoicing.py`:
  1. `POST /{project_id}/payment-links` (`create_payment_link`, line 13)
  2. `GET /{project_id}/invoices` (`get_invoices`, line 28)
  3. `POST /{project_id}/invoices` (`create_invoice`, line 41)
* **Direct SQL / ORM Queries**:
  * `PaymentService` (`services/payment_service.py`) bypasses `InvoiceRepository` and `PaymentLinkRepository`, executing `self.db.add(link)` (`line 37`), `self.db.add(invoice)` (`line 60`), and `select(Invoice).where(Invoice.project_id == project_id)` (`line 67`) directly.
* **`verify_project_access` Usage**: **7 occurrences**:
  * 4 in `payments_invoicing.py` (`lines 8, 22, 35, 51`).
  * 3 in `domains/billing/service.py` (`_verify_project_access` at `lines 20, 34, 46`).
* **Active Cross-Tenant IDOR Vulnerability**:
  * **Cross-Tenant Customer Invoice Injection (`POST /{project_id}/invoices`)**: `create_invoice` (`payments_invoicing.py:44`, `payment_service.py:42–63`) accepts a caller-supplied `customer_id: UUID` in the request body and persists `Invoice(project_id=project_id, customer_id=customer_id, ...)` **without verifying that `customer_id` belongs to `project_id`**. Tenant A can attach invoices to Tenant B's `CustomerProfile`.
* **External Side Effects**: **LOW** (`PaymentService.create_payment_link` generates a mock URL string `f"https://buy.stripe.com/test_{project_id}_{datetime.now().timestamp()}"`; `# import stripe` is commented out at `line 9`).
* **Existing Security Tests**: **0 tests**.

---

### 4.4 Candidate 4: CRM Pipeline / Deals (`REPOSITORY-BASED EVIDENCE`)
* **Files**:
  * `backend/app/api/v1/deals.py` (146 lines)
  * `backend/app/domains/crm/models.py` (`PipelineStage`, `Deal` — 172 lines)
  * `backend/app/domains/crm/repository.py` (`PipelineStageRepository`, `DealRepository` — 186 lines; **Note: file modified in Frozen Group 8**)
  * `backend/app/domains/crm/service.py` (`CRMService` — 57 lines; **Note: file modified in Frozen Group 8**)
* **API Route Count**: 5 routes in `deals.py`:
  1. `GET /{project_id}/stages` (`get_stages`, line 17)
  2. `POST /{project_id}/stages` (`create_stage`, line 34)
  3. `GET /{project_id}/deals` (`get_deals`, line 59)
  4. `POST /{project_id}/deals` (`create_deal`, line 79)
  5. `PATCH /{project_id}/deals/{deal_id}` (`update_deal`, line 113)
* **Direct SQL Queries**: **6 raw SQL queries/mutations** directly in `deals.py` (`lines 26, 52, 69, 93, 108, 126`), completely bypassing `PipelineStageRepository` and `DealRepository`.
* **`verify_project_access` Usage**: **6 occurrences** in `deals.py` (`lines 9, 24, 44, 67, 90, 124`).
* **Active Cross-Tenant IDOR Vulnerabilities**:
  1. **Cross-Tenant Customer Deal Linking (`POST /{project_id}/deals`)**: Accepts `customer_id: Optional[UUID] = None` (`line 85`) and inserts `Deal(..., customer_id=customer_id)` (`lines 101–108`) without verifying that `customer_id` belongs to `project_id`.
  2. **Cross-Tenant Stage Reassignment (`PATCH /{project_id}/deals/{deal_id}`)**: Accepts `stage_id: Optional[UUID] = None` (`line 117`) and sets `deal.stage_id = stage_id` (`lines 136–137`) without verifying that the target `stage_id` belongs to `project_id`.
* **Boundary Constraint**: `backend/app/domains/crm/repository.py` and `backend/app/domains/crm/service.py` were modified and frozen in Group 8. While `deals.py` itself was outside Group 8, adding new methods to `domains/crm/repository.py` would touch a Group 8 file unless isolated in a dedicated `deals_repository.py` module.
* **Existing Security Tests**: **0 tests**.

---

### 4.5 Candidate 5: Projects & Tenant Membership Administration (`REPOSITORY-BASED EVIDENCE`)
* **Files**:
  * `backend/app/api/v1/projects.py` (118 lines)
  * `backend/app/domains/projects/service.py` (263 lines)
  * `backend/app/domains/projects/repository.py` (59 lines)
  * `backend/app/domains/projects/models.py` (136 lines)
* **API Route Count**: 10 routes in `projects.py` (`POST ""`, `GET ""`, `GET /{project_id}`, `PATCH /{project_id}`, `DELETE /{project_id}`, `GET /{project_id}/members`, `POST /{project_id}/members`, `PATCH /{project_id}/members/{target_user_id}`, `DELETE /{project_id}/members/{target_user_id}`, `GET /{project_id}/dashboard`).
* **Critical Authorization Bypass in `domains/projects/service.py`**:
  1. `list_project_members` (`lines 169–202`): Contains `if project.owner_id != user_uuid: pass` (`lines 185–187`). Any authenticated user can list all members, names, emails, and roles of any project ID.
  2. `add_project_member` (`lines 204–231`): Comment states `# Basic validation omitted for brevity, adding directly` (`line 206`). The caller's `user_id` is never checked against `project_id`. Any authenticated user can add themselves as `ProjectRole.OWNER` or `ProjectRole.ADMIN` to any tenant's project, which immediately grants them a valid `TenantContext` via `get_tenant_context` (`backend/app/api/dependencies/tenant.py:42–63`) across all project-scoped endpoints.
  3. `update_project_member_role` (`lines 233–241`) & `remove_project_member` (`lines 243–250`): Neither method checks whether the caller (`user_id`) owns or administers `project_id`. Any authenticated user can escalate roles or delete members in any project.
* **External Side Effects**: **NONE**.
* **Existing Security Tests**: Basic project access is tested via `test_tenant_security.py`, but **0 tests** cover the `/members` endpoints (`list_project_members`, `add_project_member`, `update_project_member_role`, `remove_project_member`).

---

### 4.6 Candidate 6: Subscriptions & User Billing (`REPOSITORY-BASED EVIDENCE`)
* **Files**:
  * `backend/app/api/v1/subscriptions.py` (606 lines)
  * `backend/app/services/subscription_service.py` (598 lines)
  * `backend/app/services/usage_tracker.py` (203 lines)
* **API Route Count**: 12 routes in `subscriptions.py` (note: `@router.get("/check-limit/{resource}")` is defined twice at `lines 362` and `566`).
* **Ownership Model**: User-level account billing (`user_id = Depends(get_current_user_id)`), not project-scoped (`TenantContext`), except `UsageTracker` (`services/usage_tracker.py`) which accepts `project_id` and `user_id` without verifying project ownership (though `UsageTracker` is not currently exposed via any API route).
* **External Side Effects**: **NONE** (Local database tier/usage calculations; no live Stripe calls).

---

### 4.7 Candidate 7: Admin & Authentication (`REPOSITORY-BASED EVIDENCE`)
* **Files**: `backend/app/api/v1/admin.py` (161 lines), `backend/app/api/v1/auth.py` (323 lines), `backend/app/domains/auth/*`.
* **Characteristics**: `admin.py` is gated at the router level by `Depends(require_role("admin"))` (`line 16`); `auth.py` handles user login, registration, JWT issuance, and 2FA outside project tenant scoping.

---

## 5. External Side Effects & Background Worker Audit

### 5.1 Untrusted Identifier → DB Lookup → Credential Retrieval → External Provider Paths
Across all remaining domains outside Groups 1–8, two domains contain active external side-effect pipelines lacking a `TenantContext` repository boundary:

1. **Analytics & Reporting (`reports.py` & `services/report_generator.py`)**:
   * **Path A (`GET /api/v1/reports/{project_id}/dashboard-summary`)**:
     ```text
     project_id (Path)
       → local verify_project_access (owner-only check, no TenantContext)
       → raw SQL: select(Integration).where(Integration.project_id == project_id)
       → raw credential access: integration.extra_data (Facebook/Instagram OAuth tokens)
       → external provider: FacebookClient.get_page_engagement() / InstagramClient.get_instagram_engagement()
     ```
   * **Path B (`POST /api/v1/reports/{project_id}/generate`)**:
     ```text
     project_id (Path)
       → local verify_project_access (no TenantContext)
       → ReportGenerator(db, project_id)
       → raw SQL: select(Order).where(Order.project_id == self.project_id)
       → external provider: self.ai_provider.generate_response(prompt=...) (Gemini API)
     ```
2. **Product Catalog & Media Storage (`products.py`, `domains/products/service.py`, `services/file_storage.py`)**:
   * **Path C (`POST /api/v1/products/{project_id}/{product_id}/images` & `DELETE .../images/{image_index}`)**:
     ```text
     project_id, product_id (Path)
       → ProductService._verify_project_access (no TenantContext)
       → unconstrained SQL: product_repo.get(prod_uuid) (loads any tenant's Product into memory)
       → Python-only check: if not product or product.project_id != proj_uuid
       → credential access: settings.S3_ACCESS_KEY / settings.S3_SECRET_KEY / IMAGE_STORAGE_DATABASE_URL
       → external provider: S3StorageService.upload_image / delete_image / generate_presigned_url
     ```

### 5.2 Background Workers Audit (`backend/app/workers/` & `backend/app/services/`)
1. **`backend/app/workers/tasks/core.py` (747 lines)**:
   * `generate_daily_reports` (`lines 665–701`): Queries `select(Project).where(Project.status == "active")` without `TenantContext` and instantiates `Report(project_id=project.id, type="daily_summary", data=...)` using non-existent column names (`Project.status`, `Report.type`, `Report.data` instead of `Report.report_type`, `Report.payload`).
   * `cleanup_old_logs` (`lines 720–747`): Executes global `delete(APILog).where(APILog.created_at < cutoff_date)`.
   * Legacy integration/message tasks (`sync_shopify_orders`, `send_message_task`, `process_message_queue`, `process_inbound_message`, `generate_ai_response`, `verify_integration`, `schedule_followup`, `train_model`): Superseded by `backend/app/workers/celery_workers.py` (migrated in Group 5) and `backend/app/workers/tasks/ai_tasks.py` (migrated in Group 7).
2. **`backend/app/services/background_tasks.py` (46 lines) & `backend/app/services/smart_tracker.py` (182 lines)**:
   * Launched on application startup (`main.py:96`). `SmartTrackerService` queries `select(Project).where(Project.is_active == True)` and `select(Order).where(Order.project_id == project.id, ...)` without `TenantContext`, and invokes `AIOrchestrator` using legacy methods (`self.ai.gemini.generate_response`, `self.ai._send_message`).

---

## 6. Frozen-Group Findings (Recorded Only — Do Not Reopen)

In accordance with Section 8 (`DO NOT REOPEN COMPLETED GROUPS`), the following residual findings in Frozen Groups 1–8 were observed during the repository scan and are recorded strictly outside the next scope:

* **`FROZEN-GROUP FINDING — NOT PART OF NEXT SCOPE`**:
  1. `backend/app/api/v1/chat_bot.py` (`lines 39, 82, 133, 181`): Contains a local `verify_project_access` definition and 3 route usages (classified under Group 1 / Messaging in `phase_2_group_7_scope.md`).
  2. `backend/app/api/v1/messages.py` (`lines 36, 43, 536, 582`) & `backend/app/domains/messages/service.py` (`lines 24, 140, 153`) & `backend/app/domains/customers/service.py` (`lines 15, 29, 38`): Residual `verify_project_access` helper definitions/methods in Group 1 files.
  3. `backend/app/api/v1/integrations.py` (`line 46`): Unused `verify_project_access` function definition in Group 2 router.

---

## 7. Security-Risk Comparison & Candidate Ranking

| Rank | Candidate Domain | Exposed Routes | Raw / Unscoped Queries | `verify_project_access` | IDOR Potential | External Side Effects | Credential Sensitivity | Worker Risk | Data Sensitivity | Security Tests | Rule 11 Violations (`>250` lines) | Frozen Group Overlap |
| :---: | :--- | :---: | :---: | :---: | :--- | :--- | :--- | :--- | :--- | :---: | :--- | :--- |
| **1** | **Analytics & Reporting** (`reports.py`, `report_generator.py`, `domains/analytics/`) | 4 | **19** (18 raw SQL + 1 unconstrained `repo.get`) | **8** | **MEDIUM-HIGH** (`report_id` fetched globally in `AnalyticsService`; raw `project_id` primitives) | **HIGH** (Live Meta Graph API + Gemini AI calls) | **HIGH** (OAuth `access_token` in `Integration.extra_data` + `GEMINI_API_KEY`) | **MEDIUM** (`generate_daily_reports` in `core.py`) | **HIGH** (Revenue, customer PII in order reports, AI costs) | 0 | **2 files** (`reports.py`: 465, `report_generator.py`: 548) | **NONE** |
| **2 (Tie)** | **Product Catalog, Media & File Storage** (`products.py`, `photos.py`, `storage.py`, `domains/products/`, `file_storage.py`) | 13 | **12** (6 unconstrained `product_repo.get` + 6 raw SQL) | **10** (+3 raw `Project` checks) | **HIGH** (6 Python-only product checks; global `STATIC_DIR` wipe in `photos.py`; unauth `storage.py`) | **HIGH** (Cloudflare R2 / S3 upload, delete, presign; DB/disk file writes) | **MEDIUM-HIGH** (`S3_ACCESS_KEY`, `S3_SECRET_KEY`, `IMAGE_STORAGE_DATABASE_URL`) | **NONE** | **MEDIUM** (Catalog prices, stock, images) | 0 | **2 files** (`products/service.py`: 372, `file_storage.py`: 485) | **NONE** |
| **3** | **Projects & Tenant Membership** (`projects.py`, `domains/projects/`) | 10 | **2** (raw SQL in `projects/service.py`) | 0 | **CRITICAL** (4 `/members` routes omit caller authorization; allows `TenantContext` takeover) | **NONE** | **LOW** (User emails, roles) | **NONE** | **HIGH** (Tenant membership & RBAC control plane) | Partial (0 on `/members`) | **1 file** (`projects/service.py`: 263) | **NONE** |
| **4** | **Payments & Invoicing** (`payments_invoicing.py`, `payment_service.py`, `domains/billing/`) | 3 | **3** (in `payment_service.py`) | **7** | **HIGH** (`POST /{project_id}/invoices` links arbitrary cross-tenant `customer_id`) | **LOW** (Mock Stripe URL string only) | **LOW** (No live Stripe key used) | **NONE** | **MEDIUM-HIGH** (Invoices, payment links) | 0 | **0 files** | **NONE** |
| **5** | **CRM Pipeline / Deals** (`deals.py`, `domains/crm/`) | 5 | **6** (in `deals.py`) | **6** | **HIGH** (`create_deal` links arbitrary `customer_id`; `update_deal` links arbitrary `stage_id`) | **NONE** | **NONE** | **NONE** | **MEDIUM** (Deals, pipeline stages) | 0 | **0 files** |Touches `domains/crm/` (Group 8) |
| **6** | **Subscriptions & User Billing** (`subscriptions.py`, `subscription_service.py`, `usage_tracker.py`) | 12 | **22** (user-scoped SQL) | 0 | **LOW** (Bound to `get_current_user_id`; user-level SaaS billing) | **NONE** | **NONE** | **NONE** | **MEDIUM** (User tier, quotas) | 0 | **2 files** (`subscriptions.py`: 606, `subscription_service.py`: 598) | **NONE** |

---

## 8. Recommended Next Candidate & Tie Analysis (`RECONSTRUCTED NEXT SCOPE`)

### Selected Recommendation: **Analytics & Reporting Security Migration**

**Why Analytics & Reporting is selected as the primary recommendation**:
1. **Highest Concentration of Raw SQL Bypasses + Live External Side Effects**:
   * It is the only remaining domain that combines **18 raw SQL queries** across its router and service layer with **live outbound third-party API calls using tenant OAuth credentials** (`FacebookClient.get_page_engagement()` and `InstagramClient.get_instagram_engagement()` in `reports.py:211–244`) and **live AI provider calls** (`self.ai_provider.generate_response()` in `services/report_generator.py:465–469`).
2. **Direct Provenance in Surviving Audit Artifacts**:
   * `remaining_security_audit.md` (Section 2 & Section 4) explicitly lists `Reporting / Analytics` as one of the 8 core domains requiring migration from `verify_project_access` and direct SQL to `TenantContext`.
   * `backend/phase_2_group_8_scope.md` explicitly deferred `backend/app/api/v1/reports.py` and `backend/app/services/report_generator.py` at the Group 8 boundary.
3. **Eliminates Cross-Domain Aggregation & PII Leakage Risk**:
   * `reports.py` and `services/report_generator.py` query across `Order`, `Message`, `Integration`, and `Report` tables, returning raw customer PII (`customer_name`, `customer_email`) and financial totals without repository-level `TenantContext` enforcement.
4. **Zero Overlap with Frozen Groups 1–8**:
   * The entire migration is self-contained within `backend/app/api/v1/reports*`, `backend/app/services/report_generator*`, and `backend/app/domains/analytics/*`.

**Documented Near-Tie with Product Catalog, Media & File Storage (and Projects / Payments)**:
* **Product Catalog, Media & File Storage** (`products.py`, `photos.py`, `storage.py`, `domains/products/`, `services/file_storage.py`) is a very close #2 (near-tie) because `domains/products/service.py` performs 6 unconstrained `product_repo.get(prod_uuid)` queries with Python-only tenant checks, invokes S3/R2 storage side effects, and `photos.py` overwrites a global `STATIC_DIR` across tenants.
* **Analytics & Reporting** is preferred first because (a) `reports.py` directly extracts sensitive third-party OAuth tokens (`Integration.extra_data`) in the router to call external Meta Graph APIs, (b) `reports.py` has 11 raw SQL queries directly in the API router (whereas `products.py` already delegates to `ProductService`), and (c) `Reporting / Analytics` is explicitly flagged in `remaining_security_audit.md` as a legacy `verify_project_access` router domain.

---

## 9. Exact Reconstructed Scope

### In Scope
1. **API Layer**:
   * `backend/app/api/v1/reports.py` (currently 465 lines — must be decomposed under Rule 11 `<= 250` lines, e.g., into `reports.py` and `reports_dashboard.py` or delegated cleanly to `AnalyticsService`).
2. **Domain Layer**:
   * `backend/app/domains/analytics/repository.py` (`ReportRepository`, `APILogRepository` — enforce `TenantContext` on all reads and writes).
   * `backend/app/domains/analytics/service.py` (`AnalyticsService` — remove `_verify_project_access`, enforce `TenantContext`, eliminate unconstrained `repo.get(UUID(report_id))`).
   * `backend/app/domains/analytics/models.py` (read-only verification or index/constraint alignment if needed; preserve schema).
   * `backend/app/domains/analytics/schemas.py` (preserve existing API schemas).
3. **Service Layer**:
   * `backend/app/services/report_generator.py` (currently 548 lines — must be decomposed under Rule 11 `<= 250` lines and refactored to require `TenantContext` before any database query or external Gemini AI call).
4. **Dedicated Security Test Suite**:
   * `backend/tests/test_analytics_security.py` (to be created during implementation).

### Dependencies (Read-Only / Existing Repositories)
* `backend/app/core/context.py` (`TenantContext`)
* `backend/app/api/dependencies/tenant.py` (`get_tenant_context`)
* `backend/app/domains/orders/repository.py` (`OrderRepository` — Frozen Group 6)
* `backend/app/domains/messages/repository.py` (`MessageRepository` — Frozen Group 1)
* `backend/app/domains/integrations/repository.py` (`IntegrationRepository` — Frozen Group 2)

---

## 10. Explicit Exclusions

The following domains and files are **EXPLICITLY OUT OF SCOPE** and must NOT be modified during the Analytics & Reporting migration:

* **Frozen Groups 1–8**: All API routers, domain services/repositories, workers, and security test suites from Groups 1–8.
* **Product Catalog, Media & File Storage**: `backend/app/api/v1/products.py`, `backend/app/api/v1/photos.py`, `backend/app/api/v1/storage.py`, `backend/app/domains/products/*`, `backend/app/services/file_storage.py`.
* **Payments & Invoicing**: `backend/app/api/v1/payments_invoicing.py`, `backend/app/services/payment_service.py`, `backend/app/domains/billing/*`.
* **CRM Pipeline / Deals**: `backend/app/api/v1/deals.py`, `backend/app/domains/crm/*`.
* **Projects & Tenant Membership**: `backend/app/api/v1/projects.py`, `backend/app/domains/projects/*`.
* **Subscriptions & User Billing**: `backend/app/api/v1/subscriptions.py`, `backend/app/services/subscription_service.py`, `backend/app/services/usage_tracker.py`.
* **Predictive ML Analytics**: `backend/app/services/analytics/predictive.py` (standalone scikit-learn utility not wired to any API route or database session).
* **External Provider SDKs**: `backend/app/services/integrations/facebook.py`, `backend/app/services/integrations/instagram.py`, `backend/app/domains/ai/providers/gemini.py`.

---

## 11. Security Contract & Invariants

The Analytics & Reporting domain must enforce the canonical architecture:

```text
API (reports.py)
 ↓
TenantContext (Depends(get_tenant_context))
 ↓
tenant-scoped repository (ReportRepository / IntegrationRepository / OrderRepository / MessageRepository)
 ↓
domain/service (AnalyticsService / ReportGenerator)
 ↓
validated tenant resource (Report / Integration / Aggregated Metrics)
 ↓
external side effect (Meta Graph API engagement fetch / Gemini AI insights generation)
```

### Mandatory Security Invariants
1. **Zero `verify_project_access`**: Remove the local `verify_project_access` function in `reports.py` and `_verify_project_access` in `domains/analytics/service.py`. All routes in `reports.py` must depend on `context: TenantContext = Depends(get_tenant_context)`.
2. **Cross-Tenant Read Denial**: `GET /api/v1/reports/{project_id}/{report_id}` and `ReportRepository.get_by_context(report_id, context)` must enforce `WHERE Report.id == report_id AND Report.project_id == context.project_id` in SQL. Unconstrained `repo.get(report_id)` followed by Python filtering is strictly forbidden. Cross-tenant `report_id` requests must return HTTP `404`.
3. **Cross-Tenant Write Denial**: `POST /api/v1/reports/{project_id}/generate` must bind `Report.project_id = context.project_id` via `ReportRepository.create_report(..., context=context)`.
4. **Missing `TenantContext` Rejection**: Any call to `ReportRepository`, `APILogRepository`, `AnalyticsService`, or `ReportGenerator` without a valid `TenantContext` must raise `PermissionError` or `ValueError` before executing any SQL query or external call.
5. **Pre-Authorization Before External Side Effects & Credential Access**:
   * In `GET /{project_id}/dashboard-summary`, tenant authorization via `TenantContext` and tenant-scoped integration lookup via `IntegrationRepository(db, context).list_for_project(context.project_id)` must complete before any `FacebookClient` or `InstagramClient` instantiation or external HTTP call. If a caller is unauthorized for `project_id`, `0` Meta Graph API calls may occur.
   * In `POST /{project_id}/generate`, tenant authorization via `TenantContext` and tenant-scoped data aggregation must complete before `self.ai_provider.generate_response` is called. If a caller is unauthorized for `project_id`, `0` Gemini AI calls may occur.
6. **Aggregation & Reporting Isolation**: Every aggregation query (`sales`, `orders`, `customers`, `performance`, `roi`, `dashboard-summary`) must filter `Order.project_id == context.project_id`, `Message.project_id == context.project_id`, and `Integration.project_id == context.project_id` at the SQL level. Tenant A's reports and dashboard summaries must never include counts, revenue, customer PII, or social engagement from Tenant B.

---

## 12. Rule 11 Audit (`<= 250` Lines Per File)

All files in the recommended Analytics & Reporting scope were audited against Rule 11 (`<= 250` lines):

| File Path | Current Lines | Rule 11 Status | Proposed Concrete Modularization Boundary |
| :--- | :---: | :---: | :--- |
| `backend/app/api/v1/reports.py` | **465** | **VIOLATION (`>250`)** | Remove dead duplicate helper functions `_generate_sales_report`, `_generate_messages_report`, `_generate_performance_report` (`lines 288–436`, which are unused duplicates of `services/report_generator.py`) and move dashboard/summary orchestration into `domains/analytics/service.py` (or `api/v1/reports_dashboard.py`), reducing `reports.py` to `< 180` lines. |
| `backend/app/services/report_generator.py` | **548** | **VIOLATION (`>250`)** | Split into two focused modules under `<= 250` lines each:<br>1. `backend/app/services/report_generator.py` (`<= 230` lines): Core `ReportGenerator` entrypoint, `generate_sales_report`, `generate_order_report`, `generate_customer_report`, and `generate_report` dispatcher.<br>2. `backend/app/services/report_insights.py` (`<= 220` lines): `generate_performance_report`, `generate_roi_report`, `_generate_ai_insights`, and `_calculate_engagement_trend`. |
| `backend/app/domains/analytics/models.py` | 113 | PASS | Keep under 250 lines. |
| `backend/app/domains/analytics/schemas.py` | 70 | PASS | Keep under 250 lines. |
| `backend/app/domains/analytics/service.py` | 45 | PASS | Keep under 250 lines after adding `TenantContext` orchestration methods. |
| `backend/app/domains/analytics/repository.py` | 26 | PASS | Keep under 250 lines after adding `TenantContext`-scoped methods. |

---

## 13. Test-Gap Analysis

* **Current Security Test Coverage**: **0 tests** exist for `reports.py`, `services/report_generator.py`, `domains/analytics/repository.py`, or `domains/analytics/service.py`.
* **Required Security Tests for Future Implementation (`backend/tests/test_analytics_security.py`)**:
  1. `test_same_tenant_generate_and_get_report_allowed` — Tenant A can generate and retrieve a report for Project A.
  2. `test_cross_tenant_get_report_by_id_blocked` — Tenant A requesting Tenant B's `report_id` via `GET /api/v1/reports/{project_a_id}/{report_b_id}` receives `404 Not Found` via SQL-level predicate (`WHERE id = :id AND project_id = :ctx.project_id`).
  3. `test_unauthorised_project_access_blocked_on_all_report_routes` — Tenant A targeting `{project_b_id}` on `POST /generate`, `GET /`, `GET /dashboard-summary`, and `GET /{report_id}` receives `404 Not Found`.
  4. `test_cross_tenant_list_reports_isolated` — `GET /api/v1/reports/{project_a_id}` returns only Project A reports and never leaks Project B reports.
  5. `test_sales_and_order_report_aggregation_tenant_isolated` — Generating `sales`, `orders`, `customers`, `performance`, and `roi` reports for Project A aggregates only Project A's `Order`, `Message`, and `Integration` records, excluding Project B's revenue and customer PII.
  6. `test_dashboard_summary_aggregation_and_meta_side_effect_isolated` — `GET /api/v1/reports/{project_a_id}/dashboard-summary` aggregates only Project A stats and only invokes `FacebookClient` / `InstagramClient` for Project A's integrations (`0` calls with Project B's credentials).
  7. `test_unauthorized_generate_report_suppresses_ai_side_effect` — An unauthorized request to `POST /api/v1/reports/{project_b_id}/generate` fails before `ReportGenerator` or `ai_provider.generate_response` is invoked (`0` external AI calls).
  8. `test_missing_tenant_context_rejected_by_repository_and_generator` — Calling `ReportRepository`, `AnalyticsService`, or `ReportGenerator` without a valid `TenantContext` raises `PermissionError` / `ValueError`.

---

## 14. Functional-Preservation Constraints

The eventual security migration MUST NOT redesign or alter:
* **API Route Paths & HTTP Methods**: `POST /{project_id}/generate`, `GET /{project_id}`, `GET /{project_id}/dashboard-summary`, `GET /{project_id}/{report_id}`.
* **Request & Response Schemas**: `ReportGenerate`, `ReportResponse`, and the JSON payload structures for `sales`, `orders`, `customers`, `performance`, `roi`, and `dashboard-summary`.
* **Business & Aggregation Formulas**: Date-range bucketing (`last_7_days`, `last_30_days`, `custom`), ROI time/cost estimation formulas, fulfillment/cancellation rate calculations, and AI insight prompt structure.
* **Database Schema**: `Report` and `APILog` table definitions in `backend/app/domains/analytics/models.py`.

---

## 15. Frozen Group 1–8 Boundary

All files modified or created in Groups 1–8 are strictly frozen and must remain untouched:
* **Group 1 (CRM / Messages)**: `backend/app/api/v1/messages.py`, `backend/app/domains/customers/*`, `backend/app/domains/messages/*`, `backend/tests/test_tenant_security.py`.
* **Groups 2–4 (Integrations / Webhooks / OAuth)**: `backend/app/api/v1/integrations.py`, `backend/app/api/v1/webhooks.py`, `backend/app/domains/integrations/*`, `backend/app/services/webhook_*.py`, `backend/app/services/integrations/meta_oauth.py`, `backend/app/services/integrations/wa_gateway_service.py`, `backend/tests/test_webhook_security.py`, `backend/tests/test_webhook_idempotency.py`, `backend/tests/test_integration_security.py`, `backend/tests/test_oauth_db.py`, `backend/tests/test_oauth_concurrency.py`.
* **Group 5 (Background Integration Workers)**: `backend/app/workers/celery_workers.py`, `backend/tests/test_direct_service_security.py`.
* **Reconstructed Group 6 (Orders / Commerce)**: `backend/app/api/v1/orders.py`, `backend/app/api/v1/order_management.py`, `backend/app/domains/orders/*`, `backend/app/services/order_manager_service.py`, `backend/tests/test_order_security.py`, `backend/phase_2_group_6*`.
* **Reconstructed Group 7 (AI Assistant / Training)**: `backend/app/api/v1/assistant*.py`, `backend/app/api/v1/bot_training.py`, `backend/app/api/v1/enhanced_bot*.py`, `backend/app/api/v1/knowledge.py`, `backend/app/domains/ai/*`, `backend/app/workers/tasks/ai_tasks.py`, `backend/tests/test_ai_security.py`, `backend/phase_2_group_7*`.
* **Reconstructed Group 8 (Social Media / Campaigns)**: `backend/app/api/v1/social_media*.py`, `backend/app/api/v1/drip_campaigns.py`, `backend/app/domains/social/*`, `backend/app/domains/crm/repository.py`, `backend/app/domains/crm/service.py`, `backend/app/services/social_media_*.py`, `backend/app/services/drip_engine.py`, `backend/tests/test_social_security.py`, `backend/phase_2_group_8*`.

---

## 16. Final Provenance Classification

```text
NEXT-GROUP SCOPE RECOVERY COMPLETE

HISTORICAL NEXT GROUP:
NOT RECOVERABLE

RECOMMENDED RECONSTRUCTED NEXT SCOPE:
Analytics & Reporting (backend/app/api/v1/reports.py, backend/app/services/report_generator.py, backend/app/domains/analytics/)

PROVENANCE:
RECONSTRUCTED NEXT-GROUP SCOPE — NOT HISTORICALLY VERIFIED

IMPLEMENTATION STATUS:
NOT STARTED
```
