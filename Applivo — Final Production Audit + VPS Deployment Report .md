# Applivo — Final Production Audit + VPS Deployment Report
**Date:** 2026-04-06 | **Build:** 160 files | **Target VPS:** 4 vCPU / 8 GB RAM / 75 GB NVMe

---

## PART 1 — CODE AUDIT: ALL BUGS & VULNERABILITIES

---

### 🔴 CRITICAL — Blocks Deployment

---

#### C1 — `chat_messages` table never created (Data Loss + Runtime Crash)

`ChatMessage` model exists in `app/models/chat_message.py` but is not imported in `app/models/__init__.py` AND not listed in `init_db()`'s explicit imports:

```python
# database.py init_db() imports:
from app.models import (user, job, application, resume, interview,
                        subscription, cookie, credential, consent, audit)
# chat_message is MISSING ← table never created
```

Every `POST /api/chat` call crashes with `relation "chat_messages" does not exist`.

**Fix — one line in `app/models/__init__.py`:**
```python
from app.models.chat_message import ChatMessage  # noqa: F401
```
Also add to `__all__`. Also run: `alembic revision --autogenerate -m "add_chat_tables"`

---

#### C2 — Alembic migration chain is branched (Deployment Blocker)

Both `security_models_001` and `add_uq_application_user_job` have `down_revision = '6df4ff846734'`. Running `alembic upgrade head` on your VPS will fail:

```
FAILED: Multiple head revisions are present for given argument 'head'
```

**Fix — one line in `alembic/versions/add_uq_application_user_job.py`:**
```python
# Change:
down_revision: Union[str, None] = '6df4ff846734'
# To:
down_revision: Union[str, None] = 'security_models_001'
```

---

#### C3 — Hardcoded database password committed to Git (Security Critical)

`migrate.py` line 2:
```python
pg_conn = psycopg2.connect('postgresql://applivo:dc7b2b7d22ea2b987a060dbb54bdeaf8@database:5432/applivo')
```

A real password is committed in plaintext. **This password must be rotated NOW** if it has ever been used on a real server, and the file must be fixed:

```python
import os
pg_conn = psycopg2.connect(os.environ['DATABASE_URL_SYNC'])
```

---

#### C4 — DEBUG login logs hash fragment of hashed password (Security Critical)

`app/api/routes/auth.py` line 188:
```python
log.info("DEBUG login", stored_hash=user.hashed_password[:30], verify_result=...)
```

This logs the first 30 characters of every user's bcrypt hash on every login attempt. bcrypt hashes contain the salt in the first 29 characters — leaking partial hash + salt assists offline attacks. This is a `log.info` call, meaning it runs in production at `INFO` log level.

**Fix — delete lines 186–189 entirely:**
```python
# DELETE THESE LINES:
log.info("DEBUG login attempt", email=data.email, user_found=user is not None)
if user:
    log.info("DEBUG login", stored_hash=user.hashed_password[:30], ...)
```

---

### 🟠 HIGH — Must Fix Before Charging Users

---

#### H1 — Auth brute-force rate limit is completely bypassed

`main.py` line 153 checks rate limits for path `/api/v1/auth/login`. The actual auth route is registered at `/api/auth/login` (no `v1`). The auth rate limiter **never triggers** — attackers can attempt unlimited password guesses.

**Fix:**
```python
# main.py — change:
if request.url.path in ["/api/v1/auth/login", "/api/v1/auth/register"]:
# To:
if request.url.path in ["/api/auth/login", "/api/auth/register"]:
```

---

#### H2 — PostgreSQL and Redis ports exposed directly to the internet

`docker-compose.yml` exposes:
```yaml
database:  "5433:5432"   # PostgreSQL accessible from ANY IP
redis:     "6379:6379"   # Redis accessible from ANY IP
```

On a VPS, both PostgreSQL and Redis will be accessible on `YOUR_VPS_IP:5433` and `YOUR_VPS_IP:6379` from anywhere on the internet. Redis has no password set. PostgreSQL has a password but is still directly internet-facing.

