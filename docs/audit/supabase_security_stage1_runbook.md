# Stage 1 Supabase Security Verification Runbook (Read-Only)

## 1. Document Control & Scope Boundaries

* **Objective**: Define a strictly read-only, non-destructive verification protocol to inspect live Supabase database state, access control, RLS policies, schemas, routines, and indexes.
* **Execution Mode**: **Manual Human-Controlled Execution** via an authorized interactive `psql` session (direct port 5432 or session pooler) using a staged transaction sequence.
* **Destructive Command Ban**: Strictly **ZERO** DDL (`CREATE`, `ALTER`, `DROP`), **ZERO** DML (`INSERT`, `UPDATE`, `DELETE`, `TRUNCATE`), **ZERO** grant modifications (`GRANT`, `REVOKE`), and **ZERO** migrations.
* **Environment Quarantine**: The development database remains **QUARANTINED** and must never be targeted by this runbook.
* **Group Status**: Group 12 is **NOT SIGNED OFF**; Group 13 is **NOT STARTED**.
* **Pre-Verification State**: All live parameters (RLS enforcement, discretionary grants, role attributes, exposed schemas, and index states) are **UNVERIFIED ASSUMPTIONS** until this runbook is manually executed and its output artifacts recorded.

---

## 2. Mandatory Pre-Execution Safety Protocol & Guardrails

Before running any query, the human operator must verify the following safety checks. If any check cannot be confirmed, the operator must **STOP IMMEDIATELY**.

### Check 1: Target Identity & Environment Confirmation
The operator must confirm that the connection endpoint matches the designated staging or production Supabase project, and does not resolve to local development or quarantined endpoints.
* **Target Project Reference**: Confirm the 20-character reference (e.g. `[PROJECT_REF]`).
* **Environment Tier**: Confirm `staging` or `production`.
* **Endpoint Host Verification**: Confirm host is `db.[PROJECT_REF].supabase.co` or an authorized pooler host (`aws-0-[REGION].pooler.supabase.com`), and is **not** the quarantined development database endpoint.

### Check 2: Staged Transaction Read-Only Safeguard & Execution Order
The audit procedure must be executed via one dedicated, interactive `psql` session (connecting to direct port 5432 or the Supabase Session Pooler).

**Execution-Order Defect in Single-Batch Submissions**:
Submitting `BEGIN READ ONLY; SHOW transaction_read_only; [Catalog Queries]; ROLLBACK;` in a single unpaused execution block is defective:
1. The client does not pause execution while the operator inspects the `SHOW` output.
2. Client error guards (such as `\set ON_ERROR_STOP on`) halt execution only when the PostgreSQL engine returns an error status; they do **not** evaluate string query results or stop execution if `SHOW transaction_read_only;` returns `off`.
3. The operator must manually perform a visual gate check between starting the transaction and running catalog queries; the client does not automatically evaluate the displayed value.

**Approved Staged Execution Sequence (Per Protocol)**:
Every protocol must follow a three-stage sequence within the same persistent database connection:

* **Stage A — Start and Verify Read-Only Transaction**:
  ```sql
  BEGIN READ ONLY;
  SHOW transaction_read_only;
  ```
  *Operator Gate Check*: The operator must inspect the output of `SHOW transaction_read_only;`.
  * If the output is **`on`**, proceed to Stage B within the same open transaction and connection.
  * If the output is **`off`**, or if `BEGIN READ ONLY;` fails or produces an unexpected status, execute `ROLLBACK;` immediately and terminate the session. **Do NOT execute catalog queries.**

* **Stage B — Execute Catalog Queries**:
  Only after Stage A is verified, execute the approved catalog `SELECT` statements within the **same connection and still-open read-only transaction**.
  * **No Intervening BEGIN**: Do not issue another `BEGIN` between stages.
  * **No Session Switching**: Do not disconnect, reconnect, or switch sessions between stages.

* **Stage C — Close Transaction**:
  After capturing the required query results, execute:
  ```sql
  ROLLBACK;
  ```
  Verify that the transaction terminates cleanly (`ROLLBACK`), and terminate or clear the dedicated audit session.

