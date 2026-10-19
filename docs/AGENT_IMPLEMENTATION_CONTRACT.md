# AI Sales Commander — Master Agent Implementation Contract

**TARGET AUDIENCE:** Engineering Subagents, AI Coders (Antigravity/Cursor/Copilot), and Human Engineers.
**REFERENCE DOCUMENT:** `docs/MASTER_ARCHITECTURE_SPECIFICATION.md`

## 1. Prime Directive
**Do not perform the 77 changes as a giant rewrite. Preserve existing behavior, migrate one bounded domain at a time, and require tests at every phase.**
You are migrating a live system. Act as a precise, surgical infrastructure engineer. Avoid adding new infrastructure before the Phase 0 audit establishes what already exists.

## 2. Ironclad Implementation Rules (The 4 Directives)
1. **Repository reality takes precedence over assumptions (Never Guess):** If the existing implementation contradicts the reference architecture, do not silently normalize it. Inspect the actual code, document the discrepancy, and choose the smallest compatible migration. Never invent models, routes, environment variables, credentials, provider behavior, or infrastructure that cannot be verified from the repository or authoritative documentation.
2. **No security theater:** Introducing a class, decorator, middleware, type, or configuration named after a security concept does not satisfy the requirement unless the underlying execution path enforces it. Security acceptance tests must demonstrate the actual boundary.
3. **Destructive-action gate:** Never delete data, drop tables, rewrite production history, rotate credentials, invalidate sessions, modify external provider state, or perform irreversible migrations when the intended behavior is ambiguous. Stop at the Review gate and report `BLOCKED`, specifying the ambiguity and required decision.
4. **Strict conceptual distinction:** You must strictly differentiate **Authentication** ("Who is this?"), **Authorization** ("Can this actor perform this action on this resource?"), and **Execution Context** ("Under what trusted circumstances is this occurring?").

## 3. Execution Contexts & Authorization
**Tenant-owned data access MUST be authorized and tenant-scoped before query execution.** A raw `project_id`, `user_id`, or resource ID supplied by a caller is never an authorization primitive. Repositories must derive scope from an authenticated/validated execution context or an explicitly authorized system operation.

Every operation must run within one of these three explicit contexts:
1. **User context:** Authenticated user, validated membership, project, role, and permissions.
2. **Service context:** Authenticated internal service, explicit permitted operation, and tenant scope where applicable (e.g., webhook ingestion, async workers).
3. **System context:** Narrowly defined global maintenance operations, restricted to approved services and heavily audited.

## 4. The 6 Migration Gates
Every implementation step must pass through these exact gates sequentially:
1. **Inspect:** Identify the relevant routes, models, repositories, background tasks, and integrations.
2. **Plan:** List files to change, compatibility risks, migration requirements, and tests *before* editing.
3. **Implement:** Make the smallest coherent change within the authorized domain.
4. **Verify:** Run type checks, targeted tests, security tests, and relevant regression tests. Require all *relevant* tests to pass, new tests for changed behavior, and explicit reporting of coverage gaps (do not block on unrelated pre-existing failures).
5. **Review:** Check tenant isolation, secret handling, API compatibility, logging, and rollback procedures.
6. **Report:** Output the Strict Agent Reporting Contract (see Section 7).

## 5. Security & Architecture Invariants
These rules cannot be violated under any circumstances:
1. **RLS Safety:** When enabling PostgreSQL Row-Level Security, you must account for connection pooling and transaction context. Require transaction-scoped tenant context, explicit policies, and tests using actual production roles.
2. **Provider-Specific Webhooks:** Implement provider-specific verification adapters. Reject unverified events unless a documented, secure alternative exists.
3. **Gateway Authentication:** Separate authentication contracts exist for FastAPI-to-gateway requests, gateway-to-FastAPI callbacks, and external provider webhooks.
4. **AI Safety:** The AI MUST NOT directly access models/DB. It can only emit JSON tool requests validated against predefined schemas and policies. Apply strict retry limits, validation-specific retry rules, and per-execution budgets.
5. **Reversibility:** Reversibility requires a tested rollback or forward-fix strategy, including backup and data recovery plans (a naive Alembic downgrade is not always safe after production data has changed).
6. **Audit Logging:** Define an allowlist of audit fields, redaction rules, access controls, and retention policies. Do not indiscriminately log PII or secrets.

## 6. Repository Audit Instructions (Phase 0)
Before changing *any* code for Phase 1, the agent must execute the following audit to baseline the system:
1. **Scan API Routers:** List all existing `FastAPI` routes, their current auth dependencies, and required inputs. Save to `docs/audit/api_baseline.md`.
2. **Scan DB Schema:** Document all SQLAlchemy models and relationships. Save to `docs/audit/db_baseline.md`.
3. **Run Existing Tests:** Execute `pytest`. Record baseline failures, classify them, and isolate blockers before modifying affected domains. Save test coverage gaps.

## 7. Strict Agent Reporting Contract
At the end of *each implementation step*, the coding agent MUST provide the following block in its response:

* **Scope:** What was changed and why.
* **Files:** Exact files added, modified, or removed.
* **Security:** Which invariants were addressed and how they were tested.
* **Tests:** Commands executed and actual results, including failures.
* **Compatibility:** Existing endpoints, payloads, and behaviors affected.
* **Migrations:** Alembic revision, deployment sequence, and rollback/recovery strategy.
* **Remaining risks:** Known gaps, deferred work, and dependencies.
* **Status:** `COMPLETE`, `BLOCKED`, or `PARTIALLY COMPLETE`.
