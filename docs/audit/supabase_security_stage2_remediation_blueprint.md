# Stage 2: Production Security Remediation Blueprint (Final Safety Gate Review)

- **Document Version**: 3.0.0
- **Review Date**: 2026-10-17 19:00:00 UTC
- **Target Project Reference**: `ccejhzadokkjssjiwmxt`
- **Target Organization**: `automind`
- **Target Environment Tier**: PRODUCTION (`mainProduction`, AWS `eu-north-1`)
- **Execution Mode**: **PLANNING AND SAFETY GATE REVIEW ONLY (HARD STOP — ZERO EXECUTION)**
- **Prerequisite Verified Evidence**: `docs/audit/supabase_security_stage1_verification_evidence.md`
- **Canonical Runbook**: `docs/audit/supabase_security_stage1_runbook.md`

---

## 1. Executive Summary & Three Decoupled Security Objectives

A critical flaw in naive security remediation is treating public API hardening and multi-tenant database isolation as the same problem. They are separate security domains governed by different controls, roles, and engine mechanics.

This blueprint explicitly decouples the remediation into three distinct, non-conflated security objectives:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ OBJECTIVE A: Reduce Unauthorized Direct Access via Exposed API Roles                   │
│ Focus: Neutralize external HTTP PostgREST / GraphQL attack vectors for unauthenticated │
│ roles (anon, authenticated).                                                           │
│ Controls: Revoke discretionary grants (DAC), neutralize default ACLs, remove public    │
│ schema from PostgREST exposure, and enable RLS default-deny.                           │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │ DOES NOT ENFORCE
                                            ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ OBJECTIVE B: Enforce Multi-Tenant Isolation for Ordinary Database Roles                │
│ Focus: Ensure Tenant A cannot read or mutate Tenant B's data at the database layer.    │
│ Reality: The backend connection currently uses role 'postgres' (rolbypassrls = true).  │
│ Enabling RLS does NOT enforce tenant isolation on connections using that role.         │
│ Solution: Formulate a distinct Phase 2 migration to an unprivileged application role   │
│ (automind_app) with transaction-scoped GUCs under PgBouncer transaction pooling.       │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │ MUST PRESERVE
                                            ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ OBJECTIVE C: Preserve Legitimate Backend, Worker, Webhook, and Migration Operations    │
│ Focus: Prevent application outages, Celery worker crashes, webhook ingestion failures, │
│ and Alembic migration breakages during and after security hardening.                   │
│ Guardrail: Avoid forcing RLS on bypass roles; decouple DDL/migration credentials from  │
│ DML runtime credentials.                                                               │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### Mandatory Architectural Truth
* **Objective A does NOT achieve Objective B**: Revoking permissions from `anon`/`authenticated` and enabling RLS shuts down external PostgREST exploitation. However, because the backend connects as `postgres` (`rolbypassrls = true`), PostgreSQL completely ignores RLS policies for application queries.
* **Objective B requires Application & Role Refactoring**: Enforcing tenant isolation at the database layer requires a non-bypass role, transaction-local tenant context, and session GUC lifecycle hooks in SQLAlchemy.
* **The Interim Architecture**: In the immediate remediation phase, tenant isolation continues to be enforced **exclusively by the FastAPI application layer** (`verify_project_access` and repository filtering). Database RLS serves strictly as an engine-level perimeter firewall against non-bypass roles (`anon`, `authenticated`).

---

## 2. Evidence Baseline vs. Unproven Claims Register

To maintain strict audit integrity, every material claim in this blueprint is classified as either **Catalog-Verified Fact** (supported by Stage 1 raw evidence) or **Unverified Assumption** (marked for explicit confirmation).

### 1. Catalog-Verified Evidence

