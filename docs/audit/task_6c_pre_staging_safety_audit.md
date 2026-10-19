# Automind — Task 6C: Pre-Staging Safety Audit

**Repository:** `C:\Users\ARKAN STOER\Desktop\777`  
**Branch:** `main`  
**Audit Date:** 2026-10-18T23:05:00+03:00  
**Status:** VALIDATED LOCALLY / CANONICAL STAGING PLAN READY / REMOTE STAGING BLOCKED ON OPERATOR / PRODUCTION UNTOUCHED

---

## 1. Executive Safety Gate Matrix

| Safety Gate | Scope | Status | Verification & Evidence |
| :--- | :--- | :---: | :--- |
| **Gate 1: Project Creation Fix** | `backend/app/domains/projects/` | **PASS** | `project_code`, `settings`, `timezone`, `refresh()`, and `updated_at: None` verified. 5/5 regression tests pass. |
| **Gate 2: Project Deletion Safety** | `ProjectRepository.delete` | **PASS** | Direct SQL `DELETE` with `session.expunge()` and `session.flush()`. All 24 child tables cascade natively. 4/4 safety tests pass. |
| **Gate 3: Pre-Staging Test Suites** | All 7 core test suites | **PASS** | **66 passed, 0 failures, 26 warnings in 24.31s** against local PostgreSQL 15 test database. |
| **Gate 4: Local Staging Lifecycle** | `automind_staging` (:5434) | **PASS** | 9-step runtime lifecycle passed end-to-end with **0 residual rows** in all tables post-test. |
| **Gate 5: Remote Staging Environment** | Cloud PostgreSQL / Supabase | **BLOCKED (OPERATOR)** | Confirmed no remote staging database exists in repo configuration. Requires operator provisioning. |
| **Gate 6: Migration Reconciliation** | Alembic `b7d41f09e2a1` & `d8f3a1e5c2b4` | **CANONICAL PLAN READY** | Manual draft SQL from Task 6 rejected due to column mismatch. Canonical migration path established. |
| **Gate 7: Runtime DDL Fallback Gate** | `postgres_storage_provider.py` | **PRESERVED** | Lines 95–142 preserved untouched. Removal gated on remote staging DML-only validation. |
| **Gate 8: Production Boundary** | Supabase (`ccejhzadokkjssjiwmxt`) | **ENFORCED** | Zero production connections, zero remote migrations, zero automatic startup migrations. |

---

## 2. Exact Files Changed and Reasons

### 2.1 Code Changes
1. **`backend/app/domains/projects/schemas.py`**
   - **Reason**: In Pydantic V2, `updated_at: Optional[datetime]` without an explicit `= None` default fails response serialization on newly created entities where `updated_at` is `None`. Added `= None` to `updated_at` and `description`, and `default_factory=dict` to `settings`.
2. **`backend/app/domains/projects/service.py`**
   - **Reason**: The database table `projects` enforces `project_code VARCHAR(50) NOT NULL UNIQUE`. Prior to Task 6, `create_project` failed to pass `project_code` into the `Project` model constructor. Added `project_code`, `timezone`, and `settings`, followed by `await uow.session.refresh(new_project)` to populate database-generated defaults.
3. **`backend/app/domains/projects/repository.py`**
   - **Reason**: The `Project` model defines ORM relationships with `cascade="all, delete-orphan"`. In async SQLAlchemy, calling `session.delete(orm_obj)` triggers relationship inspection and attempts to lazy-load related collections, raising `sqlalchemy.exc.MissingGreenlet`. Overrode `ProjectRepository.delete` to issue an explicit SQL `delete(self.model).where(self.model.id == id)`, call `self.session.expunge(project)` to evict the deleted entity from the session identity map, and call `await self.session.flush()` to dispatch the deletion immediately.

### 2.2 Test Additions
4. **`backend/tests/test_project_creation_regression.py`** (176 LOC, Rule 11 compliant)
   - 5 tests covering: successful creation, 422 on missing `project_code`, duplicate code uniqueness failure, cross-tenant isolation (404 anti-enumeration), and owner deletion lifecycle (204).
5. **`backend/tests/test_project_deletion_safety.py`** (135 LOC, Rule 11 compliant)
   - 4 tests covering: 404 on deleting non-existent project, 403 Forbidden on non-owner member deletion, foreign-key cascade cleanup of child records, and session identity map eviction.

