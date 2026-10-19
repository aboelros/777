# Stage 2: Production Security Remediation Proposed Execution Packet

- **Document Version**: 3.1.0 (Forensic Corrections, Micro-Batching & Production Safety Gate Revision)
- **Revision Date**: 2026-10-17 23:00:00 UTC
- **Target Project Reference**: `ccejhzadokkjssjiwmxt`
- **Target Organization**: `automind`
- **Target Environment Tier**: PRODUCTION (`mainProduction`, AWS `eu-north-1`)
- **Execution Status**: **PROPOSED EXECUTION PLAN ONLY — STRICT HARD STOP — NOT EXECUTED**
- **Baseline Evidence**: `docs/audit/supabase_security_stage1_verification_evidence.md`
- **Reference Blueprint**: `docs/audit/supabase_security_stage2_remediation_blueprint.md` (v3.0.0)

---

## 1. Safety Notice & HARD STOP Enforcement

> [!CAUTION]
> **STRICT HARD STOP: NO EXECUTION PERMITTED**
> This document is a formal, reviewable, hardened execution packet. It is **NOT** an executable script.
> - **NO** production database connections have been established for mutation.
> - **NO** SQL commands, DDL statements, grants, or revocations have been executed.
> - **NO** application code, models, or migrations have been edited or run.
> - **NO** project settings, API configurations, or credentials have been altered.
> Execution of any stage, sub-group, or micro-batch requires separate, explicit human operator sign-off at each defined gate. Automatic progression between sub-groups or micro-batches is strictly prohibited.

---

## 2. Review of Blueprint Version 3.0.0 & Technical Corrections (DEF-01 to DEF-05)