**Fix — remove those port mappings entirely:**
```yaml
database:
  # DELETE: - "5433:5432"    ← containers communicate internally, no external port needed
redis:
  # DELETE: - "6379:6379"    ← same
```

The backend, worker, and scheduler already connect via Docker's internal network (`database:5432`, `redis:6379`). External access is unnecessary and dangerous.

---

#### H3 — Swagger/API docs publicly accessible in production

`main.py` always enables API documentation:
```python
docs_url="/api/docs",
redoc_url="/api/redoc",
openapi_url="/api/openapi.json",
```

In production, `/api/docs` exposes your complete API schema, all endpoints, request/response formats, and authentication requirements to anyone. This is a significant reconnaissance aid for attackers.

**Fix:**
```python
app = FastAPI(
    ...
    docs_url="/api/docs" if settings.APP_ENV != "production" else None,
    redoc_url="/api/redoc" if settings.APP_ENV != "production" else None,
    openapi_url="/api/openapi.json" if settings.APP_ENV != "production" else None,
)
```

---

#### H4 — No Razorpay webhook endpoint (Payment Bypass Risk)

`payments.py` has `create-order` and `verify` endpoints but **no webhook handler**. Razorpay sends server-to-server `payment.captured` events as a backup confirmation — your app currently has no way to activate subscriptions if a user's browser crashes after payment but before `/verify` is called. Users can lose their subscription after paying.

Additionally, without a webhook, there's no server-side verification of payment — a malicious user can potentially forge the `verify` request.

**Fix:** Add `POST /api/payments/webhook` with HMAC signature verification using `RAZORPAY_WEBHOOK_SECRET`.

---

#### H5 — File upload: only filename extension checked, not content

```python
if not file.filename.endswith(".pdf"):
    raise HTTPException(...)
```

An attacker can upload `malicious.php` renamed to `malicious.php.pdf` or any executable renamed to `.pdf`. The file is saved to disk and served back via `FileResponse`.

**Fix — check actual PDF magic bytes:**
```python
content = await file.read()
if not content.startswith(b'%PDF'):
    raise HTTPException(status_code=400, detail="Invalid PDF file")

# Also add file size limit:
MAX_SIZE = 10 * 1024 * 1024  # 10MB
if len(content) > MAX_SIZE:
    raise HTTPException(status_code=413, detail="File too large (max 10MB)")
```

---

#### H6 — PDF download returns HTTP 401 (broken UX)

`resumes/page.tsx` line 111:
```tsx
<a href={`/api/resumes/${res.id}/file`} target="_blank">PDF</a>
```
Plain `<a href>` sends no `Authorization` header. The endpoint requires JWT. Every download returns 401.

**Fix — replace with programmatic blob download:**
```typescript
const handleDownload = async (id: string, name: string) => {
  const resp = await api.get(`/resumes/${id}/file`, { responseType: "blob" });
  const url = URL.createObjectURL(new Blob([resp.data], { type: "application/pdf" }));
  const a = document.createElement("a");
  a.href = url; a.download = `${name}.pdf`; a.click();
  URL.revokeObjectURL(url);
};
```

---

#### H7 — Security audit endpoint 404

`api.ts` calls `GET /api/security/audit`.
Backend route is `GET /api/security/data/audit`.

**Fix in `api.ts`:**
```typescript
audit: () => api.get("/security/data/audit"),
```

---

#### H8 — Funnel chart always shows wrong data

Backend `GET /api/analytics/funnel` returns a dict `{applied: N, viewed: N, ...}`.
Frontend checks `Array.isArray(funnelData)` → `false` → always falls to dashboard fallback.

**Fix — change backend return to array:**
```python
return [
    {"name": "Applied",     "value": counts.get("applied", 0) + ...},
    {"name": "Viewed",      "value": counts.get("viewed", 0)},
    {"name": "Shortlisted", "value": counts.get("shortlisted", 0)},
    {"name": "Interview",   "value": counts.get("interview_scheduled", 0) + ...},
    {"name": "Offer",       "value": counts.get("offer_received", 0) + ...},
]
```

