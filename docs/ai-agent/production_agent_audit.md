# Production AI Sales Agent Subsystem Audit

**Document:** `docs/ai-agent/production_agent_audit.md`  
**Target:** Automind AI Sales Agent Runtime  
**Audit Standard:** Master Architecture Specification & Production Engineering Principles  
**Date:** 2026-11-01  

---

## Executive Summary

An exhaustive code-level audit was conducted across the backend AI services, API endpoints, domains, database models, worker tasks, and test suites. 

While the application exhibits strong tenant isolation in certain migrated repositories (`app/domains/ai/repository.py`) and basic multi-provider interfaces (`app/domains/ai/providers/gemini.py`, `openrouter.py`), the runtime remains vulnerable to severe production defects:
1. **Unverified Retrieval (RAG)**: The existing `RAGService` does not execute semantic or keyword similarity searches; it retrieves arbitrary top-N records from the tenant's knowledge table. Embeddings are generated on an ad-hoc local transformer and discarded without storage or vector querying.
2. **Untyped & Incomplete Tool Execution**: Tool calls lack formal Pydantic schema validation, permission checks, and customer resource ownership checks (e.g. order lookup by number permits IDOR between customers within the same tenant).
3. **Cross-Tenant Caching Hazard**: The `AIOptimizer` cache key is computed without the tenant/project ID, risking cross-tenant response leakage.
4. **Missing Observability & Evals**: No structured `AIExecution` trace logging, per-step latency measurement, token accounting, or automated behavioral/adversarial evaluation suites exist.
5. **Prompt Security Gaps**: System prompts mix instructions, untrusted retrieved documents, and customer inputs with simple markdown delimiters, vulnerable to prompt injection and jailbreaks.

---

## 1. Capability Classification Matrix

| Capability Dimension | Classification | Primary Files / Components | Verification Evidence / Existing Tests | Critical Findings |
| :--- | :--- | :--- | :--- | :--- |
| **System Prompts & Assembly** | `PARTIAL` | `app/core/prompts.py`<br>`app/core/ai_personas.py`<br>`app/domains/ai/orchestrator.py:320-372` | None. Untested in automated suites. | Hardcoded string templates. No prompt versioning or SHA tracking. Instructions concatenated directly with unverified customer inputs and raw product dumps. |
| **LLM Providers & Fallbacks** | `PARTIAL` | `app/domains/ai/providers/gemini.py`<br>`app/domains/ai/providers/openrouter.py`<br>`app/domains/ai/orchestrator.py:374-412` | None for fallback logic. Mock unit tests only for config parsing. | Basic round-robin rotation for Gemini API keys. Fallback between Gemini and OpenRouter is a single nested try-block. No exponential backoff, circuit breaking, or jittered retries. |
| **Tenant & Conversation Context** | `PARTIAL` | `app/core/context.py`<br>`app/domains/ai/orchestrator.py:47-57`<br>`app/domains/messages/repository.py` | `tests/test_tenant_security.py`<br>`tests/test_ai_security.py` | `TenantContext` safely scopes project boundaries at repository level. However, conversation history lacks token budgeting and window truncation. |
| **Catalog, Orders & Policy Data** | `PARTIAL` | `app/domains/products/repository.py`<br>`app/domains/orders/repository.py`<br>`app/domains/ai/models.py:BotInstruction` | `tests/test_order_security.py` | Products dumped into prompt as plain text. Operational policies (shipping, return windows, max refund limits) are free-text instructions without deterministic schemas. |
| **Retrieval / RAG Pipeline** | `MISSING` | `app/domains/ai/rag_service.py`<br>`app/domains/ai/models.py:KnowledgeBase` | None. Embeddings never asserted in tests. | Severe gap: `rag_service.py` fetches the first 3 active items using SQL `LIMIT 3` without query filtering. No vector indexing or pgvector integration in database schema. |
| **Controlled Tools & Execution** | `PARTIAL` | `app/domains/ai/tool_executor.py`<br>`app/domains/ai/orchestrator.py:560-660`<br>`app/domains/ai/providers/gemini.py:862-875` | `tests/test_ai_security.py` (limited to repository checks) | Tool registry missing. Handlers lack Pydantic input/output schemas. `get_order_status` does not verify customer ownership (`customer_id`), allowing customer-to-customer data exposure. |
| **Authorization & Tenant Isolation** | `PARTIAL` | `app/api/dependencies/tenant.py`<br>`app/domains/ai/service.py`<br>`app/domains/ai/repository.py` | `tests/test_ai_security.py` (5 passing tests) | Project-level isolation is enforced on DB writes. Customer-level and role-level (RBAC) tool invocation checks are missing. Model proposes actions without permission gates. |
| **Guardrails & Prompt Injection** | `MISSING` | `app/services/ai_confidence.py`<br>`app/domains/ai/orchestrator.py` | None. No adversarial security tests. | `HallucinationGuard` class exists in `ai_confidence.py` but is never invoked to sanitize or block model outputs. No input sanitization for delimiter escapes or jailbreak vectors. |
| **Caching & Rate Limiting** | `MISSING` | `app/services/ai_optimizer.py`<br>`app/services/subscription_service.py` | None. | `AIOptimizer` cache is an unauthenticated in-memory dict. Key generation uses `hash(prompt + context)` with NO `project_id`, enabling cross-tenant cache pollution. Naive string replacement corrupts words. |
| **Observability & Tracing** | `MISSING` | `app/domains/ai/models.py:BotActivity`<br>`app/workers/tasks/ai_tasks.py` | `tests/test_bot_activity_model.py` | `BotActivity` logs basic textual descriptions. No structured trace entities (`AIExecution`, `AIToolCall`), no correlation IDs, no prompt version tags, and no PII redaction policy. |
| **Cost & Latency Instrumentation** | `MISSING` | `app/domains/ai/providers/gemini.py:222-273` | None. | Rough heuristic `len(text) // 4` used for tokens. No actual model token counts from API response metadata recorded. Latency is not timed per LLM call or tool execution. |
| **Automated Evaluation Suite** | `MISSING` | `backend/tests/` | None. Zero eval tests for accuracy, grounding, or safety. | No golden dataset, prompt regression suite, multilingual benchmark (Arabic/English), or policy enforcement evaluations exist in repository. |

