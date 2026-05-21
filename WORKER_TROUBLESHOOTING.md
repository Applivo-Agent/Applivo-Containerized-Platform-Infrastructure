# Browser Worker Task Consumption Troubleshooting Guide

## Current Status
- ✅ Backend API working (POST /api/applications returns 200)
- ✅ Deploy button queues tasks successfully (celery_task_id generated)
- ✅ Redis receives queued messages
- ❌ **Browser worker is NOT consuming apply_queued_batch tasks**

## Diagnostic Steps (Run on VPS)

### Step 1: Check Worker Container Status
```bash
cd /opt/applivo-fixed
docker compose ps worker-browsing
```
Expected: Status should be "Up" and healthy.

### Step 2: Rebuild Worker Container (Pick up Latest Code)
The worker container needs to rebuild to include the latest `celery_app.py` with explicit task import.

```bash
cd /opt/applivo-fixed
docker compose build --no-cache worker-browsing
docker compose up -d --no-deps --force-recreate worker-browsing
```

### Step 3: Verify Task Registration (Most Important)
Watch worker startup logs for task registration:

```bash
docker compose logs -f worker-browsing --tail=50 | grep -E "tasks|Received|connected|ready|ERROR|Import"
```

**Expected Output:**
```
applivo-worker-browser | [tasks]
applivo-worker-browser |   . app.celery_tasks.apply_queued_batch
applivo-worker-browser |   . app.celery_tasks.auto_apply
applivo-worker-browser |   . app.celery_tasks.scrape_jobs
applivo-worker-browser |   . app.celery_tasks.analyze_jobs
applivo-worker-browser |   ... (other tasks)
applivo-worker-browser | [worker] Connected to redis://...
applivo-worker-browser | [worker] Ready to accept tasks
```

**If you see `[tasks]` but it's EMPTY or unregistered:**
```
applivo-worker-browser | [tasks]
applivo-worker-browser | [worker] Connected to redis://...
```

This means tasks are not being discovered. Go to Step 4.

**If you see an ImportError:**
```
applivo-worker-browser | ERROR: Failed to import...
applivo-worker-browser | ModuleNotFoundError: No module named 'app'
```

This means PYTHONPATH is not set. Go to Step 5.

### Step 4: Verify Task Import in Container
If tasks aren't registering, test the import directly:

```bash
docker compose exec worker-browsing python -c "import app.celery_tasks; print('OK')"
```

Expected: `OK`

If it fails with import error, the app package is not accessible in the container.

### Step 5: Check Dockerfile Entrypoint
Verify worker-browsing uses the correct Dockerfile (should be `Dockerfile`, not `Dockerfile.slim`):

```bash
docker compose config | grep -A 5 "worker-browsing:" | grep dockerfile
```

Expected: `dockerfile: Dockerfile` (must have Dockerfile, not Dockerfile.slim)

### Step 6: Verify Playwright is Installed
The browser worker needs Playwright chromium:

```bash
docker compose exec worker-browsing python -m playwright install --with-deps chromium
```

Expected: Installs Playwright, creates `~/.cache/ms-playwright/`

### Step 7: Monitor Live Task Execution
Queue a test task and monitor worker logs:

**In one terminal (watch worker logs):**
```bash
docker compose logs -f worker-browsing
```

**In another terminal (trigger Deploy from UI):**
Click the "Deploy" button in the UI frontend.

**Expected sequence in logs:**
1. `[queues] . apply` (listening to apply queue)
2. `[Received task: app.celery_tasks.apply_queued_batch[...]]` (task received)
3. `[Task app.celery_tasks.apply_queued_batch[...] succeeded]` or similar
4. Apply activity (opening Playwright, logging in, applying jobs)

**If you DON'T see "Received task" message:**
- Worker is not listening to "apply" queue
- OR task is being routed to wrong queue
- OR worker died after startup

### Step 8: Check Worker Command Line Arguments
Verify the worker is starting with correct queue config:

```bash
docker compose logs worker-browsing | head -30 | grep "worker\|queue"
```

Expected to see:
```
...worker --loglevel=info --concurrency=1 -Q scraping,apply
```

If -Q flags are missing or different, check `start_browser_worker.sh`.

### Step 9: Check Redis Connection
Verify the worker can reach Redis:

```bash
docker compose exec worker-browsing redis-cli -a $(grep REDIS_PASSWORD .env | cut -d= -f2) ping
```

Expected: `PONG`

If connection fails, check REDIS_PASSWORD in .env.

### Step 10: Check Task Routing in Celery Config
Verify the task route exists:

```bash
docker compose exec backend python -c "from app.celery_app import celery_app; print(celery_app.conf.task_routes.get('app.celery_tasks.apply_queued_batch', 'NOT FOUND'))"
```

Expected: `{'queue': 'apply'}`

## Common Issues & Fixes

### Issue 1: Worker Starts But Shows Empty [tasks]
**Symptom:**
```
[tasks]
[worker] Connected to redis://...
```

**Root Cause:** Task module not being imported
**Fix:**
```bash
docker compose rebuild --no-cache worker-browsing
docker compose up -d --force-recreate worker-browsing
sleep 5
docker compose logs worker-browsing | head -50
```

### Issue 2: "Task unregistered" Error
**Symptom:**
```
Received an unregistered task of type 'app.celery_tasks.apply_queued_batch'
```

**Root Cause:** Worker restarted without registering tasks (short TTL)
**Fix:** Tasks re-register after 3600 seconds by default. Restart worker:
```bash
docker compose restart worker-browsing
```

### Issue 3: Playwright Browsers Not Found
**Symptom:**
```
playwright._repo._impl._driver_process.Error: Failed to connect to the browser.
```

**Root Cause:** Playwright chromium not installed
**Fix:**
```bash
docker compose exec worker-browsing python -m playwright install --with-deps chromium
# OR permanently in Dockerfile:
# RUN python -m playwright install --with-deps chromium
```

### Issue 4: Worker Crashes on Task Receive
**Symptom:**
```
Task worker crashed: ... (then worker stops)
```

**Likely Causes:**
- Missing dependency (e.g., browser not installed)
- Database connection error
- Redis connection lost

**Fix:**
```bash
# Check logs for actual error
docker compose logs worker-browsing --tail=100 | grep -i "error\|traceback"

# Restart and watch
docker compose restart worker-browsing
docker compose logs -f worker-browsing
```

### Issue 5: Worker Listens But Never Receives Tasks
**Symptom:**
```
[worker] Ready to accept tasks
... (but nothing comes through even after Deploy)
```

**Root Cause:** Task is being routed to wrong queue (e.g., default instead of apply)
**Fix:**
1. Check Redis to see where the task landed:
```bash
docker compose exec redis redis-cli -a $(grep REDIS_PASSWORD .env | cut -d= -f2) KEYS "celery*"
```

2. Verify task_routes in celery_app.py match task names exactly

3. Monitor Redis queues in real-time:
```bash
docker compose exec redis redis-cli -a $(grep REDIS_PASSWORD .env | cut -d= -f2) SUBSCRIBE celery
# (in another terminal, click Deploy)
```

## Expected Final State (Success)

After clicking Deploy button:

**Backend logs:**
```
POST /api/agent/run - Agent task dispatched
apply_queued dispatched to browser worker, celery_task_id=6c1c4e2c...
```

**Worker logs:**
```
[Received task: app.celery_tasks.apply_queued_batch[...]]
[celery.py] Applying to app_id=... (job_id=123456)
[playwright] Navigating to https://internshala.com/jobs/apply/...
[apply_bot] Applied successfully to job 123456
[apply_bot] Applied: 3, Skipped: 2, Failed: 0
[Task app.celery_tasks.apply_queued_batch[...] succeeded]
```

**Database:**
```sql
SELECT COUNT(*) FROM applications WHERE status='APPLIED' AND applied_at > NOW() - INTERVAL 1 MINUTE;
-- Should show count > 0
```

**Frontend:**
Agent status polling updates to show "Completed: Applied 3 jobs"

## Next Steps After Fixing Worker

1. **Monitor first 5 apply runs** for patterns in logs
2. **Record VNC session** (port 5900 in docker-compose.yml) to debug browser issues
3. **Set up automated retry logic** for failed applies
4. **Add email notifications** when deploy completes

---

## Quick Reference: Rebuild & Test Sequence

```bash
# 1. Rebuild worker
docker compose build --no-cache worker-browsing

# 2. Restart with force-recreate
docker compose up -d --no-deps --force-recreate worker-browsing

# 3. Wait 5 seconds
sleep 5

# 4. Check task registration (should NOT be empty)
docker compose logs worker-browsing | grep -A 20 "\[tasks\]"

# 5. Install Playwright (if needed)
docker compose exec worker-browsing python -m playwright install --with-deps chromium

# 6. Monitor logs while testing Deploy
docker compose logs -f worker-browsing | grep -E "Received|apply|success|error"

# 7. In separate terminal: test Deploy button from UI
# (watch the logs in terminal from step 6)
```