**Defense-in-Depth Role Qualification**:
Setting `rolsuper = false` and `rolbypassrls = false` with discretionary `SELECT` grants is **defense in depth** and not by itself an absolute safety guarantee. A truly restricted role boundary requires independent verification across:
* Role membership grants and role-switching capabilities (`SET ROLE` / `rolinherit`) that permit assuming or exercising a more privileged role.
* Membership in predefined broad-privilege roles, such as broad read access (`pg_read_all_data`, presenting confidentiality risk) or broad write capabilities (`pg_write_all_data`, presenting integrity risk).
* Engine-level superuser (`rolsuper`) and Row-Level Security bypass (`rolbypassrls`) flags.
* Explicit direct grants, permissions granted to `PUBLIC`, and object ownership.
* Privileges in non-public schemas (such as `extensions`, `auth`, `storage`, or `cron`).
* Database-level and schema-level creation privileges (`CREATE TEMP TABLE`, schema `CREATE`).
* Execution privileges on callable routines or user-defined functions with side effects.
These properties are **unverified assumptions** until catalog inspection proves their absence; therefore, the operator must never assume that basic role flags alone eliminate operational risk.

> [!WARNING]
> **Boundaries of SQL Read-Only Protection & Engine Mechanics**:
> * **Documented Scope of `READ ONLY`**: Setting transaction mode to `READ ONLY` is a high-level engine restriction that instructs PostgreSQL to disallow table modifications (`INSERT`, `UPDATE`, `DELETE`, `TRUNCATE`) targeting non-temporary tables, and to disallow DDL and privilege-altering commands (`CREATE`, `ALTER`, `DROP`, `GRANT`, `REVOKE`) on permanent database objects.
> * **Temporary Table Exception**: Under official PostgreSQL documentation (Chapter 19, `default_transaction_read_only` and Chapter 13, `SET TRANSACTION`), PostgreSQL explicitly permits temporary tables to be created, modified, and dropped within a read-only transaction (`pg_temp`), and operations on temporary tables are unlogged. A read-only transaction does not prevent every possible disk write.
> * **Sequence Mechanics**: Calling `nextval()` on permanent sequences is blocked within a read-only transaction. However, sequence generators (`nextval`, `setval`) are fundamentally **non-transactional**; if sequences were modified in concurrent or prior transactions, `ROLLBACK` never undoes sequence-state advances.
> * **Isolation & Concurrent Session Activity**: A read-only transaction restricts only the current transaction; it does **not** prevent concurrent transactions in other sessions (such as FastAPI workers, Celery jobs, or replication streams) from modifying data. Under PostgreSQL's default `READ COMMITTED` transaction isolation, successive statements in the same transaction can observe data committed by concurrent transactions between those statements.
> * **Locking Semantics**: Ordinary `SELECT` queries acquire `ACCESS SHARE` locks on referenced relations. `ACCESS SHARE` locks normally coexist with concurrent read and write operations (`SELECT`, `INSERT`, `UPDATE`, `DELETE`), but strictly conflict with `ACCESS EXCLUSIVE` locks (such as those acquired by `ALTER TABLE`, `DROP TABLE`, or `VACUUM FULL`).
> * **Session Side Effects**: If session-level advisory locks (`pg_advisory_lock`) are invoked, they survive transaction `ROLLBACK` and persist until explicitly released or until the connection terminates (unlike transaction-scoped `pg_advisory_xact_lock`). None of the catalog queries in this runbook invoke advisory locks or temporary table operations.
---

## 3. Query Suite & Interpretation Framework

### Protocol 1: Server Identity & Connection Role Audit

#### Purpose:
Identify the connected database catalog, host, session user, and administrative privilege flags (`SUPERUSER`, `BYPASSRLS`).

#### Staged Execution Procedure:

**Stage A — Start and Verify Read-Only Transaction**:
```sql
BEGIN READ ONLY;
SHOW transaction_read_only;
```
*(Operator Gate Check: Inspect result. If output is NOT `on`, execute `ROLLBACK;` and terminate session immediately. Do NOT proceed to Stage B).*