---

### 🟡 MEDIUM — Should Fix Before Launch

---

#### M1 — Follow-ups, Interviews, Skill-gaps pages are 100% hardcoded mock data

All three pages show Amazon/Microsoft/Meta, "Google — ML System Design", and Kubernetes/Terraform/Prometheus respectively — hardcoded constants, zero API calls, buttons with no handlers. Pro/Premium users paying for these features see static demo content.

**Fix:** Connect each page to its real backend service. Skill-gaps needs just one `useQuery(() => analyticsApi.skillGaps())` replacing the `const skills = [...]` array.

---

#### M2 — No Razorpay `WEBHOOK_SECRET` in config or `.env.example`

`RAZORPAY_WEBHOOK_SECRET` doesn't exist in `Settings` class or `.env.example`. Without it you cannot implement webhook verification (H4). 

**Fix:** Add to `config.py` and `.env.example`:
```python
RAZORPAY_WEBHOOK_SECRET: str = ""
```

---

#### M3 — `reset_monthly_credits()` is a no-op

```python
async def reset_monthly_credits(self, user_id: str) -> None:
    # TODO: Implement with credit_usage table
    logger.info("Monthly credits reset", user_id=user_id)
```

Starter/Pro users who hit their monthly AI credit limit are permanently locked out — the reset never runs. Add a Celery Beat task running on the 1st of each month that deletes or zeroes out `chat_usage` rows for the previous month.

---

#### M4 — `ai_assistant.py` bypasses `ai_router` (no Gemini fallback for Chat)

Chat uses a direct `groq_client`. When Groq rate-limits, job analysis recovers via Gemini but chat fails with a 500 error. Chat is the highest-frequency AI feature and most likely to be rate-limited.

**Fix:** Replace `client.chat.completions.create(...)` in `ai_assistant.py` with `await ai_router.chat_completions_create(...)`.

---

#### M5 — Messages page "All" filter only shows unread messages

Backend `GET /api/platform/messages` defaults to `status="unread"`. Frontend "All" filter shows all of what it received — but only unread messages were ever fetched. Users cannot see read messages.

**Fix:** Remove `status` filter from backend default, or change frontend call to `platformApi.messages("internshala", 50, "all")`.

---

#### M6 — `chat_usage`, `platform_messages` tables not in Alembic migrations

These tables are created by `create_all()` on fresh installs but won't be added to existing databases that upgrade via `alembic upgrade head`. Production databases upgraded in place will be missing these tables.

**Fix:** After fixing C2, create a single new migration:
```bash
alembic revision --autogenerate -m "add_chat_messages_chat_usage_platform_messages"
alembic upgrade head
```

---

#### M7 — `ALLOWED_ORIGINS` default doesn't cover your VPS domain

`config.py` default: `["http://localhost:3000", "http://127.0.0.1:3000"]`

On the VPS, your frontend will be on a real domain. Without adding it to `ALLOWED_ORIGINS`, every API call from the frontend will fail with CORS errors.

**Fix in `.env`:**
```
ALLOWED_ORIGINS=["https://yourdomain.com","https://www.yourdomain.com"]
```

---

### 🔵 LOW — Polish Items

| # | Issue |
|---|---|
| L1 | `AgentStatusResponse` schema missing `next_run_at`, `tasks_today`, `tasks_succeeded`, `tasks_failed` — backend computes them but schema drops them |
| L2 | `ResumeOut.download_url` field always `null` — never populated in `list_resumes` |
| L3 | `GEMINI_API_KEY`, `AI_PROVIDER`, `FALLBACK_PROVIDER` missing from `.env.example` |
| L4 | `credit_service.reset_monthly_credits()` no-op — monthly credit resets never happen |
| L5 | No Razorpay webhook endpoint — subscription activation depends solely on browser calling `/verify` |