| Catalog Fact | Source Protocol | Raw Verification Result | Architectural Reality |
| :--- | :---: | :--- | :--- |
| **Server Identity** | 1A | Host `2a05:d016:...` port 5432, PG 17.6 on aarch64 AWS `eu-north-1`. | Live Production Supabase instance confirmed. |
| **Connection Role Bypass** | 1B | Active user `postgres` has `rolbypassrls = true`, `rolsuper = false`. | Backend connections using `postgres` bypass all RLS policies at engine level. |
| **Table RLS Status** | 2A | 30 tables in schema `public` have `rls_enabled = f`, `rls_forced = f`. | Engine does not evaluate row policies on any table in `public`. |
| **RLS Policies** | 2B | `pg_policies` returned `(0 rows)` for schema `public`. | Zero row-level filtering rules are defined in the database. |
| **Table Privileges** | 3A | `anon` and `authenticated` have `can_select/insert/update/delete = t` on all 30 tables. | PostgREST API roles currently have full CRUD access across all tables. |
| **Explicit Relation ACLs** | 3B | Explicit grants of `arwdDxtm` to `anon`, `authenticated`, `service_role`. | Table ACLs explicitly grant full permissions to client API roles. |
| **Default Privileges** | 3C | `postgres` and `supabase_admin` grant `arwdDxtm` to `anon`/`authenticated` by default. | Future tables created in `public` automatically inherit broad API role grants. |
| **Sequences** | 3D | `api_logs_id_seq` has `USAGE`, `SELECT`, `UPDATE` granted to `anon`/`authenticated`. | External callers can inspect and advance the sequence. |
| **GraphQL Extension** | 4A | `pg_graphql` v1.5.11 installed in schema `graphql`. | GraphQL schema reflection is installed on the database. |
| **Data API GUC** | 4B | `pgrst.db_schemas` returned empty string in connection pooler session. | GUC not populated in standard session; dashboard setting is authoritative. |
| **Public Routines** | 5 | `pg_proc` returned `(0 rows)` in schema `public`. | Zero RPC function surface; no `SECURITY DEFINER` vulnerabilities in `public`. |
| **Subscription Constraints** | 6A | `subscriptions_pkey` (PK), `subscriptions_user_id_key` (UNIQUE `user_id`). | `subscriptions(user_id)` is backed by a relational unique constraint. |
| **Subscription Indexes** | 6B | Duplicate unique B-tree indexes: `subscriptions_user_id_key` & `ix_subscription_user`. | Identical B-tree indexes; write amplification and storage waste confirmed. |
| **FK Coverage** | 7 | 41 FK constraints: 27 `EXACT_PREFIX`, 14 `CANDIDATE_UNINDEXED`. | 14 FK relationships lack covering B-tree indexes on child tables. |

### 2. Claims That Cannot Yet Be Proven From Current Evidence (Unverified Assumptions)

| Claim ID | Unproven Claim / Assumption | Why It Cannot Be Proven From Catalog Alone | Required Verification Action |
| :--- | :--- | :--- | :--- |
| **CLAIM-01** | No third-party integration (e.g. Zapier, Make, Retool, custom scripts) queries PostgREST directly. | Repository audit confirmed frontend and backend do not use PostgREST. However, external webhook configs or SaaS automations outside git cannot be seen from repository files. | **Operator Sign-Off Required**: Confirm no out-of-repo tools use `https://ccejhzadokkjssjiwmxt.supabase.co/rest/v1/*`. |
| **CLAIM-02** | The exact HTTP status code returned by PostgREST for all ungranted requests will universally be 401 or 403. | Gateway response depends on whether request has an `Authorization` header, whether anon key is valid, and PostgREST version/error-mapping configuration. Some endpoints may return 404 or empty JSON array. | **Empirical Validation Required**: Run negative tests in Stage 2E and document exact status codes. |
| **CLAIM-03** | The frontend will never require direct Supabase Realtime or Storage access. | Frontend package audit confirmed `@supabase/supabase-js` is absent; however, future roadmap requirements must be verified before permanently locking down API roles. | **Operator Sign-Off Required**: Confirm no client-side Supabase SDK usage is planned for near-term release. |
| **CLAIM-04** | All 14 candidate-unindexed foreign keys require indexes for production performance. | Protocol 7 catalog scan identifies structural prefix matching, not query execution statistics or table cardinality. Adding indexes to write-heavy tables with zero parent deletes degrades performance. | **Workload Profiling Required**: Triage by delete frequency and query patterns (Section 7). |

---

## 3. Security-Objective and Control-Boundary Matrix

The matrix below maps each database surface to its governing security objective, the exact proposed control, and an explicit statement of what the control does and does not protect.

| Database Surface | Primary Objective | Proposed Control Boundary | What the Control DOES Protect | What the Control DOES NOT Protect | Supporting Catalog Evidence |
| :--- | :---: | :--- | :--- | :--- | :--- |
| **Existing Tables (30)** | Objective A | `REVOKE ALL ON ALL TABLES IN SCHEMA public FROM anon, authenticated;` | Halts external PostgREST queries at the PostgreSQL DAC layer before RLS evaluation. | Does not enforce multi-tenant isolation for backend connections connecting as `postgres`. | Protocol 3A & 3B |
| **Default Privileges** | Objective A | `ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE ALL ...` | Prevents future tables created by Alembic from automatically granting access to `anon`/`authenticated`. | Does not alter permissions on already existing tables. | Protocol 3C |
| **Row-Level Security (MAC)** | Objective A | `ALTER TABLE public.<table_name> ENABLE ROW LEVEL SECURITY;` | Enforces engine-level default-deny on any non-bypass role (`anon`, `authenticated`, future app role). | Completely ignored by the current backend connection role (`postgres` has `rolbypassrls = true`). | Protocol 1B & 2A |
| **PostgREST HTTP Gateway** | Objective A | Remove `public` from Exposed Schemas in Supabase Dashboard. | Shuts down HTTP routing layer; PostgREST returns 404 for all `/rest/v1/*` table endpoints. | Does not change database permissions; direct SQL connections can still query tables. | Protocol 4B & Dashboard |
| **GraphQL Surface** | Objective A | Revoke table grants; unexpose `public` schema. | Prevents GraphQL schema reflection and resolver execution against public tables. | Does not drop the extension `pg_graphql` from schema `graphql`. | Protocol 4A |
| **Dedicated Sequences** | Objective A & C | `REVOKE ALL ON ALL SEQUENCES IN SCHEMA public FROM anon, authenticated;` | Prevents external callers from inspecting sequence counters or exhausting values via `nextval()`. | Does not protect table rows; must preserve `USAGE` for the backend application role. | Protocol 3D |
| **Stored Routines** | Objective A | `ALTER DEFAULT PRIVILEGES ... REVOKE ALL ON ROUTINES ...` | Ensures future database functions are not callable as PostgREST RPC endpoints (`/rpc/`) by default. | Does not affect functions in other schemas (`auth`, `storage`, `graphql`). | Protocol 5 |
| **Operational Metadata (`alembic_version`)**| Objective A & C | Revoke all from `anon`/`auth`; enable RLS with zero policies; unexpose from API. | Prevents migration state fingerprinting and unauthorized tampering with Alembic revisions. | Does not protect application tables; must remain accessible to the migration runner. | Protocol 2A & 3A |
| **Backend Connection Role** | Objective B & C | Interim: Retain `postgres`. Target (Phase 2): Migrate to `automind_app` with session GUC. | Interim preserves backend stability. Target enforces true engine-level tenant isolation. | Interim does not provide database-level tenant isolation; target requires application code changes. | Protocol 1B |