**Stage B — Execute Catalog Queries (in same connection and open transaction)**:
```sql
-- 1A: Basic Server Identity
SELECT
    current_database() AS database_name,
    current_user AS active_role,
    session_user AS login_role,
    inet_server_addr() AS server_ip,
    inet_server_port() AS server_port,
    version() AS postgres_version;

-- 1B: Connection Role Capabilities and Bypass Flags
SELECT
    rolname,
    rolsuper AS is_superuser,
    rolbypassrls AS bypasses_rls,
    rolinherit AS inherits_privileges,
    rolcanlogin AS can_login
FROM pg_roles
WHERE rolname = current_user;
```

**Stage C — Close Transaction**:
```sql
ROLLBACK;
```
*(Verify transaction termination and clean session state).*

#### Evidence Interpretation:
* **What It Proves**: Identifies the exact PostgreSQL role executing the verification and whether that role possesses engine-level administrative bypass flags (`rolsuper`, `rolbypassrls`).
* **What It Does NOT Prove**: Does not prove the role identity or privilege level used by the FastAPI backend in staging or production.
* **Unsafe Conclusions**: Concluding that Row-Level Security is actively enforced against application traffic simply because tables have RLS enabled. If the backend connects as a superuser or a role with `rolbypassrls = true`, PostgreSQL completely bypasses all RLS policies.

---

### Protocol 2: Table RLS Status and Policy Inspection

#### Purpose:
Determine whether Row-Level Security is enabled (`relrowsecurity`) and forced (`relforcerowsecurity`) on each table in schema `public`, and inventory all policy expressions.

#### Staged Execution Procedure:

**Stage A — Start and Verify Read-Only Transaction**:
```sql
BEGIN READ ONLY;
SHOW transaction_read_only;
```
*(Operator Gate Check: Inspect result. If output is NOT `on`, execute `ROLLBACK;` and terminate session immediately. Do NOT proceed to Stage B).*

**Stage B — Execute Catalog Queries (in same connection and open transaction)**:
```sql
-- 2A: Table-Level RLS Configuration
SELECT
    c.relname AS table_name,
    pg_get_userbyid(c.relowner) AS table_owner,
    c.relrowsecurity AS rls_enabled,
    c.relforcerowsecurity AS rls_forced
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE n.nspname = 'public'
  AND c.relkind IN ('r', 'p')
ORDER BY c.relname;

-- 2B: Active Policy Definitions
SELECT
    schemaname,
    tablename,
    policyname,
    permissive,
    roles,
    cmd,
    qual,
    with_check
FROM pg_policies
WHERE schemaname = 'public'
ORDER BY tablename, policyname;
```

**Stage C — Close Transaction**:
```sql
ROLLBACK;
```
*(Verify transaction termination and clean session state).*

#### Evidence Interpretation:
* **What It Proves**: Confirms whether the PostgreSQL engine evaluates row policies on non-bypass roles for tables in schema `public`, and details the exact SQL predicate expressions (`USING` / `WITH CHECK`).
* **What It Does NOT Prove**: Does not prove that the application backend is protected by these policies.
* **Critical Architectural Reality**: Supabase default policies rely on `auth.uid()`, which reads `current_setting('request.jwt.claim.sub', true)`. Because the FastAPI backend issues custom HS256 JWTs and queries PostgreSQL via SQLAlchemy asyncpg without setting session GUCs, `auth.uid()` evaluates to `NULL` for all backend queries.
* **Unsafe Conclusions**: Assuming that RLS policies using `auth.uid()` provide tenant isolation for the application. If RLS is enabled with `auth.uid()` on an unprivileged role, all backend queries return zero rows; if connected under a bypass role, the policies never execute.

---

### Protocol 3: API Role Discretionary Access, ACLs, and Default Privileges

#### Purpose:
Audit effective discretionary permissions across relations, inspect explicit Access Control Lists (ACLs), catalog default privileges, and inventory sequences.

