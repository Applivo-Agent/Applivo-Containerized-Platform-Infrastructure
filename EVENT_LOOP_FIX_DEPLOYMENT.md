# Event Loop Fix - VPS Deployment Guide

## 🎯 What's Fixed

The worker was crashing with **"Event loop is closed"** error. This has been **FIXED** by properly isolating event loops in `app/celery_tasks.py`.

---

## 🚀 Deploy to VPS (5 minutes)

### Step 1: Verify Latest Code
Confirm you have the updated `app/celery_tasks.py` with the fixed `_run_async()`:

```bash
cat app/celery_tasks.py | grep -A 8 "def _run_async"
```

Expected output:
```python
def _run_async(coro):
    """Run an async coroutine from a Celery worker with a fresh event loop."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()
        asyncio.set_event_loop(None)
```

If you don't see `asyncio.set_event_loop(loop)` and `asyncio.set_event_loop(None)`, pull the latest code.

### Step 2: Rebuild Worker Container

```bash
cd /opt/applivo-fixed
docker compose build --no-cache worker-browsing
```

Wait for build to complete (2-3 minutes).

### Step 3: Restart Worker

```bash
docker compose up -d worker-browsing
sleep 5
```

### Step 4: Verify Task Registration

```bash
docker compose logs worker-browsing | head -40 | grep -E "tasks|Ready|ERROR"
```

Expected output:
```
[tasks]
  . app.celery_tasks.apply_queued_batch
  . app.celery_tasks.auto_apply
  . app.celery_tasks.scrape_jobs
  . app.celery_tasks.analyze_jobs
  . app.celery_tasks.apply_to_job
  ...
[worker] Ready to accept tasks
```

**If you see empty `[tasks]` or ERROR**, stop and run:
```bash
docker compose logs worker-browsing --tail=50 | grep ERROR
```

### Step 5: Install Playwright (if needed)

```bash
docker compose exec worker-browsing python -m playwright install --with-deps chromium
```

Expected: Downloads Playwright and installs dependencies (1-2 minutes).

### Step 6: Test Apply Flow

**In one terminal, watch logs:**
```bash
docker compose logs -f worker-browsing | grep -E "Received|apply|Applied|success|error|Event loop|Future"
```

**In another terminal (or UI), trigger Deploy:**
- Open frontend UI
- Click "Deploy" button
- Watch worker logs (should NOT show errors)

---

## ✅ Success Criteria

After clicking Deploy, you should see in worker logs:

```
[Received task: app.celery_tasks.apply_queued_batch[<id>]]
[worker] Applying queued batch for user_id=<id>
[apply_bot] Launching browser for job_id=123456
[apply_bot] Navigating to https://internshala.com/jobs/apply/123456
[apply_bot] Submitting application...
[apply_bot] Applied successfully
[Task app.celery_tasks.apply_queued_batch[<id>] succeeded in 42.5s]
```

**NOT:**
```
RuntimeError: Event loop is closed
Future <...> attached to a different loop
Apply queued batch failed - retry in 180s
```

---

## 🔍 Verification Checklist

```bash
# 1. Worker is running
docker compose ps worker-browsing
# Expected: Status = "Up"

# 2. Tasks are registered
docker compose logs worker-browsing | grep -c "app.celery_tasks"
# Expected: Output >= 10 (number of tasks)

# 3. Worker can reach database
docker compose exec worker-browsing python -c "from app.core.database import get_db_context; print('DB OK')"
# Expected: "DB OK"

# 4. Worker can reach Redis
docker compose exec worker-browsing redis-cli -a $(grep REDIS_PASSWORD .env | cut -d= -f2) ping
# Expected: "PONG"

# 5. Playwright is installed
docker compose exec worker-browsing python -c "from playwright.async_api import async_playwright; print('Playwright OK')"
# Expected: "Playwright OK"
```

If any check fails, go back to the corresponding step above.

---

## 📊 Expected Timeline

| Task | Time |
|------|------|
| Build worker | 2-3 min |
| Restart worker | 1 min |
| Verify registration | 30 sec |
| Install Playwright | 1-2 min |
| **Total** | **5-7 min** |

---

## 🐛 Troubleshooting

### Issue: Still seeing "Event loop is closed" error

**Cause:** Old container hasn't been rebuilt

**Fix:**
```bash
docker compose down worker-browsing
docker compose build --no-cache worker-browsing
docker compose up -d worker-browsing
sleep 10
docker compose logs worker-browsing | head -50
```

### Issue: Tasks list is empty `[tasks]` but no ERROR

**Cause:** Celery autodiscovery didn't find tasks

**Fix:**
```bash
docker compose exec worker-browsing python -c "import app.celery_tasks; print('Import OK')"
docker compose restart worker-browsing
sleep 5
docker compose logs worker-browsing | grep tasks
```

### Issue: Worker crashes immediately after start

**Cause:** Missing dependency or database issue

**Fix:**
```bash
# Check logs for actual error
docker compose logs worker-browsing --tail=100 | grep -i "error\|traceback"

# If database error, verify connection
docker compose exec database psql -U applivo -d applivo -c "SELECT 1;"

# If dependency error, rebuild with fresh image
docker compose build --no-cache --pull worker-browsing
```

### Issue: Playwright error during apply

**Cause:** Browser binaries not installed or corrupted

**Fix:**
```bash
docker compose exec worker-browsing rm -rf ~/.cache/ms-playwright
docker compose exec worker-browsing python -m playwright install --with-deps chromium
docker compose restart worker-browsing
```

---

## 📝 After Deployment

1. **Monitor first 3 applies** to ensure they complete successfully
2. **Check database:** Applications should be marked `APPLIED` (not PENDING/QUEUED)
3. **Check timestamps:** `applied_at` should be recent (within last 5 minutes)

Query to verify:
```bash
docker compose exec database psql -U applivo -d applivo -c \
  "SELECT id, status, applied_at FROM applications WHERE applied_at > NOW() - INTERVAL 5 MINUTES LIMIT 5;"
```

Expected: Shows recent applications with `APPLIED` status.

---

## 🎉 Success!

Once you see applications being applied and marked with `APPLIED` status, the fix is complete!

Your automation bot is now working end-to-end:
```
User clicks Deploy
   ↓
Backend queues task
   ↓
Worker receives task
   ↓
Async code runs in fresh event loop ✅
   ↓
Bot applies to jobs
   ↓
Database updated
   ↓
Frontend shows completion
```

---

## 📞 If Still Failing

Collect and share:
1. Full worker logs (last 100 lines): `docker compose logs worker-browsing --tail=100`
2. Backend logs (last 50 lines): `docker compose logs backend --tail=50`
3. Redis status: `docker compose exec redis redis-cli -a $(grep REDIS_PASSWORD .env | cut -d= -f2) info`
4. Database query: `docker compose exec database psql -U applivo -d applivo -c "SELECT COUNT(*) FROM applications WHERE status='PENDING_APPROVAL';"`