---

## 4. Table-by-Table Enforcement Matrix

The table below catalogs all 30 public tables from the Stage 1 audit, documenting current and proposed roles, RLS applicability, and the primary tenant-isolation mechanism.

| Table Name | Table Owner | Data Sensitivity & Purpose | Current Role (`postgres`) RLS Applicability | Proposed Runtime Role (`automind_app`) RLS Applicability | Primary Tenant Isolation Mechanism | Foreign-Key Relationship Path to Tenant Root (`Project` / `User`) |
| :--- | :---: | :--- | :--- | :--- | :--- | :--- |
| `alembic_version` | `postgres` | Operational Metadata | Bypassed (`rolbypassrls = true`) | Not Used (Migration role only) | Access Restricted to Migration Runner | System table; no tenant key. |
| `api_logs` | `postgres` | High (Request/Response logs) | Bypassed (`rolbypassrls = true`) | Subject to RLS (`NOBYPASSRLS`) | Application `TenantContext` + repo filter | Direct: `project_id` $\rightarrow$ `projects.id` |
| `auto_response_templates` | `postgres` | High (Bot templates) | Bypassed (`rolbypassrls = true`) | Subject to RLS (`NOBYPASSRLS`) | Application `TenantContext` + repo filter | Direct: `project_id` $\rightarrow$ `projects.id` |
| `bot_activities` | `postgres` | High (Bot action history) | Bypassed (`rolbypassrls = true`) | Subject to RLS (`NOBYPASSRLS`) | Application `TenantContext` + repo filter | Direct: `project_id` $\rightarrow$ `projects.id` |
| `bot_instructions` | `postgres` | High (Prompt instructions) | Bypassed (`rolbypassrls = true`) | Subject to RLS (`NOBYPASSRLS`) | Application `TenantContext` + repo filter | Direct: `project_id` $\rightarrow$ `projects.id` |
| `campaign_enrollments` | `postgres` | High (Drip enrollments) | Bypassed (`rolbypassrls = true`) | Subject to RLS (`NOBYPASSRLS`) | Application `TenantContext` + repo filter | Direct: `project_id` $\rightarrow$ `projects.id` |
| `conversation_history` | `postgres` | Critical (Customer chat history) | Bypassed (`rolbypassrls = true`) | Subject to RLS (`NOBYPASSRLS`) | Application `TenantContext` + repo filter | Direct: `project_id` $\rightarrow$ `projects.id` |
| `customer_profiles` | `postgres` | Critical (Customer PII/CRM) | Bypassed (`rolbypassrls = true`) | Subject to RLS (`NOBYPASSRLS`) | Application `TenantContext` + repo filter | Direct: `project_id` $\rightarrow$ `projects.id` |
| `deals` | `postgres` | High (Sales pipeline deals) | Bypassed (`rolbypassrls = true`) | Subject to RLS (`NOBYPASSRLS`) | Application `TenantContext` + repo filter | Direct: `project_id` $\rightarrow$ `projects.id` |
| `drip_campaigns` | `postgres` | High (Marketing campaigns) | Bypassed (`rolbypassrls = true`) | Subject to RLS (`NOBYPASSRLS`) | Application `TenantContext` + repo filter | Direct: `project_id` $\rightarrow$ `projects.id` |
| `drip_steps` | `postgres` | High (Campaign sequences) | Bypassed (`rolbypassrls = true`) | Subject to RLS (`NOBYPASSRLS`) | Application `TenantContext` + repo filter | Indirect: `campaign_id` $\rightarrow$ `drip_campaigns.id` |
| `integrations` | `postgres` | Critical (OAuth tokens/API keys)| Bypassed (`rolbypassrls = true`) | Subject to RLS (`NOBYPASSRLS`) | Application `TenantContext` + repo filter | Direct: `project_id` $\rightarrow$ `projects.id` |
| `invoices` | `postgres` | Critical (Billing/Invoicing) | Bypassed (`rolbypassrls = true`) | Subject to RLS (`NOBYPASSRLS`) | Application `TenantContext` + repo filter | Direct: `project_id` $\rightarrow$ `projects.id` |
| `knowledge_base` | `postgres` | High (RAG embeddings & text) | Bypassed (`rolbypassrls = true`) | Subject to RLS (`NOBYPASSRLS`) | Application `TenantContext` + repo filter | Direct: `project_id` $\rightarrow$ `projects.id` |
| `messages` | `postgres` | Critical (Customer messages) | Bypassed (`rolbypassrls = true`) | Subject to RLS (`NOBYPASSRLS`) | Application `TenantContext` + repo filter | Direct: `project_id` $\rightarrow$ `projects.id` |
| `model_trainings` | `postgres` | High (Gemini fine-tuning jobs) | Bypassed (`rolbypassrls = true`) | Subject to RLS (`NOBYPASSRLS`) | Application `TenantContext` + repo filter | Direct: `project_id` $\rightarrow$ `projects.id` |
| `oauth_states` | `postgres` | Critical (OAuth CSRF tokens) | Bypassed (`rolbypassrls = true`) | Subject to RLS (`NOBYPASSRLS`) | Application `TenantContext` + repo filter | Direct: `project_id` $\rightarrow$ `projects.id`, `user_id` $\rightarrow$ `users.id` |
| `orders` | `postgres` | Critical (E-commerce orders) | Bypassed (`rolbypassrls = true`) | Subject to RLS (`NOBYPASSRLS`) | Application `TenantContext` + repo filter | Direct: `project_id` $\rightarrow$ `projects.id` |
| `payment_links` | `postgres` | Critical (Stripe payment links)| Bypassed (`rolbypassrls = true`) | Subject to RLS (`NOBYPASSRLS`) | Application `TenantContext` + repo filter | Direct: `project_id` $\rightarrow$ `projects.id` |
| `pipeline_stages` | `postgres` | Medium (CRM stage definitions) | Bypassed (`rolbypassrls = true`) | Subject to RLS (`NOBYPASSRLS`) | Application `TenantContext` + repo filter | Direct: `project_id` $\rightarrow$ `projects.id` |
| `products` | `postgres` | High (Catalog inventory) | Bypassed (`rolbypassrls = true`) | Subject to RLS (`NOBYPASSRLS`) | Application `TenantContext` + repo filter | Direct: `project_id` $\rightarrow$ `projects.id` |
| `project_members` | `postgres` | Critical (RBAC memberships) | Bypassed (`rolbypassrls = true`) | Subject to RLS (`NOBYPASSRLS`) | Application `verify_project_access` | Direct: `project_id` $\rightarrow$ `projects.id`, `user_id` $\rightarrow$ `users.id` |
| `projects` | `postgres` | Critical (Tenant workspace root)| Bypassed (`rolbypassrls = true`) | Subject to RLS (`NOBYPASSRLS`) | Application `verify_project_access` | Root Tenant: `id` is `project_id`; `owner_id` $\rightarrow$ `users.id` |
| `refresh_tokens` | `postgres` | Critical (JWT refresh tokens) | Bypassed (`rolbypassrls = true`) | Subject to RLS (`NOBYPASSRLS`) | Application `get_current_user_id` | User-Scoped: `user_id` $\rightarrow$ `users.id` |
| `reports` | `postgres` | High (Analytics exports) | Bypassed (`rolbypassrls = true`) | Subject to RLS (`NOBYPASSRLS`) | Application `TenantContext` + repo filter | Direct: `project_id` $\rightarrow$ `projects.id` |
| `social_media_comments`| `postgres` | High (Social feed comments) | Bypassed (`rolbypassrls = true`) | Subject to RLS (`NOBYPASSRLS`) | Application `TenantContext` + repo filter | Direct: `project_id` $\rightarrow$ `projects.id` |
| `social_media_posts` | `postgres` | High (Social feed posts) | Bypassed (`rolbypassrls = true`) | Subject to RLS (`NOBYPASSRLS`) | Application `TenantContext` + repo filter | Direct: `project_id` $\rightarrow$ `projects.id` |
| `subscriptions` | `postgres` | Critical (SaaS subscription) | Bypassed (`rolbypassrls = true`) | Subject to RLS (`NOBYPASSRLS`) | Application `get_current_user_id` | User-Scoped: `user_id` $\rightarrow$ `users.id` |
| `usage_tracking` | `postgres` | High (Resource consumption) | Bypassed (`rolbypassrls = true`) | Subject to RLS (`NOBYPASSRLS`) | Application `get_current_user_id` | User-Scoped: `user_id` $\rightarrow$ `users.id` |
| `users` | `postgres` | Critical (Auth credentials/PII) | Bypassed (`rolbypassrls = true`) | Subject to RLS (`NOBYPASSRLS`) | Application `get_current_user_id` | Global user directory (`id`) |