#### Staged Execution Procedure:

**Stage A — Start and Verify Read-Only Transaction**:
```sql
BEGIN READ ONLY;
SHOW transaction_read_only;
```
*(Operator Gate Check: Inspect result. If output is NOT `on`, execute `ROLLBACK;` and terminate session immediately. Do NOT proceed to Stage B).*

**Stage B — Execute Catalog Queries (in same connection and open transaction)**:
```sql
-- 3A: Effective Discretionary Privileges for API Roles and PUBLIC
-- (PostgreSQL privilege inquiry functions support 'public' as a pseudo-role argument)
SELECT
    c.relname AS object_name,
    c.relkind AS object_type,
    r.role_name,
    has_table_privilege(r.role_name, c.oid, 'SELECT') AS can_select,
    has_table_privilege(r.role_name, c.oid, 'INSERT') AS can_insert,
    has_table_privilege(r.role_name, c.oid, 'UPDATE') AS can_update,
    has_table_privilege(r.role_name, c.oid, 'DELETE') AS can_delete
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
CROSS JOIN (VALUES ('anon'), ('authenticated'), ('public')) AS r(role_name)
WHERE n.nspname = 'public'
  AND c.relkind IN ('r', 'v', 'm', 'p')
ORDER BY c.relname, r.role_name;

-- 3B: Explicit Access Control Lists (ACLs) on Relations
-- (Inspects explicit grants; relations with relacl IS NULL rely on PostgreSQL default owner privileges)
SELECT
    c.relname AS object_name,
    c.relkind AS object_type,
    CASE
        WHEN a.grantee = 0 THEN 'PUBLIC'
        ELSE COALESCE(grantee.rolname, a.grantee::text)
    END AS grantee_role,
    pg_get_userbyid(c.relowner) AS object_owner,
    a.privilege_type,
    a.is_grantable
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
CROSS JOIN LATERAL aclexplode(c.relacl) a
LEFT JOIN pg_roles grantee ON grantee.oid = a.grantee
WHERE n.nspname = 'public'
  AND c.relkind IN ('r', 'v', 'm', 'p')
ORDER BY c.relname, grantee_role;

-- 3C: Default Privileges Governing Future Objects
SELECT
    pg_get_userbyid(defaclrole) AS granter,
    CASE
        WHEN defaclnamespace = 0 THEN 'GLOBAL (ALL SCHEMAS)'
        ELSE defaclnamespace::regnamespace::text
    END AS target_schema,
    defaclobjtype AS object_type,
    defaclacl AS default_permissions
FROM pg_default_acl
WHERE defaclnamespace = 'public'::regnamespace
   OR defaclnamespace = 0;

-- 3D: Dedicated Sequence Privileges Inventory
SELECT
    c.relname AS sequence_name,
    r.role_name,
    has_sequence_privilege(r.role_name, c.oid, 'USAGE') AS can_use,
    has_sequence_privilege(r.role_name, c.oid, 'SELECT') AS can_select,
    has_sequence_privilege(r.role_name, c.oid, 'UPDATE') AS can_update
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
CROSS JOIN (VALUES ('anon'), ('authenticated'), ('public')) AS r(role_name)
WHERE n.nspname = 'public'
  AND c.relkind = 'S'
ORDER BY c.relname, r.role_name;
```

**Stage C — Close Transaction**:
```sql
ROLLBACK;
```
*(Verify transaction termination and clean session state).*

#### Evidence Interpretation:
* **What It Proves**:
  * Protocol 3A calculates **effective discretionary table access** for `anon`, `authenticated`, and `public`. For real roles, `has_table_privilege` automatically incorporates direct grants, privileges granted to `public`, and inherited role memberships.
  * Protocol 3B isolates **explicit ACL entries**. In PostgreSQL, `c.relacl IS NULL` indicates that no explicit `GRANT` or `REVOKE` has been issued on that object; it means the relation relies on standard PostgreSQL default privileges (the object owner holds all privileges, and others hold none on tables). It does **not** mean the object has no privileges.
  * Protocol 3C reveals **automatic permissions applied to future objects** created by `defaclrole`.
  * Protocol 3D evaluates sequence-specific privileges separately from table ACLs.
