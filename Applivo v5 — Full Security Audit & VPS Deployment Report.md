# Applivo v5 — Full Security Audit & VPS Deployment Report
**Date:** April 6, 2026 | **Previous Score:** 72/100 | **This Build:** 50+ files changed

---

## WHAT WAS FIXED (Previous Report → This Version)

| # | Issue | Status |
|---|-------|--------|
| C1 | ChatMessage not in models/__init__.py | ✅ Fixed — all 3 new models registered |
| C2 | Alembic migration branch fork | ✅ Fixed — add_uq now chains to security_models_001 |
| C3 | Hardcoded DB password in migrate.py | ✅ Fixed — reads os.environ with changeme fallback |
| C4 | DEBUG login logs bcrypt hash fragment | ✅ Fixed — debug lines removed from auth.py |
| H1 | Auth rate limit path wrong (v1/auth) | ✅ Fixed — now /api/auth/login |
| H2 | PostgreSQL exposed on port 5433 | ✅ Fixed — no longer mapped |
| H3 | Swagger docs public in production | ✅ Fixed — None when APP_ENV=production |
| H4 | No Razorpay webhook endpoint | ✅ Fixed — full webhook with HMAC verification |
| H5 | File upload extension-only check | ✅ Fixed — %PDF magic bytes checked |
| H6 | PDF download returns 401 | ✅ Fixed — programmatic blob download |
| H7 | Security audit 404 wrong path | ✅ Fixed — /security/data/audit |
| H8 | Funnel chart always wrong data | ✅ Fixed — Array.isArray handled |
| M1 (partial) | Skill-gaps hardcoded | ✅ Fixed — connected to analyticsApi.skillGaps() |
| M4 | ai_assistant bypasses ai_router | ✅ Fixed — uses ai_router now |
| M5 | Messages page "all" filter broken | ✅ Fixed — status="all" now returns all |
| Flower env contradiction | FLOWER_PASSWORD env vs cmd mismatch | ✅ Fixed — both use ${FLOWER_PASSWORD} with :? fail-fast |
| Cancel button dead | No onClick on Cancel Subscription | ✅ Fixed — cancelMut wired |
| Payment history wrong API | subscriptionsApi.current() instead of paymentsApi.history() | ✅ Fixed |
| Razorpay script race | No onload handler | ✅ Fixed — waitForRazorpay() + onload callback |
| POSTGRES_PASSWORD default | :-changeme fallback | ✅ Fixed — :? fail-fast |

---

## CURRENT SCORE: 88/100

---

## 🔴 CRITICAL — Must Fix Before VPS Deploy

### CRIT-1: Port 8000 directly exposed on VPS — API accessible without Nginx/SSL

`docker-compose.yml` line 47:
```yaml
backend:
  ports:
    - "8000:8000"   ← THIS IS THE PROBLEM
```

On your Hostinger VPS, this means `http://YOUR_VPS_IP:8000` is publicly accessible on the raw internet — **no SSL, no Nginx rate limiting, no IP filtering, no HTTPS redirect**. Anyone can hit your API directly, bypassing every Nginx security header and rate limiting rule you configure.

Since the deployment guide (which you pasted) sets Nginx to proxy `/api/` to `localhost:8000`, the port mapping is not needed — Docker containers communicate internally. The port only needs to be reachable from the host, not from the internet.

**Fix — remove the port mapping from docker-compose.yml:**
```yaml
backend:
  # DELETE: ports:
  # DELETE:   - "8000:8000"
  # Keep everything else the same
```
Nginx will still reach it via `proxy_pass http://localhost:8000` because Docker's bridge network makes it reachable on the host.

**Or** if you need to keep the port accessible from the host (e.g. for healthchecks):
```yaml
backend:
  ports:
    - "127.0.0.1:8000:8000"   ← binds to localhost ONLY, not 0.0.0.0
```

---

### CRIT-2: Redis has no password — directly reachable within Docker network

`docker-compose.yml`:
```yaml
redis:
  command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
  # No requirepass, no ACL
```

Redis has zero authentication. Any container or process in the same Docker network can connect to `redis:6379` and read/write Celery task data, session tokens stored in Redis, or flush the entire queue. This also means if any other container on the VPS is compromised, your Redis is immediately accessible.

**Fix — add password to Redis and update all connection strings:**