---

## 5. Architectural Paths: Interim Model vs. Target Least-Privilege Role

To resolve the RLS-bypass reality without inducing application failure, the remediation is structured into two explicit architectural paths:

### Path 1: The Interim Production Model (Immediate Scope — Stage 2)
* **Objective**: Fulfill Objective A (eliminate external API exposure) and Objective C (zero backend disruption).
* **Architecture**:
  * External API roles (`anon`, `authenticated`, `PUBLIC`) have all permissions revoked from all 30 tables, sequences, and routines.
  * Schema `public` is removed from PostgREST Exposed Schemas in the Supabase Dashboard.
  * RLS is enabled on all 30 tables with zero policies (establishing engine-level default-deny for all non-bypass roles).
  * Backend application, Celery workers, and Alembic continue connecting as `postgres` (`rolbypassrls = true`).
* **Explicit Boundary Statement**: In Path 1, **RLS does NOT enforce tenant isolation for application queries**. Tenant isolation is enforced 100% by FastAPI authorization guards (`verify_project_access`, `get_project_member`) and repository filtering. RLS functions exclusively as a perimeter firewall blocking external non-bypass access.

### Path 2: The Target Least-Privilege Application Role (Phase 2 Architectural Track)
* **Objective**: Fulfill Objective B (engine-enforced tenant isolation).
* **Role Specification (`automind_app`)**:
  ```sql
  -- Create dedicated non-bypass application role
  CREATE ROLE automind_app WITH 
      LOGIN 
      PASSWORD 'STRONG_GENERATED_PASSWORD'
      NOSUPERUSER 
      NOCREATEDB 
      NOCREATEROLE 
      NOREPLICATION 
      NOBYPASSRLS;
  ```
