# Master Architecture Specification

## 1. Core architectural principles

### Principle 1 — The application is authoritative
```text
AI ≠ authority
Frontend ≠ authority
Gateway ≠ authority
External provider ≠ authority
```
Only the backend domain layer can authorize and mutate business state.
```text
Frontend → API → Authentication → Authorization → Domain Service → Policy → Repository / External Adapter
```

### Principle 2 — Every resource belongs to a tenant
Every tenant-owned resource must have an ownership chain:
`User → Membership → Project → Resource`
A request must never be able to select a resource and bypass that chain.

### Principle 3 — External systems are untrusted
Treat WhatsApp, Meta, Telegram, Shopify, TikTok, customer messages, product descriptions, comments, uploaded files, webhook payloads, and AI output as **untrusted input**.
Everything entering the system gets:
`authentication → validation → normalization → authorization → processing`

---

## 2. Trust boundaries
```text
                     UNTRUSTED
                         │
     ┌───────────────────┼────────────────────┐
     │                   │                    │
 Customer             External APIs       Browser
     │                   │                    │
     └───────────────────┼────────────────────┘
                         │
                    TRUST BOUNDARY
                         │
                         ▼
                ┌──────────────────┐
                │     FastAPI      │
                │   API / BFF      │
                └────────┬─────────┘
                         │
                  AUTHORIZATION
                         │
                         ▼
                ┌──────────────────┐
                │  Domain Layer    │
                │                  │
                │ Tenant + RBAC    │
                │ Business Rules   │
                └────────┬─────────┘
                         │
                  TRUST BOUNDARY
                         │
            ┌────────────┼────────────┐
            ▼            ▼            ▼
       PostgreSQL      Workers      Tool Layer
```
The AI sits **inside an isolated execution boundary**, not alongside the domain authority.

---

## 3. Recommended backend structure
```text
app/
├── core/
├── identity/
├── tenants/
├── messaging/
├── crm/
├── commerce/
├── integrations/
├── ai/
│   ├── agent.py, context.py, policies.py
│   ├── providers/
│   ├── tools/ (registry.py, executor.py, messaging.py, commerce.py)
│   └── safety/ (input.py, output.py, prompt_injection.py)
├── jobs/
├── analytics/
├── audit/
└── api/
```
**Routers don't contain business logic.**

---

## 4. Request lifecycle
Every authenticated API request follows:
`HTTP Request → Request ID → Authentication → User → Project Resolution → Membership → Permission Check → Input Validation → Domain Service → Business Rules → Repository / Adapter → Audit Event → Response`

---

## 5. Tenant context
Create a first-class object:
```python
class TenantContext:
    user_id: UUID
    project_id: UUID
    role: Role
    permissions: set[str]
```
Services receive `tenant=tenant_context` rather than raw IDs.

---

## 6. Database defense-in-depth
Application-level tenant filtering is **Required**.
Database-level isolation (Row-Level Security) is **Strongly recommended**.

---

## 7. RBAC should become ABAC where necessary
**RBAC + policy-based authorization:**
`Role + Resource + Action + Context → Policy Engine → ALLOW / DENY / REQUIRE_APPROVAL`

---

## 8. Message model
Explicitly separate: `Conversation`, `Message`, `MessageDelivery`, `MessageEvent`.

---

## 9. Provider-neutral messaging interface
Create a `MessagingProvider(Protocol)` for WA, Meta, Telegram so the domain doesn't care how messages are delivered.

---

## 10. WhatsApp Go gateway
The Go service is a **protocol adapter**, not a second backend. It owns sessions, connections, and events. It does NOT own customers, orders, AI, or business rules.

---

## 11. Gateway security
Use mTLS or HMAC service authentication + timestamp + nonce + request ID. The gateway should be on a private network, not exposed to the public internet.

---

## 12. Webhook architecture
All providers go through a common webhook pipeline:
`Webhook endpoint → verify signature → validate timestamp → identify provider → normalize event → calculate event ID → idempotency check → WebhookEvent → Queue → Event Handler`

---

## 13. Idempotency everywhere
Use for message sending, order mutation, refund, integration creation, sync jobs, AI tool execution, webhook processing.

---

## 14. Outbox + inbox patterns
**INBOX** → protects against duplicate inbound events.
**DOMAIN** → database transaction.
**OUTBOX** → protects outbound domain events (worker handles external API).

---

## 15. AI Agent Runtime
A completely separate subsystem handling Context, Memory, Prompt Policies, Model Routing, Tool Registry/Executor, Output Validation, Cost Control, and Human Handoff.

---

## 16. AI execution should be traceable
Create `AIExecution` and `AIToolCall` records linking the conversation to model calls, tool calls, status, and duration.

---

## 17. Tool registry
Every tool must be registered explicitly with a risk level and schema. The AI never dynamically discovers arbitrary Python functions.

---