* **What It Does NOT Prove**:
  * SQL-level discretionary access (`can_select = true`) does **not** prove that rows can be exfiltrated via external APIs. If RLS is enabled on the table, the query still returns zero rows unless an RLS policy permits it.
  * Default privileges do **not** describe the current ACL state of existing tables; they only govern tables created in the future under the specified role and schema conditions.
* **Unsafe Conclusions**: Concluding that a table is safe from unauthenticated access simply because `information_schema.role_table_grants` shows no direct grant to `anon`. Grants to `public`, view encapsulation, or sequence accessibility could still permit data interaction.

---

### Protocol 4: PostgREST & GraphQL Surface Verification

#### Purpose:
Determine which schemas are exposed through external HTTP APIs and verify GraphQL reflection extensions.

#### Authoritative Dashboard Source:
1. Navigate to **Supabase Dashboard** $\rightarrow$ **Project Settings** $\rightarrow$ **API** $\rightarrow$ **PostgREST Configuration**.
2. Inspect the **Exposed schemas** setting.
3. Record whether `public` is present in the list of exposed schemas.

#### Supplemental Read-Only SQL (Diagnostics Only):

**Stage A — Start and Verify Read-Only Transaction**:
```sql
BEGIN READ ONLY;
SHOW transaction_read_only;
```
*(Operator Gate Check: Inspect result. If output is NOT `on`, execute `ROLLBACK;` and terminate session immediately. Do NOT proceed to Stage B).*

**Stage B — Execute Diagnostic Catalog Queries (in same connection and open transaction)**:
```sql
-- 4A: Check GraphQL Extension Presence
SELECT
    extname,
    extversion,
    extnamespace::regnamespace AS installed_schema
FROM pg_extension
WHERE extname IN ('pg_graphql', 'pgjwt', 'pghashlib');

-- 4B: Attempt GUC Inspection (Informational Only - Expected to return NULL in standard sessions)
SELECT current_setting('pgrst.db_schemas', true) AS pgrst_db_schemas_guc;
```

**Stage C — Close Transaction**:
```sql
ROLLBACK;
```
*(Verify transaction termination and clean session state).*

#### Evidence Interpretation:
* **What It Proves**: Confirms whether `pg_graphql` is installed.
* **What It Does NOT Prove**: A `NULL` or empty return for `pgrst_db_schemas_guc` **does not prove that schema public is unexposed**. PostgREST reads exposed schemas from daemon configuration or environment variables; database sessions running in Supabase Studio or `psql` do not reliably populate this GUC. The Supabase Dashboard API setting is the only authoritative configuration evidence.
* **GraphQL Reflection Distinction**: `pg_graphql` reflects tables in exposed schemas into a GraphQL schema graph. Schema visibility exposes metadata (table names, column types, and relationships). Querying actual data records through GraphQL is still strictly gated by PostgreSQL table discretionary privileges and active RLS policies.

---

### Protocol 5: Routine Execution and Security Definer Audit

#### Purpose:
Catalog all functions in schema `public`, identifying argument signatures, execution grants to `anon`/`authenticated`/`public`, routine ownership, runtime configuration, and `SECURITY DEFINER` flags.

#### Staged Execution Procedure:

**Stage A — Start and Verify Read-Only Transaction**:
```sql
BEGIN READ ONLY;
SHOW transaction_read_only;
```
*(Operator Gate Check: Inspect result. If output is NOT `on`, execute `ROLLBACK;` and terminate session immediately. Do NOT proceed to Stage B).*