* **Inheritance & Bypass Protection**:
  * `automind_app` must **NOT** inherit from `postgres` or `service_role`.
  * `automind_app` must **NOT** be granted `rolbypassrls`.
  * `automind_app` must **NOT** own tables in schema `public` (table owner is `postgres`).
* **Minimum Required Privileges**:
  * `GRANT USAGE ON SCHEMA public TO automind_app;`
  * `GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO automind_app;`
  * `GRANT USAGE, SELECT, UPDATE ON ALL SEQUENCES IN SCHEMA public TO automind_app;` (Mandatory: omitting sequence `USAGE` causes inserts on `api_logs` to fail with permission denied on `api_logs_id_seq`).
* **DDL / Migration Credential Separation**:
  * `automind_app` holds **zero DDL privileges**.
  * Alembic migrations **cannot** run as `automind_app`.
  * The production deployment pipeline must maintain two separate connection strings:
    * `MIGRATION_DATABASE_URL`: Connects as `postgres` (or dedicated migration owner) for `alembic upgrade head`.
    * `DATABASE_URL`: Connects as `automind_app` for FastAPI runtime execution.
* **Transaction-Safe Session GUC Mechanics under PgBouncer**:
  * **The Connection Pooling Constraint**: Production uses Supabase PgBouncer pooler in **Transaction Mode** (`aws-1-eu-north-1.pooler.supabase.com:5432`). In transaction mode, connection state is discarded between transactions. Standard `SET app.current_tenant_id = ...` leaks to subsequent transactions assigned to that backend connection.
  * **The Transaction-Scoped Solution**: The FastAPI SQLAlchemy session lifecycle must execute `SET LOCAL` strictly within an explicit transaction block:
    ```python
    async with AsyncSessionLocal() as session:
        async with session.begin():
            # Transaction-scoped GUC: automatically cleared on COMMIT or ROLLBACK
            await session.execute(
                text("SET LOCAL app.current_project_id = :pid"),
                {"pid": str(tenant_context.project_id)}
            )
            yield session
    ```
  * **Engine Policy Evaluation**:
    ```sql
    CREATE POLICY tenant_isolation_policy ON public.<table_name>
        FOR ALL TO automind_app
        USING (project_id = NULLIF(current_setting('app.current_project_id', true), '')::uuid)
        WITH CHECK (project_id = NULLIF(current_setting('app.current_project_id', true), '')::uuid);
    ```
  * **Fail-Closed Behavior**: If `app.current_project_id` is unset or empty, `current_setting(..., true)` returns `NULL`. The comparison `project_id = NULL` evaluates to `NULL` (falsy in SQL boolean logic). The engine rejects the query or returns zero rows.
* **Worker & Webhook Handling**:
  * Celery workers performing cross-tenant aggregation (e.g. daily usage calculation) cannot execute under a single project GUC. They require a distinct administrative task role or explicit `ServiceContext` bypass policy.

---

## 6. Privilege-Revocation Verification, Intended Behavior, and Recovery Plan