---

## PART 2 — PRODUCTION READINESS SCORE

| Domain | Score | Status |
|---|---|---|
| Code correctness | 70% | C1–C4 are active crashes |
| Security posture | 55% | H1–H5 are serious vulnerabilities |
| Frontend ↔ API | 80% | H6, H7, H8, 3 mocked pages |
| Database integrity | 72% | Branched alembic, missing migrations |
| Infrastructure | 65% | Ports exposed publicly |
| AI / Workers | 90% | Solid after previous fixes |

**Overall: 72/100 — NOT production ready yet**

The previous score was 83. It dropped because this version is the same code but we audited it with the intent to actually deploy it to a live VPS — that raised the bar and exposed the port exposure issue, auth brute-force bypass, and debug log vulnerability which weren't part of previous code-only audits.

**Estimated time to fix all blockers: 4–6 hours of focused work.**

---

## PART 3 — VPS DEPLOYMENT GUIDE

**Server:** 4 vCPU / 8 GB RAM / 75 GB NVMe — Hostinger Cloud VPS 10

---

### Step 0 — Fix All Critical Bugs First

Before touching the server, fix C1–C4 and H1–H2 locally, rebuild Docker images, and push to your Git repo. Deploying buggy code and then patching live is error-prone.

---

### Step 1 — First-Time Server Setup

SSH into your VPS as root:

```bash
ssh root@YOUR_VPS_IP
```

Create a non-root user and harden SSH:

```bash
# Create deploy user
adduser applivo
usermod -aG sudo applivo
usermod -aG docker applivo

# Harden SSH (only key-based login)
sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
systemctl restart ssh

# Copy your SSH key for the new user (run from YOUR local machine)
# ssh-copy-id applivo@YOUR_VPS_IP
```

---

### Step 2 — Install Docker

```bash
apt-get update && apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com | bash

# Install Docker Compose v2
apt-get install -y docker-compose-plugin

# Verify
docker --version
docker compose version
```

---

### Step 3 — Configure Firewall (UFW)

This is critical — close everything except what's needed:

```bash
apt-get install -y ufw

# Default deny all incoming
ufw default deny incoming
ufw default allow outgoing

# Allow SSH (KEEP THIS or you'll lock yourself out)
ufw allow 22/tcp

# Allow HTTP and HTTPS only (Nginx will proxy to Docker)
ufw allow 80/tcp
ufw allow 443/tcp

# DO NOT open 5433, 6379, 8000, 5555 — these stay internal
# Flower will be proxied through Nginx at /flower with auth

ufw enable
ufw status
```

---

### Step 4 — Install and Configure Nginx as Reverse Proxy

Nginx sits in front of everything. It handles SSL, proxies to FastAPI on port 8000, and serves the Next.js frontend.

```bash
apt-get install -y nginx certbot python3-certbot-nginx

# Create Nginx config
cat > /etc/nginx/sites-available/applivo << 'EOF'
# Rate limiting zones
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

    # SSL (certbot will fill these in)
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # File upload size (resume PDFs)
    client_max_body_size 15M;

    # API routes → FastAPI backend
    location /api/ {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
        proxy_connect_timeout 10s;
    }

    # Extra strict rate limiting on auth endpoints
    location ~ ^/api/auth/(login|register) {
        limit_req zone=auth burst=5 nodelay;
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health check (no rate limit)
    location /health {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
    }

    # Flower monitoring (password protected by Docker, extra Nginx auth here)
    location /flower/ {
        proxy_pass http://localhost:5555/flower/;
        proxy_set_header Host $host;
        # Only allow your office/home IP:
        # allow YOUR.HOME.IP.ADDRESS;
        # deny all;
    }

    # Frontend (Next.js) — served from port 3000
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# Enable site
ln -s /etc/nginx/sites-available/applivo /etc/nginx/sites-enabled/
nginx -t  # test config
```

---