## 18. Tool execution pipeline
`Gemini requests tool → Parse JSON → Schema validation → Tenant authorization → Permission check → Risk policy (LOW=execute, MEDIUM=policy eval, HIGH=human approval)`

---

## 19. AI prompt injection defense
Create explicit boundaries: `SYSTEM POLICY → BUSINESS POLICY → TOOL POLICY → CONTEXT DATA → CUSTOMER CONTENT`.
Customer content must never be interpreted as policy.

---

## 20. AI data minimization
Don't send the entire database context to Gemini. Send only relevant conversation, customer fields, and specific business instructions.

---

## 21. Memory architecture
Separate Conversation history, Customer facts, Business knowledge, AI instructions, and temporary context. Never mix them into one vector database indiscriminately.

---

## 22. Human handoff race condition
When human takeover occurs, `conversation.ai_mode = SUSPENDED`. Every AI execution checks the current state **again immediately before sending**.

---

## 23. Conversation concurrency
Use optimistic concurrency (`conversation_id` + `version`) to prevent stale AI executions from modifying newer state.

---

## 24. Celery queues
Explicitly create queues and workers for AI, Messaging, Webhooks, Integrations, Analytics, Maintenance, and Critical tasks to scale independently.

---

## 25. Retry policy
Use exponential backoff + jitter. Don't retry 400, 401, 403. Retry 429, 500, timeouts, and invalid AI output.

---

## 26. Dead-letter queue
After N failures, move jobs to a DLQ, storing payload, error, and attempts, and expose to admins.

---

## 27. Integration sync engine
Create a generic `SyncEngine` with cursor management, retry, rate-limit handling, checkpointing, and reconciliation.

---

## 28. Reconciliation
Run periodic reconciliation (local state vs provider state) to prevent silent corruption.

---

## 29. OAuth
Create a generic `OAuthManager` with provider adapters (Meta, TikTok, Shopify). Do not duplicate OAuth logic.

---

## 30. Secrets
Use a Secret Manager in production. Database stores encrypted integration tokens. No production secrets in `.env` or source code.

---

## 31. Security logging
Create a dedicated, searchable security event stream (AUTH_LOGIN, PERMISSION_DENIED, WEBHOOK_SIGNATURE_FAILURE, AI_POLICY_BLOCK, etc.).

---

## 32. API error handling
Don't leak internal exceptions. Return generic business/system error codes and log the stack trace internally against a request ID.

---

## 33. API versioning
Keep `/api/v1` and use `/api/v2` when breaking changes become necessary.

---

## 34. Frontend security
Don't put secrets into `VITE_*` (except public keys). The frontend receives only short-lived authenticated tokens.

---

## 35. Frontend authorization
UI hiding (`if (!isAdmin) hideDeleteButton()`) is UX. Actual authorization must happen server-side.

---

## 36. Content Security Policy
Deploy a strong CSP, HSTS, X-Content-Type-Options, Referrer-Policy, and Permissions-Policy.

---

## 37. WAF / edge protection
Use a WAF (e.g., Cloudflare) for DDoS, basic bot filtering, rate limiting, and TLS. WAF is not the authorization system.

---

## 38. Database indexes
Index heavily queried patterns, but verify with actual query plans rather than blindly indexing everything.

---

## 39. Database migrations
Use Alembic strictly. Generate → review → test on copy → backup → migrate → health check.

---

## 40. Analytics separation
Eventually move analytics off the transactional DB to an Analytics pipeline/warehouse via domain events.

---

## 41. Security testing matrix
Automate Tenant tests, Role tests, AI tests (prompt injection, human takeover, invalid tools), Gateway tests, and OAuth tests.

---

## 42. Chaos testing
Deliberately break dependencies (Redis, Postgres, Celery, Gateway, Gemini) and verify the system degrades gracefully (e.g., human inbox still works if AI is down).

---

## 43. Graceful degradation
Design explicit fallbacks for when services go down.

---

## 44. Implementation Roadmap (8 Phases)

### Phase 0 — Baseline
1. Freeze current behavior
2. Capture API contracts
3. Capture DB schema
4. Run complete existing tests
5. Establish coverage baseline
6. Establish performance baseline
7. Establish security baseline

### Phase 1 — Security Foundation
8. Tenant authorization
9. TenantContext
10. Centralized authorization
11. PostgreSQL RLS where appropriate
12. RBAC
13. Go gateway authentication
14. Webhook signatures
15. OAuth state validation
16. Secret encryption / Secret-management migration
17. Rate limiting
18. Audit logging
19. Security headers & CORS hardening
20. CSRF protection

### Phase 2 — Reliability
21. Inbox pattern
22. Outbox pattern
23. Idempotency keys
24. Message state machine
25. Optimistic concurrency
26. Retries
27. DLQ
28. Conversation ordering
29. Distributed locks
30. Reconciliation