### 1. Detailed Revocation Specifications

| Target Object Group | Affected Privileges | Affected Roles | Inherited Via | Intended PostgREST / Gateway Behavior Afterward | Risk of Breaking Undocumented Consumers | Verification SQL Query |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **All 30 Public Tables** | `SELECT, INSERT, UPDATE, DELETE, TRUNCATE, REFERENCES, TRIGGER` | `anon`, `authenticated`, `PUBLIC` | Explicit `relacl` + `PUBLIC` pseudo-role | PostgREST halts query at DAC check; returns HTTP `401 Unauthorized` or `403 Forbidden` (SQLSTATE `42501`). | High if out-of-repo webhooks or BI tools connect directly to PostgREST. Low for repository code. | `SELECT has_table_privilege('anon', 'public.projects', 'SELECT');` (Expect `f`) |
| **Public Sequences** | `USAGE, SELECT, UPDATE` | `anon`, `authenticated`, `PUBLIC` | Explicit `relacl` | Direct sequence inspection/advancement via PostgREST is denied. | Low. Sequences are consumed by table inserts. | `SELECT has_sequence_privilege('anon', 'public.api_logs_id_seq', 'USAGE');` (Expect `f`) |
| **Public Routines** | `EXECUTE` | `anon`, `authenticated`, `PUBLIC` | Default routine ACLs | PostgREST RPC endpoints (`/rest/v1/rpc/*`) return 404/403. | Zero (Protocol 5 confirmed 0 routines exist in `public`). | `SELECT has_function_privilege('anon', oid, 'EXECUTE') FROM pg_proc WHERE pronamespace = 'public'::regnamespace;` (Expect 0 rows) |
| **Default Table Privileges** | Future `arwdDxtm` grants | `anon`, `authenticated` | `pg_default_acl` | Future tables created by Alembic will not inherit public permissions. | Zero. Internal migration protection. | `SELECT count(*) FROM pg_default_acl WHERE defaclnamespace = 'public'::regnamespace;` |

### 2. Recovery Authority & Atomic Rollback Script
* **Recovery Authority**: The connection role `postgres` holds table ownership and retains the authority to grant and revoke all privileges.
* **Atomic Rollback Script (Stage 2B Rollback)**:
  ```sql
  BEGIN;
  -- Restore original discretionary permissions to API roles
  GRANT ALL ON ALL TABLES IN SCHEMA public TO anon, authenticated, service_role;
  GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated, service_role;
  GRANT ALL ON ALL ROUTINES IN SCHEMA public TO anon, authenticated, service_role;

  -- Restore default privileges for future objects
  ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public 
      GRANT ALL ON TABLES TO anon, authenticated, service_role;
  ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public 
      GRANT ALL ON SEQUENCES TO anon, authenticated, service_role;
  ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public 
      GRANT ALL ON ROUTINES TO anon, authenticated, service_role;

  ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA public 
      GRANT ALL ON TABLES TO anon, authenticated, service_role;
  ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA public 
      GRANT ALL ON SEQUENCES TO anon, authenticated, service_role;
  ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA public 
      GRANT ALL ON ROUTINES TO anon, authenticated, service_role;
  COMMIT;
  ```
* **Rollback Limitation Warning**: Re-granting permissions restores previous operational state, but **it cannot restore confidentiality to any data accessed or copied while privileges were exposed**.

---

## 7. Separate Performance Optimization Plan

### 1. Subscription Index Deduplication Analysis
* **Verified Evidence from Protocol 6A & 6B**:
  * `subscriptions_user_id_key`: Backing index for relational constraint `UNIQUE (user_id)` (`contype = 'u'`). Definition: `CREATE UNIQUE INDEX subscriptions_user_id_key ON public.subscriptions USING btree (user_id)`.
  * `ix_subscription_user`: Standalone index created by Alembic migration. Definition: `CREATE UNIQUE INDEX ix_subscription_user ON public.subscriptions USING btree (user_id)`.
* **Equivalence & Constraint Preservation Verification**:
  * Both indexes are identical single-column B-tree unique indexes on column 2 (`user_id`).
  * `subscriptions_user_id_key` is strictly required to back the relational constraint `UNIQUE (user_id)`.
  * `ix_subscription_user` is redundant.
  * **Safety Proof**: Dropping `ix_subscription_user` preserves `subscriptions_user_id_key`. The SQL unique constraint remains **100% enforced** by PostgreSQL.
* **Execution SQL**:
  ```sql
  DROP INDEX CONCURRENTLY IF EXISTS public.ix_subscription_user;
  ```

### 2. Foreign-Key Indexing Triage & Scan Cost Analysis
* **PostgreSQL Engine Mechanics**: In PostgreSQL 17, parent row deletions or primary-key updates execute an internal check on child tables. Without an index on the child foreign-key column, PostgreSQL executes a **full sequential scan** of the child table.
* **Lock vs. Scan Distinction**: An unindexed foreign key causes prolonged transaction duration, high I/O, and prolonged parent row locks; it does **not** take an exclusive table lock on the child table under normal operation.
* **Triage Analysis**: Blindly indexing all 14 `CANDIDATE_UNINDEXED` foreign keys creates unnecessary write amplification on high-churn tables where parent rows are never deleted.

