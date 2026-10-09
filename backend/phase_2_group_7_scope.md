# Phase 2 Group 7 Scope — AI Assistant / Training Security

### 1. Provenance
* **Original Group 7**: `NOT RECOVERABLE`
* **Why it is unavailable**: The explicit label "Group 7" does not exist in any historical artifact, document, or git commit in the entire repository. The highest recovered group was Group 5. Group 6 was a reconstruction, and Group 7 is a reconstruction.
* **Evidence for AI Assistant / Training**: `RECOVERED HISTORICAL FACT` — The surviving `remaining_security_audit.md` explicitly lists "External Side Effect Before Auth (High Risk)" in `enhanced_bot.py` and "Caller-supplied IDs as Primitives (Medium Risk)" in `bot_training.py` and `social_media.py`. It explicitly designates AI Assistant / Training as the next largest risk surface containing 33 routes and 10 direct SQL bypasses.

### 2. Reconstructed Objective
`RECONSTRUCTED GROUP 7 SCOPE`
Strictly harden the AI Assistant / Training domain to eliminate raw SQL bypasses, enforce the `TenantContext -> tenant-scoped repository SQL -> service` architectural pattern, and stop unauthorized external AI side-effects or cross-tenant data access from occurring before strict boundaries are proven at the DB layer.

### 3. Boundary Definition

#### IN SCOPE
**API Routers (Require Context Injection and Repo Usage)**
* `backend/app/api/v1/assistant.py`
* `backend/app/api/v1/bot_training.py`
* `backend/app/api/v1/enhanced_bot.py`
* `backend/app/api/v1/knowledge.py`

**AI Domain Services & Repositories (Require Context Propagation)**
* `backend/app/domains/ai/orchestrator.py`
* `backend/app/domains/ai/service.py`
* `backend/app/domains/ai/rag_service.py`
* `backend/app/domains/ai/repository.py`

**Background Workers (Require Context Initialization)**
* `backend/app/workers/tasks/ai_tasks.py`

#### EXPLICITLY OUT OF SCOPE
* **Social Media / Campaigns**: `backend/app/api/v1/social_media.py`, `drip_campaigns.py` (To be handled in a subsequent group).
* **Payments and Invoicing**: Handled in a subsequent group.
* **Database Schemas**: Models in `backend/app/domains/ai/models.py` already possess `project_id`. Do not modify database schemas.
* **New AI Features**: Do not add AI functionality.
* **Model/Prompt Quality**: Do not modify AI prompt logic or upgrade LLM functionality. Focus strictly on isolation and authorization.
* **Groups 1-6 Implementations**: Orders/Commerce & Integrations code must not be refactored further.

### 4. Security Audit & Vulnerabilities Addressed
`REPOSITORY-BASED EVIDENCE`

* **Raw DB Access & Bypass**: The identified AI routers contain over 30 instances of `db.execute(select(...))` combined with `verify_project_access`, circumventing the repository layer.
* **Cross-Domain Violations**: `AIOrchestrator` directly fetches `Order`, `CustomerProfile`, `Message`, and `Integration` records via raw SQL instead of routing through the secured repositories established in Groups 1–6.
* **Missing AI Execution Boundaries**: The AI model is untrusted. `AIOrchestrator` relies on caller-supplied or AI-generated `customer_id` and `order_id` values to fetch database records. Functions like `_get_customer` execute `select(CustomerProfile).where(CustomerProfile.id == customer_id)` WITHOUT enforcing `project_id`. This allows a malicious AI prompt or background task to leak Cross-Tenant data into the execution context and send it to external providers (Gemini/Shopify).
* **Worker Identity Desync**: Background tasks in `ai_tasks.py` instantiate raw async database sessions and pass unverified queue payloads (`project_id`, `customer_id`) directly to services without establishing a trusted `TenantContext` boundary.

### 5. Required Architectural Changes
`RECONSTRUCTED GROUP 7 SCOPE`
* **TenantContext Integration**: Refactor `backend/app/domains/ai/repository.py` to inherit `TenantContext` semantics so `project_id` is structurally applied to `BotInstruction`, `KnowledgeBase`, and `ModelTraining` queries.
* **Strict Repository Pattern**: Remove all raw SQLAlchemy queries from the four AI routers. Delegate data access to the updated AI repositories.
* **Cross-Domain Repository Contract**: The `AIOrchestrator` must stop using raw SQL to access `Order`, `CustomerProfile`, `Message`, and `Integration`. It must be injected with `TenantContext` and rely exclusively on `OrderRepository`, `CustomerProfileRepository`, etc., ensuring that even if an AI model guesses a valid UUID for another tenant, the repository will return `None`.
* **Worker Security Boundary**: Tasks in `ai_tasks.py` must explicitly initialize `TenantContext(project_id=project_id, roles=["system"])` before dispatching to the `AIOrchestrator`.

### 6. Security Acceptance Criteria
`RECONSTRUCTED GROUP 7 SCOPE`

**Same tenant**
* Tenant A → Tenant A training data / AI features → ALLOW

**Cross tenant**
* Tenant A → Tenant B training data / AI features → DENY (404 Not Found)

**Missing tenant context**
* Route or service called with No `TenantContext` → DENY / fail closed

**Forged project ID**
* Caller supplies a valid token but requests `project_id` they do not own → DENY (403 Forbidden)

**AI-generated resource ID**
* The LLM outputs a function call with an `order_id` or `customer_id` belonging to Tenant B. The orchestrator attempts to load it → DENY (Repository returns None, AI execution halted or error returned to LLM).

**Worker replay / forged task**
* Task arguments reference `project_id = A`, but `customer_id = B`. The worker attempts to load the customer profile via `CustomerProfileRepository` → DENY (Repository returns None, task gracefully aborts without leaking data).

**Training/Knowledge isolation**
* Tenant A cannot read/write/delete Tenant B's `BotInstruction` or `KnowledgeBase` records via any API endpoint.

**External provider**
* Unauthorized tenant data must never reach Gemini, OpenAI, or Shopify. An external side-effect is only triggered after all local DB queries have passed repository-level tenant checks.

RECONSTRUCTED GROUP 7 SCOPE — READY FOR IMPLEMENTATION