---

## 2. Detailed Technical Audit Findings

### 2.1 System Prompts and Prompt Assembly
- **Location:** `backend/app/core/prompts.py` (`MASTER_SALES_AGENT_PROMPT`), `backend/app/domains/ai/orchestrator.py` (lines 320–372).
- **Architecture:** The orchestrator concatenates several multi-line strings:
  `f"{system_prompt}\n{shop_guidelines}\n{instructions_context}\n{product_catalog_text}{knowledge_context}{catalog_instruction}"`
- **Vulnerabilities:**
  - Untrusted data (customer messages, external webhook data, scraped knowledge) is concatenated into the prompt without rigid boundary delimiters (e.g. XML tags or structured system/developer roles).
  - Prompts contain hardcoded external company and founder names in `WEB_ASSISTANT_BEHAVIOR_RULES` (`backend/app/domains/ai/providers/gemini.py:35-36`), violating tenant isolation and white-label neutrality.
  - No semantic versioning or hashing of prompts. When instructions change in the database or code, there is no way to trace which prompt version generated a historical customer message.

### 2.2 LLM Providers, Fallbacks, and Routing
- **Location:** `backend/app/domains/ai/providers/gemini.py`, `backend/app/domains/ai/providers/openrouter.py`.
- **Implementation:**
  - `GeminiClient` supports up to 100 round-robin keys via `GEMINI_API_KEY_1..100`.
  - Fallback in `orchestrator.py` simply executes:
    ```python
    if response_data.get("error") or not response_data.get("text"):
        # switch to openrouter / gemini
    ```
- **Gaps:**
  - No timeout deadline is propagated to HTTP calls.
  - Failures trigger an immediate single retry against the secondary provider without jitter, exponential backoff, or circuit breaking.
  - Routing does not evaluate request complexity: simple greetings and complex multi-item order disputes hit the exact same model tier.

### 2.3 Grounded Knowledge and RAG Pipeline
- **Location:** `backend/app/domains/ai/rag_service.py`.
- **Implementation:**
  ```python
  async def retrieve_context(self, context: Union[TenantContext, UUID], query: str, limit: int = 3) -> str:
      async with self.uow as uow:
          kb_repo = KnowledgeBaseRepository(uow.session)
          kb_items = await kb_repo.get_active_by_context(tenant_ctx, limit=limit)
  ```
