# Applivo — Local Development Guide

This guide helps you run Applivo locally for development, testing, and debugging.

---

## 1. Quick Start (Docker)

```bash
# 1. Switch to development environment
cp .env.development .env

# 2. Start all servic       es
./scripts/dev-setup.sh up

# 3. Wait ~30 seconds for everything to boot, then test
./scripts/dev-setup.sh test

# 4. Open the app
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/api/docs
# Flower (Celery UI): http://localhost:5555
# VNC (watch browser): localhost:5900
```

### Useful Commands

```bash
./scripts/dev-setup.sh logs        # View all logs
./scripts/dev-setup.sh logs api    # Backend logs only
./scripts/dev-setup.sh logs browser # Browser worker logs
./scripts/dev-setup.sh shell       # Shell into backend container
./scripts/dev-setup.sh down        # Stop everything
./scripts/dev-setup.sh vnc         # VNC connection info
```

---

## 2. What's Different in Dev Mode?

| Feature | Production | Development |
|---------|-----------|-------------|
| Database | PostgreSQL on VPS | PostgreSQL in Docker (port 5433) |
| Redis | Redis on VPS | Redis in Docker (port 6380) |
| Backend | `uvicorn` (no reload) | `uvicorn --reload` (auto-restart on code changes) |
| Frontend | `next start` (standalone) | `next dev` with Turbopack |
| Browser | Headless | Visible via VNC on port 5900 |
| Rate Limits | Strict (5/min auth) | Relaxed (50/min auth) |
| Log Level | INFO | DEBUG |

---

## 3. Testing the Apply Bot

The #1 user complaint is "not applying." Here's how to diagnose and fix it.

### Step 1: Verify Internshala Connection

Upload your cookies via the dashboard **Settings → Connect Accounts**, then test:

```bash
curl -X POST http://localhost:8000/api/platform/test-connection/internshala \
  -H "Authorization: Bearer <YOUR_JWT_TOKEN>"
```

**Expected response if working:**
```json
{
  "connected": true,
  "reason": "Session is active and valid",
  "diagnostics": {
    "has_dashboard": true,
    "page_url": "https://internshala.com/student/dashboard"
  }
}
```

**If `connected: false`:**
- Your cookies expired → Re-upload fresh cookies
- You were blocked → Log in manually and try again
- Bot detection → Wait a few hours and retry

### Step 2: Trigger a Manual Scrape

```bash
curl -X POST http://localhost:8000/api/scheduler/trigger/scrape_jobs \
  -H "Authorization: Bearer <YOUR_JWT_TOKEN>"
```

