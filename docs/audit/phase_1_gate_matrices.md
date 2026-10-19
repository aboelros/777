# Phase 0 Closure & Phase 1 Gate Matrices

### 1. Tenant Ownership Matrix (29 Tables)

| Table Name | Classification | Inferred Path |
| --- | --- | --- |
| `bot_instructions` | **DIRECT_TENANT** | `project_id` |
| `usage_tracking` | **UNKNOWN** | Indirect Relation or UNKNOWN |
| `deals` | **DIRECT_TENANT** | `project_id` |
| `drip_campaigns` | **DIRECT_TENANT** | `project_id` |
| `auto_response_templates` | **DIRECT_TENANT** | `project_id` |
| `api_logs` | **DIRECT_TENANT** | `project_id` |
| `customer_profiles` | **DIRECT_TENANT** | `project_id` |
| `model_trainings` | **DIRECT_TENANT** | `project_id` |
| `users` | **GLOBAL** | Global Entity |
| `drip_steps` | **INDIRECT_TENANT** | Indirect Relation or UNKNOWN |
| `projects` | **DIRECT_TENANT** | `project_id` |
| `social_media_comments` | **DIRECT_TENANT** | `project_id` |
| `payment_links` | **GLOBAL** | Global Entity |
| `conversation_history` | **DIRECT_TENANT** | `project_id` |
| `business_context` | **DIRECT_TENANT** | `project_id` |
| `campaign_enrollments` | **DIRECT_TENANT** | `project_id` |
| `invoices` | **DIRECT_TENANT** | `project_id` |
| `social_media_posts` | **DIRECT_TENANT** | `project_id` |
| `messages` | **DIRECT_TENANT** | `project_id` |
| `products` | **DIRECT_TENANT** | `project_id` |
| `orders` | **DIRECT_TENANT** | `project_id` |
| `project_members` | **DIRECT_TENANT** | `project_id` |
| `knowledge_base` | **DIRECT_TENANT** | `project_id` |
| `integrations` | **DIRECT_TENANT** | `project_id` |
| `product_images` | **INDIRECT_TENANT** | Indirect Relation or UNKNOWN |
| `pipeline_stages` | **DIRECT_TENANT** | `project_id` |
| `refresh_tokens` | **GLOBAL** | Global Entity |
| `subscriptions` | **GLOBAL** | Global Entity |
| `reports` | **DIRECT_TENANT** | `project_id` |

### 2. Route Authorization Matrix (181 Routes)

| Prefix | Example Route | Method | Auth | Authorization | Repository | Tenant Scoped | Risk |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `/admin` | `/api/v1/admin/users` | GET, POST, PATCH | JWT (Admin) | `require_role('admin')` | Direct DB | N/A (Global) | **High** |
| `/auth` | `/api/v1/auth/login` | POST | None / JWT | N/A | Auth DB | N/A (Global) | **High** |
| `/projects` | `/api/v1/projects/{project_id}` | GET, PATCH | JWT | `verify_project_access`? | Direct DB | `project_id` URL | **High** |
| `/integrations`| `/api/v1/integrations/{project_id}` | POST, GET | JWT | `verify_project_access`? | Direct DB | `project_id` URL | **Critical** |
| `/messages` | `/api/v1/messages/{project_id}` | POST, GET | JWT | ? | MessageRepo/DB | `project_id` URL | **Critical** |
| `/webhooks` | `/api/v1/webhooks/whatsapp` | POST | Signature | Service Context | WebhookProcessor | Provider payload | **Critical** |
| `/*` (others) | `/api/v1/products/...` | GET, POST | JWT | ? | Direct DB | URL Param | **High** |


### 3. Execution Context Findings

1. **Raw `project_id` usage:** Almost all project-specific routes accept `{project_id}` in the URL and query the DB via `where(Model.project_id == project_id)`. Without explicit middleware/service-layer checks binding the JWT's `user_id` to that `project_id`, this is a massive IDOR vulnerability.
2. **Direct SQLAlchemy Access in Routers:** Routers in `/api/v1/admin.py`, `/api/v1/assistant.py`, `/api/v1/auth.py`, and likely others directly receive `AsyncSession` via `Depends(get_db)`. This completely bypasses repository boundaries.
3. **Auth Dependencies:** `get_current_user_id` extracts `user_id` from JWT payload. It DOES NOT check project membership globally.
4. **Service/Background Contexts:** Background tasks (e.g., Celery in `app/workers/tasks/`) execute without a structured `TenantContext`. They pass raw IDs and perform operations indiscriminately.
5. **Webhook Endpoints:** Webhooks currently receive untrusted data. Provider signature verification adapters must be reviewed before they can be considered running under a trusted `ServiceContext`.
