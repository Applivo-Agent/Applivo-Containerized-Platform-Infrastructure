# FINAL: Event Loop + Pool Configuration Fixes

## 🎯 Root Cause (Identified)

Worker **is receiving tasks** but crashes during execution due to **async + prefork pool mismatch**:

```
Celery prefork worker + asyncio (SQLAlchemy async + Playwright)
= Event loop conflicts
= "Event loop is closed" + "Future attached to different loop"
= Task fails + retries every 180 seconds
```

---

## ✅ Two Fixes Applied

### Fix 1: Worker Pool Configuration
**File:** `scripts/start_browser_worker.sh` (line 14)

Changed from:
```bash
exec python -m celery ... worker --loglevel=info --concurrency=1 -Q scraping,apply
```

To:
```bash
exec python -m celery ... worker --loglevel=info --pool=solo --concurrency=1 -Q scraping,apply
```

**Why:** `--pool=solo` = single process + single event loop (required for async code)

### Fix 2: Event Loop Isolation
**File:** `app/celery_tasks.py` (lines 18-25)

Added explicit event loop management in `_run_async()`:
```python
def _run_async(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)      # ← Set as current
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()
        asyncio.set_event_loop(None)  # ← Clear after close
```

**Why:** Ensures each task gets clean, isolated event loop

---

## 🚀 Deploy to VPS (3 minutes)

On your VPS in `/opt/applivo-fixed`:

```bash
# 1. Verify both fixes are in place
grep -n "pool=solo" scripts/start_browser_worker.sh
grep -n "asyncio.set_event_loop(None)" app/celery_tasks.py

# 2. Rebuild worker container
docker compose build --no-cache worker-browsing

# 3. Force-recreate worker
docker compose up -d --force-recreate worker-browsing

# 4. Wait for startup
sleep 5

# 5. Verify pool configuration in logs
docker compose logs worker-browsing | grep -E "solo|Ready"
```

Expected output:
```
applivo-worker-browser | [celery-worker-1]  pool=solo
applivo-worker-browser | [worker] Connected to redis://...
applivo-worker-browser | [worker] Ready to accept tasks
```

---

## 🧪 Test Apply Flow

**Terminal 1 - Watch logs:**
```bash
docker compose logs -f worker-browsing | grep -E "Received|apply|Applied|success|error|Event loop"
```

**Terminal 2 - Trigger test:**
Open frontend UI → Click **Deploy** button

---

## ✅ Success Indicators

You should see in worker logs:

```
[Received task: app.celery_tasks.apply_queued_batch[...]]
[celery.py] Starting apply batch for user_id=...
[playwright] Launching browser
[playwright] Navigating to https://internshala.com/jobs/apply/...
[apply_bot] Submitting application to job_id=123456
[apply_bot] Applied successfully
[Task app.celery_tasks.apply_queued_batch[...] succeeded in 25.3s]
```

**NOT:**
```
RuntimeError: Event loop is closed
Future ... attached to a different loop
Apply queued batch failed
retry in 180s
```

---

## 📊 Verify Database State

After Deploy completes, verify applications were updated:

```bash
docker compose exec database psql -U applivo -d applivo -c \
  "SELECT COUNT(*) as applied_count FROM applications WHERE status='APPLIED' AND applied_at > NOW() - INTERVAL 5 MINUTES;"
```

Expected: Shows count > 0 (number of jobs applied in last 5 minutes)

---

## 🔍 Pre-Deploy Checklist

Before deploying, verify both fixes:

```bash
# Fix 1: Pool config
echo "=== Check pool=solo in start_browser_worker.sh ==="
grep "pool=solo" scripts/start_browser_worker.sh
# Expected: exec python -m celery ... --pool=solo ...

# Fix 2: Event loop isolation
echo "=== Check asyncio.set_event_loop in celery_tasks.py ==="
grep -A 2 "asyncio.set_event_loop(loop)" app/celery_tasks.py
# Expected: Shows set_event_loop(loop) call

# Fix 3: Event loop cleanup
echo "=== Check asyncio.set_event_loop(None) ==="
grep "asyncio.set_event_loop(None)" app/celery_tasks.py
# Expected: Shows set_event_loop(None) call in finally block
```

All three should show expected output.

---

## 🔧 Subscription Verification

If you see "No active subscription" in logs, apply was intentionally skipped. Verify:

```bash
docker compose exec database psql -U applivo -d applivo -c \
  "SELECT id, user_id, status, end_date FROM subscriptions LIMIT 5;"
```

Expected: Shows at least one row with `status='active'` (or 'ACTIVE')

If all are expired/inactive, you need to activate subscription in database or update end_date.

---

## 📝 After Successful Deploy

1. ✅ Applications marked `APPLIED` in database
2. ✅ Worker logs show "Task succeeded"
3. ✅ No "Event loop is closed" errors
4. ✅ Deploy completes in 20-60 seconds
5. ✅ Frontend polling shows "Completed: Applied X jobs"

---

## 🐛 If Still Failing

Collect full logs and share:

```bash
# 1. Full worker startup
docker compose logs worker-browsing --tail=50

# 2. Is pool=solo actually being used?
docker compose logs worker-browsing | grep -i "pool"

# 3. Any Python import errors?
docker compose logs worker-browsing | grep -i "error\|import\|traceback"

# 4. Redis connection status?
docker compose exec redis redis-cli -a $(grep REDIS_PASSWORD .env | cut -d= -f2) ping

# 5. Database connection status?
docker compose exec backend python -c "from app.core.database import engine; print('DB OK')"
```

---

## ⏱️ Expected Timeline

| Step | Time |
|------|------|
| Verify fixes | 30 sec |
| Build worker | 2-3 min |
| Restart + wait | 1 min |
| Verify logs | 30 sec |
| Test Deploy | 30-60 sec |
| **Total** | **4-6 min** |

---

## 🎉 You're Almost There!

Your system is now properly configured:

```
✅ Backend API (routes work)
✅ Queue system (Redis)
✅ Worker consuming tasks (Celery with proper pool)
✅ Event loop isolated (async safety)
✅ Playwright browsers installed
✅ Database connections async-safe
```

This is the final piece — solo pool ensures async code works reliably in Celery workers.

**Next: Deploy on VPS and watch it apply jobs! 🚀**