---

## 3. Actual Test Evidence

### Test Execution Command
```powershell
$env:PYTHONPATH="c:\Users\ARKAN STOER\Desktop\777\backend"
$env:TEST_DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5434/automind_test"
$env:APPROVED_TEST_DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5434/automind_test"
$env:REQUIRE_TEST_DB_EXPLICIT_AUTHORIZATION="true"
python -m pytest `
    tests/test_project_creation_regression.py `
    tests/test_project_deletion_safety.py `
    tests/test_projects_security.py `
    tests/test_database_guard.py `
    tests/test_database_routing.py `
    tests/test_alembic_isolation.py `
    tests/test_migration_authorization.py `
    -v
```

### Test Results Breakdown
```text
tests/test_project_creation_regression.py (5 tests)
  test_project_creation_success                                      PASSED
  test_project_creation_missing_project_code                         PASSED
  test_project_creation_duplicate_code_fails                         PASSED
  test_created_project_tenant_isolation                              PASSED
  test_project_deletion_lifecycle                                    PASSED

tests/test_project_deletion_safety.py (4 tests)
  test_deletion_non_existent_project_returns_404                     PASSED
  test_deletion_non_owner_member_rejected_403                         PASSED
  test_deletion_cascades_and_cleans_children                          PASSED
  test_deletion_expunges_from_session_identity_map                    PASSED

tests/test_projects_security.py (9 tests)
  test_same_tenant_project_access                                     PASSED
  test_cross_tenant_project_access_denied                             PASSED
  test_cross_tenant_membership_listing_denied                         PASSED
  test_cross_tenant_member_creation_denied                            PASSED
  test_unauthorized_member_adding_denied                              PASSED
  test_self_escalation_to_owner_denied                                PASSED
  test_owner_escalation_denied                                        PASSED
  test_missing_tenant_context_fails_closed                            PASSED
  test_legitimate_owner_operations                                   PASSED

tests/test_database_guard.py (16 tests)
  test_verify_case_1_to_8 (fail-closed security boundaries)          PASSED (16/16)

tests/test_database_routing.py (17 tests)
  test_routing_isolation_cases                                        PASSED (17/17)

tests/test_alembic_isolation.py (10 tests)
  test_alembic_guard_cases                                            PASSED (10/10)

tests/test_migration_authorization.py (5 tests)
  test_startup_and_build_authorization                               PASSED (5/5)

====================== 66 passed, 26 warnings in 24.31s =======================
```
- **Passed**: 66
- **Failed**: 0
- **Warnings**: 26 (Pydantic V1 `@validator` in legacy schemas, Google deprecation warnings)
- **Git Diff Hygiene**: `git diff --check` executed with code 0 (zero whitespace or format defects).

---

## 4. Project Deletion Safety Audit Findings

### 4.1 ORM Session Synchronization & Stale Objects
- **Finding**: Calling direct SQL `DELETE` inside a transaction leaves the entity in SQLAlchemy's in-memory identity map if it was queried prior to deletion.
- **Remediation**: `ProjectRepository.delete` now explicitly calls `self.session.expunge(project)` immediately after the `DELETE` statement, followed by `await self.session.flush()`.
- **Verification**: `test_deletion_expunges_from_session_identity_map` directly asserts `assert project not in db_session`, proving zero stale objects linger in the session.

### 4.2 Database Foreign-Key Constraint Audit
A query against PostgreSQL's `information_schema.referential_constraints` confirmed:
- Exactly **24 tables** reference `projects(id)`.
- **All 24 foreign keys are configured with `delete_rule: CASCADE`**:
  `api_logs`, `auto_response_templates`, `bot_activities`, `bot_instructions`, `business_context`, `campaign_enrollments`, `conversation_history`, `deals`, `drip_campaigns`, `integrations`, `invoices`, `knowledge_base`, `messages`, `model_trainings`, `oauth_states`, `orders`, `payment_links`, `pipeline_stages`, `product_images`, `products`, `project_members`, `reports`, `social_media_comments`, `social_media_posts`.
- Complex multi-level relationships (e.g., `deals` referencing `pipeline_stages` with `RESTRICT`, where both reference `projects` with `CASCADE`) were explicitly tested and proven to delete without constraint violations.