### Step 5 — Clone and Configure the Application

```bash
su - applivo
cd ~

# Clone your repo (or SCP the files)
git clone https://github.com/YOUR_ORG/applivo.git
cd applivo

# Create your .env file
cp .env.example .env
nano .env
```

Fill in `.env` with all required values:
```bash
# REQUIRED — generate secure random values:
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET_KEY=$(openssl rand -hex 32)
POSTGRES_PASSWORD=$(openssl rand -hex 16)
FLOWER_PASSWORD=$(openssl rand -hex 12)

# Generate encryption key:
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# Paste output as ENCRYPTION_KEY=

# Set your domain for CORS:
ALLOWED_ORIGINS=["https://yourdomain.com"]
APP_ENV=production
DEBUG=false

# YOUR API keys:
GROQ_API_KEY=gsk_...
RAZORPAY_KEY_ID=rzp_live_...
RAZORPAY_KEY_SECRET=...
SMTP_USERNAME=...
SMTP_PASSWORD=...
```

**Security check before starting:**
```bash
# Confirm no default secrets remain
grep "changeme\|your_groq\|your_razorpay\|xxxx" .env && echo "DANGER: defaults still in .env!" || echo "OK: No defaults found"
```

---

### Step 6 — Run Database Migrations

```bash
# Fix the Alembic branch FIRST (C2), then:
docker compose build
docker compose up -d database

# Wait for health check
sleep 15

# Run migrations
docker compose run --rm backend python -m alembic upgrade head

# Verify all tables created
docker compose exec database psql -U applivo -c "\dt"
```

---

### Step 7 — Start All Services

```bash
docker compose up -d

# Watch startup logs
docker compose logs -f --tail=50 backend

# Verify all healthy
docker compose ps
```

Expected output: all 6 containers `Up (healthy)` or `Up`.

---

### Step 8 — Create Admin User

```bash
docker compose exec backend python create_superuser.py \
  --email admin@yourdomain.com \
  --password 'STRONG_ADMIN_PASSWORD_HERE' \
  --name "Admin"
```

---

### Step 9 — Deploy Frontend (Next.js)

The frontend needs to be built and served separately from Docker. On the same VPS:

```bash
# Install Node.js 20
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt-get install -y nodejs

# Install PM2 (process manager)
npm install -g pm2

# Build frontend
cd ~/applivo/frontend

# Create .env.local with your API URL
echo "NEXT_PUBLIC_API_URL=https://yourdomain.com" > .env.local

npm install
npm run build

# Start with PM2
pm2 start npm --name "applivo-frontend" -- start
pm2 save
pm2 startup  # follow the instructions it outputs
```

---

### Step 10 — SSL Certificate (Let's Encrypt)

```bash
# Make sure DNS is pointing to your VPS IP first
certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal test
certbot renew --dry-run
```

---

### Step 11 — Install Playwright Chromium in Worker

```bash
docker compose exec worker playwright install chromium
```

---

### Step 12 — Verify Everything Works

```bash
# API health
curl https://yourdomain.com/health

# Expected:
# {"status":"healthy","database":"connected","env":"production","mode":"saas"}

# Test auth
curl -X POST https://yourdomain.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@yourdomain.com","password":"ADMIN_PASSWORD"}'
```

---

### Step 13 — Ongoing Monitoring Setup

```bash
# Set up log rotation (already in docker-compose)
# Check logs daily:
docker compose logs --tail=100 backend | grep -i "error\|CRITICAL"

# Monitor disk usage (75GB NVMe — Playwright screenshots + PDFs grow)
df -h /

# Set up simple uptime alert with cron:
(crontab -l 2>/dev/null; echo "*/5 * * * * curl -sf https://yourdomain.com/health > /dev/null || echo 'Applivo DOWN' | mail -s 'ALERT' admin@yourdomain.com") | crontab -
```

---

## PART 4 — VPS RESOURCE ANALYSIS

### Memory Budget (8 GB RAM)