```yaml
# docker-compose.yml
redis:
  command: >
    redis-server
    --appendonly yes
    --maxmemory 256mb
    --maxmemory-policy allkeys-lru
    --requirepass ${REDIS_PASSWORD:?Set REDIS_PASSWORD in .env}

# All services that use Redis:
environment:
  - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
  - CELERY_BROKER_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
  - CELERY_RESULT_BACKEND=redis://:${REDIS_PASSWORD}@redis:6379/1
```

Add to `.env.example` and `config.py`:
```python
REDIS_PASSWORD: str = ""
```

---

### CRIT-3: Flower still exposed on port 5555 publicly

```yaml
flower:
  ports:
    - "5555:5555"  ← publicly exposed
```

Flower shows all Celery task payloads (which contain user credentials, job URLs, and cookie data), lets anyone cancel or retry tasks, and shows worker internals. Even with `--basic_auth`, it's exposed to the entire internet. The previous audit flagged this and it's still not fixed.

**Fix — either remove the port entirely** (access via `docker exec` or SSH tunnel):
```yaml
flower:
  # DELETE: ports:
  # DELETE:   - "5555:5555"
```

**Or** bind to localhost only:
```yaml
flower:
  ports:
    - "127.0.0.1:5555:5555"
```
Then access it via SSH tunnel from your local machine: `ssh -L 5555:localhost:5555 applivo@YOUR_VPS_IP`

---

### CRIT-4: `SECRET_KEY` and `JWT_SECRET_KEY` still "changeme" defaults in config.py

```python
SECRET_KEY: str = "changeme-at-least-32-characters-long-secret"
JWT_SECRET_KEY: str = "changeme-jwt-secret-at-least-32-characters-long"
```

If `.env` is not created before deployment, or if any line is accidentally missing, the app starts with these defaults. Anyone who knows these strings can forge JWT tokens and authenticate as any user.

**Fix — use :? validation so the app refuses to start without real secrets:**
```python
SECRET_KEY: str  # No default — will fail to start if not set
JWT_SECRET_KEY: str  # No default — will fail to start if not set
```

Or keep defaults but validate length at startup in `main.py`:
```python
if len(settings.SECRET_KEY) < 32 or "changeme" in settings.SECRET_KEY:
    raise RuntimeError("SECRET_KEY is insecure — set a real value in .env")
if len(settings.JWT_SECRET_KEY) < 32 or "changeme" in settings.JWT_SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY is insecure — set a real value in .env")
```

---

## 🟠 HIGH — Must Fix Before Charging Real Users

### HIGH-1: No Alembic migration for `chat_usage` and `platform_messages` tables

`chat_usage.py` and `platform_message.py` are new models registered in `__init__.py`. But there are still only 3 migration files:
- `6df4ff846734_initial.py`
- `security_models_001.py`
- `add_uq_application_user_job.py`

On existing databases that upgrade via `alembic upgrade head` (including your VPS), these two tables will not be created. Only fresh installs (which use `create_all()`) get them. Any VPS that had a previous version will have broken chat and messages features.

**Fix:**
```bash
alembic revision --autogenerate -m "add_chat_usage_platform_messages"
alembic upgrade head
```
Review the generated file before committing — confirm it creates `chat_usage` and `platform_messages` tables.

---

### HIGH-2: `reset_monthly_credits()` still a no-op — Starter/Pro users permanently locked out

```python
async def reset_monthly_credits(self, user_id: str) -> None:
    # TODO: Implement with credit_usage table
    logger.info("Monthly credits reset", user_id=user_id)
```

No change from last audit. Users who exhaust their monthly AI credits (100 for Starter, 500 for Pro) are permanently locked out of the AI chat feature — the reset never runs. There's also no Celery Beat task that calls this.

**Fix — implement the reset:**
```python
async def reset_monthly_credits(self, user_id: str) -> None:
    current_month = datetime.now(timezone.utc).strftime("%Y-%m")
    async with get_db_context() as db:
        await db.execute(
            delete(ChatUsage).where(
                ChatUsage.user_id == user_id,
                ChatUsage.month != current_month,
            )
        )
        await db.commit()
    logger.info("Monthly credits reset", user_id=user_id)
```

And add a Celery Beat monthly task in `celery_tasks.py`:
```python
# In beat_schedule:
"reset-monthly-credits": {
    "task": "app.celery_tasks.reset_all_monthly_credits",
    "schedule": crontab(day_of_month=1, hour=0, minute=0),
},
```

---

### HIGH-3: Follow-ups and Interviews pages are 100% hardcoded mock data