- **Flaws:**
  - The repository call `get_active_by_context` retrieves items using `SELECT ... WHERE project_id = :project_id AND is_active = true LIMIT :limit` completely ignoring the `query` parameter!
  - `SentenceTransformer('all-MiniLM-L6-v2')` is loaded in memory if installed, but `generate_embedding()` is never called during storage, querying, or ingestion.
  - The database table `knowledge_base` has no vector column, no similarity index, and no document chunking.

### 2.4 Controlled Tools and Action Security
- **Location:** `backend/app/domains/ai/tool_executor.py` and `backend/app/domains/ai/orchestrator.py:560-660`.
- **Implementation:**
  - `ToolExecutor` provides 3 methods: `search_products`, `get_order_status`, `check_inventory`.
  - `orchestrator.py` implements a separate parallel switch with 12 functions.
- **Security Deficiencies:**
  - **IDOR in Order Lookup:** In `tool_executor.py:52-65`, `get_order_status` takes `order_number` and executes `OrderRepository.get_by_number(project_id, order_number)`. It does NOT require or verify `customer_id`. Any customer who knows or guesses another customer's order number in that tenant can read the complete order amount, date, and status.
  - **Lack of Typed Schemas:** Tool arguments are accepted as untyped `Dict[str, Any]` without Pydantic validation before execution.
  - **Missing Authorization Gates:** Destructive or state-changing actions (such as `update_order_status` and `create_order`) are routed without verifying whether the caller has user, admin, or customer authorization.
  - **No Tool Policy / Risk Classification:** Read-only actions (catalog search) and financial/order-modifying actions share the same direct dispatch pipeline without human escalation or confirmation gates.

### 2.5 Caching and Rate Limiting
- **Location:** `backend/app/services/ai_optimizer.py`.
- **Flaws:**
  - In `AIOptimizer._generate_cache_key`:
    ```python
    cache_string = f"{prompt}:{json.dumps(context or {}, sort_keys=True)}"
    return hashlib.md5(cache_string.encode()).hexdigest()
    ```
    The cache key lacks `project_id`. If Customer X from Store A asks "What is your refund policy?", Store B's customer could receive Store A's cached response.
  - In `AIOptimizer.optimize_prompt`:
    Arbitrary substring replacement (`"customer": "cust"`, `"product": "prod"`, `"message": "msg"`) mutates valid JSON schemas, URLs, and natural language text, corrupting prompt semantics.

### 2.6 Observability, Tracing, and Latency
- **Location:** `backend/app/domains/ai/models.py:BotActivity`.
- **Flaws:**
  - Traces do not capture model latency, token breakdown (prompt vs completion), prompt template version, tool invocation inputs/outputs, or confidence metrics.
  - Standard logging risks writing unredacted customer phone numbers, messages, and shipping addresses to application logs.

---

## 3. Audit Verdict & Priority Engineering Backlog

The current AI sales agent implementation is **NOT PRODUCTION-READY** (`NO-GO` in its current state).

### Immediate Required Engineering Priorities:
1. **Layer 1 (Prompts & Brand Identity):** Implement tenant-isolated, versioned prompt configurations with strict operational boundaries (no price hallucinations, explicit refund/discount policy ceilings).
2. **Layer 2 (Grounded Knowledge / RAG):** Implement a real, tenant-scoped semantic retrieval pipeline with chunking, metadata attribution, vector similarity, and negative fallback when evidence is missing.
3. **Layer 3 & 4 (Controlled Tools & RBAC):** Implement typed Pydantic tool schemas, tool registry, risk levels, and server-side resource ownership validation (solving IDOR in order tracking and inventory).
4. **Layer 5 (Guardrails & Prompt Injection Defense):** Implement structural prompt delimiters, input size checks, adversarial detection, and output verification.
5. **Layer 6 (Routing, Caching & Cost Control):** Fix multi-tenant cache keys (`tenant_id:hash`), remove destructive text replacements, and add token cost tracking.
6. **Layer 7 (Observability & Tracing):** Implement structured, privacy-safe tracing records capturing prompt versions, latencies, tokens, and tool outcomes.
7. **Layer 8 (Evaluations):** Implement comprehensive regression and adversarial test suites covering business rules, bilingual Arabic/English queries, IDOR attempts, and prompt injections.