A comprehensive technical review of [`docs/audit/supabase_security_stage2_remediation_blueprint.md`](file:///c:/Users/ARKAN%20STOER/Desktop/777/docs/audit/supabase_security_stage2_remediation_blueprint.md) against the verified catalog evidence in [`docs/audit/supabase_security_stage1_verification_evidence.md`](file:///c:/Users/ARKAN%20STOER/Desktop/777/docs/audit/supabase_security_stage1_verification_evidence.md) and the findings of the v3.0.0 Forensic Audit establishes the following critical technical corrections implemented in this Version 3.1.0 release:

### 1. Contradictions Identified & Resolved
* **Single Massive Transaction vs. Production Concurrency**:
  * *Blueprint Contradiction*: Blueprint Sections 8, 2B, and 2C prescribed executing `REVOKE` and `ALTER TABLE ... ENABLE ROW LEVEL SECURITY` across all 30 tables in single "atomic SQL blocks".
  * *Engine Reality*: Both `REVOKE` (which updates `pg_class.relacl`) and `ENABLE ROW LEVEL SECURITY` acquire an `ACCESS EXCLUSIVE` lock on each table. Bundling all 30 tables into a single transaction queues behind any active read or write on any of the 30 tables. In a live production system, this lock-queuing stalls all incoming backend queries across all domains, exhausting the PgBouncer pool and causing HTTP 504 Gateway Timeouts.
  * *Resolution*: Decomposed execution into **dependency-isolated sub-groups and micro-batches** containing $\le 3$ tables per transaction, executed with strict `lock_timeout = '2s'` and `statement_timeout = '4s'`.

### 2. Missing Preconditions & Safeguards Resolved
* **Lock Timeout Mechanics**: Mandated transaction-scoped `SET LOCAL lock_timeout = '2s'`. In PostgreSQL 17, `lock_timeout` limits the duration a statement will wait to acquire a lock. It protects against lock-queuing storms but does **not** prevent lock contention or deadlocks, nor does it guarantee statement success.
* **Wildcard / Bulk Syntax Risk**: Eliminated all bulk wildcard syntax (`ALL TABLES IN SCHEMA public`). Every single table (30) and sequence (1) is explicitly enumerated.
* **Pre-Execution Backup & PITR Timestamp**: Mandated recording an active Point-in-Time Recovery (PITR) timestamp before initiating any DDL.
* **Default Privileges Authority**: Identified that altering default privileges for `supabase_admin` requires role membership, which is unverified in catalog evidence.

### 3. Unsafe Assumptions Corrected
* **Tenant Isolation Reality**: Enabling RLS must **never** be claimed as achieving multi-tenant isolation for the backend. Because the FastAPI backend connects as `postgres` (`rolbypassrls = true`), PostgreSQL completely ignores RLS policies for backend queries. RLS in this remediation phase acts purely as an engine-level perimeter block against non-bypass roles (`anon`, `authenticated`).
* **Non-Uniform HTTP Status Codes**: Rejected blanket `401/403/404` status assertions. Status codes are explicitly labeled as unverified environmental assumptions until empirically measured. Post-Stage 2/4 is assumed to yield `401/403` (DAC/RLS denial from database), while Post-Stage 5 is assumed to yield `404` (gateway schema unexposure).
* **GraphQL Separation**: Clarified that removing `public` from PostgREST Exposed Schemas does not inherently disable or alter the `pg_graphql` resolver running in schema `graphql`.

### 4. Detailed Resolutions for Forensic Audit Defects (DEF-01 through DEF-05)

| Defect ID | Severity | Root Cause Identified in v3.0.0 Audit | Technical Correction Implemented in v3.1.0 |
| :--- | :--- | :--- | :--- |
| **DEF-01 & DEF-05** | **CRITICAL** | **Cumulative Lock Accumulation & Multi-Statement Timeouts in Groups 4 & 5**: Previous execution plan grouped 9 tables into single transactions in Group 4 (CRM) and Group 5 (Automation). Because `AccessExclusiveLock` is held cumulatively until transaction termination, locks held on earlier tables persisted while later tables were processed. Furthermore, `statement_timeout` only bounds individual queries, NOT the cumulative duration of the 9-statement transaction, creating an unbounded lock-holding window under concurrent production traffic. | **Decomposed into 6 Micro-Batches ($\le 3$ tables per transaction)**: Group 4 is partitioned into 4A, 4B, 4C; Group 5 is partitioned into 5A, 5B, 5C. Each micro-batch has independent `BEGIN`/`COMMIT`, `SET LOCAL lock_timeout = '2s'`, `SET LOCAL statement_timeout = '4s'`, and evaluated PostgreSQL 17 `SET LOCAL transaction_timeout = '6s'`. Each micro-batch has a dedicated post-commit verification query and an independent, symmetric rollback block. |
| **DEF-02** | **HIGH** | **Future-Table RLS Blindspot & Scope Confusion**: `ALTER DEFAULT PRIVILEGES` only governs Discretionary Access Control (`relacl`). It has zero mechanism or syntax to enable Row-Level Security (`relrowsecurity`) on future tables created by migrations. Relying solely on `ALTER DEFAULT PRIVILEGES` leaves newly created tables with RLS disabled. | **Architectural Migration Policy Mandate**: Explicitly documented this PostgreSQL engine limitation. Established a mandatory architectural migration policy requiring all future Alembic migrations creating tables to explicitly include `op.execute("ALTER TABLE <name> ENABLE ROW LEVEL SECURITY;")`, categorizing new tables into tenant-aware, default-deny, internal, or justified-exempt. |
| **DEF-03** | **MEDIUM** | **GraphQL Introspection Exposure Misstatement**: Prior audit asserted that GraphQL `__schema` and `__type` introspection is unconditionally exposed and leaks metadata after DAC revocation. Under official `pg_graphql` documentation, introspection is disabled by default for non-service roles. | **Corrected Introspection Architecture & Preflight Gate**: Clarified that data access denial (via DAC/RLS) is decoupled from schema introspection. Documented that `pg_graphql` disables `__schema` by default unless explicitly configured. Added a dedicated preflight verification gate to empirically inspect live GraphQL endpoint behavior. |
| **DEF-04** | **HIGH** | **PostgREST Configuration Reload Failure over PgBouncer**: `NOTIFY pgrst, 'reload config'` was prescribed over pooler port 5432. In PgBouncer transaction pooling mode (or port 6543), `LISTEN`/`NOTIFY` is not supported, meaning notifications cannot reliably reach the PostgREST daemon. | **Dual-Method Reload Procedure & Container Fallback**: Identified connection mode prerequisites. Documented Method 1 (Supabase Dashboard API Settings save / container reload) and Method 2 (Direct session-mode connection over port 5432). Added post-reload verification probe and service restart fallback via Dashboard. |

---

## 3. Separation of Independent Security Controls & Future-Table Policy

To ensure zero architectural ambiguity, the four core security controls are decoupled and defined independently:

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│ CONTROL A: Remove Direct External API Exposure                                                  │
│ • Target: External PostgREST HTTP endpoints (/rest/v1/*) & GraphQL (/graphql/v1)                │
│ • Mechanisms: Dashboard Exposed Schema restriction + PostgREST DAC revocation                  │
│ • What it Protects: Stops external unauthenticated or anon-key HTTP requests from reaching db  │
│ • What it Does NOT Protect: Does not isolate tenants from each other within backend queries     │
└────────────────────────────────────────────────┬────────────────────────────────────────────────┘
                                                 │ INDEPENDENT
                                                 ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│ CONTROL B: Least-Privilege Database Grants (DAC Hardening)                                      │
│ • Target: PostgreSQL Relation & Sequence Access Control Lists (relacl)                          │
│ • Mechanisms: Explicit REVOKE on existing objects + ALTER DEFAULT PRIVILEGES neutralization     │
│ • What it Protects: Strips anon and authenticated roles of table-level SQL permissions          │
│ • What it Does NOT Protect: Does not restrict the backend connection role (postgres)            │
└────────────────────────────────────────────────┬────────────────────────────────────────────────┘
                                                 │ INDEPENDENT
                                                 ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│ CONTROL C: Tenant Isolation for Non-Bypass Roles (MAC / RLS)                                    │
│ • Target: PostgreSQL Row-Level Security Engine                                                  │
│ • Mechanisms: ALTER TABLE ... ENABLE ROW LEVEL SECURITY (Default Deny)                          │
│ • Reality: Backend connects as postgres (rolbypassrls = true) -> RLS is BYPASSED for backend   │
│ • What it Protects: Second-layer engine firewall if an unprivileged role ever gains DAC grants │
│ • What it Does NOT Protect: DOES NOT ENFORCE TENANT ISOLATION FOR CURRENT BACKEND QUERIES       │
│ • Requirement for True Tenant Isolation: Phase 2 unprivileged role (automind_app) migration    │
└────────────────────────────────────────────────┬────────────────────────────────────────────────┘
                                                 │ INDEPENDENT
                                                 ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│ CONTROL D: Operational Continuity Preservation                                                  │
│ • Target: FastAPI application, Celery workers, webhooks, and Alembic migrations                 │
│ • Mechanisms: Retain postgres bypass role during interim; zero disruption to DDL / DML         │
│ • Safeguards: Explicit isolation of alembic_version; strict exclusion of performance DDL        │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Mandatory Architectural Migration Policy for Future Tables

Because PostgreSQL `ALTER DEFAULT PRIVILEGES` does not and cannot enable Row-Level Security on newly created tables, the following policy is binding on all future Alembic migrations:

1. **Mandatory Security Configuration in Migration**: Every Alembic migration script that creates a table via `op.create_table(...)` must include an explicit security directive in the same migration file.
2. **Table Security Classification**:
   * **Category 1: Tenant-Isolated Tables**: Tables storing tenant-specific business data must execute `op.execute("ALTER TABLE <name> ENABLE ROW LEVEL SECURITY;")` and, upon transition to non-bypass application roles (Phase 2), declare tenant-filtering RLS policies (`CREATE POLICY ... USING (project_id = current_setting(...))`).
   * **Category 2: Default-Deny Application Tables**: Tables not immediately equipped with custom RLS policies must execute `op.execute("ALTER TABLE <name> ENABLE ROW LEVEL SECURITY;")`. With zero policies defined, PostgreSQL enforces an engine-level default-deny posture against all non-bypass roles.
   * **Category 3: Internal System & Metadata Tables**: Tables reserved for operational tooling, caching, or migration metadata must enable RLS and remain strictly unexposed to PostgREST or external API roles.
   * **Category 4: Justified RLS-Exempt Tables**: If RLS is intentionally omitted (e.g., public static reference catalogs), the migration author must document the explicit security rationale in a top-level docstring in the migration file and secure Lead DBA approval.
3. **Automated Migration Review / Linter Safeguard**: An automated test or CI check must inspect all new migration files in `backend/alembic/versions/` to verify that every `op.create_table` call is accompanied by an `ENABLE ROW LEVEL SECURITY` statement.

---

## 4. Preflight Prerequisites, Safety Gates & Partial-Rollout Runbook

### 1. Required Preflight Authorizations & Confirmations

Prior to executing any operational step, the following five preflight gates must be evaluated:

| Gate | Focus Area | Verification Criteria & Required Artifacts | Current Gate Status |
| :---: | :--- | :--- | :---: |
| **Gate A** | **Database Role Authority** | Read-only catalog confirmation that session user has authority to alter target objects and default privileges, and verification of `rolsuper`, `rolbypassrls`, and `supabase_admin` membership. | **BLOCKED — LIVE EVIDENCE REQUIRED** |
| **Gate B** | **External API Consumers** | Written sign-off from Product, Engineering, and Operations leads confirming zero out-of-repo webhooks, BI platforms, or client apps query `/rest/v1/*` or `/graphql/v1`. | **BLOCKED — LIVE EVIDENCE REQUIRED** |
| **Gate C** | **Baseline HTTP Behavior** | Empirical read-only HTTP probes of `/rest/v1/` and `/graphql/v1` capturing status codes, response headers, and response bodies prior to changes. | **BLOCKED — LIVE EVIDENCE REQUIRED** |
| **Gate D** | **Recovery Readiness** | Verification of active Point-in-Time Recovery (PITR), latest verified backup timestamp, designated recovery DBA, and documented restore procedure. | **BLOCKED — LIVE EVIDENCE REQUIRED** |
| **Gate E** | **Execution & Rollback Readiness**| Syntactic validation of SQL, micro-batch transaction boundaries, lock parameters, post-commit checks, and matching symmetric rollbacks. | **VERIFIED (Documentation Complete)** |

### 2. Standardized Abort Conditions & Lock Mechanics

To prevent operational outages, all database transactions must adhere to strict concurrency limits:

* **Lock Contention vs. Lock Timeout vs. Statement Timeout vs. Transaction Timeout**:
  * `ACCESS EXCLUSIVE` lock conflicts with all other lock modes (including concurrent `SELECT`, `INSERT`, `UPDATE`, `DELETE`).
  * `lock_timeout = '2s'` limits how long a statement will **wait** to acquire a lock. If any table is blocked by an active query, PostgreSQL cancels the waiting statement after 2 seconds with SQLSTATE `55P03` (`lock_not_available`), preventing unbounded query queues in PgBouncer.
  * `statement_timeout = '4s'` applies to **each individual statement** in the transaction. It does not bound the cumulative execution time of a multi-statement transaction.
  * In PostgreSQL 17, `transaction_timeout = '6s'` limits the **total elapsed duration** of the entire transaction from `BEGIN` to `COMMIT`. On PostgreSQL 15/16 instances, this parameter does not exist and will raise an error if set; it is therefore evaluated conditionally based on Gate A server version verification.
  * **Lock Accumulation Rule**: In PostgreSQL, all locks acquired by any statement within a transaction are held until the transaction ends (`COMMIT` or `ROLLBACK`). Bundling fewer tables ($\le 3$) per transaction bounds the time locks are accumulated, drastically reducing concurrent blocking.
* **Immediate Halt Criteria**:
  If any of the following events occur during any micro-batch, the operator must immediately halt:
  - Statement cancelled due to lock timeout (`55P03`).
  - Statement cancelled due to statement timeout or transaction timeout.
  - FastAPI application 5xx error rate rises above 0.0% in Railway metrics.
  - Celery background workers throw database connection or permission errors.
  - Role `postgres` or `service_role` loses unexpected privileges.

### 3. Partial-Rollout Failure Runbook (Step-by-Step Procedure)

If an error, lock timeout (`55P03`), or operational anomaly occurs during any micro-batch execution (e.g., Micro-Batch 2.4B aborts):

1. **STOP IMMEDIATELY**: Do not proceed to subsequent micro-batches. Automatic cascade is strictly prohibited.
2. **CAPTURE FAILURE METADATA**: Record exact error text, timestamp (UTC), and SQLSTATE code in the incident log.
3. **UNDERSTAND TRANSACTION ISOLATION**:
   * The failed micro-batch transaction was aborted and automatically rolled back by PostgreSQL. Its target tables remain in their pre-transaction state.
   * **Persistence of Committed Work**: Earlier successfully committed micro-batches **remain committed**. They do not automatically revert when a later independent transaction fails.
4. **ESTABLISH ACTUAL CURRENT STATE (READ-ONLY CATALOG AUDIT)**:
   Do not guess. Execute the read-only catalog discovery query across all 30 public tables:
   ```sql
   -- Proposed Diagnostic Query (Read-Only)
   SELECT 
       c.relname AS table_name,
       c.relrowsecurity AS rls_enabled,
       has_table_privilege('anon', c.oid, 'SELECT') AS anon_can_select,
       has_table_privilege('authenticated', c.oid, 'SELECT') AS auth_can_select
   FROM pg_class c
   JOIN pg_namespace n ON n.oid = c.relnamespace
   WHERE n.nspname = 'public' AND c.relkind = 'r'
   ORDER BY c.relname;
   ```
5. **DETERMINE EXACT SYSTEM BOUNDARY**:
   * Completed micro-batches: Privileges revoked / RLS enabled.
   * Failed micro-batch: Unchanged (transaction aborted).
   * Untouched micro-batches: Unchanged (pre-execution baseline).
6. **PROHIBITION OF BLIND ROLLBACK**: Do not execute a global rollback script or blindly re-run the failed micro-batch.
7. **HUMAN DECISION GATE**:
   * Escalate findings to Lead DBA and Incident Commander.
   * **Option A (Retry)**: If the failure was purely a lock timeout (`55P03`) and application traffic is stable, retry the failed micro-batch during a verified quieter window with identical timeouts.
   * **Option B (Selective Rollback)**: If an operational regression or unintended breakage is detected, roll back only the completed micro-batches in **reverse dependency order** (e.g., 2.4A, then 2.3, then 2.2, then 2.1).
8. **ROLLBACK CONTENTION WARNING**:
   * Rollback scripts execute `GRANT` or `ALTER TABLE ... DISABLE ROW LEVEL SECURITY` with `SET LOCAL lock_timeout = '2s'`.
   * **Rollback is NOT guaranteed to succeed instantly**: If concurrent lock contention persists, the rollback statement will also hit lock timeout (`55P03`) and cancel.
   * If rollback cancels due to lock contention, the operator must inspect active blocking processes via `pg_blocking_pids()` or temporarily throttle incoming traffic before re-attempting rollback.
9. **ESCALATION & RECOVERY LIMITATION**:
   * If automated recovery cannot be completed within 5 minutes, maintain the hard stop and escalate to the Lead DBA.
   * **Irreversible Limitation**: Rollback restores previous configuration, but **cannot reverse historical data exfiltration or disclosure** that occurred during the exposure window.

---

## 5. Reviewable Table Groups (Dependency-Aware Partitioning & Micro-Batches)

The 30 public tables and 1 sequence are partitioned into reviewable sub-groups and decomposed into micro-batches of $\le 3$ tables per transaction to eliminate lock accumulation hazards:

| Group / Micro-Batch | Category | Target Objects Included | Table Count | Concurrency Characteristics & Rationale |
| :---: | :--- | :--- | :---: | :--- |
| **G1** | **Operational Metadata** | `alembic_version` | 1 | Zero runtime application traffic. Used exclusively by Alembic migration runner. Zero lock contention risk. |
| **G2** | **Identity & Global Auth** | `users`, `refresh_tokens`, `subscriptions` | 3 | Core user identity and authentication tables. Scoped to individual users. High query frequency, low batch lock duration. |
| **G3** | **Workspace Tenancy Root** | `projects`, `project_members` | 2 | Tenancy anchor for the entire system. Looked up on nearly every tenant request. Low row count; requires fast lock acquisition. |
| **G4A** | **CRM Core** | `customer_profiles`, `deals`, `pipeline_stages` | 3 | Core sales pipeline and CRM entities. Moderate transaction volume. |
| **G4B** | **Commerce & Billing** | `orders`, `invoices`, `payment_links` | 3 | Financial and checkout transactions. High integrity requirements; decoupled from CRM stages. |
| **G4C** | **Product & Knowledge** | `products`, `knowledge_base`, `integrations` | 3 | Catalog, support context, and external credentials. Predominantly read-heavy. |
| **G5A** | **Marketing Automation** | `drip_campaigns`, `drip_steps`, `campaign_enrollments` | 3 | Asynchronous campaign and drip workflow tables. Worker-driven updates. |
| **G5B** | **AI Agent Configuration** | `auto_response_templates`, `bot_instructions`, `model_trainings` | 3 | AI bot behavioral configuration and training metadata. Infrequent writes. |
| **G5C** | **Analytics & Operations**| `reports`, `oauth_states`, `usage_tracking` | 3 | System reporting, OAuth handshakes, and resource telemetry. Asynchronous writes. |
| **G6** | **High-Throughput Streaming**| `api_logs`, `messages`, `conversation_history`, `bot_activities`, `social_media_comments`, `social_media_posts`, `api_logs_id_seq` | 6 + 1 seq | **Highest write concurrency**. Live customer chat and social feeds. Greatest lock-queuing hazard; requires mandatory low-traffic maintenance window. |

---

## 6. Proposed Execution Packet (Step-by-Step Plans)

### Stage 1: Pre-Execution Environment & Baseline Verification

* **Objective**: Confirm administrative session continuity, verify read-only safety, capture active session configuration, and evaluate server version capabilities before applying changes.
* **Exact Affected Objects & Roles**: Session environment; role `postgres`.
* **Preconditions**: Interactive `psql` session open to Supabase pooler as `postgres`.
* **Proposed SQL (NOT EXECUTED)**:
  ```sql
  -- PROPOSED SQL (NOT EXECUTED)
  -- Step 1.1: Verify session user, server version, and connection identity
  SELECT 
      current_database(), 
      current_user, 
      session_user, 
      inet_server_addr(), 
      server_version(),
      current_setting('server_version_num')::integer AS server_version_num;

  -- Step 1.2: Verify role attributes and bypassrls capability of active user
  SELECT 
      rolname, 
      rolsuper, 
      rolbypassrls, 
      rolcanlogin 
  FROM pg_roles 
  WHERE rolname = current_user;
  ```
* **Expected Effect**: Confirms active user is `postgres` with `rolbypassrls = true`. Verifies whether `server_version_num >= 170000` to determine if `transaction_timeout` is supported.
* **Potential Breakage**: None (read-only queries).
* **Verification Query**: Returned values match Protocol 1 baseline in evidence artifact.
* **Rollback Procedure**: Not applicable.
* **Required Approval Gate**: **GATE 1: Preflight Environment Verification**.

---

### Stage 2: Discretionary Access Control (DAC) Revocations

* **Objective**: Fulfill **Control B** and begin **Control A** by stripping `anon`, `authenticated`, and `PUBLIC` of all discretionary permissions on all 30 existing public tables and the 1 public sequence.
* **Safety Protocol**:
  - Every batch executes within an explicit transaction setting:
    ```sql
    SET LOCAL lock_timeout = '2s';
    SET LOCAL statement_timeout = '4s';
    -- If PostgreSQL 17+: SET LOCAL transaction_timeout = '6s';
    ```
  - Zero wildcards (`ALL TABLES`) used. Every table is explicitly enumerated.
  - Roles `service_role` and `postgres` are **NOT** revoked, preserving internal dashboard and administrative functions.
  - **No Automatic Progression**: Each micro-batch must be verified and approved by the operator before the next micro-batch begins.
  - **Comprehensive 8-Privilege Verification Standard**: Citations: [PostgreSQL 17 System Information Functions (`has_table_privilege`, `has_sequence_privilege`)](https://www.postgresql.org/docs/17/functions-info.html#FUNCTIONS-INFO-ACCESS-TABLE). Every table is verified across `anon`, `authenticated`, and `PUBLIC` for all 8 supported table privileges: `SELECT`, `INSERT`, `UPDATE`, `DELETE`, `TRUNCATE`, `REFERENCES`, `TRIGGER`, and `MAINTAIN`.

#### Stage 2.1: Group 1 Revocation (Operational Metadata)
* **Exact Affected Objects**: Table `public.alembic_version`.
* **Affected Roles**: `anon`, `authenticated`, `PUBLIC`.
* **Preconditions**: Gate 1 passed.
* **Proposed SQL (NOT EXECUTED)**:
  ```sql
  BEGIN;
  SET LOCAL lock_timeout = '2s';
  SET LOCAL statement_timeout = '4s';

  REVOKE ALL ON TABLE public.alembic_version FROM anon, authenticated, PUBLIC;

  COMMIT;
  ```
* **Comprehensive Verification Query (Post-Execution Check)**:
  ```sql
  SELECT 
      t.table_name,
      r.role_name,
      p.privilege_name,
      has_table_privilege(r.role_name, 'public.' || t.table_name, p.privilege_name) AS has_privilege
  FROM (VALUES ('alembic_version')) AS t(table_name)
  CROSS JOIN (VALUES ('anon'), ('authenticated'), ('public')) AS r(role_name)
  CROSS JOIN (VALUES ('SELECT'), ('INSERT'), ('UPDATE'), ('DELETE'), ('TRUNCATE'), ('REFERENCES'), ('TRIGGER'), ('MAINTAIN')) AS p(privilege_name)
  WHERE has_table_privilege(r.role_name, 'public.' || t.table_name, p.privilege_name) = true;
  -- Expected Result: Exactly 0 rows.
  ```
* **Abort Condition**: Statement cancellation due to lock timeout (`55P03`) or permission error.
* **System State on Failure**: Transaction rolls back cleanly; `alembic_version` retains original grants.
* **Rollback SQL (NOT EXECUTED)**:
  ```sql
  BEGIN;
  SET LOCAL lock_timeout = '2s';
  SET LOCAL statement_timeout = '4s';
  GRANT ALL ON TABLE public.alembic_version TO anon, authenticated;
  COMMIT;
  ```
* **Required Approval Gate**: **GATE 2.1: Group 1 DAC Revocation Sign-Off**.

#### Stage 2.2: Group 2 Revocation (Identity & Global Auth)
* **Exact Affected Objects**: Tables `public.users`, `public.refresh_tokens`, `public.subscriptions`.
* **Affected Roles**: `anon`, `authenticated`, `PUBLIC`.
* **Preconditions**: Gate 2.1 verified and approved.
* **Proposed SQL (NOT EXECUTED)**:
  ```sql
  BEGIN;
  SET LOCAL lock_timeout = '2s';
  SET LOCAL statement_timeout = '4s';

  REVOKE ALL ON TABLE public.users FROM anon, authenticated, PUBLIC;
  REVOKE ALL ON TABLE public.refresh_tokens FROM anon, authenticated, PUBLIC;
  REVOKE ALL ON TABLE public.subscriptions FROM anon, authenticated, PUBLIC;

  COMMIT;
  ```
* **Comprehensive Verification Query (Post-Execution Check)**:
  ```sql
  SELECT 
      t.table_name,
      r.role_name,
      p.privilege_name,
      has_table_privilege(r.role_name, 'public.' || t.table_name, p.privilege_name) AS has_privilege
  FROM (VALUES ('users'), ('refresh_tokens'), ('subscriptions')) AS t(table_name)
  CROSS JOIN (VALUES ('anon'), ('authenticated'), ('public')) AS r(role_name)
  CROSS JOIN (VALUES ('SELECT'), ('INSERT'), ('UPDATE'), ('DELETE'), ('TRUNCATE'), ('REFERENCES'), ('TRIGGER'), ('MAINTAIN')) AS p(privilege_name)
  WHERE has_table_privilege(r.role_name, 'public.' || t.table_name, p.privilege_name) = true;
  -- Expected Result: Exactly 0 rows.
  ```
* **Abort Condition**: Lock timeout (>2s) or error on any table.
* **System State on Failure**: Group 2 transaction aborted. Group 1 remains revoked. Follow Partial-Rollout Runbook (Section 4.3).
* **Rollback SQL (NOT EXECUTED)**:
  ```sql
  BEGIN;
  SET LOCAL lock_timeout = '2s';
  SET LOCAL statement_timeout = '4s';
  GRANT ALL ON TABLE public.users TO anon, authenticated;
  GRANT ALL ON TABLE public.refresh_tokens TO anon, authenticated;
  GRANT ALL ON TABLE public.subscriptions TO anon, authenticated;
  COMMIT;
  ```
* **Required Approval Gate**: **GATE 2.2: Group 2 DAC Revocation Sign-Off**.

#### Stage 2.3: Group 3 Revocation (Workspace Tenancy Root)
* **Exact Affected Objects**: Tables `public.projects`, `public.project_members`.
* **Affected Roles**: `anon`, `authenticated`, `PUBLIC`.
* **Preconditions**: Gate 2.2 verified and approved.
* **Proposed SQL (NOT EXECUTED)**:
  ```sql
  BEGIN;
  SET LOCAL lock_timeout = '2s';
  SET LOCAL statement_timeout = '4s';

  REVOKE ALL ON TABLE public.projects FROM anon, authenticated, PUBLIC;
  REVOKE ALL ON TABLE public.project_members FROM anon, authenticated, PUBLIC;

  COMMIT;
  ```
* **Comprehensive Verification Query (Post-Execution Check)**:
  ```sql
  SELECT 
      t.table_name,
      r.role_name,
      p.privilege_name,
      has_table_privilege(r.role_name, 'public.' || t.table_name, p.privilege_name) AS has_privilege
  FROM (VALUES ('projects'), ('project_members')) AS t(table_name)
  CROSS JOIN (VALUES ('anon'), ('authenticated'), ('public')) AS r(role_name)
  CROSS JOIN (VALUES ('SELECT'), ('INSERT'), ('UPDATE'), ('DELETE'), ('TRUNCATE'), ('REFERENCES'), ('TRIGGER'), ('MAINTAIN')) AS p(privilege_name)
  WHERE has_table_privilege(r.role_name, 'public.' || t.table_name, p.privilege_name) = true;
  -- Expected Result: Exactly 0 rows.
  ```
* **Abort Condition**: Lock timeout (>2s) or error.
* **System State on Failure**: Group 3 transaction aborted; Groups 1-2 remain revoked.
* **Rollback SQL (NOT EXECUTED)**:
  ```sql
  BEGIN;
  SET LOCAL lock_timeout = '2s';
  SET LOCAL statement_timeout = '4s';
  GRANT ALL ON TABLE public.projects TO anon, authenticated;
  GRANT ALL ON TABLE public.project_members TO anon, authenticated;
  COMMIT;
  ```
* **Required Approval Gate**: **GATE 2.3: Group 3 DAC Revocation Sign-Off**.

#### Stage 2.4A: Micro-Batch 4A Revocation (CRM Core)
* **Exact Affected Objects**: Tables `public.customer_profiles`, `public.deals`, `public.pipeline_stages`.
* **Affected Roles**: `anon`, `authenticated`, `PUBLIC`.
* **Preconditions**: Gate 2.3 verified and approved.
* **Proposed SQL (NOT EXECUTED)**:
  ```sql
  BEGIN;
  SET LOCAL lock_timeout = '2s';
  SET LOCAL statement_timeout = '4s';

  REVOKE ALL ON TABLE public.customer_profiles FROM anon, authenticated, PUBLIC;
  REVOKE ALL ON TABLE public.deals FROM anon, authenticated, PUBLIC;
  REVOKE ALL ON TABLE public.pipeline_stages FROM anon, authenticated, PUBLIC;

  COMMIT;
  ```
* **Comprehensive Verification Query (Post-Execution Check)**:
  ```sql
  SELECT 
      t.table_name,
      r.role_name,
      p.privilege_name,
      has_table_privilege(r.role_name, 'public.' || t.table_name, p.privilege_name) AS has_privilege
  FROM (VALUES ('customer_profiles'), ('deals'), ('pipeline_stages')) AS t(table_name)
  CROSS JOIN (VALUES ('anon'), ('authenticated'), ('public')) AS r(role_name)
  CROSS JOIN (VALUES ('SELECT'), ('INSERT'), ('UPDATE'), ('DELETE'), ('TRUNCATE'), ('REFERENCES'), ('TRIGGER'), ('MAINTAIN')) AS p(privilege_name)
  WHERE has_table_privilege(r.role_name, 'public.' || t.table_name, p.privilege_name) = true;
  -- Expected Result: Exactly 0 rows.
  ```
* **Abort Condition**: Lock timeout (>2s) or error on any table.
* **System State on Failure**: Micro-Batch 4A aborted; Groups 1-3 remain revoked.
* **Rollback SQL (NOT EXECUTED)**:
  ```sql
  BEGIN;
  SET LOCAL lock_timeout = '2s';
  SET LOCAL statement_timeout = '4s';
  GRANT ALL ON TABLE public.customer_profiles TO anon, authenticated;
  GRANT ALL ON TABLE public.deals TO anon, authenticated;
  GRANT ALL ON TABLE public.pipeline_stages TO anon, authenticated;
  COMMIT;
  ```
* **Required Approval Gate**: **GATE 2.4A: Micro-Batch 4A DAC Sign-Off**.

#### Stage 2.4B: Micro-Batch 4B Revocation (Commerce & Billing)
* **Exact Affected Objects**: Tables `public.orders`, `public.invoices`, `public.payment_links`.
* **Affected Roles**: `anon`, `authenticated`, `PUBLIC`.
* **Preconditions**: Gate 2.4A verified and approved.
* **Proposed SQL (NOT EXECUTED)**:
  ```sql
  BEGIN;
  SET LOCAL lock_timeout = '2s';
  SET LOCAL statement_timeout = '4s';

  REVOKE ALL ON TABLE public.orders FROM anon, authenticated, PUBLIC;
  REVOKE ALL ON TABLE public.invoices FROM anon, authenticated, PUBLIC;
  REVOKE ALL ON TABLE public.payment_links FROM anon, authenticated, PUBLIC;

  COMMIT;
  ```
* **Comprehensive Verification Query (Post-Execution Check)**:
  ```sql
  SELECT 
      t.table_name,
      r.role_name,
      p.privilege_name,
      has_table_privilege(r.role_name, 'public.' || t.table_name, p.privilege_name) AS has_privilege
  FROM (VALUES ('orders'), ('invoices'), ('payment_links')) AS t(table_name)
  CROSS JOIN (VALUES ('anon'), ('authenticated'), ('public')) AS r(role_name)
  CROSS JOIN (VALUES ('SELECT'), ('INSERT'), ('UPDATE'), ('DELETE'), ('TRUNCATE'), ('REFERENCES'), ('TRIGGER'), ('MAINTAIN')) AS p(privilege_name)
  WHERE has_table_privilege(r.role_name, 'public.' || t.table_name, p.privilege_name) = true;
  -- Expected Result: Exactly 0 rows.
  ```
* **Abort Condition**: Lock timeout (>2s) or error on any table.
* **System State on Failure**: Micro-Batch 4B aborted; Groups 1-3 and 4A remain revoked.
* **Rollback SQL (NOT EXECUTED)**:
  ```sql
  BEGIN;
  SET LOCAL lock_timeout = '2s';
  SET LOCAL statement_timeout = '4s';
  GRANT ALL ON TABLE public.orders TO anon, authenticated;
  GRANT ALL ON TABLE public.invoices TO anon, authenticated;
  GRANT ALL ON TABLE public.payment_links TO anon, authenticated;
  COMMIT;
  ```
* **Required Approval Gate**: **GATE 2.4B: Micro-Batch 4B DAC Sign-Off**.

#### Stage 2.4C: Micro-Batch 4C Revocation (Product & Knowledge)
* **Exact Affected Objects**: Tables `public.products`, `public.knowledge_base`, `public.integrations`.
* **Affected Roles**: `anon`, `authenticated`, `PUBLIC`.
* **Preconditions**: Gate 2.4B verified and approved.
* **Proposed SQL (NOT EXECUTED)**:
  ```sql
  BEGIN;
  SET LOCAL lock_timeout = '2s';
  SET LOCAL statement_timeout = '4s';

  REVOKE ALL ON TABLE public.products FROM anon, authenticated, PUBLIC;
  REVOKE ALL ON TABLE public.knowledge_base FROM anon, authenticated, PUBLIC;
  REVOKE ALL ON TABLE public.integrations FROM anon, authenticated, PUBLIC;

  COMMIT;
  ```
* **Comprehensive Verification Query (Post-Execution Check)**:
  ```sql
  SELECT 
      t.table_name,
      r.role_name,
      p.privilege_name,
      has_table_privilege(r.role_name, 'public.' || t.table_name, p.privilege_name) AS has_privilege
  FROM (VALUES ('products'), ('knowledge_base'), ('integrations')) AS t(table_name)
  CROSS JOIN (VALUES ('anon'), ('authenticated'), ('public')) AS r(role_name)
  CROSS JOIN (VALUES ('SELECT'), ('INSERT'), ('UPDATE'), ('DELETE'), ('TRUNCATE'), ('REFERENCES'), ('TRIGGER'), ('MAINTAIN')) AS p(privilege_name)
  WHERE has_table_privilege(r.role_name, 'public.' || t.table_name, p.privilege_name) = true;
  -- Expected Result: Exactly 0 rows.
  ```
* **Abort Condition**: Lock timeout (>2s) or error on any table.
* **System State on Failure**: Micro-Batch 4C aborted; Groups 1-3, 4A, 4B remain revoked.
* **Rollback SQL (NOT EXECUTED)**:
  ```sql
  BEGIN;
  SET LOCAL lock_timeout = '2s';
  SET LOCAL statement_timeout = '4s';
  GRANT ALL ON TABLE public.products TO anon, authenticated;
  GRANT ALL ON TABLE public.knowledge_base TO anon, authenticated;
  GRANT ALL ON TABLE public.integrations TO anon, authenticated;
  COMMIT;
  ```
* **Required Approval Gate**: **GATE 2.4C: Micro-Batch 4C DAC Sign-Off**.

#### Stage 2.5A: Micro-Batch 5A Revocation (Marketing Automation)
* **Exact Affected Objects**: Tables `public.drip_campaigns`, `public.drip_steps`, `public.campaign_enrollments`.
* **Affected Roles**: `anon`, `authenticated`, `PUBLIC`.
* **Preconditions**: Gate 2.4C verified and approved.
* **Proposed SQL (NOT EXECUTED)**:
  ```sql
  BEGIN;
  SET LOCAL lock_timeout = '2s';
  SET LOCAL statement_timeout = '4s';

  REVOKE ALL ON TABLE public.drip_campaigns FROM anon, authenticated, PUBLIC;
  REVOKE ALL ON TABLE public.drip_steps FROM anon, authenticated, PUBLIC;
  REVOKE ALL ON TABLE public.campaign_enrollments FROM anon, authenticated, PUBLIC;

  COMMIT;
  ```
* **Comprehensive Verification Query (Post-Execution Check)**:
  ```sql
  SELECT 
      t.table_name,
      r.role_name,
      p.privilege_name,
      has_table_privilege(r.role_name, 'public.' || t.table_name, p.privilege_name) AS has_privilege
  FROM (VALUES ('drip_campaigns'), ('drip_steps'), ('campaign_enrollments')) AS t(table_name)
  CROSS JOIN (VALUES ('anon'), ('authenticated'), ('public')) AS r(role_name)
  CROSS JOIN (VALUES ('SELECT'), ('INSERT'), ('UPDATE'), ('DELETE'), ('TRUNCATE'), ('REFERENCES'), ('TRIGGER'), ('MAINTAIN')) AS p(privilege_name)
  WHERE has_table_privilege(r.role_name, 'public.' || t.table_name, p.privilege_name) = true;
  -- Expected Result: Exactly 0 rows.
  ```
* **Abort Condition**: Lock timeout (>2s) or error.
* **System State on Failure**: Micro-Batch 5A aborted; Groups 1-4 remain revoked.
* **Rollback SQL (NOT EXECUTED)**:
  ```sql
  BEGIN;
  SET LOCAL lock_timeout = '2s';
  SET LOCAL statement_timeout = '4s';
  GRANT ALL ON TABLE public.drip_campaigns TO anon, authenticated;
  GRANT ALL ON TABLE public.drip_steps TO anon, authenticated;
  GRANT ALL ON TABLE public.campaign_enrollments TO anon, authenticated;
  COMMIT;
  ```
* **Required Approval Gate**: **GATE 2.5A: Micro-Batch 5A DAC Sign-Off**.

#### Stage 2.5B: Micro-Batch 5B Revocation (AI Agent Configuration)
* **Exact Affected Objects**: Tables `public.auto_response_templates`, `public.bot_instructions`, `public.model_trainings`.
* **Affected Roles**: `anon`, `authenticated`, `PUBLIC`.
* **Preconditions**: Gate 2.5A verified and approved.
* **Proposed SQL (NOT EXECUTED)**:
  ```sql
  BEGIN;
  SET LOCAL lock_timeout = '2s';
  SET LOCAL statement_timeout = '4s';

  REVOKE ALL ON TABLE public.auto_response_templates FROM anon, authenticated, PUBLIC;
  REVOKE ALL ON TABLE public.bot_instructions FROM anon, authenticated, PUBLIC;
  REVOKE ALL ON TABLE public.model_trainings FROM anon, authenticated, PUBLIC;

  COMMIT;
  ```
* **Comprehensive Verification Query (Post-Execution Check)**:
  ```sql
  SELECT 
      t.table_name,
      r.role_name,
      p.privilege_name,
      has_table_privilege(r.role_name, 'public.' || t.table_name, p.privilege_name) AS has_privilege
  FROM (VALUES ('auto_response_templates'), ('bot_instructions'), ('model_trainings')) AS t(table_name)
  CROSS JOIN (VALUES ('anon'), ('authenticated'), ('public')) AS r(role_name)
  CROSS JOIN (VALUES ('SELECT'), ('INSERT'), ('UPDATE'), ('DELETE'), ('TRUNCATE'), ('REFERENCES'), ('TRIGGER'), ('MAINTAIN')) AS p(privilege_name)
  WHERE has_table_privilege(r.role_name, 'public.' || t.table_name, p.privilege_name) = true;
  -- Expected Result: Exactly 0 rows.
  ```
* **Abort Condition**: Lock timeout (>2s) or error.
* **System State on Failure**: Micro-Batch 5B aborted; Groups 1-4 and 5A remain revoked.
* **Rollback SQL (NOT EXECUTED)**:
  ```sql
  BEGIN;
  SET LOCAL lock_timeout = '2s';
  SET LOCAL statement_timeout = '4s';
  GRANT ALL ON TABLE public.auto_response_templates TO anon, authenticated;
  GRANT ALL ON TABLE public.bot_instructions TO anon, authenticated;
  GRANT ALL ON TABLE public.model_trainings TO anon, authenticated;
  COMMIT;
  ```
* **Required Approval Gate**: **GATE 2.5B: Micro-Batch 5B DAC Sign-Off**.

#### Stage 2.5C: Micro-Batch 5C Revocation (Analytics & Operations)
* **Exact Affected Objects**: Tables `public.reports`, `public.oauth_states`, `public.usage_tracking`.
* **Affected Roles**: `anon`, `authenticated`, `PUBLIC`.
* **Preconditions**: Gate 2.5B verified and approved.
* **Proposed SQL (NOT EXECUTED)**:
  ```sql
  BEGIN;
  SET LOCAL lock_timeout = '2s';
  SET LOCAL statement_timeout = '4s';

  REVOKE ALL ON TABLE public.reports FROM anon, authenticated, PUBLIC;
  REVOKE ALL ON TABLE public.oauth_states FROM anon, authenticated, PUBLIC;
  REVOKE ALL ON TABLE public.usage_tracking FROM anon, authenticated, PUBLIC;

  COMMIT;
  ```
* **Comprehensive Verification Query (Post-Execution Check)**:
  ```sql
  SELECT 
      t.table_name,
      r.role_name,
      p.privilege_name,
      has_table_privilege(r.role_name, 'public.' || t.table_name, p.privilege_name) AS has_privilege
  FROM (VALUES ('reports'), ('oauth_states'), ('usage_tracking')) AS t(table_name)
  CROSS JOIN (VALUES ('anon'), ('authenticated'), ('public')) AS r(role_name)
  CROSS JOIN (VALUES ('SELECT'), ('INSERT'), ('UPDATE'), ('DELETE'), ('TRUNCATE'), ('REFERENCES'), ('TRIGGER'), ('MAINTAIN')) AS p(privilege_name)
  WHERE has_table_privilege(r.role_name, 'public.' || t.table_name, p.privilege_name) = true;
  -- Expected Result: Exactly 0 rows.
  ```
* **Abort Condition**: Lock timeout (>2s) or error.
* **System State on Failure**: Micro-Batch 5C aborted; Groups 1-4, 5A, 5B remain revoked.
* **Rollback SQL (NOT EXECUTED)**:
  ```sql
  BEGIN;
  SET LOCAL lock_timeout = '2s';
  SET LOCAL statement_timeout = '4s';
  GRANT ALL ON TABLE public.reports TO anon, authenticated;
  GRANT ALL ON TABLE public.oauth_states TO anon, authenticated;
  GRANT ALL ON TABLE public.usage_tracking TO anon, authenticated;
  COMMIT;
  ```
* **Required Approval Gate**: **GATE 2.5C: Micro-Batch 5C DAC Sign-Off**.

#### Stage 2.6: Group 6 Revocation (High-Throughput Streaming & Sequences)
* **Exact Affected Objects**: Tables `public.api_logs`, `public.messages`, `public.conversation_history`, `public.bot_activities`, `public.social_media_comments`, `public.social_media_posts`; Sequence `public.api_logs_id_seq`.
* **Affected Roles**: `anon`, `authenticated`, `PUBLIC`.
* **Preconditions**: Gate 2.5C verified and approved. Must execute during lowest-traffic production maintenance window.
* **Proposed SQL (NOT EXECUTED)**:
  ```sql
  BEGIN;
  SET LOCAL lock_timeout = '2s';
  SET LOCAL statement_timeout = '4s';

  REVOKE ALL ON TABLE public.api_logs FROM anon, authenticated, PUBLIC;
  REVOKE ALL ON TABLE public.messages FROM anon, authenticated, PUBLIC;
  REVOKE ALL ON TABLE public.conversation_history FROM anon, authenticated, PUBLIC;
  REVOKE ALL ON TABLE public.bot_activities FROM anon, authenticated, PUBLIC;
  REVOKE ALL ON TABLE public.social_media_comments FROM anon, authenticated, PUBLIC;
  REVOKE ALL ON TABLE public.social_media_posts FROM anon, authenticated, PUBLIC;

  REVOKE ALL ON SEQUENCE public.api_logs_id_seq FROM anon, authenticated, PUBLIC;

  COMMIT;
  ```
* **Comprehensive Verification Query (Post-Execution Check)**:
  ```sql
  -- 1. Verify all 6 high-throughput tables across all 8 privileges
  SELECT 
      t.table_name,
      r.role_name,
      p.privilege_name,
      has_table_privilege(r.role_name, 'public.' || t.table_name, p.privilege_name) AS has_privilege
  FROM (VALUES 
      ('api_logs'), ('messages'), ('conversation_history'), 
      ('bot_activities'), ('social_media_comments'), ('social_media_posts')
  ) AS t(table_name)
  CROSS JOIN (VALUES ('anon'), ('authenticated'), ('public')) AS r(role_name)
  CROSS JOIN (VALUES ('SELECT'), ('INSERT'), ('UPDATE'), ('DELETE'), ('TRUNCATE'), ('REFERENCES'), ('TRIGGER'), ('MAINTAIN')) AS p(privilege_name)
  WHERE has_table_privilege(r.role_name, 'public.' || t.table_name, p.privilege_name) = true;
  -- Expected Result: Exactly 0 rows.

  -- 2. Verify sequence api_logs_id_seq across all sequence privileges
  SELECT 
      r.role_name,
      p.privilege_name,
      has_sequence_privilege(r.role_name, 'public.api_logs_id_seq', p.privilege_name) AS has_privilege
  FROM (VALUES ('anon'), ('authenticated'), ('public')) AS r(role_name)
  CROSS JOIN (VALUES ('USAGE'), ('SELECT'), ('UPDATE')) AS p(privilege_name)
  WHERE has_sequence_privilege(r.role_name, 'public.api_logs_id_seq', p.privilege_name) = true;
  -- Expected Result: Exactly 0 rows.
  ```
* **Abort Condition**: Lock timeout (>2s) on active messaging tables.
* **System State on Failure**: Group 6 transaction aborted; Groups 1-5 remain revoked.
* **Rollback SQL (NOT EXECUTED)**:
  ```sql
  BEGIN;
  SET LOCAL lock_timeout = '2s';
  SET LOCAL statement_timeout = '4s';
  GRANT ALL ON TABLE public.api_logs TO anon, authenticated;
  GRANT ALL ON TABLE public.messages TO anon, authenticated;
  GRANT ALL ON TABLE public.conversation_history TO anon, authenticated;
  GRANT ALL ON TABLE public.bot_activities TO anon, authenticated;
  GRANT ALL ON TABLE public.social_media_comments TO anon, authenticated;
  GRANT ALL ON TABLE public.social_media_posts TO anon, authenticated;
  GRANT ALL ON SEQUENCE public.api_logs_id_seq TO anon, authenticated;
  COMMIT;
  ```
* **Required Approval Gate**: **GATE 2.6: Group 6 DAC Revocation Sign-Off**.

---

### Stage 3: Default Privilege Neutralization (Future Object Immunity)

* **Objective**: Neutralize default ACLs in `pg_default_acl` so newly created tables, sequences, and routines generated by future migrations do not inherit automatic public grants to `anon` and `authenticated`.
* **Scope & Limitation**: Citation: [PostgreSQL 17 `ALTER DEFAULT PRIVILEGES`](https://www.postgresql.org/docs/17/sql-alterdefaultprivileges.html). Modifies **future objects only**. It does not alter grants on existing tables or sequences, nor does it enable RLS on future tables.

#### 1. Confirmed Step: Role `postgres` Neutralization
* **Executor Authority**: Role `postgres` is verified as active user (`rolsuper = f`, `rolcanlogin = t`, `rolcreaterole = t`). Under PostgreSQL 17 rules, `postgres` has full authority to alter its own default privileges.
* **Proposed SQL (NOT EXECUTED)**:
  ```sql
  BEGIN;
  SET LOCAL lock_timeout = '2s';
  SET LOCAL statement_timeout = '4s';

  ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public 
      REVOKE ALL ON TABLES FROM anon, authenticated;
  ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public 
      REVOKE ALL ON SEQUENCES FROM anon, authenticated;
  ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public 
      REVOKE ALL ON ROUTINES FROM anon, authenticated;

  COMMIT;
  ```
* **Verification Query (Post-Execution Check)**:
  ```sql
  SELECT 
      defaclrole::regrole AS granter,
      defaclnamespace::regnamespace AS target_schema,
      defaclobjtype AS object_type,
      defaclacl AS default_permissions
  FROM pg_default_acl 
  WHERE defaclnamespace = 'public'::regnamespace 
    AND defaclrole = 'postgres'::regrole;
  -- Expected Result: defaclacl shows no grants to anon or authenticated.
  ```
* **Symmetrical Rollback SQL for `postgres` (NOT EXECUTED)**:
  ```sql
  BEGIN;
  SET LOCAL lock_timeout = '2s';
  SET LOCAL statement_timeout = '4s';
  ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public 
      GRANT ALL ON TABLES TO anon, authenticated;
  ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public 
      GRANT ALL ON SEQUENCES TO anon, authenticated;
  ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public 
      GRANT ALL ON ROUTINES TO anon, authenticated;
  COMMIT;
  ```

#### 2. Conditional / BLOCKED Step: Role `supabase_admin` Neutralization
* **Technical Blocker Analysis**:
  * PostgreSQL Documentation explicitly mandates: *"You can change default privileges only for objects that will be created by yourself or by roles that you are a member of."*
  * Stage 1 catalog evidence proves that `supabase_admin` exists, but contains **ZERO evidence that `postgres` is a member of `supabase_admin`** (`pg_auth_members`).
  * If `postgres` is not a member of `supabase_admin`, executing `ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin ...` will immediately fail with:
    `ERROR: must be member of role "supabase_admin"`
* **Status**: **BLOCKED — REQUIRES PROOF OF ROLE MEMBERSHIP (Gate A)**.
* **Precondition Check Query (Read-Only)**:
  ```sql
  SELECT pg_has_role('postgres', 'supabase_admin', 'MEMBER') AS is_member;
  ```
* **Rule of Engagement**:
  - If `is_member = true`: Proceed to execute the `ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin ...` block.
  - If `is_member = false`: **DO NOT EXECUTE**. Mark step as permanently blocked for session user `postgres`.
* **Conditional Rollback SQL for `supabase_admin` (APPLICABLE ONLY IF STEP 3.2 WAS EXECUTED)**:
  ```sql
  -- CONDITIONAL ROLLBACK (NOT EXECUTED - APPLICABLE ONLY IF STEP 3.2 RUNS)
  -- BEGIN;
  -- SET LOCAL lock_timeout = '2s';
  -- SET LOCAL statement_timeout = '4s';
  -- ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA public 
  --     GRANT ALL ON TABLES TO anon, authenticated;
  -- ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA public 
  --     GRANT ALL ON SEQUENCES TO anon, authenticated;
  -- ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA public 
  --     GRANT ALL ON ROUTINES TO anon, authenticated;
  -- COMMIT;
  ```
* **Required Approval Gate**: **GATE 3: Default Privilege Neutralization Sign-Off**.

---

### Stage 4: Mandatory Access Control (MAC) — Row-Level Security Enablement

* **Objective**: Fulfill **Control C** by establishing an engine-level default-deny posture on all 30 public tables. Citation: [PostgreSQL 17 Row Security Policies](https://www.postgresql.org/docs/17/ddl-rowsecurity.html).
* **Critical Engine Behavior & Limitations**:
  * With zero policies defined, enabling RLS causes PostgreSQL to **deny all rows** (`SELECT` returns empty, `INSERT/UPDATE/DELETE` fails) for any non-bypass role.
  * Because the FastAPI backend connects as `postgres` (`rolbypassrls = true`), **the backend completely bypasses this check**.
  * **RLS in this phase does NOT enforce tenant isolation for backend queries**. Application-level guards remain 100% required.
  * **DO NOT** execute `FORCE ROW LEVEL SECURITY`. Table owners and bypass roles must remain unforced.
* **Safety Protocol**:
  - Executed in the exact same decomposed micro-batches with `lock_timeout = '2s'` and `statement_timeout = '4s'`.
  - Every micro-batch has an independent, fully isolated rollback procedure.
  - **No Automatic Progression**: Each micro-batch requires human verification and sign-off before proceeding.

#### Stage 4.1: Enable RLS on Group 1 (Metadata)
* **Proposed SQL (NOT EXECUTED)**:
  ```sql
  BEGIN;
  SET LOCAL lock_timeout = '2s';
  SET LOCAL statement_timeout = '4s';

  ALTER TABLE public.alembic_version ENABLE ROW LEVEL SECURITY;

  COMMIT;
  ```
* **Verification Query**:
  ```sql
  SELECT relname, relrowsecurity, relforcerowsecurity 
  FROM pg_class 
  WHERE relnamespace = 'public'::regnamespace AND relname = 'alembic_version';
  -- Expected Result: relrowsecurity = t, relforcerowsecurity = f.
  ```
* **Rollback SQL (NOT EXECUTED)**:
  ```sql
  BEGIN;
  SET LOCAL lock_timeout = '2s';
  SET LOCAL statement_timeout = '4s';
  ALTER TABLE public.alembic_version DISABLE ROW LEVEL SECURITY;
  COMMIT;
  ```
* **Required Approval Gate**: **GATE 4.1: Group 1 RLS Enablement Sign-Off**.

#### Stage 4.2: Enable RLS on Group 2 (Identity & Auth)
* **Proposed SQL (NOT EXECUTED)**:
  ```sql
  BEGIN;
  SET LOCAL lock_timeout = '2s';
  SET LOCAL statement_timeout = '4s';

  ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
  ALTER TABLE public.refresh_tokens ENABLE ROW LEVEL SECURITY;
  ALTER TABLE public.subscriptions ENABLE ROW LEVEL SECURITY;

  COMMIT;
  ```
* **Verification Query**:
  ```sql
  SELECT relname, relrowsecurity, relforcerowsecurity FROM pg_class 
  WHERE relnamespace = 'public'::regnamespace 
    AND relname IN ('users', 'refresh_tokens', 'subscriptions');
  -- Expected Result: 3 rows returned; all relrowsecurity = t, relforcerowsecurity = f.
  ```
* **Rollback SQL (NOT EXECUTED)**:
  ```sql
  BEGIN;
  SET LOCAL lock_timeout = '2s';
  SET LOCAL statement_timeout = '4s';
  ALTER TABLE public.users DISABLE ROW LEVEL SECURITY;
  ALTER TABLE public.refresh_tokens DISABLE ROW LEVEL SECURITY;
  ALTER TABLE public.subscriptions DISABLE ROW LEVEL SECURITY;
  COMMIT;
  ```
* **Required Approval Gate**: **GATE 4.2: Group 2 RLS Enablement Sign-Off**.

#### Stage 4.3: Enable RLS on Group 3 (Tenancy Root)
* **Proposed SQL (NOT EXECUTED)**:
  ```sql
  BEGIN;
  SET LOCAL lock_timeout = '2s';
  SET LOCAL statement_timeout = '4s';

  ALTER TABLE public.projects ENABLE ROW LEVEL SECURITY;
  ALTER TABLE public.project_members ENABLE ROW LEVEL SECURITY;

  COMMIT;
  ```
* **Verification Query**:
  ```sql
  SELECT relname, relrowsecurity, relforcerowsecurity FROM pg_class 
  WHERE relnamespace = 'public'::regnamespace 
    AND relname IN ('projects', 'project_members');
  -- Expected Result: 2 rows returned; all relrowsecurity = t, relforcerowsecurity = f.
  ```
* **Rollback SQL (NOT EXECUTED)**:
  ```sql
  BEGIN;
  SET LOCAL lock_timeout = '2s';
  SET LOCAL statement_timeout = '4s';
  ALTER TABLE public.projects DISABLE ROW LEVEL SECURITY;
  ALTER TABLE public.project_members DISABLE ROW LEVEL SECURITY;
  COMMIT;
  ```
* **Required Approval Gate**: **GATE 4.3: Group 3 RLS Enablement Sign-Off**.

#### Stage 4.4A: Enable RLS on Micro-Batch 4A (CRM Core)
* **Proposed SQL (NOT EXECUTED)**:
  ```sql
  BEGIN;
  SET LOCAL lock_timeout = '2s';
  SET LOCAL statement_timeout = '4s';

  ALTER TABLE public.customer_profiles ENABLE ROW LEVEL SECURITY;
  ALTER TABLE public.deals ENABLE ROW LEVEL SECURITY;
  ALTER TABLE public.pipeline_stages ENABLE ROW LEVEL SECURITY;

  COMMIT;
  ```
* **Verification Query**:
  ```sql
  SELECT relname, relrowsecurity, relforcerowsecurity FROM pg_class 
  WHERE relnamespace = 'public'::regnamespace 
    AND relname IN ('customer_profiles', 'deals', 'pipeline_stages');
  -- Expected Result: 3 rows returned; all relrowsecurity = t, relforcerowsecurity = f.
  ```
* **Rollback SQL (NOT EXECUTED)**:
  ```sql
  BEGIN;
  SET LOCAL lock_timeout = '2s';
  SET LOCAL statement_timeout = '4s';
  ALTER TABLE public.customer_profiles DISABLE ROW LEVEL SECURITY;
  ALTER TABLE public.deals DISABLE ROW LEVEL SECURITY;
  ALTER TABLE public.pipeline_stages DISABLE ROW LEVEL SECURITY;
  COMMIT;
  ```
* **Required Approval Gate**: **GATE 4.4A: Micro-Batch 4A RLS Sign-Off**.

#### Stage 4.4B: Enable RLS on Micro-Batch 4B (Commerce & Billing)
* **Proposed SQL (NOT EXECUTED)**:
  ```sql
  BEGIN;
  SET LOCAL lock_timeout = '2s';
  SET LOCAL statement_timeout = '4s';

  ALTER TABLE public.orders ENABLE ROW LEVEL SECURITY;
  ALTER TABLE public.invoices ENABLE ROW LEVEL SECURITY;
  ALTER TABLE public.payment_links ENABLE ROW LEVEL SECURITY;

  COMMIT;
  ```
* **Verification Query**:
  ```sql
  SELECT relname, relrowsecurity, relforcerowsecurity FROM pg_class 
  WHERE relnamespace = 'public'::regnamespace 
    AND relname IN ('orders', 'invoices', 'payment_links');
  -- Expected Result: 3 rows returned; all relrowsecurity = t, relforcerowsecurity = f.
  ```
* **Rollback SQL (NOT EXECUTED)**:
  ```sql
  BEGIN;
  SET LOCAL lock_timeout = '2s';
  SET LOCAL statement_timeout = '4s';
  ALTER TABLE public.orders DISABLE ROW LEVEL SECURITY;
  ALTER TABLE public.invoices DISABLE ROW LEVEL SECURITY;
  ALTER TABLE public.payment_links DISABLE ROW LEVEL SECURITY;
  COMMIT;
  ```
* **Required Approval Gate**: **GATE 4.4B: Micro-Batch 4B RLS Sign-Off**.

#### Stage 4.4C: Enable RLS on Micro-Batch 4C (Product & Knowledge)
* **Proposed SQL (NOT EXECUTED)**:
  ```sql
  BEGIN;
  SET LOCAL lock_timeout = '2s';
  SET LOCAL statement_timeout = '4s';

  ALTER TABLE public.products ENABLE ROW LEVEL SECURITY;
  ALTER TABLE public.knowledge_base ENABLE ROW LEVEL SECURITY;
  ALTER TABLE public.integrations ENABLE ROW LEVEL SECURITY;

  COMMIT;
  ```
* **Verification Query**:
  ```sql
  SELECT relname, relrowsecurity, relforcerowsecurity FROM pg_class 
  WHERE relnamespace = 'public'::regnamespace 
    AND relname IN ('products', 'knowledge_base', 'integrations');
  -- Expected Result: 3 rows returned; all relrowsecurity = t, relforcerowsecurity = f.
  ```
* **Rollback SQL (NOT EXECUTED)**:
  ```sql
  BEGIN;
  SET LOCAL lock_timeout = '2s';
  SET LOCAL statement_timeout = '4s';
  ALTER TABLE public.products DISABLE ROW LEVEL SECURITY;
  ALTER TABLE public.knowledge_base DISABLE ROW LEVEL SECURITY;
  ALTER TABLE public.integrations DISABLE ROW LEVEL SECURITY;
  COMMIT;
  ```
* **Required Approval Gate**: **GATE 4.4C: Micro-Batch 4C RLS Sign-Off**.

#### Stage 4.5A: Enable RLS on Micro-Batch 5A (Marketing Automation)
* **Proposed SQL (NOT EXECUTED)**:
  ```sql
  BEGIN;
  SET LOCAL lock_timeout = '2s';
  SET LOCAL statement_timeout = '4s';

  ALTER TABLE public.drip_campaigns ENABLE ROW LEVEL SECURITY;
  ALTER TABLE public.drip_steps ENABLE ROW LEVEL SECURITY;
  ALTER TABLE public.campaign_enrollments ENABLE ROW LEVEL SECURITY;

  COMMIT;
  ```
* **Verification Query**:
  ```sql
  SELECT relname, relrowsecurity, relforcerowsecurity FROM pg_class 
  WHERE relnamespace = 'public'::regnamespace 
    AND relname IN ('drip_campaigns', 'drip_steps', 'campaign_enrollments');
  -- Expected Result: 3 rows returned; all relrowsecurity = t, relforcerowsecurity = f.
  ```
* **Rollback SQL (NOT EXECUTED)**:
  ```sql
  BEGIN;
  SET LOCAL lock_timeout = '2s';
  SET LOCAL statement_timeout = '4s';
  ALTER TABLE public.drip_campaigns DISABLE ROW LEVEL SECURITY;
  ALTER TABLE public.drip_steps DISABLE ROW LEVEL SECURITY;
  ALTER TABLE public.campaign_enrollments DISABLE ROW LEVEL SECURITY;
  COMMIT;
  ```
* **Required Approval Gate**: **GATE 4.5A: Micro-Batch 5A RLS Sign-Off**.

#### Stage 4.5B: Enable RLS on Micro-Batch 5B (AI Agent Configuration)
* **Proposed SQL (NOT EXECUTED)**:
  ```sql
  BEGIN;
  SET LOCAL lock_timeout = '2s';
  SET LOCAL statement_timeout = '4s';

  ALTER TABLE public.auto_response_templates ENABLE ROW LEVEL SECURITY;
  ALTER TABLE public.bot_instructions ENABLE ROW LEVEL SECURITY;
  ALTER TABLE public.model_trainings ENABLE ROW LEVEL SECURITY;

  COMMIT;
  ```
* **Verification Query**:
  ```sql
  SELECT relname, relrowsecurity, relforcerowsecurity FROM pg_class 
  WHERE relnamespace = 'public'::regnamespace 
    AND relname IN ('auto_response_templates', 'bot_instructions', 'model_trainings');
  -- Expected Result: 3 rows returned; all relrowsecurity = t, relforcerowsecurity = f.
  ```
* **Rollback SQL (NOT EXECUTED)**:
  ```sql
  BEGIN;
  SET LOCAL lock_timeout = '2s';
  SET LOCAL statement_timeout = '4s';
  ALTER TABLE public.auto_response_templates DISABLE ROW LEVEL SECURITY;
  ALTER TABLE public.bot_instructions DISABLE ROW LEVEL SECURITY;
  ALTER TABLE public.model_trainings DISABLE ROW LEVEL SECURITY;
  COMMIT;
  ```
* **Required Approval Gate**: **GATE 4.5B: Micro-Batch 5B RLS Sign-Off**.

#### Stage 4.5C: Enable RLS on Micro-Batch 5C (Analytics & Operations)
* **Proposed SQL (NOT EXECUTED)**:
  ```sql
  BEGIN;
  SET LOCAL lock_timeout = '2s';
  SET LOCAL statement_timeout = '4s';

  ALTER TABLE public.reports ENABLE ROW LEVEL SECURITY;
  ALTER TABLE public.oauth_states ENABLE ROW LEVEL SECURITY;
  ALTER TABLE public.usage_tracking ENABLE ROW LEVEL SECURITY;

  COMMIT;
  ```
* **Verification Query**:
  ```sql
  SELECT relname, relrowsecurity, relforcerowsecurity FROM pg_class 
  WHERE relnamespace = 'public'::regnamespace 
    AND relname IN ('reports', 'oauth_states', 'usage_tracking');
  -- Expected Result: 3 rows returned; all relrowsecurity = t, relforcerowsecurity = f.
  ```
* **Rollback SQL (NOT EXECUTED)**:
  ```sql
  BEGIN;
  SET LOCAL lock_timeout = '2s';
  SET LOCAL statement_timeout = '4s';
  ALTER TABLE public.reports DISABLE ROW LEVEL SECURITY;
  ALTER TABLE public.oauth_states DISABLE ROW LEVEL SECURITY;
  ALTER TABLE public.usage_tracking DISABLE ROW LEVEL SECURITY;
  COMMIT;
  ```
* **Required Approval Gate**: **GATE 4.5C: Micro-Batch 5C RLS Sign-Off**.

#### Stage 4.6: Enable RLS on Group 6 (High-Throughput Streaming)
* **Proposed SQL (NOT EXECUTED)**:
  ```sql
  BEGIN;
  SET LOCAL lock_timeout = '2s';
  SET LOCAL statement_timeout = '4s';

  ALTER TABLE public.api_logs ENABLE ROW LEVEL SECURITY;
  ALTER TABLE public.messages ENABLE ROW LEVEL SECURITY;
  ALTER TABLE public.conversation_history ENABLE ROW LEVEL SECURITY;
  ALTER TABLE public.bot_activities ENABLE ROW LEVEL SECURITY;
  ALTER TABLE public.social_media_comments ENABLE ROW LEVEL SECURITY;
  ALTER TABLE public.social_media_posts ENABLE ROW LEVEL SECURITY;

  COMMIT;
  ```
* **Verification Query**:
  ```sql
  SELECT relname, relrowsecurity, relforcerowsecurity FROM pg_class 
  WHERE relnamespace = 'public'::regnamespace 
    AND relname IN ('api_logs', 'messages', 'conversation_history', 'bot_activities', 'social_media_comments', 'social_media_posts');
  -- Expected Result: 6 rows returned; all relrowsecurity = t, relforcerowsecurity = f.
  ```
* **Rollback SQL (NOT EXECUTED)**:
  ```sql
  BEGIN;
  SET LOCAL lock_timeout = '2s';
  SET LOCAL statement_timeout = '4s';
  ALTER TABLE public.api_logs DISABLE ROW LEVEL SECURITY;
  ALTER TABLE public.messages DISABLE ROW LEVEL SECURITY;
  ALTER TABLE public.conversation_history DISABLE ROW LEVEL SECURITY;
  ALTER TABLE public.bot_activities DISABLE ROW LEVEL SECURITY;
  ALTER TABLE public.social_media_comments DISABLE ROW LEVEL SECURITY;
  ALTER TABLE public.social_media_posts DISABLE ROW LEVEL SECURITY;
  COMMIT;
  ```
* **Required Approval Gate**: **GATE 4.6: Group 6 RLS Enablement Sign-Off**.

---

### Stage 5: Gateway Surface Lockdown (PostgREST Exposed Schema Removal)

* **Objective**: Fulfill **Control A** at the HTTP routing layer by removing schema `public` from PostgREST Exposed Schemas in the Supabase Dashboard.
* **Exact Affected Systems**: Supabase PostgREST HTTP Gateway (`https://ccejhzadokkjssjiwmxt.supabase.co/rest/v1/*`) and GraphQL resolver (`/graphql/v1`).
* **Preconditions**: Stages 2, 3, and 4 verified complete. Preflight Gate B (External Consumer Sign-Off) cleared.
* **Connection Mode Differentiation & Reload Mechanics**:
  - In Supabase, if connecting through PgBouncer in transaction pooling mode (e.g. port 6543), `LISTEN` and `NOTIFY` statements are not supported and cannot reliably reach the PostgREST listener.
  - **Method 1 (Recommended Official Procedure)**: Modifying and saving API settings directly in the Supabase Dashboard automatically triggers a PostgREST configuration reload / container reload via the platform management plane.
  - **Method 2 (Direct Session Mode)**: If reloading via SQL, the connection must be established in direct session mode (port 5432 direct) as `postgres`, executing:
    ```sql
    NOTIFY pgrst, 'reload config';
    NOTIFY pgrst, 'reload schema';
    ```
* **Proposed Operational Action (Dashboard)**:
  1. Navigate to: `Project Settings` $ightarrow$ `API` $ightarrow$ `Data API Settings`.
  2. Locate: `Exposed Schemas`.
  3. Action: Remove `public` from the list of exposed schemas (set to empty or a dedicated non-existent schema, e.g., `private`).
  4. Save changes (which triggers the official Supabase platform reload).
* **Expected Effect**: PostgREST returns HTTP `404 Not Found` for all `/rest/v1/*` requests. GraphQL returns schema errors on public table types.
* **Potential Breakage**: Breaks any client attempting to access the database via Supabase HTTP endpoints. Verified that FastAPI backend connects over PostgreSQL pooler port 5432, completely independent of PostgREST.
* **Post-Reload Verification Probe**:
  - Execute read-only probe:
    `curl -i -H "apikey: <ANON_KEY>" https://ccejhzadokkjssjiwmxt.supabase.co/rest/v1/users`
  - Expected: HTTP `404 Not Found`.
* **Fallback Procedure**:
  - If PostgREST continues serving cached routes, restart PostgREST via Supabase Dashboard: `Project Settings` $ightarrow$ `Infrastructure` $ightarrow$ `Restart PostgREST / Restart Services`.
* **Rollback Procedure**:
  - Re-add `public` to `Exposed Schemas` in Supabase Project Settings $ightarrow$ API and save.
* **Required Approval Gate**: **GATE 5: PostgREST Gateway Lockdown Sign-Off**.

---

## 7. Security Verification & Test Plan (Negative & Positive Probes)

### 1. Differentiated Negative Security Test Matrix (PostgREST & GraphQL)

> [!WARNING]
> **UNVERIFIED ENVIRONMENT-SPECIFIC ASSUMPTIONS**
> Expected HTTP status codes (`401/403` vs `404`) and specific JSON response bodies are theoretical deductions based on upstream documentation. They are **unverified assumptions** until baseline behavior is empirically captured on the target instance (Preflight Gate C).
> Furthermore, **GraphQL behavior differs fundamentally between data queries and schema introspection**:
> - Under official `pg_graphql` documentation, `__schema` and `__type` introspection are disabled by default for non-service roles.
> - Data queries over GraphQL are rejected based on underlying PostgreSQL table permissions and RLS.
> - Whether the GraphQL endpoint itself is exposed or disabled must be empirically verified.
> **STRICT PROHIBITION**: Production write probes (including `POST /rest/v1/orders`) are **strictly prohibited** unless separate explicit approval authorizes a controlled synthetic test using an isolated synthetic identifier and immediate database row-count check. Never use real customer, financial, or business data for a probe.

| Test ID | Method & Target Path | Tested Access Type | Rollout Phase | Assumed Status Code | Denial Mechanism | Expected Response Body Structure | Proof of Non-Mutation Method | Abort Condition |
| :--- | :--- | :--- | :---: | :---: | :--- | :--- | :--- | :--- |
| **TEST-NEG-01A** | `GET /rest/v1/users?select=*` | Unauthenticated read of user credentials | Post-Stage 2 & 4 (Pre-Stage 5) | `401 / 403` (Assumed) | Database DAC / RLS rejection (SQLSTATE `42501`) | Assumed JSON error: `{"code":"42501","message":"permission denied for table users"}`. **Must NOT contain user array `[]`**. | Not applicable (read request). | Status `200 OK` or any user data returned in body. |
| **TEST-NEG-01B** | `GET /rest/v1/users?select=*` | Unauthenticated read of user credentials | Post-Stage 5 | `404 Not Found` (Assumed) | Gateway routing rejection (Schema `public` unexposed) | Assumed route error: `{"code":"PGRST106","message":"The schema must be one of..."}`. | Not applicable (read request). | Status `200/401/403` or any data returned. |
| **TEST-NEG-02** | `GET /rest/v1/projects?select=*` | Tenant workspace enumeration | Post-Stage 5 | `404 Not Found` (Assumed) | Gateway routing rejection | PostgREST route error JSON. Body must not contain project records. | Not applicable (read request). | Status `200 OK` or projects array returned. |
| **TEST-NEG-03** | `GET /rest/v1/messages?select=*` | Chat history exfiltration | Post-Stage 5 | `404 Not Found` (Assumed) | Gateway routing rejection | PostgREST route error JSON. Body must not contain chat transcripts. | Not applicable (read request). | Status `200 OK` or messages array returned. |
| **TEST-NEG-04** | `POST /rest/v1/orders` | Unauthorized order injection | Post-Stage 5 | `404 Not Found` (Assumed) | Gateway routing rejection | Error JSON. Body must NOT contain inserted order ID. | **Strictly Guarded Future Test (Requires Separate Sign-Off)**: Proving non-mutation requires synthetic ID `order_number = 'SEC_SYNTHETIC_PROBE_9999'` and catalog check: `SELECT count(*) FROM orders WHERE order_number = 'SEC_SYNTHETIC_PROBE_9999'`. Status code alone does not prove non-mutation. | Status `201 Created` or row count in DB increases. |
| **TEST-NEG-05** | `GET /rest/v1/alembic_version?select=*`| Migration fingerprinting | Post-Stage 5 | `404 Not Found` (Assumed) | Gateway routing rejection | Error JSON. Must not return revision hashes. | Not applicable (read request). | Status `200 OK` or version string returned. |
| **TEST-NEG-06A** | `POST /graphql/v1` (`{ users { id } }`)| GraphQL relation data query | Post-Stage 5 | `400 / 404` (Assumed) | GraphQL schema resolution / DAC failure | GraphQL error: `{"errors":[{"message":"Cannot query field 'users' on type 'Query'"}]}`. **`data` must be null or absent**. | Not applicable (read request). | Status `200 OK` with non-null `data.users`. |
| **TEST-NEG-06B** | `POST /graphql/v1` (`{ __schema { types { name } } }`)| GraphQL schema introspection | Post-Stage 5 | `400 / 403` (Assumed) | `pg_graphql` default introspection restriction | GraphQL error or disabled introspection response. | Not applicable (read request). | Status `200 OK` exposing full public relation catalog. |

### 2. Positive Operational Test Matrix (FastAPI Backend Smoke Suite)
Executed against production backend (`https://ai-sales-bot-api-production-412b.up.railway.app`):

| Test ID | Operation & Method | Target Endpoint | Expected Status | Operational Assertion | Abort Condition |
| :--- | :--- | :--- | :---: | :--- | :--- |
| **TEST-POS-01** | User Authentication (`POST`) | `/api/v1/auth/login` | `200 OK` | Backend authenticates users and issues HS256 JWTs using direct DB pooler. | Login fails with `500 Internal Server Error` or DB permission denied. |
| **TEST-POS-02** | Workspace Listing (`GET`) | `/api/v1/projects/` | `200 OK` | Authorized caller receives workspace list; join on `projects` and `project_members` succeeds. | Returns empty array or `500`. |
| **TEST-POS-03** | Cross-Tenant Read Rejection (`GET`) | `/api/v1/projects/{unauth_id}/messages` | `403 / 404` | Application-level tenant isolation actively rejects cross-tenant reads (`verify_project_access`). | Returns `200 OK` with messages of unauthorized tenant. |
| **TEST-POS-04** | Celery Worker Heartbeat | Background execution | Active | Asynchronous background tasks process without DB permission errors. | Task worker crashes or throws `PermissionDenied`. |
| **TEST-POS-05** | Webhook Processing (`POST`) | `/api/v1/webhooks/stripe` | `200 OK` | Signed webhook payload processed. **Must use test payload with sandbox customer ID to prevent live financial side effects.** | Returns `500` or fails DB insert. |
| **TEST-POS-06** | Alembic Metadata Access | `psql` query | Valid | `SELECT version_num FROM alembic_version;` succeeds for `postgres`. | Returns permission denied on `alembic_version`. |

* **Required Approval Gate**: **GATE 6: Final Verification & Production Acceptance**.

---

## 8. Separate Future Plan: Performance Optimization (Track 2)

> [!IMPORTANT]
> **PERFORMANCE WORK DECOUPLED FROM SECURITY REMEDIATION**
> In accordance with production change-management discipline, index removals and foreign-key creations are strictly excluded from the security remediation stages. They are scheduled as a separate future optimization track with independent approval gates.

### 1. Subscription Index Deduplication Plan
* **Identified Duplicate**: `ix_subscription_user` is a redundant unique B-tree index on `subscriptions(user_id)`.
* **Constraint Preservation**: Relational constraint `UNIQUE (user_id)` is backed by `subscriptions_user_id_key` (`contype = 'u'`). Dropping `ix_subscription_user` leaves the unique constraint 100% active.
* **Proposed Future SQL (NOT EXECUTED)**:
  ```sql
  -- PROPOSED FUTURE SQL (NOT EXECUTED - SCHEDULED IN TRACK 2)
  DROP INDEX CONCURRENTLY IF EXISTS public.ix_subscription_user;
  ```
* **Locking Behavior**: `DROP INDEX CONCURRENTLY` acquires a `SHARE UPDATE EXCLUSIVE` lock, allowing uninterrupted concurrent `SELECT`, `INSERT`, `UPDATE`, and `DELETE` operations on `subscriptions`.

### 2. Prioritized Foreign-Key Covering Index Plan
* **Mechanics**: Foreign key index absence causes full sequential scans on child tables during parent row updates or deletes.
* **Triage Prioritization**:
  - **High Priority** (Deploy first):
    - `invoices(order_id)`
    - `deals(stage_id)`
    - `campaign_enrollments(campaign_id)`
    - `drip_steps(campaign_id)`
    - `project_members(user_id)`
  - **Deferred** (High-churn tables, parent deletes rare):
    - `bot_activities(customer_id)`
    - `refresh_tokens(user_id)`
* **Proposed Future SQL Pattern (NOT EXECUTED)**:
  ```sql
  -- PROPOSED FUTURE SQL (NOT EXECUTED - SCHEDULED IN TRACK 2)
  CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_invoices_order_id ON public.invoices (order_id);
  CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_deals_stage_id ON public.deals (stage_id);
  CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_campaign_enrollments_campaign_id ON public.campaign_enrollments (campaign_id);
  CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_drip_steps_campaign_id ON public.drip_steps (campaign_id);
  CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_project_members_user_id ON public.project_members (user_id);
  ```
* **Required Approval Gate**: **GATE 7: Future Performance Track Sign-Off**.

---

## 9. Comprehensive Summary of Approval Gates & Sign-Off Requirements

Every stage and micro-batch requires explicit human review and sign-off before execution. Automatic cascading is strictly prohibited:

| Gate ID | Target Stage / Group | Micro-Batch Scope | Required Sign-Off Items | Human Approver Required |
| :---: | :--- | :--- | :--- | :--- |
| **Gate 1** | Stage 1 | Environment Baseline | Verify read-only baseline; confirm active `psql` connection as `postgres`; confirm server version and PITR enabled. | Lead DBA / DevSecOps |
| **Gate 2.1** | Stage 2.1 | DAC Group 1 | Approve REVOKE on `alembic_version` with `lock_timeout = '2s'`. Review comprehensive verification query output. | Lead DBA |
| **Gate 2.2** | Stage 2.2 | DAC Group 2 | Review auth login traffic; approve REVOKE on `users`, `refresh_tokens`, `subscriptions`. Review 8-privilege query. | Lead DBA & Security Lead |
| **Gate 2.3** | Stage 2.3 | DAC Group 3 | Approve REVOKE on `projects`, `project_members`. Review 8-privilege query. | Lead DBA |
| **Gate 2.4A**| Stage 2.4A | DAC Micro-Batch 4A | Approve REVOKE on `customer_profiles`, `deals`, `pipeline_stages`. Review 8-privilege query. | Lead DBA & Tech Lead |
| **Gate 2.4B**| Stage 2.4B | DAC Micro-Batch 4B | Approve REVOKE on `orders`, `invoices`, `payment_links`. Review 8-privilege query. | Lead DBA & Tech Lead |
| **Gate 2.4C**| Stage 2.4C | DAC Micro-Batch 4C | Approve REVOKE on `products`, `knowledge_base`, `integrations`. Review 8-privilege query. | Lead DBA & Tech Lead |
| **Gate 2.5A**| Stage 2.5A | DAC Micro-Batch 5A | Approve REVOKE on `drip_campaigns`, `drip_steps`, `campaign_enrollments`. Review 8-privilege query. | Lead DBA |
| **Gate 2.5B**| Stage 2.5B | DAC Micro-Batch 5B | Approve REVOKE on `auto_response_templates`, `bot_instructions`, `model_trainings`. Review 8-privilege query. | Lead DBA |
| **Gate 2.5C**| Stage 2.5C | DAC Micro-Batch 5C | Approve REVOKE on `reports`, `oauth_states`, `usage_tracking`. Review 8-privilege query. | Lead DBA |
| **Gate 2.6** | Stage 2.6 | DAC Group 6 | **Mandatory low-traffic maintenance window**; approve REVOKE on 6 streaming tables and `api_logs_id_seq`. Review table and sequence queries. | Lead DBA & Tech Lead |
| **Gate 3** | Stage 3 | Default ACLs | Approve `ALTER DEFAULT PRIVILEGES FOR ROLE postgres`. Review conditional status of `supabase_admin` (hold unless membership proven via `pg_has_role`). | Lead DBA |
| **Gate 4.1** | Stage 4.1 | RLS Group 1 | Approve `ALTER TABLE alembic_version ENABLE ROW LEVEL SECURITY`. Verify RLS status. | Security Lead |
| **Gate 4.2** | Stage 4.2 | RLS Group 2 | Approve `ENABLE ROW LEVEL SECURITY` on `users`, `refresh_tokens`, `subscriptions`. Verify RLS status. | Security Lead |
| **Gate 4.3** | Stage 4.3 | RLS Group 3 | Approve `ENABLE ROW LEVEL SECURITY` on `projects`, `project_members`. Verify RLS status. | Security Lead |
| **Gate 4.4A**| Stage 4.4A | RLS Micro-Batch 4A | Approve `ENABLE ROW LEVEL SECURITY` on `customer_profiles`, `deals`, `pipeline_stages`. Verify RLS status. | Security Lead |
| **Gate 4.4B**| Stage 4.4B | RLS Micro-Batch 4B | Approve `ENABLE ROW LEVEL SECURITY` on `orders`, `invoices`, `payment_links`. Verify RLS status. | Security Lead |
| **Gate 4.4C**| Stage 4.4C | RLS Micro-Batch 4C | Approve `ENABLE ROW LEVEL SECURITY` on `products`, `knowledge_base`, `integrations`. Verify RLS status. | Security Lead |
| **Gate 4.5A**| Stage 4.5A | RLS Micro-Batch 5A | Approve `ENABLE ROW LEVEL SECURITY` on `drip_campaigns`, `drip_steps`, `campaign_enrollments`. Verify RLS status. | Security Lead |
| **Gate 4.5B**| Stage 4.5B | RLS Micro-Batch 5B | Approve `ENABLE ROW LEVEL SECURITY` on `auto_response_templates`, `bot_instructions`, `model_trainings`. Verify RLS status. | Security Lead |
| **Gate 4.5C**| Stage 4.5C | RLS Micro-Batch 5C | Approve `ENABLE ROW LEVEL SECURITY` on `reports`, `oauth_states`, `usage_tracking`. Verify RLS status. | Security Lead |
| **Gate 4.6** | Stage 4.6 | RLS Group 6 | **Mandatory low-traffic maintenance window**; approve `ENABLE ROW LEVEL SECURITY` on 6 streaming tables. Verify RLS status. | Security Lead |
| **Gate 5** | Stage 5 | Gateway Lockdown | **Confirm Preflight Gate B cleared**; approve removal of `public` from PostgREST Exposed Schemas in Dashboard. Trigger official reload. | Product Owner & Tech Lead |
| **Gate 6** | Stage 6 | Final Acceptance | Review negative probe results and positive backend smoke tests; confirm system stability and zero regression. | Tech Lead & Operator |
| **Gate 7** | Track 2 | Performance Track | Independent future approval for `DROP INDEX CONCURRENTLY` and FK covering indexes. | Lead DBA |

---

## 10. Catalog of Preflight Evidence Gates & Repository Divergence Findings

### 1. Preflight Evidence Gates (Diagnostic Queries & Evaluation)

Before advancing to human approval for execution, the following five preflight evidence gates must be independently evaluated:

#### Preflight Gate A — Database Role Authority & Capabilities
* **Status**: **BLOCKED — LIVE EVIDENCE REQUIRED**
* **Rationale**: Production database connection is strictly prohibited during planning. Read-only catalog evidence must be gathered upon authorization.
* **Required Catalog Queries**:
  ```sql
  -- A.1: Server Version & Session Identity
  SELECT current_database(), current_user, session_user, inet_server_addr(), server_version();

  -- A.2: Role Attributes & Bypass Capabilities
  SELECT rolname, rolsuper, rolbypassrls, rolcreaterole, rolcanlogin 
  FROM pg_roles 
  WHERE rolname IN (current_user, 'postgres', 'supabase_admin', 'anon', 'authenticated', 'service_role');

  -- A.3: Role Membership for supabase_admin
  SELECT pg_has_role(current_user, 'supabase_admin', 'MEMBER') AS is_member_of_supabase_admin;

  -- A.4: Object Ownership Authority
  SELECT c.relname, r.rolname AS owner 
  FROM pg_class c 
  JOIN pg_roles r ON r.oid = c.relowner 
  JOIN pg_namespace n ON n.oid = c.relnamespace 
  WHERE n.nspname = 'public' AND c.relkind = 'r' 
  ORDER BY c.relname;
  ```

#### Preflight Gate B — External API Consumers
* **Status**: **BLOCKED — LIVE EVIDENCE REQUIRED**
* **Rationale**: Codebase searches alone cannot prove the absence of third-party webhooks, Zapier/Make automations, Retool/Metabase dashboards, or mobile clients communicating directly with `https://ccejhzadokkjssjiwmxt.supabase.co/rest/v1/*` or `/graphql/v1`.
* **Required Action**: Written sign-off from Product Owner, Engineering Lead, and Customer Operations confirming zero external consumers rely on the Supabase HTTP APIs.

#### Preflight Gate C — Baseline HTTP Behavior
* **Status**: **BLOCKED — LIVE EVIDENCE REQUIRED**
* **Rationale**: Direct remote HTTP probes against production are prohibited until authorized.
* **Required Baseline Probes (Read-Only)**:
  - `curl -i -H "apikey: <ANON_KEY>" https://ccejhzadokkjssjiwmxt.supabase.co/rest/v1/users?select=id`
  - `curl -i -H "apikey: <ANON_KEY>" https://ccejhzadokkjssjiwmxt.supabase.co/rest/v1/projects?select=id`
  - `curl -i -X POST -H "apikey: <ANON_KEY>" -H "Content-Type: application/json" -d '{"query":"{ __schema { types { name } } }"}' https://ccejhzadokkjssjiwmxt.supabase.co/graphql/v1`
  - Evidence Report must capture: UTC Timestamp, HTTP Status, Response Headers, Sanitized Body Structure (zero secrets recorded).

#### Preflight Gate D — Recovery Readiness & PITR
* **Status**: **BLOCKED — LIVE EVIDENCE REQUIRED**
* **Rationale**: Recovery capability cannot be assumed from documentation alone.
* **Required Verification**:
  - Live verification of Point-in-Time Recovery (PITR) active status in Supabase Dashboard.
  - Recording latest restorable timestamp in UTC.
  - Designation of on-duty DBA responsible for restoration in the event of an unrecoverable failure.

#### Preflight Gate E — Execution & Rollback Readiness
* **Status**: **VERIFIED (Documentation & Syntax Validated)**
* **Rationale**: Every SQL statement, micro-batch boundary, lock timeout, statement timeout, post-commit check, and matching rollback has been fully detailed and structurally reviewed.

---

### 2. Comprehensive Repository / Database Divergence Audit

A thorough forensic comparison between the application codebase (`backend/app/domains/`), Alembic migrations (`backend/alembic/versions/`), and the captured Stage 1 database catalog resolves the eight divergent database objects:

| Object Name | Source File / Definition | Migration Exists in Repo? | Migration Applied in Stage 1 DB? | Exists in Production DB Catalog? | Codebase References & Usage | Operational Classification |
| :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| **`developer_apps`** | `backend/app/domains/apps/models.py:13` | **NO** | **NO** | **NO** | Defined as SQLAlchemy declarative model; imported in domain schemas. No active API database queries. | **EXPLAINED — UNMIGRATED FUTURE DOMAIN MODEL**: Feature defined in domain layer but database migration has not been authored or applied. Zero impact on Stage 2 remediation. |
| **`app_installations`** | `backend/app/domains/apps/models.py:37` | **NO** | **NO** | **NO** | Defined as SQLAlchemy model; child relationship to `developer_apps`. | **EXPLAINED — UNMIGRATED FUTURE DOMAIN MODEL**: Feature defined in domain layer; migration not authored. Zero impact on Stage 2 remediation. |
| **`ai_trace_logs`** | `backend/app/domains/analytics/models.py:86` | **NO** | **NO** | **NO** | Defined as SQLAlchemy model for telemetry tracking. | **EXPLAINED — UNMIGRATED FUTURE DOMAIN MODEL**: Telemetry model pending migration authoring. Zero impact on Stage 2 remediation. |
| **`product_images`** | `backend/app/domains/products/models.py:19` | **NO** | **NO** | **NO** | Referenced in `products/service.py` and `image_service.py`. | **EXPLAINED — UNMIGRATED FEATURE MODEL**: Product media model defined in code; migration pending authoring. Zero impact on Stage 2 remediation. |
| **`business_context`** | `backend/app/domains/projects/models.py:90` | **NO** | **NO** | **NO** | Referenced in `enhanced_bot_context.py` and `enhanced_ai_service.py`. | **EXPLAINED — UNMIGRATED FEATURE MODEL**: Bot context model defined in code; migration pending authoring. Zero impact on Stage 2 remediation. |
| **`webhook_endpoints`** | `backend/app/domains/webhooks/models.py:13` | **NO** | **NO** | **NO** | Defined in domain models. | **EXPLAINED — UNMIGRATED FEATURE MODEL**: Outbound webhook models pending migration authoring. Zero impact on Stage 2 remediation. |
| **`webhook_deliveries`** | `backend/app/domains/webhooks/models.py:38` | **NO** | **NO** | **NO** | Defined in domain models. | **EXPLAINED — UNMIGRATED FEATURE MODEL**: Outbound webhook models pending migration authoring. Zero impact on Stage 2 remediation. |
| **`bot_activities`** | Database Table in schema `public` | **YES** (`2025_11_28_2335-034157d2ccf7`) | **YES** | **YES** (Group 6 Table) | Created via Alembic migration; populated by background workers/direct queries. Lacks declarative ORM model in `backend/app/domains/`. | **EXPLAINED — LEGACY MIGRATION WITHOUT DOMAIN ORM MODEL**: Real production table in active database. Fully incorporated into Stage 2 remediation as part of Group 6 (DAC revoked, RLS enabled). |

---

### Execution Packet Status: REMEDIATION REVISION 3.1.0 COMPLETE — HARD STOP IN EFFECT

**NO MUTATIONS WERE EXECUTED**. All proposed statements remain purely informational and subject to formal gate sign-off prior to any future execution.