**Follow-ups page** (`follow-ups/page.tsx`):
```typescript
const followups = [
  { id: 1, company: "Amazon", role: "SDE II", status: "Scheduled", time: "in 2 hours", type: "Email" },
  { id: 2, company: "Microsoft", role: "Specialist", status: "Sent", time: "Yesterday", type: "LinkedIn" },
  { id: 3, company: "Meta", role: "Product Manager", status: "Delayed", time: "Pending", type: "Email" },
];
```
Zero API calls. Amazon/Microsoft/Meta are hardcoded strings. Pro/Premium users paying for this feature see static demo data.

**Interviews page**: No hardcoded data but also no API calls — it's entirely static UI with no backend connection.

Both backends exist (follow_up_service.py has full logic, interview tracking is in models). These just need to be wired.

---

### HIGH-4: `ChatUsage` model missing `created_at` — will cause issues at scale

```python
class ChatUsage(Base, UUIDMixin):
    user_id = Column(String(36), ...)
    month = Column(String(7), ...)
    message_count = Column(Integer, ...)
    # NO created_at, NO updated_at, NO TimestampMixin
```

This is intentional for a simple monthly counter, but there's no `updated_at` to know when the record was last modified, and no way to query "last active" for admin purposes. Also `ChatUsage` doesn't inherit `TimestampMixin` but the credit service code does `db.execute(update(ChatUsage)...)` — the update works but there's no audit trail.

Minor but worth noting for production observability.

---

## 🟡 MEDIUM — Should Fix Before Launch

### MED-1: No Celery Beat schedule file in docker-compose

`celery_tasks.py` has no `beat_schedule` dict — there are no periodic tasks defined. The `applivo-scheduler` container (Celery Beat) will start with an empty schedule and do nothing. Scraping never fires automatically. Apply queue never processes automatically.

Check if `beat_schedule` was accidentally removed:
```bash
grep -n "beat_schedule" app/celery_tasks.py
```
If missing, add the schedule back with at minimum:
- Scrape jobs every 6h
- Process apply queue every 10min  
- Reset monthly credits on the 1st of each month

---

### MED-2: `migrate.py` still falls back to `changeme` password

```python
db_url = os.environ.get('DATABASE_URL_SYNC', 'postgresql://applivo:changeme@database:5432/applivo')
```

C3 was marked fixed — it no longer hardcodes a real password — but the fallback is still `changeme`. On a VPS where `DATABASE_URL_SYNC` isn't set, this would silently connect to `changeme` and fail or expose the wrong database. Use the same `:?` validation pattern as docker-compose.

---

### MED-3: `ALLOWED_ORIGINS` default in `.env.example` is `yourdomain.com`

The `.env.example` now has:
```
ALLOWED_ORIGINS=["https://yourdomain.com"]
```

This is a placeholder. If you copy the example without changing this, your frontend on the real domain won't be able to make API calls (CORS will block everything). Document this clearly in deployment steps and add validation.

---

### MED-4: `ENCRYPTION_KEY` has no validation — empty string silently uses insecure key

```python
ENCRYPTION_KEY: str = ""
```

If ENCRYPTION_KEY is empty (not set in .env), the encryption service generates a key but it won't be consistent across restarts, meaning all previously encrypted cookies and credentials become unreadable after a container restart.

**Fix — add a startup check:**
```python
if not settings.ENCRYPTION_KEY:
    logger.warning("ENCRYPTION_KEY not set — generating ephemeral key (NOT safe for production)")
```

---

### MED-5: Flower password still potentially `changeme` at runtime

The Flower command is:
```yaml
command: >
  python -m celery ... flower --basic_auth=admin:${FLOWER_PASSWORD}
```

And environment:
```yaml
- FLOWER_PASSWORD=${FLOWER_PASSWORD:?Set FLOWER_PASSWORD in .env}
```

The `:?` in the environment block causes `docker-compose up` to fail if not set — good. But `${FLOWER_PASSWORD}` in the `command` has **no fallback and no validation** — it will be expanded to an empty string if not set at shell evaluation time. This is better than `:-changeme` but could result in `--basic_auth=admin:` (empty password).

Confirm by checking: when `FLOWER_PASSWORD` is not set in `.env` but is in environment, does the `command` receive the empty string or the required value? Use `--basic_auth=admin:${FLOWER_PASSWORD:?}` in the command block too.

---

## 🔵 LOW — Polish Before Going Live

