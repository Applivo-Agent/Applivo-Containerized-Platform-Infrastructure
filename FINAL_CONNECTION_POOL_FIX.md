# CRITICAL: Final Connection Pool Cleanup Fix

## Problem Found in Logs

Your worker logs showed:
```
[solo]  ✅ Pool is correct
RuntimeError: Event loop is closed  ❌ But connection pool cleanup fails
```

The `--pool=solo` fix is working, but asyncpg's connection pool tries to cleanup AFTER the event loop is closed.

---

## What Was Fixed

**File:** `app/celery_tasks.py` → `_run_async()` function (lines 10-40)

**Before:**
```python
def _run_async(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()  # ❌ Closes loop BEFORE connection cleanup
        asyncio.set_event_loop(None)
```

**After (FIXED):**
```python
def _run_async(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        # Dispose DB connections WHILE loop is still active ✅
        try:
            from app.core.database import engine
            loop.run_until_complete(engine.dispose())
        except Exception as e:
            logger.warning("Failed to dispose engine", error=str(e))
        
        # THEN close loop
        loop.close()
        asyncio.set_event_loop(None)
```

**Why This Works:**
1. Task executes async code → completes successfully
2. Finally block runs
3. **Dispose engine FIRST** (while loop is active) → all asyncpg connections close properly
4. **Then close loop** → no stale references
5. Result: No "Event loop is closed" errors ✅

---

## Deploy to VPS (2 minutes)

**On your VPS:**

```bash
cd /opt/applivo-fixed

# 1. Pull latest code
git pull origin main

# 2. Verify the fix is present
grep -A 5 "Dispose database connection pool" app/celery_tasks.py
# Expected: Shows the new disposal code

# 3. Rebuild worker
docker compose build --no-cache worker-browsing

# 4. Force recreate
docker compose down worker-browsing
docker compose up -d worker-browsing

# 5. Wait for startup
sleep 5

# 6. Verify logs
docker compose logs worker-browsing | head -50
```

**Expected output in logs:**
```
.> concurrency: 1 (solo)
[tasks]
  . app.celery_tasks.apply_queued_batch
  . app.celery_tasks.auto_apply
  ...
celery@... ready.
```

**NOT:**
```
RuntimeError: Event loop is closed
```

---

## Test Apply Now

**Terminal 1 - Watch logs:**
```bash
docker compose logs -f worker-browsing | grep -E "apply_queued_batch|Applied|Event loop|error"
```

**Terminal 2 - Trigger test:**
- Open frontend UI
- Click **Deploy** button

---

## Expected Success Sequence

You should see in worker logs:

```
[Received task: app.celery_tasks.apply_queued_batch[3603e81f-c373-4378-a0d5-6ea2e3910106]]
[solo] Started celery-worker-1
[apply_bot] Launching browser
[apply_bot] Navigating to internshala.com
[apply_bot] Submitting application
[apply_bot] Applied successfully
[Task app.celery_tasks.apply_queued_batch[...] succeeded in 28s]
```

**NOT:**
```
RuntimeError: Event loop is closed
Task got Future attached to a different loop
retry in 180s
```

---

## If It Still Fails

Collect this data and share:

```bash
# Check for import errors
docker compose logs worker-browsing | grep -i "error\|import\|traceback" | head -20

# Check if engine disposal is even being called
docker compose logs worker-browsing | grep -i "dispose\|Failed to dispose"

# Check full last 100 lines
docker compose logs worker-browsing --tail=100
```

---

## Success Checklist

After deployment:

- [ ] Worker shows `(solo)` in startup logs
- [ ] Worker shows `celery@... ready.`
- [ ] Click Deploy, no `RuntimeError: Event loop is closed` error
- [ ] Worker logs show `[Received task: apply_queued_batch]`
- [ ] Worker logs show `Applied successfully` or `Applying to job`
- [ ] Database shows applications marked `APPLIED` with recent `applied_at` timestamp

If all checked, **you're done!** Applications are now applying! 🎉

---

## What's Happening Now

```
User clicks Deploy
   ↓
Backend queues task (Celery)
   ↓
Worker receives task (solo pool) ✅
   ↓
Async code runs in fresh event loop ✅
   ↓
Applications processed by bot ✅
   ↓
DB connections disposed properly ✅ (NEW)
   ↓
Event loop closed cleanly ✅
   ↓
Task marked succeeded ✅
   ↓
Frontend shows completion ✅
```

All stages should now work end-to-end!