**Stage B — Execute Catalog Queries (in same connection and open transaction)**:
```sql
SELECT
    p.oid AS routine_oid,
    n.nspname AS schema_name,
    p.proname AS routine_name,
    pg_get_function_identity_arguments(p.oid) AS argument_signature,
    p.prosecdef AS is_security_definer,
    pg_get_userbyid(p.proowner) AS routine_owner,
    p.proconfig AS runtime_settings,
    has_function_privilege('anon', p.oid, 'EXECUTE') AS anon_can_execute,
    has_function_privilege('authenticated', p.oid, 'EXECUTE') AS authenticated_can_execute,
    has_function_privilege('public', p.oid, 'EXECUTE') AS public_can_execute,
    -- Check for explicit PUBLIC grant in proacl
    CASE
        WHEN p.proacl IS NULL THEN 'DEFAULT (EXECUTE TO PUBLIC)'
        WHEN EXISTS (
            SELECT 1
            FROM aclexplode(p.proacl) a
            WHERE a.grantee = 0 AND a.privilege_type = 'EXECUTE'
        ) THEN 'EXPLICIT GRANT TO PUBLIC'
        ELSE 'RESTRICTED'
    END AS public_acl_status
FROM pg_proc p
JOIN pg_namespace n ON n.oid = p.pronamespace
WHERE n.nspname = 'public'
ORDER BY p.proname, argument_signature;
```

**Stage C — Close Transaction**:
```sql
ROLLBACK;
```
*(Verify transaction termination and clean session state).*

#### Evidence Interpretation:
* **What It Proves**: Uniquely identifies functions by OID and argument signature, preventing false grouping across overloaded functions. Authoritatively reports whether API roles or `public` have execution rights.
* **What It Does NOT Prove**: A routine flagged with `is_security_definer = true` or `public_can_execute = true` is **not automatically a vulnerability or data leak**.
* **PostgreSQL Function Default Semantics**: In PostgreSQL, when `pg_proc.proacl IS NULL`, default routine permissions apply. Under default permissions, PostgreSQL grants `EXECUTE` to `PUBLIC` on all created functions.
* **Required Follow-up**: Any `SECURITY DEFINER` function callable by `anon` or `public` requires manual inspection of its source code definition (`pg_get_functiondef(routine_oid)`). The operator must verify:
  1. Does the function enforce authorization and tenant scoping internally?
  2. Does the function set a fixed, secure `search_path` (e.g. via `p.proconfig` containing `search_path=public, pg_temp`) to prevent search-path hijacking attacks?

---

### Protocol 6: Subscription Index & Constraint Dissection

#### Purpose:
Dissect constraints and indexes on `subscriptions(user_id)` to resolve the discrepancy between constraint backing indexes and explicit migration/model indexes.

#### Staged Execution Procedure:

**Stage A — Start and Verify Read-Only Transaction**:
```sql
BEGIN READ ONLY;
SHOW transaction_read_only;
```
*(Operator Gate Check: Inspect result. If output is NOT `on`, execute `ROLLBACK;` and terminate session immediately. Do NOT proceed to Stage B).*

**Stage B — Execute Catalog Queries (in same connection and open transaction)**:
```sql
-- 6A: Relational Constraints on subscriptions
SELECT
    c.conname AS constraint_name,
    c.contype AS constraint_type,
    c.conindid::regclass AS backing_index_name,
    pg_get_constraintdef(c.oid) AS constraint_definition
FROM pg_constraint c
WHERE c.conrelid = 'public.subscriptions'::regclass
  AND c.contype IN ('u', 'p');

-- 6B: Complete Index Inventory on subscriptions
SELECT
    i.relname AS index_name,
    am.amname AS access_method,
    idx.indisunique AS is_unique,
    idx.indisvalid AS is_valid,
    idx.indisready AS is_ready,
    idx.indkey::text AS indexed_column_numbers,
    pg_get_indexdef(idx.indexrelid) AS index_definition,
    cons.conname AS backing_constraint_name
FROM pg_index idx
JOIN pg_class i ON i.oid = idx.indexrelid
JOIN pg_am am ON am.oid = i.relam
LEFT JOIN pg_constraint cons ON cons.conindid = idx.indexrelid
WHERE idx.indrelid = 'public.subscriptions'::regclass
ORDER BY i.relname;
```

**Stage C — Close Transaction**:
```sql
ROLLBACK;
```
*(Verify transaction termination and clean session state).*