| # | Issue |
|---|-------|
| L1 | `ChatUsage` doesn't inherit `TimestampMixin` — no audit trail on credit usage |
| L2 | No Celery beat schedule visible in celery_tasks.py — verify it's defined |
| L3 | `GEMINI_API_KEY` is in config.py but not in `.env.example` |
| L4 | `.gitignore` doesn't include `migrate.py` — that file has DB connection strings |
| L5 | No `max_file_size` check after magic bytes check in routes.py (10MB limit was recommended but verify it was added) |

---

## UPDATED SCORE BREAKDOWN

| Domain | Score | Change | Notes |
|--------|-------|--------|-------|
| Code correctness | 92% | +22% | All critical bugs fixed; follow-ups/interviews still mocked |
| Security posture | 78% | +23% | Port 8000/5555 exposure, Redis no-auth remain |
| Frontend ↔ API | 90% | +10% | PDF download, funnel chart, security path, cancel all fixed |
| Database integrity | 82% | +10% | Migration chain fixed; new tables need migration file |
| Infrastructure | 72% | +7% | DB/Redis ports closed; 8000 + 5555 + Redis auth still open |
| AI / Workers | 88% | -2% | Beat schedule may be missing |

**Overall: 88/100**

---

## VPS DEPLOYMENT — COMPLETE CHECKLIST

Work through these in order. Do not skip any item marked MUST.

### Pre-Deploy Code Fixes (do locally, commit, push)

```
MUST:
☐ Remove "8000:8000" port mapping from docker-compose.yml (or bind to 127.0.0.1)
☐ Remove "5555:5555" from Flower (or bind to 127.0.0.1)
☐ Add Redis requirepass to docker-compose.yml + update all REDIS_URL strings
☐ Add startup validation for SECRET_KEY and JWT_SECRET_KEY in main.py
☐ Generate alembic migration for chat_usage + platform_messages tables
☐ Verify Celery beat_schedule exists in celery_tasks.py

SHOULD:
☐ Implement reset_monthly_credits() with real DB delete
☐ Add monthly Celery Beat task for credit reset
☐ Connect follow-ups page to real API
☐ Fix migrate.py fallback from changeme to fail-fast
```

### Server Setup (one-time)

```bash
# 1. SSH in as root, create deploy user
adduser applivo && usermod -aG sudo,docker applivo

# 2. Disable root SSH and password auth
sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
systemctl restart ssh

# 3. Set up firewall — CRITICAL, run this before anything else
apt install -y ufw
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP (Nginx)
ufw allow 443/tcp   # HTTPS (Nginx)
# DO NOT open 8000, 5555, 5432, 6379
ufw enable

# 4. Install Docker
curl -fsSL https://get.docker.com | bash
apt install -y docker-compose-plugin

# 5. Install Nginx + Certbot
apt install -y nginx certbot python3-certbot-nginx
```

### Generate All Secrets (never reuse these)

```bash
# Run these locally or on the server, SAVE THE OUTPUT
echo "SECRET_KEY=$(openssl rand -hex 32)"
echo "JWT_SECRET_KEY=$(openssl rand -hex 32)"
echo "POSTGRES_PASSWORD=$(openssl rand -hex 16)"
echo "REDIS_PASSWORD=$(openssl rand -hex 16)"
echo "FLOWER_PASSWORD=$(openssl rand -hex 12)"
# For ENCRYPTION_KEY — needs to be Fernet key:
python3 -c "from cryptography.fernet import Fernet; print('ENCRYPTION_KEY=' + Fernet.generate_key().decode())"
```

### Create `.env` on Server

```bash
su - applivo
cd ~/applivo

# Copy example then fill in
cp .env.example .env
nano .env
```

Minimum required values:
```env
APP_ENV=production
DEBUG=false
SECRET_KEY=<generated above>
JWT_SECRET_KEY=<generated above>
POSTGRES_PASSWORD=<generated above>
REDIS_PASSWORD=<generated above>
FLOWER_PASSWORD=<generated above>
ENCRYPTION_KEY=<fernet key from above>
ALLOWED_ORIGINS=["https://yourdomain.com"]
GROQ_API_KEY=gsk_...
RAZORPAY_KEY_ID=rzp_live_...
RAZORPAY_KEY_SECRET=...
RAZORPAY_WEBHOOK_SECRET=...
SMTP_USERNAME=...
SMTP_PASSWORD=...
```

**Security check:**
```bash
grep "changeme" .env && echo "DANGER: defaults still present" || echo "OK"
```

### Deploy