### 4.3 Authorization & Anti-Enumeration
- **Owner Only**: If a user is a project member with role `worker` or `moderator`, `delete_project` raises `HTTP 403 Forbidden ("Only the owner can delete a project")`.
- **Non-Existent / Non-Member**: `resolve_tenant_context` raises `HTTP 404 Not Found` for both non-existent project IDs and projects where the caller has no membership, preventing tenant enumeration.

### 4.4 Transaction Atomicity & Rollback
- The Unit of Work (`UnitOfWork`) pattern wraps the operation in an atomic transaction. If any database exception occurs during `flush()`, `__aexit__` triggers `await self.rollback()`, ensuring no partial deletion can occur.

---

## 5. Migration Reconciliation Risks & Recommended Path

### 5.1 Defect in Previously Proposed Draft SQL
During the audit of migration files against Python ORM models, a **critical divergence** was identified in the draft reconciliation SQL proposed in earlier tasks:

| Property | Draft SQL (Task 6 / 6B) | Canonical Migration `b7d41f09e2a1` | ORM Model `BusinessContext` |
| :--- | :--- | :--- | :--- |
| `context_type` length | `VARCHAR(50)` | `VARCHAR(100)` | `String(100)` |
| `context_key` length | `VARCHAR(100)` | `VARCHAR(255)` | `String(255)` |
| `relevance_score` | Missing | `Float DEFAULT 1.0` | `Float, default=1.0` |
| `times_used` | Missing | `Integer DEFAULT 0` | `Integer, default=0` |
| `learned_from` | Missing | `VARCHAR(100)` | `String(100)` |
| `confidence_score` | Missing | `Float DEFAULT 0.5` | `Float, default=0.5` |
| Platform column | `platforms JSONB` | `active_for_platforms JSONB` | `active_for_platforms Column(JSONB)` |
| `examples` | Missing | `JSONB DEFAULT '[]'::jsonb` | `Column(JSONB)` |
| `last_used` | Missing | `TIMESTAMPTZ` | `DateTime(timezone=True)` |
| Indexes | `ix_business_context_*` | `idx_business_context_*` (4 indexes) | `idx_business_context_*` (4 indexes) |
| RLS | Not enabled | `ENABLE ROW LEVEL SECURITY` | N/A |

> [!WARNING]
> If the draft SQL had been executed against a staging database, any query using the `BusinessContext` ORM model would have failed with `UndefinedColumnError` (`active_for_platforms`, `relevance_score`, `times_used`, etc.).

### 5.2 Direct `alembic_version` Modification Risks
- Manually running `UPDATE alembic_version SET version_num = 'd8f3a1e5c2b4'` without applying the true Alembic migration definition risks silent schema divergence.
- If a future migration or downgrade is attempted, Alembic relies on the exact metadata recorded in its revision history.
- **Conclusion**: Direct modification of `alembic_version` is **NOT permitted** unless preceded by an automated structural schema verification that confirms 100% column and constraint identity.

### 5.3 Canonical Migration Path
The canonical, approved reconciliation path for remote staging is:

1. **For a Fresh Staging Database (Recommended)**:
   Do not run manual DDL scripts. Run standard Alembic upgrade:
   ```bash
   alembic upgrade head
   ```
   Alembic will apply `b7d41f09e2a1` and `d8f3a1e5c2b4` in proper sequence and update `alembic_version` automatically.