#### Evidence Interpretation:
* **What It Proves**: Distinguishes relational unique constraints (`contype = 'u'`) from explicit standalone indexes. Shows whether `subscriptions_user_id_key` (the constraint backing index) and `ix_subscription_user` (or `idx_subscription_user`) coexist on the live database, and verifies their validity, readiness, and B-tree access method.
* **What It Does NOT Prove**: Does not prove that an index is safe to drop immediately.
* **Unsafe Actions**: Never execute `DROP INDEX` based solely on a duplicate-index warning. Verification must confirm that application queries, ORM models, foreign-key references, or database triggers do not explicitly depend on that specific index name.

---

### Protocol 7: Foreign-Key B-Tree Index Coverage Audit

#### Purpose:
Inspect system catalogs to identify foreign-key constraints that lack covering, valid, ready, live, non-partial B-tree indexes matching the foreign-key column set as leading key columns (distinguishing exact-prefix from permuted-prefix coverage).

#### Staged Execution Procedure:

**Stage A — Start and Verify Read-Only Transaction**:
```sql
BEGIN READ ONLY;
SHOW transaction_read_only;
```
*(Operator Gate Check: Inspect result. If output is NOT `on`, execute `ROLLBACK;` and terminate session immediately. Do NOT proceed to Stage B).*

**Stage B — Execute Catalog Queries (in same connection and open transaction)**:
```sql
WITH fk_constraints AS (
    SELECT
        c.oid AS constraint_oid,
        c.conname AS fk_name,
        c.conrelid AS table_oid,
        c.conrelid::regclass AS table_name,
        c.conkey AS fk_attnums,
        array_length(c.conkey, 1) AS fk_col_count,
        ARRAY(
            SELECT a.attname
            FROM unnest(c.conkey) WITH ORDINALITY AS k(attnum, ord)
            JOIN pg_attribute a ON a.attrelid = c.conrelid AND a.attnum = k.attnum
            ORDER BY k.ord
        ) AS fk_column_names
    FROM pg_constraint c
    JOIN pg_namespace n ON n.oid = c.connamespace
    WHERE c.contype = 'f'
      AND n.nspname = 'public'
),
covering_btree_indexes AS (
    SELECT
        fk.constraint_oid,
        i.relname AS index_name,
        idx.indisunique AS is_unique,
        CASE
            WHEN (string_to_array(idx.indkey::text, ' ')::int2[])[1:fk.fk_col_count] = fk.fk_attnums
                THEN 'EXACT_PREFIX'
            ELSE 'PERMUTED_PREFIX'
        END AS match_type
    FROM fk_constraints fk
    JOIN pg_index idx ON idx.indrelid = fk.table_oid
    JOIN pg_class i ON i.oid = idx.indexrelid
    JOIN pg_am am ON am.oid = i.relam
    WHERE am.amname = 'btree'
      AND idx.indisvalid = true
      AND idx.indisready = true
      AND idx.indislive = true
      AND idx.indpred IS NULL
      AND idx.indnkeyatts >= fk.fk_col_count
      AND (string_to_array(idx.indkey::text, ' ')::int2[])[1:fk.fk_col_count] @> fk.fk_attnums
)
SELECT
    fk.table_name,
    fk.fk_name,
    fk.fk_column_names,
    COALESCE(string_agg(cov.index_name || ' (' || cov.match_type || ')', ', ' ORDER BY cov.match_type, cov.index_name), 'NONE') AS covering_indexes,
    CASE
        WHEN count(CASE WHEN cov.match_type = 'EXACT_PREFIX' THEN 1 END) > 0 THEN 'EXACT_PREFIX'
        WHEN count(CASE WHEN cov.match_type = 'PERMUTED_PREFIX' THEN 1 END) > 0 THEN 'PERMUTED_PREFIX'
        ELSE 'CANDIDATE_UNINDEXED'
    END AS coverage_status
FROM fk_constraints fk
LEFT JOIN covering_btree_indexes cov ON cov.constraint_oid = fk.constraint_oid
GROUP BY fk.constraint_oid, fk.table_name, fk.fk_name, fk.fk_column_names
ORDER BY coverage_status, fk.table_name, fk.fk_name;
```