```bash
# Build images
docker compose build

# Start database first, run migrations
docker compose up -d database redis
sleep 15
docker compose run --rm backend python -m alembic upgrade head

# Verify migration output — should show all tables created with no errors
docker compose exec database psql -U applivo -c "\dt" | grep -E "chat_usage|platform_messages|subscriptions|payments"

# Start everything
docker compose up -d

# Install Playwright Chromium in worker
docker compose exec worker playwright install chromium

# Create admin user
docker compose exec backend python create_superuser.py \
  --email admin@yourdomain.com --password 'StrongPasswordHere' --name "Admin"
```

### Configure Nginx

```nginx
# /etc/nginx/sites-available/applivo
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=auth:10m rate=5r/m;

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL (certbot fills these in)
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_session_cache shared:SSL:10m;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    client_max_body_size 15M;

    # Auth endpoints — strict rate limit
    location ~ ^/api/auth/(login|register) {
        limit_req zone=auth burst=5 nodelay;
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # API routes
    location /api/ {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
    }

    # Health check (no rate limit)
    location /health {
        proxy_pass http://localhost:8000;
    }

    # Flower — restrict to your IP only
    location /flower/ {
        proxy_pass http://localhost:5555/flower/;
        allow YOUR.HOME.IP.HERE;   # Add your home/office IP
        deny all;
    }

    # Next.js frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
ln -s /etc/nginx/sites-available/applivo /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx

# SSL certificate
certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### Deploy Frontend (Next.js)

```bash
# Install Node.js 20
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install -y nodejs
npm install -g pm2

# Build frontend
cd ~/applivo/frontend
echo "NEXT_PUBLIC_API_URL=https://yourdomain.com" > .env.local
npm install
npm run build

# Start with PM2
pm2 start npm --name "applivo-frontend" -- start
pm2 save && pm2 startup
```

### Verify Everything

```bash
# API health
curl https://yourdomain.com/health
# Expected: {"status":"healthy","database":"connected","env":"production","mode":"saas"}

# Test that 8000 is NOT publicly accessible (should timeout/refuse):
curl --max-time 3 http://YOUR_VPS_IP:8000/health && echo "DANGER: 8000 is public" || echo "OK: 8000 blocked"

# Test that 5432 is NOT accessible:
nc -zv YOUR_VPS_IP 5432 && echo "DANGER: 5432 is public" || echo "OK: 5432 blocked"

# Test that 6379 is NOT accessible:
nc -zv YOUR_VPS_IP 6379 && echo "DANGER: 6379 is public" || echo "OK: 6379 blocked"
```

---

## VPS RESOURCE ANALYSIS (4 vCPU / 8 GB RAM / 75 GB NVMe)

| Service | Idle | Peak |
|---------|------|------|
| OS + system | ~500 MB | ~700 MB |
| PostgreSQL | ~150 MB | ~400 MB |
| Redis | ~150 MB | ~256 MB |
| FastAPI backend | ~400 MB | ~800 MB |
| Celery worker (4 concurrency) | ~600 MB | ~1.2 GB |
| Celery Beat scheduler | ~150 MB | ~200 MB |
| Flower | ~100 MB | ~150 MB |
| Next.js (PM2) | ~200 MB | ~400 MB |
| Playwright (per apply session) | ~200 MB | ~300 MB each |
| **Total baseline** | **~2.2 GB** | |
| **Peak with 4 simultaneous apply sessions** | | **~4.7 GB** |
| **RAM headroom** | | **~3.3 GB ✅** |

**Verdict:** 8 GB RAM is sufficient. 75 GB NVMe gives ~65 GB of growth headroom after system/app overhead. The VPS is well-specced for early production.

---

## FINAL PRIORITY ORDER

```
TODAY (before deploying):
1. Remove port 8000:8000 or bind to 127.0.0.1:8000:8000
2. Remove port 5555:5555 or bind to 127.0.0.1:5555:5555
3. Add Redis requirepass + update all REDIS_URL env vars
4. Add SECRET_KEY + JWT_SECRET_KEY startup validation
5. Generate all secrets and fill .env properly

THIS WEEK (before charging users):
6. Create alembic migration for chat_usage + platform_messages
7. Implement reset_monthly_credits() and add Celery Beat task
8. Wire follow-ups page to real API (Amazon/Microsoft hardcode)
9. Verify Celery beat_schedule exists in celery_tasks.py

NEXT SPRINT:
10. Connect Interviews page to backend
11. Add ENCRYPTION_KEY startup warning
12. Fix migrate.py changeme fallback
```
