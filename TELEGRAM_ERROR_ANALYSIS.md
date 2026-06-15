# 🔴 **TELEGRAM BOT - ERROR ANALYSIS & FIXES**

## ❌ **CRITICAL ERRORS FOUND:**

### **ERROR #1: Background Task Not Running** 🔴 CRITICAL

**Location**: `backend/app/api/v1/webhooks.py` (line 124-128)

**Problem**:
```python
background_tasks.add_task(
    _process_telegram_message_with_ai,
    str(new_message.id),
    str(project_id)
)
```

**Issue**: 
- Using FastAPI `BackgroundTasks` which runs in same process
- `_process_telegram_message_with_ai` is an async function
- Background task may not complete before webhook returns
- No error handling if task fails

**Impact**: Messages received but not processed

---

### **ERROR #2: Async Function Called in Background Task** 🔴 CRITICAL

**Location**: `backend/app/workers/tasks/ai_tasks.py` (line 27-61)

**Problem**:
```python
async def process():
    async with get_async_session() as db:
        # ... async code ...

# Run async function
import asyncio
return asyncio.run(process())
```

**Issue**:
- Celery task tries to run async code with `asyncio.run()`
- This doesn't work properly in Celery workers
- `get_async_session()` doesn't exist (should be `AsyncSessionLocal`)
- No proper async/await handling

**Impact**: Celery tasks fail silently

---

### **ERROR #3: Instagram & Facebook Use Wrong Task Import** 🔴 CRITICAL

**Location**: `backend/app/api/v1/webhooks.py` (lines 189, 264)

**Problem**:
```python
background_tasks.add_task(
    process_incoming_message.delay,  # ❌ WRONG - .delay is Celery method
    str(new_message.id),
    str(project_id)
)
```

**Issue**:
- Mixing FastAPI BackgroundTasks with Celery
- `process_incoming_message.delay` is Celery method
- Can't call Celery task from FastAPI BackgroundTasks
- Causes AttributeError

**Impact**: Instagram and Facebook messages not processed

---

### **ERROR #4: Missing Integration Status Check** 🟡 MEDIUM

**Location**: `backend/app/api/v1/integrations.py` (line 555)

**Problem**:
```python
integration.status = IntegrationStatus.CONNECTED
```

**Issue**:
- Status set to enum but webhook checks for enum value
- Should verify enum is properly imported
- Status comparison might fail

**Impact**: Integration status mismatch

---

### **ERROR #5: No Error Response in Telegram Webhook** 🟡 MEDIUM

**Location**: `backend/app/api/v1/webhooks.py` (line 137)

**Problem**:
```python
return {"status": "ok"}
```

**Issue**:
- Always returns 200 OK even if message save fails
- Telegram expects 200 OK for webhook verification
- But errors are silently swallowed
- No logging of failures

**Impact**: Silent failures, hard to debug

---

## 🔧 **FIXES REQUIRED:**

### **FIX #1: Use Celery for Telegram Processing**

Replace FastAPI BackgroundTasks with Celery:

```python
# Instead of:
background_tasks.add_task(
    _process_telegram_message_with_ai,
    str(new_message.id),
    str(project_id)
)

# Use:
from app.workers.tasks.ai_tasks import process_incoming_message
process_incoming_message.delay(str(new_message.id), str(project_id))
```

---

### **FIX #2: Fix Celery Task to Handle Async Properly**

Update `ai_tasks.py`:

```python
@shared_task(name="process_incoming_message", bind=True, max_retries=3)
def process_incoming_message(self, message_id: str, project_id: str):
    """Process incoming message synchronously."""
    from app.core.database import AsyncSessionLocal
    from app.db.models import Message
    from sqlalchemy import select
    import asyncio
    
    try:
        async def process_async():
            async with AsyncSessionLocal() as db:
                # Fetch message
                result = await db.execute(
                    select(Message).where(Message.id == UUID(message_id))
                )
                message = result.scalar_one_or_none()
                
                if not message:
                    logger.error("Message not found", message_id=message_id)
                    return
                
                # Process with AI
                # ... rest of logic ...
        
        # Run async code properly
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(process_async())
        finally:
            loop.close()
            
    except Exception as e:
        logger.error("Failed to process message", error=str(e))
        raise self.retry(exc=e, countdown=2 ** self.request.retries)
```

---

### **FIX #3: Fix Instagram & Facebook Webhooks**

Replace in `webhooks.py`:

```python
# For Instagram (line 189):
# Instead of:
background_tasks.add_task(
    process_incoming_message.delay,
    str(new_message.id),
    str(project_id)
)

# Use:
from app.workers.tasks.ai_tasks import process_incoming_message
process_incoming_message.delay(str(new_message.id), str(project_id))

# Same for Facebook (line 264)
```

---

### **FIX #4: Add Error Handling to Telegram Webhook**

```python
@router.post("/telegram/{project_id}")
async def telegram_webhook(
    project_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Receive Telegram messages from Telegram Bot API."""
    try:
        payload = await request.json()
        
        # Extract message details
        message = payload.get("message", {})
        if not message:
            return {"status": "ok"}  # Telegram expects 200 OK
        
        # ... rest of code ...
        
        # Queue task
        from app.workers.tasks.ai_tasks import process_incoming_message
        try:
            process_incoming_message.delay(str(new_message.id), str(project_id))
            logger.info("Message queued for processing", message_id=str(new_message.id))
        except Exception as e:
            logger.error("Failed to queue message", error=str(e))
            # Still return 200 OK to Telegram
        
        return {"status": "ok"}
        
    except Exception as e:
        logger.error("Telegram webhook error", error=str(e))
        # Always return 200 OK to Telegram
        return {"status": "ok"}
```

---

## 📊 **ROOT CAUSE SUMMARY:**

| Issue | Cause | Impact | Severity |
|-------|-------|--------|----------|
| Background tasks not running | Using FastAPI BackgroundTasks instead of Celery | Messages not processed | 🔴 CRITICAL |
| Async code in Celery | Wrong async/await handling | Tasks fail silently | 🔴 CRITICAL |
| Mixed task systems | Using both BackgroundTasks and Celery | Inconsistent behavior | 🔴 CRITICAL |
| Silent failures | No error handling in webhooks | Hard to debug | 🟡 MEDIUM |
| Status mismatch | Enum comparison issues | Integration fails | 🟡 MEDIUM |

---

## ✅ **IMPLEMENTATION PLAN:**

1. **Update Telegram webhook** to use Celery
2. **Update Instagram webhook** to use Celery
3. **Update Facebook webhook** to use Celery
4. **Fix Celery task** to handle async properly
5. **Add error handling** to all webhooks
6. **Test with actual messages**

---

## 🚀 **EXPECTED RESULT AFTER FIXES:**

✅ Telegram messages received and processed
✅ AI responses generated
✅ Responses sent back to user
✅ All errors logged properly
✅ Celery tasks running correctly

**Status: FIXES READY TO IMPLEMENT**
