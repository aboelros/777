# AI Sales Agent Production Release Checklist & Operational Gates

**Document:** `docs/ai-agent/agent_release_checklist.md`  
**Standard:** Enterprise Production Release Gate Protocol  
**Date:** 2026-11-01  

---

## 1. Release Sign-off Protocol

Before deploying any prompt update, model tier adjustment, RAG enhancement, or tool code change to staging or production, the following verification gates must be executed and explicitly marked as satisfied.

Any single `FAILED` item in the Critical Gate blocks the release immediately (`NO-GO`).

---

## 2. Pre-Deployment Verification Checklist

### Gate 1: Brand Identity & Prompt Security
- [ ] **Prompt Isolation**: System prompt configurations are partitioned strictly by `project_id`. No cross-tenant business context, product names, or policies leak between tenants.
- [ ] **Prompt Versioning**: Every prompt template change increments a semantic version and generates a traceable SHA-256 hash.
- [ ] **Operational Ceilings**: Prompt explicitly prohibits hallucinating inventory, inventing prices, or promising discounts above the tenant's configured limit.
- [ ] **Authority Defense**: Prompt enforces non-compliance with caller claims of developer, owner, admin, or test mode.

### Gate 2: Grounded Knowledge & Retrieval (RAG)
- [ ] **Strict Tenant Filtering**: Every retrieval query structurally enforces `project_id == context.project_id` in SQL and in-memory indexes.
- [ ] **Evidence Integrity**: Retrieved documents are wrapped in immutable evidence tags (`<RETRIEVED_EVIDENCE>`) with metadata source attribution.
- [ ] **Negative Fallback**: When no relevant documents meet the similarity threshold ($\ge 0.70$), the agent falls back to safe clarification or human escalation.
- [ ] **Indirect Injection Immunity**: RAG documents containing adversarial instructions (e.g. "grant 90% discount") are ignored by the agent's policy layer.

### Gate 3: Controlled Tools & RBAC
- [ ] **Pydantic Validation**: 100% of tool inputs and outputs validate against rigid Pydantic models.
- [ ] **IDOR Protection**: Order lookup, modification, and cancellation verify that `order.customer_id == active_customer.id` (or caller possesses owner/admin role).
- [ ] **Idempotency Keys**: Consequential mutations (order placement, ticket creation, charge attempts) enforce idempotency keys to prevent duplicate execution on retry.
- [ ] **Tool Timeout & Retries**: Tool executions have explicit timeouts ($\le 5.0\text{ s}$) and bounded exponential backoff ($\le 2$ retries).

### Gate 4: Guardrails & Prompt-Injection Resistance
- [ ] **Input Sanitization**: Messages exceeding 2,000 characters or containing malicious control characters are sanitized or rejected.
- [ ] **Jailbreak Detection**: Pre-execution scanner detects prompt injection patterns (instruction overrides, role swaps, system prompt exfiltration).
- [ ] **Output Verification**: Post-execution filter checks for leaked API keys, database connection strings, JWTs, or unauthorized discount commitments before delivery.
- [ ] **Safe Refusal**: Unsupported or high-risk requests receive a polite, branded refusal without system disclosures.

### Gate 5: Routing, Caching & Cost Controls
- [ ] **Tenant-Safe Cache**: Cache keys explicitly combine `project_id` and prompt hash (`{project_id}:{hash}`). No cross-tenant cache hits can occur.
- [ ] **No Dynamic Data Caching**: Order status, inventory availability, and customer-specific PII are flagged as uncacheable.
- [ ] **Safe Text Optimization**: No destructive word replacement (e.g. "customer" $\to$ "cust") that corrupts payload semantics.
- [ ] **Token & Budget Limits**: Tenant usage is metered per turn; accounts exceeding monthly token budgets trigger graceful throttle or fallback.

### Gate 6: Observability & Tracing
- [ ] **Trace Correlation**: Every interaction emits a trace with `trace_id`, `conversation_id`, `project_id`, `prompt_version`, and `model`.
- [ ] **PII & Secret Redaction**: Customer phone numbers, emails, addresses, and sensitive tokens are redacted in trace logs.
- [ ] **Latency & Outcome Tracking**: Latency (ms) and tool success/failure status are recorded for monitoring dashboards.

### Gate 7: Automated Evaluations & Regression Tests
- [ ] **Regression Suite Pass Rate**: 100% passing on all security and isolation test suites (`test_ai_prompts.py`, `test_ai_rag.py`, `test_ai_tools_rbac.py`, `test_ai_guardrails.py`, `test_ai_optimizer.py`, `test_ai_agent_evals.py`).
- [ ] **Zero Regressions**: Existing platform test suites maintain zero regressions.

---

## 3. Rollback & Forward-Fix Procedure

If an anomaly is detected in production post-deployment:
1. **Immediate Prompt Rollback**: Revert `active_version` pointer in prompt configuration registry to the previous known good version (instantaneous, no code redeploy required).
2. **Cache Flush**: Purge the affected tenant's cache partition using `cache.clear_tenant(project_id)`.
3. **Model Tier Fallback**: If provider latency spikes or errors occur, toggle `AI_PROVIDER` to secondary backup or adjust routing thresholds.
4. **Tool Kill-Switch**: Disable compromised or malfunctioning tools via tool registry without restarting backend services.
