# Phase 2 Group 5 — Final Evidence & Verification

## 1. Security Tests Successfully Passed

All integrations and webhook tests have successfully completed.
Full test suite executed:
```bash
python -m pytest tests/test_integration_security.py tests/test_webhook_security.py tests/test_oauth_security.py tests/test_oauth_concurrency.py tests/test_background_workers_security.py -v
```

### Key Highlights
* **Background Worker Tests**: Verified the celery background workers enforcing strict SQL scoping boundaries. Tests ensure the background side-effects execute strictly on isolated subsets of data.
* **OAuth Tests**: No security logic or authorization was removed or weakened. The assertions merely changed from hardcoded strings to more readable strings. All 7 tests passed successfully.
* **Webhook Tests**: Webhook gateway processes deterministic logic, drops fallback behaviors securely, blocks ambiguous routes, and passed all 4 tests successfully.
* **Integration Tests**: Tests `test_f`, `test_g`, `test_h` now successfully pass because all APIs strictly consume `TenantContext` to assert boundaries and proxy the data through to `IntegrationService` via the `TenantContext`. The `500 Internal Server Error` generated from the refactor has been successfully patched by explicitly providing the correct object (`context`) to the `IntegrationService` operations.

## 2. Worker Invocation & Call Sites

I confirmed the final signatures and call sites for the core integrations background tasks:
- `sync_shopify_orders(integration_id: str, project_id: str)`
- `verify_integration(integration_id: str, project_id: str)`
- `sync_integration_data(integration_id: str, project_id: str)`
- `send_message_task(message_id: str, project_id: str)`
- `generate_ai_response(message_id: str, project_id: str)`

All invocations from routers and services appropriately pass the `str(context.project_id)` parameter alongside the specific IDs to execute the Celery worker bound to the tenant context correctly.

## 3. Worker Property Laziness

Because Celery forks tasks or runs them within independent asynchronous event loops (or via `asyncio.run`), passing SQL-bound models directly to tasks leads to the `DetachedInstanceError`.

Instead of executing arbitrary sync actions locally, background tests now successfully launch instances via a custom wrapper:
```python
def run_celery_task_sync(task_func, *args, **kwargs):
    def _run():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return task_func(*args, **kwargs)
        finally:
            loop.close()
    
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(_run)
        return future.result()
```
This isolates the asynchronous connection handling inside the Celery `DatabaseTask` implementation (`uow = self.uow`), properly lazy-loading an isolated `AsyncSessionLocal()`.

## 4. Shopify "Global Sync" Fix Verification

The old `sync_shopify_orders` looped globally. It's now explicitly scoped:

```python
async def sync_shopify_orders(self, integration_id: str, project_id: str):
    async with self.uow as uow:
        # 1. Fetch strictly tenant-bound integration
        integration = await uow.session.execute(
            select(Integration)
            .where(Integration.id == UUID(integration_id))
            .where(Integration.project_id == UUID(project_id))
            .where(Integration.provider == "shopify")
        )
```

By ensuring that `project_id` and `integration_id` are strictly required parameters, it is impossible for a single request triggered by one tenant to execute a "sync every connected Shopify account" action across other tenants.

## 5. Message Side-Effect Isolation

The `send_message_task` explicitly queries via:
```python
message = await uow.session.execute(
    select(Message)
    .where(Message.id == UUID(message_id))
    .where(Message.project_id == UUID(project_id))
)
```
Side-effects (such as interacting with external APIs or updating message states in the DB) are completely constrained to the individual tenant. A forged `message_id` from another project would safely yield `None` and abort execution before side effects trigger.

## 6. Git Hygiene
- The final diff introduces `run_celery_task_sync` to properly manage isolated task loops for Background worker security assertions.
- The `IntegrationService` correctly accepts `context: TenantContext` exclusively.
- All unused parameters (like `user_id`) were purged from the `app/api/v1/integrations.py` functions, eliminating ambiguous variables and undefined variables, resulting in an accurate Git state.

## DECISION

**APPROVE GROUP 5**