**Stage C — Close Transaction**:
```sql
ROLLBACK;
```
*(Verify transaction termination and clean session state).*

#### Evidence Interpretation:
* **What It Proves**: Evaluates B-tree access methods, index validity (`indisvalid`), readiness (`indisready`), liveness (`indislive`), full-table indexing (`indpred IS NULL`), key attributes versus included columns (`indnkeyatts`), and foreign-key column set matching within leading key attributes. Guarantees **exactly one output row per foreign-key constraint** grouped by constraint OID with covering index names and match classifications aggregated.
* **Coverage Classifications**:
  * `EXACT_PREFIX`: Leading index key columns match the foreign-key column sequence in exact order (`(colA, colB)`).
  * `PERMUTED_PREFIX`: The first `k` index key columns contain all foreign-key columns, but in a permuted sequence (e.g., `(colB, colA)` for FK `(colA, colB)`). For equality lookups (such as foreign-key checks during parent row deletions and equality joins), a permuted B-tree index provides practical lookup coverage.
  * `CANDIDATE_UNINDEXED`: No qualifying full, valid, ready, live B-tree index contains the foreign-key columns as leading key attributes.
* **Catalog-Based Coverage Heuristic Note**: This query represents a catalog-based coverage heuristic, not proof that every matching index will be selected by the PostgreSQL query planner in every workload. Planner index selection depends on table cardinality, statistics, cost estimates, and query predicates.
* **Catalog Mechanics Note**: `pg_index.indkey` is of type `int2vector`. Slicing `string_to_array(idx.indkey::text, ' ')::int2[][1:fk.fk_col_count]` compares the leading key attributes against `c.conkey` (`int2[]`). The containment operator `@>` requires that all FK columns appear within the leading `k` key attributes. Expression columns (`0`) and non-key `INCLUDE` attributes (`indnkeyatts`) cannot satisfy this requirement.
* **What It Does NOT Prove**: A status of `CANDIDATE_UNINDEXED` is an inventory finding; it **does not prove a performance bottleneck**.
* **DBA Note**: Foreign-key indexes primarily prevent full-table share locks on the child table during parent row deletions (`ON DELETE CASCADE` or `RESTRICT`) and accelerate joins. If the parent table rarely deletes rows and the child table is write-heavy, creating an index increases write amplification without practical benefit. Real-world query logs and `EXPLAIN ANALYZE` must justify any new index creation.
---

## 4. Runbook Output Artifact Template

The operator must capture the outputs of Protocols 1–7 into a plain text or markdown artifact matching this format before requesting remediation planning:

```markdown
# Stage 1 Verification Output Artifact

- Date of Execution: YYYY-MM-DD HH:MM:SS UTC
- Target Project Reference: [CONFIRMED_NON_SECRET_REF]
- Target Environment Tier: [STAGING / PRODUCTION]
- Read-Only Mode Verified via SHOW transaction_read_only: [YES / NO]

## Output Log:
1. Protocol 1 (Server Identity & Connection Role): [RAW_OUTPUT]
2. Protocol 2 (Table RLS Configuration & Policies): [RAW_OUTPUT]
3. Protocol 3A (Effective Table Privileges): [RAW_OUTPUT]
4. Protocol 3B (Explicit Relation ACLs): [RAW_OUTPUT]
5. Protocol 3C (Default Privileges): [RAW_OUTPUT]
6. Protocol 3D (Sequence Privileges): [RAW_OUTPUT]
7. Protocol 4 (Dashboard PostgREST Schemas & Extensions): [RECORDED_VALUES]
8. Protocol 5 (Routine Execution & Security Definer): [RAW_OUTPUT]
9. Protocol 6 (Subscriptions Constraints & Indexes): [RAW_OUTPUT]
10. Protocol 7 (Foreign Key B-Tree Index Coverage): [RAW_OUTPUT]
```