| Foreign Key | Child Table | FK Column | Parent Table | Parent Delete Frequency | Child Write Volume | Triage Recommendation |
| :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| `invoices_order_id_fkey` | `invoices` | `order_id` | `orders` | Low | Medium | **HIGH**: Accelerates order-invoice joins and cascade checks. |
| `deals_stage_id_fkey` | `deals` | `stage_id` | `pipeline_stages` | Moderate | High | **HIGH**: Stages can be deleted or reorganized by users. |
| `campaign_enrollments_campaign_id_fkey` | `campaign_enrollments` | `campaign_id` | `drip_campaigns` | Moderate | Medium | **HIGH**: Campaigns can be deleted, triggering enrollments scan. |
| `drip_steps_campaign_id_fkey` | `drip_steps` | `campaign_id` | `drip_campaigns` | Moderate | Low | **HIGH**: Small table; low write cost; joins are frequent. |
| `project_members_user_id_fkey` | `project_members` | `user_id` | `users` | Rare | Low | **HIGH**: Critical for user-membership lookup queries. |
| `bot_activities_customer_id_fkey` | `bot_activities` | `customer_id` | `customer_profiles` | Rare | High | **DEFER**: `bot_activities` is high-throughput; customers rarely deleted. |
| `refresh_tokens_user_id_fkey` | `refresh_tokens` | `user_id` | `users` | Rare | High | **DEFER**: High-churn table; user lookup already covered by token index. |
| `drip_campaigns_project_id_fkey` | `drip_campaigns` | `project_id` | `projects` | Rare | Low | **OPTIONAL**: Low row volume. |
| `projects_owner_id_fkey` | `projects` | `owner_id` | `users` | Rare | Low | **OPTIONAL**: Users rarely deleted. |
| `payment_links_invoice_id_fkey` | `payment_links` | `invoice_id` | `invoices` | Rare | Low | **OPTIONAL**: Low query volume. |
| `payment_links_project_id_fkey` | `payment_links` | `project_id` | `projects` | Rare | Low | **OPTIONAL**: Low query volume. |
| `oauth_states_project_id_fkey` | `oauth_states` | `project_id` | `projects` | Rare | Low | **SKIP**: Ephemeral table with TTL cleanup. |
| `oauth_states_user_id_fkey` | `oauth_states` | `user_id` | `users` | Rare | Low | **SKIP**: Ephemeral table with TTL cleanup. |
| `model_trainings_project_id_fkey` | `model_trainings` | `project_id` | `projects` | Rare | Low | **OPTIONAL**: Very low row count. |

* **Execution Guardrail**: Approved indexes must be created using `CREATE INDEX CONCURRENTLY` during low-traffic windows.

---

## 8. Revised Staged Rollout and Approval Gates

To avoid any intermediate window where data could be exposed, the rollout sequence places Discretionary Revocation (DAC) first, followed by Row-Level Security (MAC), followed by Gateway lockdown.

```
┌─────────────────────────────────────────────────────────────┐
│ Stage 2A: Pre-Flight Baseline & Verification                │
│ Preconditions: Active interactive psql session as postgres; │
│ verified read-only transaction; active app traffic healthy. │
└──────────────────────────────┬──────────────────────────────┘
                               │ GATE 1: Operator Sign-Off
┌──────────────────────────────▼──────────────────────────────┐
│ Stage 2B: Discretionary Revocation & Default ACL Hardening  │
│ Action: Atomic SQL block revoking all table/seq/routine     │
│ privileges from anon, authenticated, PUBLIC; neutralize     │
│ pg_default_acl.                                             │
└──────────────────────────────┬──────────────────────────────┘
                               │ GATE 2: Verify DAC Revocation
┌──────────────────────────────▼──────────────────────────────┐
│ Stage 2C: Row-Level Security Enablement on 30 Tables        │
│ Action: Atomic SQL block executing ALTER TABLE ... ENABLE   │
│ ROW LEVEL SECURITY on all 30 public tables.                 │
└──────────────────────────────┬──────────────────────────────┘
                               │ GATE 3: Verify RLS Status
┌──────────────────────────────▼──────────────────────────────┐
│ Stage 2D: PostgREST Exposed Schema Restriction              │
│ Action: Remove 'public' from PostgREST Exposed Schemas in   │
│ Supabase Dashboard Project Settings.                        │
└──────────────────────────────┬──────────────────────────────┘
                               │ GATE 4: Verify HTTP 404
┌──────────────────────────────▼──────────────────────────────┐
│ Stage 2E: Post-Hardening Verification & Regression Tests    │
│ Action: Run negative external PostgREST tests and positive  │
│ FastAPI backend health and tenant-isolation tests.          │
└──────────────────────────────┬──────────────────────────────┘
                               │ GATE 5: Verify App Health
┌──────────────────────────────▼──────────────────────────────┐
│ Stage 2F: Separate Performance Phase (Lower Priority)       │
│ Action: DROP INDEX CONCURRENTLY ix_subscription_user;       │
│ Create prioritized foreign-key indexes concurrently.        │
└─────────────────────────────────────────────────────────────┘
```