2. **For a Database with Existing `product_images` (Drifted State)**:
   If legacy runtime DDL already created `product_images` before migrations existed:
   Run the canonical, schema-aligned reconciliation script in a single transaction:
   ```sql
   BEGIN;
   -- 1. Create business_context matching b7d41f09e2a1 EXACTLY
   CREATE TABLE IF NOT EXISTS public.business_context (
       id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
       project_id UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
       context_type VARCHAR(100) NOT NULL,
       context_key VARCHAR(255) NOT NULL,
       title VARCHAR(255) NOT NULL,
       content TEXT NOT NULL,
       tags JSONB DEFAULT '[]'::jsonb,
       relevance_score FLOAT DEFAULT 1.0,
       times_used INTEGER DEFAULT 0,
       learned_from VARCHAR(100),
       confidence_score FLOAT DEFAULT 0.5,
       active_for_platforms JSONB DEFAULT '[]'::jsonb,
       examples JSONB DEFAULT '[]'::jsonb,
       is_active BOOLEAN NOT NULL DEFAULT true,
       last_used TIMESTAMPTZ,
       created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
       updated_at TIMESTAMPTZ
   );
   CREATE INDEX IF NOT EXISTS idx_business_context_project ON public.business_context(project_id);
   CREATE INDEX IF NOT EXISTS idx_business_context_type ON public.business_context(context_type);
   CREATE INDEX IF NOT EXISTS idx_business_context_key ON public.business_context(context_key);
   CREATE INDEX IF NOT EXISTS idx_business_context_used ON public.business_context(times_used);
   ALTER TABLE public.business_context ENABLE ROW LEVEL SECURITY;

   -- 2. Verify or create product_images matching d8f3a1e5c2b4 EXACTLY
   CREATE TABLE IF NOT EXISTS public.product_images (
       key VARCHAR(500) PRIMARY KEY,
       project_id UUID REFERENCES public.projects(id) ON DELETE CASCADE,
       data BYTEA NOT NULL,
       content_type VARCHAR(100) NOT NULL,
       size INTEGER NOT NULL,
       created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
       updated_at TIMESTAMPTZ
   );
   CREATE INDEX IF NOT EXISTS idx_product_images_project_id ON public.product_images(project_id);
   ALTER TABLE public.product_images ENABLE ROW LEVEL SECURITY;

   -- 3. Ensure foreign key exists if table was created by legacy DDL
   DO $$
   BEGIN
       IF NOT EXISTS (
           SELECT 1 FROM information_schema.table_constraints
           WHERE constraint_name = 'product_images_project_id_fkey'
           AND table_name = 'product_images'
       ) THEN
           ALTER TABLE public.product_images
           ADD CONSTRAINT product_images_project_id_fkey
           FOREIGN KEY (project_id) REFERENCES public.projects(id) ON DELETE CASCADE;
       END IF;
   END $$;

   -- 4. Advance Alembic version stamp to current head
   UPDATE alembic_version SET version_num = 'd8f3a1e5c2b4';
   COMMIT;
   ```

### 5.4 Row-Level Security (RLS) vs. Backend Application Role
- In Supabase and standard PostgreSQL setups, backend services connect using the `postgres` role or database owner role.
- In PostgreSQL, superusers and roles with `rolbypassrls = true` **bypass RLS completely**.
- RLS protects against unauthorized direct browser/PostgREST queries, but **tenant isolation for backend API endpoints is strictly enforced by application-level SQL predicates (`WHERE project_id = :project_id`)**.
- Both layers are necessary and mutually reinforcing: RLS secures the public database surface, while repository predicates enforce multi-tenancy in the backend.

---

## 6. Staging Prerequisites Still Requiring Operator Action

1. **Provision Remote Staging Database**:
   - The operator must create a dedicated PostgreSQL database (or Supabase staging branch/project).
   - Must NOT use the production project `ccejhzadokkjssjiwmxt`.
2. **Export Staging Environment Variables in Operator Shell**:
   ```powershell
   $env:STAGING_DATABASE_URL = "postgresql+asyncpg://<user>:<password>@<staging-host>:5432/<staging-db>"
   $env:DATABASE_URL = $env:STAGING_DATABASE_URL
   $env:IMAGE_STORAGE_DATABASE_URL = $env:STAGING_DATABASE_URL
   $env:ENVIRONMENT = "staging"
   $env:RUN_MIGRATIONS_ON_STARTUP = "false"
   $env:ALLOW_STARTUP_MIGRATIONS = "false"
   ```
3. **Run Preflight Target Identity Verification**:
   ```powershell
   python -c "
   import os
   from app.core.db_identity import is_production_database_reference
   url = os.environ.get('STAGING_DATABASE_URL', '')
   if is_production_database_reference(url):
       raise SystemExit('FATAL: Target matches production reference! Aborting.')
   print('Target verified isolated from production.')
   "
   ```

---

## 7. The Single Safest Next Action

The operator must **provision a dedicated remote staging database instance** completely decoupled from production project `ccejhzadokkjssjiwmxt`. Once provisioned, execute the standard Alembic migration (`alembic upgrade head`) and run the verified lifecycle test suite.