### Phase 3 — AI Security
31. AIOrchestrator decomposition
32. Tool Registry
33. Tool Policy Engine
34. JSON schemas
35. Prompt-injection defenses
36. Output validation
37. Cost controls
38. Runaway-loop prevention
39. Human approval
40. AI execution tracing

### Phase 4 — Integration Platform
41. Provider interfaces
42. Adapters
43. OAuth manager
44. Webhook manager
45. Capability system
46. Sync engine
47. Reconciliation

### Phase 5 — Observability
48. Structured logs
49. Metrics
50. Distributed tracing
51. Request IDs
52. Health checks
53. Security events
54. Failed-job UI
55. AI execution timeline

### Phase 6 — Data & Privacy
56. Retention
57. Deletion
58. Customer export
59. PII controls
60. Encrypted credentials
61. Backup policy
62. Restore testing

### Phase 7 — Production Hardening
63. Container hardening
64. Dependency scanning
65. SBOM
66. CI security gates
67. WAF
68. DDoS protection
69. Load testing
70. Chaos testing
71. Disaster recovery testing

### Phase 8 — Scale
72. Dedicated worker pools
73. Read replicas
74. Analytics warehouse
75. Gateway horizontal scaling
76. Database partitioning if necessary
77. Service extraction based on measured bottlenecks

---

## 45. The Most Important Architectural Decision

```text
                    ┌─────────────────┐
                    │    AI MODEL     │
                    │   UNTRUSTED     │
                    └────────┬────────┘
                             │
                       proposes action
                             │
                             ▼
                    ┌─────────────────┐
                    │  TOOL REGISTRY  │
                    └────────┬────────┘
                             │
                       schema check
                             │
                             ▼
                    ┌─────────────────┐
                    │ POLICY ENGINE   │
                    └────────┬────────┘
                             │
                   authorization check
                             │
                             ▼
                    ┌─────────────────┐
                    │ DOMAIN SERVICE  │
                    │   AUTHORITY     │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │    DATABASE     │
                    └─────────────────┘
```
**The AI is not the authority.** It merely requests a tool invocation. The application decides if it's permitted, and only the domain service executes it.

---

## 46. Final production architecture

```text
                           INTERNET
                               │
                         ┌─────▼─────┐
                         │   WAF     │
                         └─────┬─────┘
                               │
                   ┌───────────▼───────────┐
                   │     React Frontend    │
                   └───────────┬───────────┘
                               │
                         HTTPS / WSS
                               │
                   ┌───────────▼───────────┐
                   │       FastAPI         │
                   │      API / BFF        │
                   └───────────┬───────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
         Identity          Messaging        Commerce
         + Tenant            Domain           Domain
              │                │                │
              └────────────────┼────────────────┘
                               │
                       Domain Events
                               │
                     ┌─────────▼─────────┐
                     │       Redis       │
                     │ Broker / Cache    │
                     └─────────┬─────────┘
                               │
                 ┌─────────────┼─────────────┐
                 ▼             ▼             ▼
             AI Workers    Message Workers  Sync Workers
                 │             │             │
                 ▼             │             ▼
          ┌──────────────┐     │        External APIs
          │ AI Runtime   │     │
          │              │     │
          │ Context      │     │
          │ Model        │     │
          │ Tools        │     │
          │ Policies     │     │
          │ Validation   │     │
          └──────┬───────┘     │
                 │              │
                 ▼              ▼
             Tool Layer      Outbox
                 │              │
       ┌─────────┼─────────┐    │
       ▼         ▼         ▼    ▼
     CRM      Commerce   Messaging
       │         │         │
       └─────────┼─────────┘
                 │
                 ▼
            PostgreSQL
                 │
          ┌──────┴──────┐
          ▼             ▼
       Audit         Analytics
       Events        Pipeline

                 PRIVATE NETWORK
                       │
                       ▼
              ┌──────────────────┐
              │ Go WhatsApp GW   │
              │                  │
              │ Session State    │
              │ WhatsApp Client  │
              │ Event Handler    │
              │ Message Sender   │
              └──────────────────┘
```
The resulting platform is a **controlled distributed system**: identity → tenancy → domain → events → workers → AI → policy → tools → external systems. Every transition is authenticated, authorized, validated, observable, and idempotent.

## 47. Implementation Constraints
To ensure the transition from prototype to production is safe and controlled, the following constraints are non-negotiable for any agent or engineer implementing this architecture:

1. **Backward compatibility:** Existing API behavior must remain unchanged unless a migration explicitly documents a breaking change.
2. **No speculative microservices:** Keep FastAPI as the modular monolith until measured bottlenecks justify extraction.
3. **Database is the source of truth:** Redis/Celery/WebSockets are transport/cache mechanisms, never authoritative state.
4. **Fail closed for security, fail open only for non-critical UX features:** Authorization failures must never silently degrade.
5. **Every migration must be reversible:** Schema migration, code deployment, and configuration changes need rollback procedures.