Then check Flower (http://localhost:5555) to see if the scraping task succeeded.

### Step 3: Check Job Analysis

After scraping, jobs should have `status: "ANALYZED"` with a `match_score`.

```bash
curl http://localhost:8000/api/jobs \
  -H "Authorization: Bearer <YOUR_JWT_TOKEN>"
```

### Step 4: Queue & Apply

Create an application manually:

```bash
curl -X POST http://localhost:8000/api/applications \
  -H "Authorization: Bearer <YOUR_JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"job_id": "<JOB_UUID>"}'
```

Then trigger the apply bot for that application:

```bash
curl -X POST http://localhost:8000/api/agent/apply/<APPLICATION_UUID> \
  -H "Authorization: Bearer <YOUR_JWT_TOKEN>"
```

Watch the browser worker logs in real-time:
```bash
./scripts/dev-setup.sh logs browser
```

If you have VNC Viewer open at `localhost:5900`, you can **literally watch the bot fill the form**.

---

## 4. Common "Not Applying" Issues & Fixes

### Issue: "Session expired. Run save_cookies.py."

**Cause:** Cookies expired or were invalidated.

**Fix:**
1. Log in to Internshala in your real browser
2. Open DevTools → Application → Cookies → `.internshala.com`
3. Copy all cookies as JSON array
4. Paste into Dashboard → Settings → Connect Accounts → Upload Cookies
5. Re-run `/api/platform/test-connection/internshala`

### Issue: "No Apply button found on detail page"

**Cause:** Internshala changed their HTML structure.

**Fix:**
- Check the screenshot in `storage/screenshots/` for the job page
- The bot tries 20+ selectors; if all fail, the page structure changed
- Update selectors in `app/agents/apply_bot_internshala.py` around line 2366

### Issue: "Bot detected" or "CAPTCHA"

**Cause:** Internshala detected automation.

**Fix:**
- The bot has anti-detection measures, but platforms evolve
- Try using a residential proxy:
  ```env
  BROWSER_PROXY_SERVER=http://proxy-provider.com:8080
  BROWSER_PROXY_USER=your_user
  BROWSER_PROXY_PASS=your_pass
  ```
- Reduce apply frequency (increase `SCRAPE_INTERVAL_HOURS`)
- Use VNC to manually solve CAPTCHA when it appears

### Issue: "External job posting - requires manual application"

**Cause:** The job redirects to an external site (Indeed, LinkedIn, etc.).

**Fix:** This is expected. The bot only handles Internshala native applications. External postings are marked as FAILED with `retry_count=999` so they aren't retried.

### Issue: Applications stuck in `PENDING_APPROVAL`

**Cause:** `AUTO_APPLY_REQUIRE_APPROVAL=true` in `.env`.

**Fix:** In dev mode, set it to `false` for automatic applying:
```env
AUTO_APPLY_REQUIRE_APPROVAL=false
```

---

## 5. Running Without Docker (Native)

If you prefer running services directly on your machine:

### Prerequisites
```bash
# macOS
brew install postgresql@16 redis python@3.11 node@20

# Start services
brew services start postgresql@16
brew services start redis

# Python deps
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Node deps (frontend)
cd frontend && npm install
```

### Start Backend
```bash
source .venv/bin/activate
cp .env.development .env
uvicorn app.main:app --reload --port 8000
```

### Start Frontend
```bash
cd frontend
npm run dev
```

### Start Celery Workers
```bash
# Terminal 1: Standard worker
source .venv/bin/activate
celery -A app.celery_app:celery_app worker --loglevel=info -Q default,analysis,notifications,email_monitor,priority

# Terminal 2: Browser worker (needs Playwright + display)
source .venv/bin/activate
export DISPLAY=:99
Xvfb :99 -screen 0 1920x1080x24 &
celery -A app.celery_app:celery_app worker --loglevel=info --pool=solo --concurrency=1 -Q scraping,apply
```

---

## 6. Code Changes Summary

Here's what was fixed for the development environment:

| File | Fix |
|------|-----|
| `.env.development` | New file with safe local dev defaults |
| `docker-compose.dev.yml` | New compose file with hot reload, dev ports, smaller Redis memory |
| `app/api/routes/scheduler.py` | **SECURITY:** Added `get_current_user` auth to all scheduler endpoints |
| `app/services/cookie_service.py` | Fixed invalid type hint `Union[Optional[dict, list]]` |
| `app/agents/apply_bot_internshala.py` | DB cookies now preferred over shared file (multi-user bug); fixed disabled-button waiting logic |
| `app/agents/apply_bot.py` | Removed `--disable-web-security` which broke SameSite cookies |
| `app/services/application_service.py` | Fixed `db.rollback()` inside loop that discarded all previous applications |
| `app/api/routes/platform.py` | Added `/platform/test-connection/{platform}` endpoint for cookie diagnostics |
| `frontend/next.config.ts` | Build error ignoring now only in production |
| `scripts/start_browser_worker.sh` | Respects `LOG_LEVEL` env var |
| `scripts/dev-setup.sh` | New convenience script for managing dev environment |

---

## 7. Switching Back to Production

```bash
# 1. Stop dev services
./scripts/dev-setup.sh down

# 2. Restore production env
cp .env.production .env   # or git checkout .env

# 3. Deploy as usual
docker compose -f docker-compose.yml up -d
```

---

## 8. Need Help?

- Check backend logs: `./scripts/dev-setup.sh logs api`
- Check browser logs: `./scripts/dev-setup.sh logs browser`
- Check Flower for task failures: http://localhost:5555
- Look at screenshots: `storage/screenshots/`
- Test connection: `POST /api/platform/test-connection/internshala`
