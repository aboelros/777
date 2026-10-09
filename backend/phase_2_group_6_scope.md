# Phase 2 Group 6 Scope — Orders / Commerce Security

### 1. Provenance
* **Original Group 6**: `NOT RECOVERABLE`
* **Why it is unavailable**: The explicit label "Group 6" does not exist in any historical artifact, document, or git commit in the entire repository. The highest recovered group was Group 5.
* **Evidence for Orders / Commerce**: `RECOVERED HISTORICAL FACT` — The `remaining_security_audit.md` explicitly lists the `Orders / Commerce` domain (17 routes, `orders.py` & `order_management.py`) as the "RECOMMENDED NEXT MIGRATION" after the Integrations domain (which was handled by Groups 1–5). 

### 2. Reconstructed Objective
`RECONSTRUCTED GROUP 6 SCOPE`
Strictly harden the Orders / Commerce domain to eliminate raw SQL bypasses, enforce the `TenantContext → tenant-scoped repository → service` architectural pattern, and eradicate global/unscoped order queries residing in orphaned code.

### 3. Exact In-Scope Files
`REPOSITORY-BASED EVIDENCE`
* **Routers**:
  * `backend/app/api/v1/orders.py`
  * `backend/app/api/v1/order_management.py`
* **Services**:
  * `backend/app/domains/orders/service.py`
  * `backend/app/services/order_manager_service.py`
* **Repositories**:
  * `backend/app/domains/orders/repository.py`
* **Orphaned / Unsafe Dead Code (To Delete)**:
  * `backend/app/services/order_manager.py`
  * `backend/app/services/order_followups.py`
  * `backend/app/services/order_notifications.py`

### 4. Security Risks Found
`REPOSITORY-BASED EVIDENCE`
1. **Raw SQL bypassing tenant isolation**: 
   * `order_manager_service.py` executes 8+ raw `self.db.execute(select(Order)...)` queries directly, bypassing `OrderRepository`.
   * `order_management.py` (router) executes raw SQL aggregates `select(Order.status, func.count(...))` directly in the HTTP handler.
   * `backend/app/domains/orders/service.py` (`OrderService`) executes raw SQL aggregates `select(func.count(Order.id))` bypassing `OrderRepository`.
2. **Missing Tenant/Resource Binding**: 
   * `order_manager_service.py` initializes `EnhancedAIService(db, project_id)` using an undefined/unbound `project_id` instead of `self.project_id`, creating a critical crash/context leakage vector.
3. **Global Scope Leakage (Dead Code)**: 
   * `order_followups.py` executes a completely unscoped `select(Order)` globally, checking all orders across all tenants without verifying boundaries.
   * `order_notifications.py` queries `select(Order)` purely by `order_id` bypassing tenant validation.

### 5. Required Architectural Changes
`RECONSTRUCTED GROUP 6 SCOPE`
* **Strict Repository Pattern**: All raw SQLAlchemy queries (`select(Order)`) currently in routers and services must be moved into `OrderRepository` as strongly-typed, context-aware methods (e.g., `get_status_counts(context)`, `get_progress(context)`).
* **AI Context Binding**: Fix the initialization of `EnhancedAIService` to strictly use the bound `self.context.project_id`.
* **Code Eradication**: Permanently delete the unsafe orphaned modules (`order_followups.py`, `order_notifications.py`, `order_manager.py`) so they cannot be accidentally imported and trigger global side-effects.

### 6. Required Security-Test Matrix
`RECONSTRUCTED GROUP 6 SCOPE`
* Test: Cross-tenant Order read prevention (via `OrderManagerService`).
* Test: Cross-tenant Order status mutation prevention.
* Test: Cross-tenant Order auto-progress prevention.
* Test: Verify `OrderRepository` enforces `project_id` on new aggregate statistics queries.

### 7. Explicit Exclusions
`RECOVERED HISTORICAL FACT` & `RECONSTRUCTED GROUP 6 SCOPE`
* **Payments and Invoicing**: `backend/app/api/v1/payments_invoicing.py` and `subscriptions.py` are explicitly excluded by `remaining_security_audit.md` to be handled in a subsequent step.
* **Webhook Ingestion**: Order webhooks (Shopify) were already secured in Group 1 & 5. Do not modify the webhook gateway.
* **Models**: Do not modify `Order` or `CustomerProfile` schemas/models.

### 8. Dependencies on Groups 2–5
`REPOSITORY-BASED EVIDENCE`
* Relies on the canonical `TenantContext` dependency deployed in Group 2.
* Relies on the isolated background/service patterns established in Group 5.

### 9. Potential Regression Risks
`REPOSITORY-BASED EVIDENCE`
* Moving raw SQL aggregates into the repository may alter the dict/tuple shape expected by the frontend charting dashboards.
* Fixing the AI service parameter might expose underlying bugs in the `auto_progress_order` flow if it was previously silently failing.

### 10. Definition of Done
`RECONSTRUCTED GROUP 6 SCOPE`
* Zero occurrences of `select(Order)` outside of `OrderRepository`.
* Unsafe dead code files are deleted.
* AI service instantiation correctly binds to `TenantContext`.
* Security test matrix passes 100%.

RECONSTRUCTED GROUP 6 SCOPE — READY FOR IMPLEMENTATION
