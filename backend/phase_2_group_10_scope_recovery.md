# Phase 2 — Next Security Group Scope Recovery (Group 10)

## 1. Investigation Status
This is a READ-ONLY investigation. No application code, tests, schema, or configuration files were modified. The objective is to identify the logical next security migration scope ("Group 10") based purely on repository evidence, the Master Plan audit, and remaining tenant-isolation risks. Groups 1–9 are treated as HARD READ-ONLY BOUNDARIES and are not modified.

## 2. Historical Evidence for Group 10
* **HISTORICAL NEXT GROUP SPECIFICATION: `NOT RECOVERABLE`**
* There is no surviving document, git commit, branch, or planning artifact in the repository that defines an original "Group 10".
* Therefore, the proposed scope is a **RECONSTRUCTED NEXT-GROUP SCOPE — NOT HISTORICALLY VERIFIED**.

## 3. Master Plan Remaining Work Alignment
The Master Plan Completion Audit identified 34 Partially Complete and 25 Unknown capabilities. Key unmigrated security items include:
* **ID 8 (Tenant Authorization)**: Unmigrated routers (`products.py`, `photos.py`, `storage.py`, `payments_invoicing.py`, `deals.py`, `projects.py`) still use `verify_project_access` or raw DB queries.
* **ID 10 (Centralized Authorization)**: Legacy `verify_project_access` remains.
* **ID 12 (RBAC)**: Project role hierarchy is not enforced on domain actions (e.g., missing membership checks in `projects.py`).

## 4. Remaining Security Surface (Unmigrated Routers)
The following files still use legacy `verify_project_access` or raw DB queries bypassing the `TenantContext`:
* `backend/app/api/v1/projects.py`
* `backend/app/api/v1/products.py`
* `backend/app/api/v1/photos.py`
* `backend/app/api/v1/storage.py`
* `backend/app/api/v1/deals.py`
* `backend/app/api/v1/payments_invoicing.py`
* `backend/app/api/v1/subscriptions.py`

## 5. Deferred Work from Prior Groups
* `remaining_security_audit.md` explicitly lists `Projects / Settings` (which includes `projects.py`, `products.py`, `photos.py`, `storage.py`) as Domain 7 of the 8 core domains requiring migration.
* Prior group audits (like Group 8 and Group 9) explicitly deferred these domains to subsequent groups.

## 6. Candidate Scopes
1. **Projects & Tenant Membership (`projects.py`)**: Contains a critical authorization bypass in `list_project_members` (`if project.owner_id != user_uuid: pass`) and `add_project_member` (no ownership check), allowing cross-tenant privilege escalation.
2. **Product Catalog & Media Storage (`products.py`, `photos.py`, `storage.py`)**: Contains Python-only post-fetch tenant filtering and cross-tenant shared file overwrite/deletion vulnerabilities.
3. **Payments & Invoicing (`payments_invoicing.py`)**: Contains cross-tenant customer invoice injection vulnerabilities.
4. **CRM Pipeline / Deals (`deals.py`)**: Contains cross-tenant customer deal linking vulnerabilities.

## 7. Recommended Scope
**RECONSTRUCTED GROUP 10 — PROJECTS & TENANT ADMINISTRATION MIGRATION**
* **Primary Target**: `backend/app/api/v1/projects.py` and `backend/app/domains/projects/service.py`
* **Justification**: The `projects.py` domain controls the root of the tenant hierarchy (Project creation and Membership). The discovered authorization bypass in `add_project_member` allows ANY authenticated user to add themselves as an OWNER or ADMIN to ANY project ID. This is a critical security vulnerability that undermines the entire `TenantContext` isolation model established in Groups 1–9. Fixing the root tenant authorization logic is the most urgent remaining security priority.

## 8. Master Plan Alignment
Migrating Projects & Tenant Administration to the standard `TenantContext` repository model will directly advance:
* **ID 8 (Tenant Authorization)**
* **ID 10 (Centralized Authorization)**
* **ID 12 (RBAC)**

## 9. Risk/Dependency Analysis
* **Overlap Risk**: Group 10 will primarily modify `projects.py` and `domains/projects/`. These files have NOT been frozen in Groups 1–9.
* **Test Dependency**: `test_tenant_security.py` exists but does not currently cover the `/members` endpoints. New tests (e.g., `test_projects_security.py`) will be required to verify the bypass is closed.
* **Architecture Dependency**: Enforcing standard `TenantContext` here will ensure that all subsequent scopes (Products, Deals, Payments) inherit a secure foundation for `get_tenant_context` resolution.

## 10. Final Decision
> HISTORICAL NEXT GROUP: NOT RECOVERABLE
> RECONSTRUCTED NEXT-GROUP SCOPE: JUSTIFIED BY REPOSITORY EVIDENCE
> 
> RECONSTRUCTED GROUP 10 — PROJECTS & TENANT ADMINISTRATION MIGRATION
> NOT HISTORICALLY VERIFIED