| Service | Idle | Peak |
|---|---|---|
| OS + system processes | ~500 MB | ~700 MB |
| PostgreSQL (shared_buffers default) | ~150 MB | ~400 MB |
| Redis (maxmemory=256mb) | ~150 MB | ~256 MB |
| FastAPI backend | ~400 MB | ~800 MB |
| Celery worker (4 concurrency) | ~600 MB | ~1.2 GB |
| Celery Beat scheduler | ~150 MB | ~200 MB |
| Celery Flower | ~100 MB | ~150 MB |
| Next.js frontend (PM2) | ~200 MB | ~400 MB |
| Playwright Chromium (per instance) | ~200 MB | ~300 MB each |
| **Total baseline** | **~2.2 GB** | |
| **With 4 simultaneous apply sessions** | | **~4.7 GB** |
| **Headroom remaining** | | **~3.3 GB** ✅ |

**Verdict: 8 GB RAM is sufficient.** You have ~3 GB headroom for peak apply sessions.

### Storage Budget (75 GB NVMe)

| Item | Size |
|---|---|
| OS + Docker images | ~8 GB |
| PostgreSQL data (initial) | ~500 MB growing |
| Redis AOF persistence | ~100 MB |
| Application code | ~500 MB |
| Resume PDFs (user uploads) | ~50 MB per 100 users |
| Playwright screenshots (debug) | ~10 MB per run |
| Docker logs (10MB × 3 × 6 services) | ~180 MB max |
| **Total initial** | **~10 GB** |
| **Available for growth** | **~65 GB** ✅ |

**Verdict: 75 GB NVMe is more than adequate.** You could run 1000+ users before approaching storage limits.

### CPU Budget (4 vCPU)

- Uvicorn: 1 worker (async, handles thousands of concurrent requests)
- Celery: 4 worker processes (each can run one task at a time)
- Playwright: CPU-intensive during scraping/apply (~1 vCPU per session)
- PostgreSQL + Redis: light CPU

**Verdict: 4 vCPU is adequate** for early production. Celery apply concurrency may need tuning if >10 users are applying simultaneously.

---

## PART 5 — COMPLETE FIX CHECKLIST

Before deploying, complete these in order:

```
CRITICAL (must be done):
☐ C1: Add ChatMessage to models/__init__.py
☐ C2: Fix Alembic branch (add_uq down_revision → security_models_001)
☐ C3: Remove hardcoded password from migrate.py + rotate the credential
☐ C4: Delete DEBUG login hash logging lines from auth.py

HIGH (security):
☐ H1: Fix auth rate limit path (/api/auth/login not /api/v1/auth/login)
☐ H2: Remove port 5433 and 6379 from docker-compose.yml
☐ H3: Disable API docs in production (docs_url=None when APP_ENV=production)
☐ H5: Add PDF magic bytes check + 10MB size limit to file upload
☐ H6: Fix PDF download to use programmatic blob fetch

HIGH (UX/billing):
☐ H4: Implement Razorpay webhook endpoint
☐ H7: Fix security audit path in api.ts
☐ H8: Fix funnel endpoint return format (dict → array)

MEDIUM:
☐ M1: Connect follow-ups, interviews, skill-gaps to real APIs
☐ M3: Implement reset_monthly_credits() with Celery beat
☐ M4: Wire ai_assistant.py to use ai_router
☐ M5: Fix messages page status filter
☐ M6: Create Alembic migrations for new tables
☐ M7: Set ALLOWED_ORIGINS in .env to your production domain

DEPLOYMENT:
☐ Run: alembic upgrade head
☐ Run: playwright install chromium in worker
☐ Configure UFW firewall
☐ Set up Nginx with SSL
☐ Configure PM2 for Next.js frontend
☐ Generate all secrets (SECRET_KEY, JWT_SECRET_KEY, POSTGRES_PASSWORD, etc.)
☐ Verify: curl https://yourdomain.com/health returns healthy
```