---

## 9. Security Regression Test Plan

### 1. Negative Security Tests (External PostgREST & Gateway Verification)
Executed using curl or PostgREST client with the public `anon` API key:

| Test ID | Target Endpoint | HTTP Method | Expected Status | Security Assertion |
| :--- | :--- | :---: | :---: | :--- |
| **TEST-NEG-01** | `/rest/v1/users?select=*` | GET | `401 / 403 / 404` | User credentials and password hashes cannot be read by public clients. |
| **TEST-NEG-02** | `/rest/v1/projects?select=*` | GET | `401 / 403 / 404` | Tenant workspace projects cannot be enumerated. |
| **TEST-NEG-03** | `/rest/v1/messages?select=*` | GET | `401 / 403 / 404` | Customer communications cannot be exfiltrated. |
| **TEST-NEG-04** | `/rest/v1/orders` | POST | `401 / 403 / 404` | External actors cannot inject unauthorized order records. |
| **TEST-NEG-05** | `/rest/v1/invoices?id=gt.0` | DELETE | `401 / 403 / 404` | External actors cannot delete billing records. |
| **TEST-NEG-06** | `/rest/v1/alembic_version?select=*` | GET | `401 / 403 / 404` | Migration version metadata is completely shielded from fingerprinting. |
| **TEST-NEG-07** | `/graphql/v1` (Query `{ users { id } }`)| POST | `401 / 403 / 404` | GraphQL schema resolver cannot query public table relations. |

### 2. Positive Security Tests (FastAPI Backend & Application Health)
Executed against the production FastAPI backend (`https://ai-sales-bot-api-production-412b.up.railway.app`):

| Test ID | Test Description | Execution Target | Expected Result |
| :--- | :--- | :--- | :--- |
| **TEST-POS-01** | User Authentication | `POST /api/v1/auth/login` | Returns `200 OK` with valid custom HS256 access token. |
| **TEST-POS-02** | Authorized Workspace Listing | `GET /api/v1/projects/` | Returns `200 OK` listing only projects owned by or shared with caller. |
| **TEST-POS-03** | Cross-Tenant Read Rejection | `GET /api/v1/projects/{unauthorized_id}/messages` | Returns `404 Not Found` or `403 Forbidden` (`verify_project_access` denies). |
| **TEST-POS-04** | Cross-Tenant Mutation Rejection | `POST /api/v1/projects/{unauthorized_id}/orders` | Returns `404 Not Found` or `403 Forbidden`. |
| **TEST-POS-05** | Background Worker Execution | Celery background task execution | Tasks complete successfully with `200 OK` in worker logs. |
| **TEST-POS-06** | Webhook Processing | Signed webhook payload (Stripe/Shopify) | Returns `200 OK`; order/message record inserted with correct `project_id`. |
| **TEST-POS-07** | Database Migration Readiness | Offline migration validation | `alembic current` executes cleanly as `postgres`. |

---

## 10. Explicit Approval Checklist

Before advancing to Stage 3 or executing any remediation steps, the operator must explicitly review and sign off on each checkpoint below:

- [ ] **Sign-Off 1: Objective Decoupling**: Acknowledged that Stage 2 hardening achieves Objective A (external API exposure reduction), while Objective B (engine-enforced tenant isolation) remains governed by the FastAPI application layer until Phase 2 role migration.
- [ ] **Sign-Off 2: Discretionary Revocations (Stage 2B)**: Approved executing `REVOKE ALL PRIVILEGES ON ALL TABLES, SEQUENCES, ROUTINES IN SCHEMA public FROM anon, authenticated, PUBLIC;` and neutralizing `pg_default_acl`.
- [ ] **Sign-Off 3: Row-Level Security Enablement (Stage 2C)**: Approved executing `ALTER TABLE public.<table_name> ENABLE ROW LEVEL SECURITY;` across all 30 public tables.
- [ ] **Sign-Off 4: External Consumer Verification**: Confirmed that no out-of-repo webhooks, Zapier/Make automations, or BI tools depend on direct Supabase PostgREST access.
- [ ] **Sign-Off 5: Rollout Order**: Approved the rollout sequence (DAC first, MAC second, Gateway third).
- [ ] **Sign-Off 6: Performance Deduplication**: Approved dropping `ix_subscription_user CONCURRENTLY` in the separate performance phase.

---

### Final Safety Gate Status: REVIEW COMPLETE & READY FOR OPERATOR SIGN-OFF

**HARD STOP ENFORCED**: No production database connections were opened, no queries were executed, no database mutations or permission alterations occurred, and no application files were edited. Execution remains strictly halted awaiting operator sign-off.
