# Production AI Sales Agent Architecture Specification

**Document:** `docs/ai-agent/production_agent_architecture.md`  
**Target:** Automind AI Sales Agent Runtime  
**Status:** Approved Technical Blueprint  
**Standard:** Master Architecture Specification & The 40 Mandatory Laws  

---

## 1. System Architectural Overview

The production AI Sales Agent runtime transforms the conversational agent from a naive LLM wrapper into an enterprise-grade, deterministic, and securely bounded multi-tenant sales execution system.

```
       Customer Channel (WhatsApp / Telegram / Web / Instagram)
                                   │
                                   ▼
                   FastAPI Controller / Webhook Gateway
                                   │
                                   ▼
             TenantContext & RBAC Layer (Auth, Project ID)
                                   │
                                   ▼
          ┌──────────────────────────────────────────────────┐
          │             AI Agent Runtime Pipeline            │
          │                                                  │
          │  1. Input Sanitization & Jailbreak Guard         │
          │  2. Tenant-Aware Semantic Cache Check            │
          │  3. Model Complexity Router (Fast vs Deep)       │
          │  4. Prompt Builder (Versioned, Isolated Prompts) │
          │  5. Grounded RAG Retriever (Tenant Chunks)       │
          │  6. Multi-Provider LLM Engine (Gemini/OpenRouter)│
          │  7. Controlled Tool Registry & IDOR Guard        │
          │  8. Output Verifier & Safety Redaction           │
          │  9. Observability & Privacy-Safe Tracing         │
          └──────────────────────────────────────────────────┘
                                   │
                   ┌───────────────┴───────────────┐
                   ▼                               ▼
         Domain Repositories             Audited External APIs
     (Products, Orders, Customers)       (Shopify, Stripe, Meta)
```

The AI model operates **inside an untrusted execution sandbox**. It is never treated as a trusted decision-maker or given direct database access. It can only request strictly typed tool calls, which the backend independently validates, authorizes, and executes.

---

## 2. Layer-by-Layer Architectural Design

### Layer 1: Brand Identity & Versioned System Prompts
- **Isolated Configuration:** Every tenant maintains an isolated `BrandProfile` and `SalesPolicy` defining store identity, approved tone, supported channels, return windows, discount limits, and prohibited claims.
- **Strict Delimited Assembly:** Instructions are assembled using strict XML tags (`<SYSTEM_INSTRUCTIONS>`, `<TENANT_POLICY>`, `<RETRIEVED_EVIDENCE>`, `<CUSTOMER_MESSAGE>`).
- **Deterministic Prompt Versioning:** Each prompt configuration is versioned with semantic versioning and a SHA-256 fingerprint, enabling exact provenance tracking across conversation logs.

### Layer 2: Grounded Business Knowledge (RAG Pipeline)
- **Tenant-Scoped Partitioning:** Knowledge records are normalized, chunked, and tagged with tenant `project_id`. Cross-tenant queries are blocked at the repository level.
- **Evidence vs Instruction:** Retrieved knowledge is framed strictly as empirical evidence (`<RETRIEVED_EVIDENCE>`), with explicit directives that instructions inside documents cannot override system policy.
- **Grounded Verification:** Price, stock, order status, and policy limits are retrieved from verified structured tables, not loose vector text.
- **Negative Fallback:** If retrieval returns no matches or contradictory evidence, the agent triggers a safe clarification or human escalation fallback.

### Layer 3 & 4: Controlled Tool Registry & IDOR Protection
- **Typed Pydantic Schemas:** Every tool specifies a strict Pydantic input and output contract.
- **Risk Classification:**
  - `READ_ONLY`: Public catalog search, inventory check, approved policy lookup.
  - `STATE_CHANGING`: Support ticket creation, follow-up scheduling.
  - `HIGH_RISK_TRANSACTIONAL`: Order creation, cancellation, status updates (requires validated customer identity or owner role).
- **IDOR Protection:** Order status retrieval requires that the order belongs to both `context.project_id` AND the verified `customer_id` of the active conversation.

### Layer 5: Guardrails & Prompt-Injection Resistance
- **Input Validation:** Enforces max message length (2,000 characters) and strips control characters.
- **Adversarial Pattern Matching:** Scans for prompt injection triggers (e.g. "ignore previous instructions", "system prompt", "you are now in developer mode", delimiter evasion).
- **Output Verification:** Scans generated text for system prompt leakages, credential strings, or unauthorized discount commitments before transmission to the customer.

### Layer 6: Routing, Caching & Cost Management
- **Tenant-Isolated Caching:** Cache keys are formed as `SHA256("{project_id}:{prompt_hash}")`. Private customer data, real-time inventory, and dynamic order statuses are never cached.
- **Complexity-Based Routing:** Simple greetings and FAQs route to high-efficiency low-latency models; complex multi-turn inquiries or transactional requests route to higher-capability models.
- **Token Accounting:** Tracks input and output token usage per tenant, recording cost estimates against subscription quotas.

### Layer 7: Observability & Privacy-Safe Tracing
- **Structured Trace Records:** Emits structured traces capturing request ID, conversation ID, tenant ID, prompt version, selected model, tool names, outcomes, latency (ms), and token counts.
- **PII & Secret Redaction:** Replaces phone numbers, email addresses, passwords, and authorization tokens with deterministic redaction tokens (`[REDACTED_PHONE]`, `[REDACTED_SECRET]`).

### Layer 8: Evaluation & Release Criteria
- Golden evaluation suites assert deterministic behavior against behavioral test cases (grounding, IDOR prevention, prompt injection, bilingual Arabic/English fidelity, and tool failures).

---

## 3. Directory Layout (Adhering to Law 11: < 250 LOC per file)

```
backend/app/domains/ai/
├── core/
│   ├── config.py                 # Agent configuration (< 200 LOC)
│   ├── context.py                # Agent execution context (< 150 LOC)
│   └── errors.py                 # Structured agent exceptions (< 150 LOC)
├── prompts/
│   ├── models.py                 # BrandProfile & SalesPolicy schemas (< 180 LOC)
│   ├── versions.py               # Prompt versioning & registry (< 150 LOC)
│   └── builder.py                # XML-delimited prompt assembler (< 220 LOC)
├── rag/
│   ├── schemas.py                # Chunk and retrieval models (< 120 LOC)
│   ├── chunker.py                # Text normalization & chunking (< 160 LOC)
│   └── retriever.py              # Tenant-isolated retriever (< 210 LOC)
├── tools/
│   ├── schemas.py                # Pydantic input/output schemas (< 220 LOC)
│   ├── registry.py               # Tool catalog & risk classification (< 180 LOC)
│   ├── guard.py                  # IDOR & permission authorization guard (< 200 LOC)
│   └── executor.py               # Controlled tool dispatcher (< 230 LOC)
├── guardrails/
│   ├── sanitizer.py              # Input size & char normalization (< 160 LOC)
│   ├── injection_detector.py     # Adversarial pattern matching (< 190 LOC)
│   └── output_verifier.py        # Leakage & policy compliance guard (< 180 LOC)
├── optimizer/
│   ├── cache.py                  # Tenant-safe semantic cache (< 190 LOC)
│   ├── router.py                 # Model complexity router (< 180 LOC)
│   └── cost_tracker.py           # Token usage and pricing metrics (< 160 LOC)
├── observability/
│   ├── models.py                 # Trace data contracts (< 140 LOC)
│   ├── redact.py                 # PII & secret redactor (< 150 LOC)
│   └── tracer.py                 # Request trace emitter (< 200 LOC)
└── agent.py                      # Production AI Sales Agent orchestrator (< 240 LOC)
```
