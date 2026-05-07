<p align="center">
  <img src="assets/applivologo.png" alt="Applivo Logo" width="100"/>
</p>

<h1 align="center">applivo</h1>

<p align="center">
  <strong>The AI-powered job application platform.</strong>
</p>


<p align="center">
  <img src="https://img.shields.io/badge/license-MIT-brightgreen"/>
  &nbsp;
  <img src="https://img.shields.io/badge/version-2.0.0-6366f1"/>
  &nbsp;
  <img src="https://img.shields.io/badge/deployed-applivo.in-black?logo=vercel&logoColor=white"/>
  &nbsp;
  <img src="https://img.shields.io/badge/python-3.11+-3776AB?logo=python&logoColor=white"/>
  &nbsp;
  <img src="https://img.shields.io/badge/FastAPI-0.111-009688?logo=fastapi&logoColor=white"/>
  &nbsp;
  <a href="https://x.com/YOUR_HANDLE">
    <img src="https://img.shields.io/badge/Follow%20%40Applivo-000000?logo=x&logoColor=white"/>
  </a>
</p>

<br/>

Applivo is a production-deployed SaaS platform that automates the full internship and job application pipeline.
It scrapes listings, scores each opportunity with AI, fills screening questions, and submits applications —
entirely server-side, at scale, while adapting as job platforms and models evolve.

> [!NOTE]
> Live at [applivo.in](https://applivo.in). API docs available locally at `/api/docs` (disabled in production).
---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Architecture](#2-architecture)
3. [Project Structure](#3-project-structure)
4. [Technology Stack](#4-technology-stack)
5. [Subscription Plans & Business Model](#5-subscription-plans--business-model)
6. [Database Schema](#6-database-schema)
7. [Backend Services](#7-backend-services)
8. [API Reference](#8-api-reference)
9. [Background Workers & Task Queue](#9-background-workers--task-queue)
10. [Scraper Engine](#10-scraper-engine)
11. [Apply Bot](#11-apply-bot)
12. [AI Integration](#12-ai-integration)
13. [Cookie & Session Management](#13-cookie--session-management)
14. [Notification System](#14-notification-system)
15. [Payment Integration (Razorpay)](#15-payment-integration-razorpay)
16. [Frontend Architecture](#16-frontend-architecture)
17. [Infrastructure & Docker](#17-infrastructure--docker)
18. [Environment Variables](#18-environment-variables)
19. [Installation & Deployment](#19-installation--deployment)
20. [Alembic Migrations](#20-alembic-migrations)
21. [Security Architecture](#21-security-architecture)
22. [Rate Limiting & Quota System](#22-rate-limiting--quota-system)
23. [Priority Queue System](#23-priority-queue-system)
24. [Monitoring & Logging](#24-monitoring--logging)
25. [Development Guide](#25-development-guide)
26. [Troubleshooting](#26-troubleshooting)

---

## 1. System Overview

Applivo is a **production-deployed, multi-user SaaS platform** at [applivo.in](https://applivo.in) that automates the complete job application workflow. Users subscribe, connect their Internshala account, upload their resume, and the platform continuously scrapes new listings, generates AI-powered answers to screening questions, and submits applications — entirely server-side.

### What Applivo Does

```
User registers → Email OTP verified → Subscribes → Connects Internshala → Uploads resume
        ↓
Scraper runs every 6 hours → Finds matching internships
        ↓
AI Router (Groq primary → Gemini fallback) analyzes each opportunity → Match score assigned
        ↓
Token budget checked (plan-based monthly limit)
        ↓
Apply bot fills forms → AI generates screening answers → Submits application
        ↓
Invoice generated → User notified via Email + Telegram
        ↓
Daily digest → Analytics dashboard updated
```

### Production Deployment

| Component | Details |
|-----------|---------|
| **Domain** | [https://applivo.in](https://applivo.in) |
| **VPS** | Contabo Cloud VPS 10 SSD  |
| **OS** | Ubuntu Linux |
| **SSL** | Let's Encrypt via Certbot + Nginx |
| **Reverse Proxy** | Nginx → backend :8000, frontend :3000 |
| **Firewall** | UFW: ports 22, 80, 443 only |

### Design Principles

- **Website-only** — all automation runs server-side with split worker architecture
- **Multi-tenant** — every user's data, cookies, and automation fully isolated
- **Subscription-gated** — automation only runs for users with active paid plans
- **Split workers** — `Dockerfile.slim` for API/scheduler (no Chromium), `Dockerfile` for browser workers (saves ~600MB RAM)
- **OTP-verified registration** — all accounts verified via email OTP before activation
- **Dual-provider AI** — Groq primary with automatic Gemini fallback on rate limits
- **Budget-aware AI** — per-plan monthly token limits enforced before every AI call

---

## 2. Architecture

### High-Level System Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER (Browser)                           │
│              Next.js 16 Frontend (React 19, App Router)         │
│         Dashboard · Jobs · Applications · Analytics             │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTPS (applivo.in)
                         │ Nginx reverse proxy
┌────────────────────────▼────────────────────────────────────────┐
│                    FastAPI Backend                              │
│   Auth+OTP · Billing · Profile · Jobs · Applications · Admin    │
│                                                                 │
│   Middleware: Rate Limiter · CORS · JWT Auth · Error Handler    │
│   Startup: entrypoint.sh → alembic upgrade heads → uvicorn      │
└────┬───────────────────┬───────────────────────┬────────────────┘
     │                   │                       │
     ▼                   ▼                       ▼
┌─────────┐       ┌───────────┐         ┌───────────────┐
│PostgreSQL│      │   Redis   │         │  File Storage │
│ (Primary │      │  Broker + │         │  /app/storage │
│  Database│      │  Cache +  │         │  resumes/     │
│  16-alp) │      │  Rate Lim)│         │  invoices/    │
└─────────┘       └─────┬─────┘         └───────────────┘
                        │ Task Queue
          ┌─────────────▼─────────────────────────┐
          │           Celery Workers              │
          │  ┌──────────────────┐                 │
          │  │ worker-standard  │  Dockerfile.slim│
          │  │ --concurrency=2  │  (no Chromium)  │
          │  │ Queues: default, │                 │
          │  │ analysis,notifs, │                 │
          │  │ email_monitor,   │                 │
          │  │ priority         │                 │
          │  └──────────────────┘                 │
          │  ┌──────────────────┐                 │
          │  │ worker-browsing  │  Dockerfile     │
          │  │ --concurrency=1  │  (Playwright +  │
          │  │ Queues: scraping,│   Xvfb + VNC)   │
          │  │ apply            │  Port 5900 (VNC │
          │  └──────────────────┘                 │
          └───────────────────────────────────────┘
                   │
          ┌────────▼────────┐
          │  Celery Beat     │
          │  Scrape: 6h      │
          │  Apply: 1h       │
          │  Emails: 30min   │
          │  Digest: 9AM     │
          │  Expiry: 00:00   │
          └─────────────────┘
```

### Container Architecture

```
docker-compose.yml
├── database          (postgres:16-alpine)    — Primary data store
├── redis             (redis:7-alpine)        — Broker + cache + rate limiter
├── backend           (Dockerfile.slim)       — FastAPI API + entrypoint migrations
├── worker-standard   (Dockerfile.slim)       — Non-browser Celery tasks
├── worker-browsing   (Dockerfile)            — Playwright scraping + apply bot + VNC
├── scheduler         (Dockerfile.slim)       — Celery Beat periodic scheduler
├── flower            (Dockerfile.slim)       — Task monitoring UI (port 5555)
└── frontend          (frontend/Dockerfile)   — Next.js 16 SSR (Node 20, standalone)
```

---

## 3. Project Structure

```
applivo/
│
├── app/                              # Backend application
│   ├── main.py                       # FastAPI app factory, middleware, lifespan
│   ├── celery_app.py                 # Celery config + beat schedule
│   ├── celery_tasks.py               # All background task definitions
│   │
│   ├── core/                         # Cross-cutting concerns
│   │   ├── config.py                 # Pydantic Settings — all env vars
│   │   ├── database.py               # SQLAlchemy async engine + session factory
│   │   ├── security.py               # bcrypt hashing via passlib CryptContext
│   │   ├── startup_checks.py         # Password hashing verification at boot
│   │   └── logging.py                # Structlog JSON configuration
│   │
│   ├── models/                       # SQLAlchemy ORM models
│   │   ├── base.py                   # UUIDMixin, TimestampMixin, SoftDeleteMixin
│   │   ├── user.py                   # User (is_verified, verified_at), UserProfile, UserSession
│   │   ├── subscription.py           # Subscription, Payment, PlanTier enum, token limits
│   │   ├── cookie.py                 # PlatformCookie (AES-256-GCM encrypted sessions)
│   │   ├── job.py                    # Job, JobAnalysis (ai_provider field)
│   │   ├── application.py            # Application, ApplicationEvent, ApplicationStatus
│   │   ├── resume.py                 # Resume
│   │   ├── interview.py              # Interview, Notification, AgentTask
│   │   ├── chat_message.py           # Chat history
│   │   ├── chat_usage.py             # AI token usage tracking
│   │   ├── platform_message.py       # Platform inbox messages
│   │   ├── audit.py                  # AuditLog (auth, billing, admin events)
│   │   ├── consent.py                # UserConsent
│   │   └── credential.py             # CredentialVault
│   │
│   ├── api/
│   │   └── routes/
│   │       ├── auth.py               # Register+OTP, Login, Logout, Me, Refresh
│   │       ├── profile.py            # Profile CRUD, resume upload + MIME validation
│   │       ├── subscriptions.py      # Subscription management
│   │       ├── payments.py           # Razorpay order + verify + webhook + invoice
│   │       ├── platform.py           # Platform cookie connect/validate/disconnect
│   │       ├── jobs.py               # Job listing, apply, analytics
│   │       ├── quotas.py             # Daily quota + token budget status
│   │       ├── admin.py              # Admin: user list, stats, revenue, block users
│   │       ├── scheduler.py          # Manual task triggering
│   │       ├── security.py           # Session management, audit log view
│   │       ├── onboarding.py         # Post-signup onboarding flow
│   │       ├── settings_route.py     # User preferences
│   │       └── routes.py             # Applications, resumes, cover letters, analytics, chat
│   │
│   ├── services/                     # Business logic layer
│   │   ├── ai_router.py              # Dual-provider router: Groq → Gemini fallback
│   │   ├── ai_assistant.py           # Groq-backed Q&A for apply bot
│   │   ├── analyze_budget_service.py # Plan-based monthly token budget enforcement
│   │   ├── cache_service.py          # Redis-backed API response caching
│   │   ├── otp_service.py            # Redis-stored OTP generation + validation
│   │   ├── invoice_service.py        # ReportLab PDF invoice generation
│   │   ├── resume_parser.py          # pdfplumber + LLM structured data extraction
│   │   ├── subscription_service.py   # Plan lifecycle, expiry, access control
│   │   ├── payment_service.py        # Razorpay order + HMAC verification
│   │   ├── quota_service.py          # Daily application limit enforcement
│   │   ├── priority_queue.py         # Redis sorted-set premium task prioritization
│   │   ├── rate_limiter.py           # Sliding-window Redis rate limiter
│   │   ├── cookie_service.py         # AES-256-GCM cookie encrypt/decrypt/validate
│   │   ├── encryption.py             # Fernet/AES encryption utilities
│   │   ├── notification_service.py   # Email + Telegram dispatch with retry
│   │   ├── application_service.py    # Application queuing + batch processing
│   │   ├── job_analyzer.py           # Job match scoring via AI Router
│   │   ├── resume_service.py         # LaTeX resume generation + PDF rendering
│   │   ├── cover_letter_service.py   # AI cover letter generation
│   │   ├── interview_service.py      # Interview scheduling + prep
│   │   ├── follow_up_service.py      # Automated follow-up emails
│   │   ├── email_monitor_service.py  # IMAP inbox monitoring for recruiter replies
│   │   ├── market_service.py         # Market intelligence + salary benchmarks
│   │   ├── onboarding_service.py     # New user setup wizard
│   │   ├── credit_service.py         # AI credit tracking
│   │   ├── internshala_login_service.py # Session-based login fallback
│   │   └── screening_question_service.py # Application form Q&A
│   │
│   ├── agents/                       # Automation engine
│   │   ├── tasks.py                  # Async task orchestration
│   │   ├── worker.py                 # Celery worker entry point (Celery 5.x)
│   │   ├── apply_bot.py              # Playwright apply bot dispatcher
│   │   ├── apply_bot_internshala.py  # Internshala-specific form filling
│   │   └── scrapers/
│   │       ├── base.py               # Abstract scraper + DB persistence
│   │       └── internshala.py        # Three-layer scraper (AJAX → NEXT_DATA → HTML)
│   │
│   ├── templates/                    # LaTeX resume templates (6 styles)
│   │   └── invoice.html              # HTML invoice template
│   │
│   └── utils/
│       └── helpers.py
│
├── alembic/                          # Database migrations (10 revisions)
│   └── versions/
│       ├── 6df4ff846734_initial.py               # Full schema baseline
│       ├── security_models_001.py                 # Audit + credential tables
│       ├── add_uq_application_user_job.py         # Dedup constraint
│       ├── cbbc170b5f44_add_chat_usage_platform_messages.py
│       ├── add_production_tables.py               # Sessions, subscriptions, payments, cookies
│       ├── 9a2f4a2c5d91_add_missing_user_auth_columns.py
│       ├── 1f4e5c7a9b12_add_ai_provider_to_job_analyses.py
│       ├── 2e6f31d4aa10_reconcile_missing_user_scope_columns.py
│       ├── c7dc8fa94484_merge_multiple_heads.py   # Branch merge
│       └── f5f6bf535b88_add_otp_verification_fields.py # is_verified, verified_at
│
├── scripts/
│   ├── backup_db.sh                  # Daily PostgreSQL backup → /opt/backups (7-day retention)
│   ├── setup_backups.sh              # Crontab bootstrap for automated backups
│   └── start_browser_worker.sh       # Xvfb + Fluxbox + VNC + Celery browser worker
│
├── scratch/                          # Dev-only utility scripts (not deployed)
│
├── frontend/                         # Next.js 16 + React 19
│   ├── Dockerfile                    # Multi-stage Node 20 → standalone output
│   └── app/ components/ lib/         # (see Section 16)
│
├── Dockerfile                        # Full image: Python 3.11 + Playwright + Xvfb + VNC
├── Dockerfile.slim                   # Slim image: Python 3.11 + libmagic (no browser)
├── docker-compose.yml                # 8-container production stack
├── entrypoint.sh                     # alembic upgrade heads → exec CMD
├── requirements.txt                  # Python dependencies (incl. sentry-sdk, python-magic)
├── alembic.ini
└── .env.example
```

---

## 4. Technology Stack

### Backend

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Web Framework | FastAPI | 0.111.0 | Async REST API |
| ASGI Server | Uvicorn | 0.30.1 | Production ASGI server |
| ORM | SQLAlchemy | 2.0.30 | Async ORM |
| DB Driver | asyncpg | 0.29.0 | Async PostgreSQL driver |
| Migrations | Alembic | 1.13.1 | 10-revision migration chain |
| Settings | pydantic-settings | 2.3.0 | Type-safe env loading |
| Auth | python-jose | 3.3.0 | JWT tokens |
| Passwords | passlib[bcrypt] | 1.7.4 | bcrypt via CryptContext |
| Encryption | cryptography | 42.0.8 | AES-256-GCM |
| MIME Validation | python-magic | 0.4.27 | File upload security |
| Task Queue | Celery | 5.4.0 | Distributed task processing |
| Broker | Redis | 7 | Broker + cache + rate limiter |
| AI Primary | Groq (openai SDK) | 1.30.1 | llama3-70b / llama3-8b |
| AI Fallback | google-generativeai | 0.8.3 | Gemini auto-fallback |
| Browser | Playwright | 1.44.0 | Headless Chromium automation |
| VNC Server | x11vnc + Xvfb | — | Browser worker visualization |
| HTTP Client | httpx | 0.27.0 | Async HTTP |
| HTML Parser | BeautifulSoup4 | 4.12.3 | Scraping |
| PDF Parser | pdfplumber + PyPDF2 | 0.10.3 | Resume text extraction |
| PDF Generation | weasyprint + reportlab | 62.1 | Resumes + invoices |
| Email | aiosmtplib | 3.0.1 | Async SMTP |
| Logging | structlog | 24.1.0 | Structured JSON logs |
| Error Tracking | sentry-sdk[fastapi] | 2.3.1 | Production error monitoring |
| Retry | tenacity | 8.3.0 | Exponential backoff |
| Monitoring | Flower | 2.0.1 | Celery UI |
| Payment | Razorpay (REST) | — | INR subscription billing |

### Frontend

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Framework | Next.js | 16.2.2 | App Router + standalone output |
| Language | TypeScript | 5+ | Strict mode |
| UI | Radix UI | Various | Accessible headless components |
| Styling | Tailwind CSS | 3.4.19 | Utility-first CSS |
| Data Fetching | TanStack Query | 5.96.1 | Server state + caching |
| HTTP | Axios | 1.14.0 | JWT interceptors |
| Forms | react-hook-form + zod | 7.72.1 | Validation |
| Charts | Recharts | 3.8.1 | Analytics |
| Animations | Framer Motion | 12.38.0 | Page transitions |
| Notifications | Sonner | 2.0.7 | Toast messages |
| Icons | Lucide React | 1.7.0 | Icon set |
| Theming | next-themes | 0.4.6 | Dark/light mode |

### Infrastructure

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Database | PostgreSQL 16 | Primary relational store |
| Cache/Broker | Redis 7 (512MB) | Celery + rate limiter + OTP + cache |
| Containers | Docker + Compose | 8-service orchestration |
| Build | Multi-stage Dockerfiles | Slim (API) + Full (browser) images |
| Reverse Proxy | Nginx | HTTPS termination + routing |
| SSL | Certbot (Let's Encrypt) | Auto-renewing certificates |
| Backups | scripts/backup_db.sh | Daily pg_dump → /opt/backups, 7-day retention |

---

## 5. Subscription Plans & Business Model

Applivo uses a **tiered SaaS billing model** with Razorpay (INR). Payments generate PDF invoices via `InvoiceService`.

### Plan Comparison

| Feature | Starter | Pro | Premium |
|---------|---------|-----|---------|
| **Price** | ₹200/month | ₹400/month | ₹800/month |
| **Daily Application Limit** | 150 | 250 | 500 |
| **Queue Priority** | Low (1) | Medium (2) | High (3) |
| **Monthly AI Token Budget** | Standard | Extended | Unlimited |
| Job Scraping | ✅ | ✅ | ✅ |
| Auto Apply | ✅ | ✅ | ✅ |
| Basic AI Answers | ✅ | ✅ | ✅ |
| Resume Upload + Parse | ✅ | ✅ | ✅ |
| Email Notifications | ✅ | ✅ | ✅ |
| Analytics Dashboard | ✅ | ✅ | ✅ |
| PDF Invoice on Payment | ✅ | ✅ | ✅ |
| Telegram Notifications | ❌ | ✅ | ✅ |
| AI Cover Letters | ❌ | ✅ | ✅ |
| Interview Tracking | ❌ | ✅ | ✅ |
| Email Inbox Monitoring | ❌ | ✅ | ✅ |
| Follow-up Automation | ❌ | ✅ | ✅ |
| AI Skill Gap Analysis | ❌ | ✅ | ✅ |
| Advanced AI Answers | ❌ | ❌ | ✅ |
| Market Intelligence | ❌ | ❌ | ✅ |
| Advanced Analytics | ❌ | ❌ | ✅ |

### Access Control Layers

1. **`get_active_subscriber()`** FastAPI dependency — raises HTTP 402 if no active subscription
2. **`QuotaService`** — blocks applications at daily limit
3. **`AnalyzeBudgetService`** — blocks AI calls at monthly token limit per plan
4. **`PriorityQueueService`** — Premium before Pro before Starter in Celery queues
5. **Frontend AuthGuard** — shows upgrade prompts for plan-gated routes

---

## 6. Database Schema

### Entity Relationship Overview

```
users ────────────────────────────────────────────────────────────┐
  │  (is_verified, verified_at — OTP-verified on registration)   │
  ├── profiles (1:1)           ← skills, roles, bio              │
  ├── user_sessions (1:N)      ← device-tracked JWT sessions     │
  ├── subscriptions (1:1)      ← plan, status, token budget      │
  │     └── payments (1:N)     ← Razorpay records + invoices     │
  ├── platform_cookies (1:N)   ← AES-256-GCM encrypted sessions  │
  ├── resumes (1:N)            ← uploaded + parsed PDFs          │
  ├── applications (1:N)       ← per job applications            │
  │     └── application_events ← status history log              │
  ├── chat_messages (1:N)      ← AI chat history                 │
  ├── chat_usage (1:N)         ← token usage per AI call         │
  ├── platform_messages (1:N)  ← scraped inbox messages          │
  ├── notifications (1:N)      ← email/telegram dispatch log     │
  ├── credential_vaults (1:N)  ← AES-encrypted third-party creds │
  ├── user_consents (1:N)      ← GDPR consent records            │
  └── audit_logs (1:N)         ← security + billing events       │
                                                                  │
jobs ─────────────────────────────────────────────────────────────┘
  ├── job_analyses             ← AI match scores + ai_provider field
  └── applications (1:N)       ← applications per job per user
```

### Core Tables

#### `users`
```sql
id              UUID PRIMARY KEY
email           VARCHAR(255) UNIQUE NOT NULL
password_hash   VARCHAR(255) NOT NULL          -- bcrypt via passlib
full_name       VARCHAR(255) NOT NULL
is_active       BOOLEAN DEFAULT true
is_superuser    BOOLEAN DEFAULT false
is_verified     BOOLEAN DEFAULT false          -- email OTP verified
verified_at     TIMESTAMPTZ                    -- when OTP was confirmed
created_at      TIMESTAMPTZ NOT NULL
updated_at      TIMESTAMPTZ NOT NULL
deleted_at      TIMESTAMPTZ                    -- soft delete
```

#### `user_sessions`
```sql
id                       UUID PRIMARY KEY
user_id                  UUID REFERENCES users(id)
device_id                VARCHAR(255) NOT NULL
device_name              VARCHAR(255)
browser / os             VARCHAR(100)
ip_address               VARCHAR(45)
refresh_token_hash       VARCHAR(255)          -- bcrypt of refresh token
refresh_token_expires_at TIMESTAMPTZ
access_token_jti         VARCHAR(255)          -- for blacklist check
last_used_at             TIMESTAMPTZ
is_current               BOOLEAN DEFAULT false
is_active                BOOLEAN DEFAULT true
UNIQUE(user_id, device_id)
```

#### `subscriptions`
```sql
id                          UUID PRIMARY KEY
user_id                     UUID REFERENCES users(id) NOT NULL
plan                        ENUM('starter','pro','premium') NOT NULL
status                      ENUM('active','expired','cancelled','pending')
start_date                  TIMESTAMPTZ NOT NULL
end_date                    TIMESTAMPTZ
razorpay_subscription_id    VARCHAR(255)
```

#### `payments`
```sql
id                    UUID PRIMARY KEY
user_id               UUID REFERENCES users(id) NOT NULL
amount                INTEGER NOT NULL          -- paise (₹400 = 40000)
currency              VARCHAR(10) DEFAULT 'INR'
status                ENUM('created','authorized','captured','refunded','failed')
razorpay_order_id     VARCHAR(255)
razorpay_payment_id   VARCHAR(255) UNIQUE
plan                  VARCHAR(50)
invoice_pdf_path      VARCHAR(500)              -- generated invoice path
```

#### `job_analyses`
```sql
id              UUID PRIMARY KEY
job_id          UUID REFERENCES jobs(id)
user_id         UUID REFERENCES users(id)
match_score     FLOAT
priority_score  FLOAT
ai_provider     VARCHAR(50)                    -- 'groq' | 'gemini' (which provider scored it)
analysis_json   JSONB
created_at      TIMESTAMPTZ
```

#### `chat_usage`
```sql
id              UUID PRIMARY KEY
user_id         UUID REFERENCES users(id)
tokens_used     INTEGER
model           VARCHAR(100)
provider        VARCHAR(50)
endpoint        VARCHAR(255)
created_at      TIMESTAMPTZ
```

---

## 7. Backend Services

### `AIRouter`
**File:** `app/services/ai_router.py`

Dual-provider router with automatic failover. Groq is primary for speed; Gemini is fallback on `429 Too Many Requests` or any Groq error.

```python
router = AIRouter()
response = await router.chat_completions_create(
    messages=[{"role": "user", "content": "..."}],
    model=settings.OPENAI_MODEL_HEAVY,   # llama3-70b-8192
    max_tokens=1000,
    temperature=0.1,
)
# Automatically falls back to Gemini if Groq fails
# Response format normalized across providers
```

### `AnalyzeBudgetService`
**File:** `app/services/analyze_budget_service.py`

Enforces monthly token budgets per plan tier before each AI job analysis run. Admins have a separate override limit (`ADMIN_ANALYZE_RUN_TOKEN_LIMIT = 150,000`).

```python
# Check before running analysis
budget = await analyze_budget_service.check_budget(user_id)
# Returns: { allowed: True, plan: "pro", monthly_used: 45230, monthly_limit: 100000 }
```

### `OTPService`
**File:** `app/services/otp_service.py`

Redis-backed OTP generation and validation for email verification at registration. OTPs stored with configurable TTL (default 10 minutes).

```python
# Generate + store OTP (send to user email)
otp = otp_service.generate_otp()         # 6-digit numeric string
await otp_service.store_otp(email, otp)  # stored in Redis with TTL

# Verify (during registration confirmation)
valid = await otp_service.verify_otp(email, submitted_otp)
# On success: user.is_verified = True, user.verified_at = now()
```

### `CacheService`
**File:** `app/services/cache_service.py`

Redis-backed response caching for expensive queries (job lists, analytics, market data). Reduces repeated DB reads during high-traffic periods.

```python
# Cache a response
await cache_service.set("jobs:user:abc123", data, ttl=60)
cached = await cache_service.get("jobs:user:abc123")
```

### `InvoiceService`
**File:** `app/services/invoice_service.py`

Generates professional PDF invoices using ReportLab after every successful Razorpay payment. Invoices stored in `storage/invoices/` and linked to the Payment record.

```python
invoice_path = await invoice_service.generate_invoice(
    payment_id=payment.id,
    user=user,
    plan=PlanTier.PRO,
    amount=400,
)
# Returns: "storage/invoices/INV-20260421-abc123.pdf"
```

### `ResumeParser`
**File:** `app/services/resume_parser.py`

Extracts structured data from uploaded PDF resumes using `pdfplumber` for text extraction and the AI Router (LLM) for structured JSON parsing. Parsed data auto-populates the user profile.

```python
parsed = await resume_parser.parse(resume_pdf_path)
# Returns structured dict:
# { name, email, phone, education[], experience[], skills[], projects[] }
```

### `SubscriptionService`
**File:** `app/services/subscription_service.py`

Full subscription lifecycle management including plan activation, auto-expiry, and access validation.

```python
sub = await subscription_service.get_active_subscription(user_id, db)
# sub.is_active() → bool
# sub.daily_limit → 150/250/500
# sub.priority → 1/2/3

await subscription_service.create_subscription(
    user_id=user_id, plan=PlanTier.PRO, duration_days=30, db=db
)
```

### `QuotaService`
**File:** `app/services/quota_service.py`

Persistent DB-count based daily quota. Crash-safe across worker restarts.

```python
quota = await QuotaService().check_quota(user_id)
# { allowed: True, plan: "pro", limit: 250, used: 47, remaining: 203 }
```

### `PaymentService`
**File:** `app/services/payment_service.py`

Razorpay REST integration with HMAC constant-time signature verification.

```python
order = await PaymentService().create_order(user_id, PlanTier.PRO)
result = await PaymentService().verify_payment(order_id, payment_id, signature, user_id)
# On success: subscription activated + invoice generated
```

### `CookieService`
**File:** `app/services/cookie_service.py`

AES-256-GCM encrypted storage and retrieval of Internshala session cookies per user.

```python
await cookie_service.save_cookies(user_id, "internshala", cookies_list)
cookies = await cookie_service.get_cookies(user_id, "internshala")
is_valid = await cookie_service.validate_session(user_id, "internshala")
```

### `RateLimiter`
**File:** `app/services/rate_limiter.py`

Redis sliding-window rate limiter applied as FastAPI middleware.

```
Auth endpoints:   5 requests / 5 minutes per IP
Global:         100 requests / 60 seconds per IP
Response:       HTTP 429 + Retry-After header
Fail behavior:  Fail-open if Redis unavailable (logged)
```

---

## 8. API Reference

All endpoints prefixed with `/api`. Docs disabled in production (`APP_ENV=production`).

### Authentication & OTP

```
POST   /api/auth/register              Register + send OTP email
POST   /api/auth/verify-otp            Verify email OTP → activate account
POST   /api/auth/login                 Login → JWT + refresh token
POST   /api/auth/refresh               Refresh access token
GET    /api/auth/me                    Current user
POST   /api/auth/logout                Blacklist JWT in Redis
POST   /api/auth/google                Google OAuth login
POST   /api/auth/forgot-password       Send reset email
POST   /api/auth/reset-password        Reset with token
```

### Subscriptions & Billing

```
GET    /api/subscriptions/plans        Plan list + pricing
GET    /api/subscriptions/me           Current subscription + token budget
POST   /api/payments/create-order      Create Razorpay order
POST   /api/payments/verify            Verify + activate + generate invoice
POST   /api/payments/webhook           Razorpay server-to-server events
GET    /api/payments/invoice/{id}      Download invoice PDF
```

### Profile & Resume

```
GET    /api/profile                    Get profile
PUT    /api/profile                    Update profile
POST   /api/resumes/upload             Upload PDF (MIME validated)
GET    /api/resumes                    List resumes
DELETE /api/resumes/{id}               Delete resume
POST   /api/resumes/{id}/parse         Parse resume → auto-fill profile
```

### Platform Connection

```
GET    /api/platform/status            Connection status for all platforms
POST   /api/platform/connect           Save encrypted cookies
POST   /api/platform/validate          Validate session liveness
DELETE /api/platform/{platform}        Disconnect platform
```

### Jobs & Applications

```
GET    /api/jobs                       List jobs (paginated, filtered)
GET    /api/jobs/{id}                  Job detail + match score
POST   /api/jobs/{id}/apply            Queue application
GET    /api/applications               User's applications
GET    /api/applications/{id}          Detail + event history
DELETE /api/applications/{id}          Cancel queued
GET    /api/analytics/dashboard        Stats + chart data
GET    /api/quotas/me                  Daily quota + monthly token budget
```

### Scheduler (Manual Trigger)

```
POST   /api/scheduler/trigger/{task}   Manually trigger background task
GET    /api/scheduler/jobs             List scheduled jobs + next run
```

Available tasks: `scrape_jobs`, `analyze_new_jobs`, `auto_apply`, `check_email_inbox`, `check_follow_ups`, `daily_digest`

### Admin (Superuser only)

```
GET    /api/admin/stats                System statistics + revenue
GET    /api/admin/users                User list with subscription info
PATCH  /api/admin/users/{id}           Modify user (block/unblock, plan override)
DELETE /api/admin/users/{id}           Delete user
GET    /api/admin/subscriptions        All subscriptions
GET    /api/admin/payments             Payment history
POST   /api/admin/payments/{id}/refund Initiate refund
```

### Health

```
GET    /health                         { status, database }
GET    /                               { app, docs, health }
```

---

## 9. Background Workers & Task Queue

### Split Worker Architecture

Workers are split into two containers using different Dockerfiles to save RAM:

| Container | Dockerfile | Queues | Concurrency | Purpose |
|-----------|-----------|--------|-------------|---------|
| `worker-standard` | `Dockerfile.slim` | default, analysis, notifications, email_monitor, priority | 2 | Non-browser tasks |
| `worker-browsing` | `Dockerfile` | scraping, apply | 1 | Playwright + Xvfb + VNC |

The browser worker runs Xvfb (virtual display) + Fluxbox + x11vnc on port 5900 for debugging apply bot sessions remotely.

### Beat Schedule

| Task | Schedule | Description |
|------|----------|-------------|
| `scrape_jobs` | Every 6h (0,6,12,18) | Scrape all platforms |
| `analyze_jobs` | After scrape | AI match scoring (budget-checked) |
| `auto_apply` | Every hour | Process queued applications |
| `check_emails` | Every 30 min | IMAP inbox monitor |
| `send_daily_digest` | Daily 9:00 AM UTC | Email + Telegram summary |
| `check_expired_subscriptions` | Daily midnight | Auto-expire + notify |
| `check_expired_cookies` | Every 4h | Validate platform sessions |
| `reset_all_monthly_credits` | 1st of month midnight | Reset monthly token budgets |

### Async Execution Pattern

```python
def _run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

@celery_app.task(bind=True, max_retries=3, default_retry_delay=300)
def scrape_jobs(self):
    try:
        _run_async(run_main_agent_cycle())
    except Exception as e:
        raise self.retry(exc=e)
```

### Task Configuration

```python
celery_app.conf.update(
    task_acks_late=True,                  # Prevent task loss on crash
    worker_prefetch_multiplier=1,         # One task at a time per worker
    task_track_started=True,              # Track STARTED state
    task_routes={ ... },                  # Per-queue routing
)
```

---

## 10. Scraper Engine

**File:** `app/agents/scrapers/internshala.py`

### Three-Layer Extraction Strategy

```
1. AJAX JSON API  (/internships/ajax-new-search-v2-and-a-half/)
   └── Requires authenticated session cookies
   └── Returns complete structured JSON

2. __NEXT_DATA__ JSON extraction
   └── Works without auth (public pages)
   └── Recursive tree search in <script id="__NEXT_DATA__">

3. BeautifulSoup HTML fallback
   └── Multi-selector resilient parsing
   └── Last resort on markup changes
```

### Session Validation

Before each cycle, validates cookies against `internshala.com/users/logged_in_check`. On failure: marks cookies invalid, disables auto-apply, notifies user.

### Retry & Deduplication

- HTTP: exponential backoff (1s → 2s → 4s) on timeout/connect errors
- DB: `INSERT OR IGNORE` pattern on `(source, source_job_id, user_id)` unique constraint
- Max per cycle: `MAX_JOBS_PER_CYCLE` (default 200)

### Scraped Categories

Configurable via `USER_DESIRED_ROLES` env var:
```
Machine Learning · Data Science · Python · Web Development
Software Development · Artificial Intelligence · Computer Vision
```

---

## 11. Apply Bot

**Files:** `app/agents/apply_bot.py`, `app/agents/apply_bot_internshala.py`

### Apply Flow

```
1. Load Application from DB
2. Load UserProfile, Resume, decrypted PlatformCookie
3. Launch Playwright Chromium (runs inside worker-browsing with Xvfb)
4. Inject decrypted cookies → verify login
5. Navigate to job page → check already-applied
6. Find Apply button → handle modal or redirect
7. Fill all form fields:
   - Textareas → Groq AI generates answer (profile + job context)
   - Dropdowns  → Groq AI selects best option
   - Phone      → from user profile
   - File upload → user's default resume PDF
8. Submit → verify success
9. Update Application: APPLIED or FAILED
10. Generate notification + update analytics
```

### AI-Powered Form Filling

Each screening question goes through `AIAssistant.answer_question()`:
- Free text: `llama3-70b-8192` → 2–4 sentence professional answer
- Dropdown/radio: `llama3-8b-8192` → exact option text match
- Profile context (skills, projects, experience level) injected into every prompt

### Anti-Detection

- `navigator.webdriver` property undefined via `add_init_script`
- Human-like typing delays: `random.uniform(40, 130)ms` per character
- Random action pauses: `random.uniform(1.5, 3.0)s`
- User agent rotation from pool of real browser strings

### CAPTCHA Handling

On detection: application reverts to `QUEUED`, user notified via Telegram/Email to resolve manually. Waits up to 2 minutes for manual resolution before timing out.

### VNC Debugging

The browser worker exposes port 5900 (VNC). Connect via SSH tunnel for live session inspection:
```bash
ssh -L 5900:127.0.0.1:5900 root@45.67.216.57
# Then open VNC viewer → localhost:5900
```

---

## 12. AI Integration

### Dual-Provider Router

```
Primary:  Groq API (llama3-70b-8192 / llama3-8b-8192)
          ↓ on 429 or error
Fallback: Google Gemini API (gemini-pro)
```

Both providers normalized through `AIRouter.chat_completions_create()`. `ai_provider` field on `job_analyses` records which provider scored each job.

### Model Selection

| Task | Model | Provider |
|------|-------|----------|
| Screening answers (complex) | llama3-70b-8192 | Groq → Gemini |
| Option selection | llama3-8b-8192 | Groq → Gemini |
| Job match scoring | llama3-70b-8192 | Groq → Gemini |
| Resume tailoring | llama3-70b-8192 | Groq → Gemini |
| Cover letter generation | llama3-70b-8192 | Groq → Gemini |
| Skill gap analysis | llama3-8b-8192 | Groq → Gemini |
| Resume parsing | llama3-8b-8192 | Groq → Gemini |

### Token Budget Enforcement

Before each AI analysis run, `AnalyzeBudgetService` checks the user's monthly token consumption against their plan limit. On budget exhaustion: run blocked, user notified, admin notified if admin quota exceeded.

```python
limits = {
    PlanTier.STARTER: 50_000,   # tokens/month
    PlanTier.PRO:     100_000,
    PlanTier.PREMIUM: float("inf"),
}
ADMIN_RUN_LIMIT = 150_000       # per-run override for admins
```

---

## 13. Cookie & Session Management

### Connection Flow

1. User logs into Internshala in their browser
2. User opens DevTools → Application → Cookies → copies all `.internshala.com` cookies as JSON
3. User pastes into Applivo's **Connect** page (`/connect`)
4. Backend encrypts with AES-256-GCM and stores in `platform_cookies`
5. Apply bot decrypts and injects into each Playwright context

### Encryption

```python
# AES-256-GCM via cryptography library
nonce = os.urandom(12)
ciphertext = aesgcm.encrypt(nonce, plaintext_bytes, None)
stored_blob = base64.b64encode(nonce + ciphertext)
```

Key derived from `ENCRYPTION_KEY` env var using PBKDF2HMAC-SHA256 (100,000 iterations).

### Cookie Schema (Playwright-compatible)

```json
[
  {
    "name": "session",
    "value": "abc123def456",
    "domain": ".internshala.com",
    "path": "/",
    "expires": 1750000000,
    "httpOnly": true,
    "secure": true,
    "sameSite": "Lax"
  }
]
```

### Session Expiry Monitoring

`check_expired_cookies` runs every 4h, hits `internshala.com/users/logged_in_check`. On failure:
- `PlatformCookie.is_valid = False`
- `UserProfile.auto_apply_enabled = False`
- User notified: "Your Internshala session expired — please reconnect"

---

## 14. Notification System

### Channels

| Channel | Config | Trigger |
|---------|--------|---------|
| **Telegram Bot** | `telegram_chat_id` in profile | All events if Pro/Premium |
| **Email (SMTP)** | `notification_email` or account email | All events |

### Events

| Event | Channels |
|-------|---------|
| Application submitted | Both |
| Application failed | Both |
| CAPTCHA detected | Both |
| Session expired | Both |
| Subscription expired | Email |
| Budget exhausted | Both |
| Daily digest | Both |
| Invoice ready | Email |

### Retry

- Telegram: 3 attempts, exponential backoff (1s → 2s → 4s)
- Email: aiosmtplib with 30s timeout + Celery `max_retries=3`
- All dispatches logged to `notifications` table with `status` + `sent_at`

---

## 15. Payment Integration (Razorpay)

### Payment Flow

```
1. POST /api/payments/create-order  { plan: "pro" }
2. Backend creates Razorpay order → returns { order_id, amount: 40000 }
3. Frontend opens Razorpay checkout
4. User pays → receives { payment_id, signature }
5. POST /api/payments/verify  { order_id, payment_id, signature }
6. Backend HMAC verify → activate subscription → generate invoice
7. User receives invoice PDF via email
```

### HMAC Verification

```python
expected = hmac.new(
    settings.RAZORPAY_KEY_SECRET.encode(),
    f"{razorpay_order_id}|{razorpay_payment_id}".encode(),
    hashlib.sha256,
).hexdigest()

if not hmac.compare_digest(expected, razorpay_signature):
    raise HTTPException(400, "Invalid payment signature")
```

### Invoice Generation

Every successful payment triggers `InvoiceService.generate_invoice()` which produces a branded A4 PDF stored at `storage/invoices/` and linked on the payment record. Users can download via `GET /api/payments/invoice/{id}`.

---

## 16. Frontend Architecture

### Deployment

The Next.js frontend is containerized in `frontend/Dockerfile` using a 3-stage Node 20 build (deps → builder → runner) with `standalone` output. Served by `applivo-frontend` container at `127.0.0.1:3000`, proxied by Nginx.

### Authentication Flow

```typescript
// Registration → OTP → Login
const register = async (email, password, name) => {
  await api.post("/auth/register", { email, password, full_name: name });
  // User receives OTP email → enters OTP on verify screen
};

const verifyOtp = async (email, otp) => {
  const { data } = await api.post("/auth/verify-otp", { email, otp });
  // Account activated → redirect to login
};
```

JWT stored in `localStorage`, attached via Axios interceptor. 401 → auto-redirect to `/login`.

### Dashboard Routes

| Route | Plan Required | Description |
|-------|--------------|-------------|
| `/dashboard` | Any | Stats, quota bar, recent applications |
| `/jobs` | Any | Paginated job feed + apply button |
| `/applications` | Any | Tracker with status filters |
| `/applications/[id]` | Any | Detail + event timeline |
| `/analytics` | Any | Recharts: applications over time, success rate |
| `/resumes` | Any | Upload, parse, manage PDFs |
| `/connect` | Any | Platform cookie wizard |
| `/subscription` | Any | Plan, upgrade, payment history, invoice download |
| `/profile` | Any | Profile + preferences |
| `/settings` | Any | Notification settings |
| `/security` | Any | Active sessions, audit log |
| `/chat` | Any | AI chat assistant |
| `/cover-letters` | Pro+ | AI-generated cover letters |
| `/interviews` | Pro+ | Interview scheduling + prep |
| `/skill-gaps` | Pro+ | Skill gap analysis |
| `/follow-ups` | Pro+ | Follow-up automation |
| `/market` | Premium | Market intelligence |
| `/messages` | Pro+ | Platform inbox monitor |
| `/admin` | Superuser | User management + system stats |

---

## 17. Infrastructure & Docker

### Two Dockerfiles

**`Dockerfile.slim`** — API, scheduler, standard worker
- Python 3.11-slim + libmagic + libpq5
- No Playwright/Chromium (~600MB smaller)
- Used by: `backend`, `worker-standard`, `scheduler`, `flower`

**`Dockerfile`** — Browser worker only
- Python 3.11-slim + full Playwright deps + Xvfb + Fluxbox + x11vnc
- `playwright install chromium --with-deps`
- Used by: `worker-browsing`

### `entrypoint.sh`

The backend runs `alembic upgrade heads` automatically before starting uvicorn — zero-downtime schema migrations on every deploy:

```bash
#!/bin/bash
set -e
echo "Running database migrations..."
alembic upgrade heads
echo "Migrations complete. Starting application..."
exec "$@"
```

### Container Services

| Container | Image | Ports | Command |
|-----------|-------|-------|---------|
| `applivo-database` | postgres:16-alpine | 127.0.0.1:5432 | Default PostgreSQL |
| `applivo-redis` | redis:7-alpine | 127.0.0.1:6379 | AOF + 512MB limit |
| `applivo-backend` | Dockerfile.slim | 127.0.0.1:8000 | entrypoint.sh → uvicorn |
| `applivo-worker-std` | Dockerfile.slim | — | celery worker (concurrency=2) |
| `applivo-worker-browser` | Dockerfile | 127.0.0.1:5900 | Xvfb + celery worker (concurrency=1) |
| `applivo-scheduler` | Dockerfile.slim | — | celery beat |
| `applivo-flower` | Dockerfile.slim | 127.0.0.1:5555 | celery flower |
| `applivo-frontend` | frontend/Dockerfile | 127.0.0.1:3000 | node server.js |

All ports bind `127.0.0.1` only — only Nginx (80/443) is publicly accessible.

### Nginx Configuration

```nginx
server {
    listen 80;
    server_name applivo.in www.applivo.in;
    # Certbot redirect → HTTPS

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 300s;
        client_max_body_size 50M;
    }

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
    }
}
```

### Automated Backups

`scripts/backup_db.sh` runs via cron daily at 02:00:
```bash
# Daily at 02:00 via crontab
0 2 * * * /opt/applivo/scripts/backup_db.sh

# Creates: /opt/backups/applivo/applivo_YYYYMMDD_HHMMSS.sql.gz
# Retains: 7 days
```

---

## 18. Environment Variables

Copy `.env.example` to `.env`. All required variables must be set before `docker compose up`.

### Required

| Variable | Description | Generate with |
|----------|-------------|---------------|
| `SECRET_KEY` | Flask/app signing secret | `openssl rand -hex 32` |
| `JWT_SECRET_KEY` | JWT signing secret | `openssl rand -hex 32` |
| `ENCRYPTION_KEY` | AES-256-GCM cookie key | `openssl rand -hex 32` |
| `POSTGRES_PASSWORD` | PostgreSQL container password | `openssl rand -hex 16` |
| `REDIS_PASSWORD` | Redis auth password | `openssl rand -hex 16` |
| `FLOWER_PASSWORD` | Flower UI basic auth | `openssl rand -hex 8` |
| `DATABASE_URL` | Async PostgreSQL URL | `postgresql+asyncpg://applivo:<pw>@database:5432/applivo` |
| `DATABASE_URL_SYNC` | Sync URL for Alembic | `postgresql://applivo:<pw>@database:5432/applivo` |
| `GROQ_API_KEY` | Groq API key | [console.groq.com](https://console.groq.com) |

### Optional — AI Fallback

| Variable | Description |
|----------|-------------|
| `GEMINI_API_KEY` | Google Gemini API key (auto-fallback when Groq fails) |
| `AI_PROVIDER` | Primary provider: `groq` (default) |
| `FALLBACK_PROVIDER` | Fallback: `gemini` (default) |

### Optional — Payment

| Variable | Description |
|----------|-------------|
| `RAZORPAY_KEY_ID` | `rzp_live_xxx` for production |
| `RAZORPAY_KEY_SECRET` | Razorpay API secret |
| `RAZORPAY_WEBHOOK_SECRET` | Webhook signature verification |

### Optional — Notifications

| Variable | Example |
|----------|---------|
| `SMTP_HOST` | `smtp.gmail.com` |
| `SMTP_PORT` | `587` |
| `SMTP_USERNAME` | `noreply@applivo.in` |
| `SMTP_PASSWORD` | Gmail App Password |
| `SMTP_FROM_EMAIL` | `noreply@applivo.in` |
| `TELEGRAM_BOT_TOKEN` | From @BotFather |

### Optional — Frontend + Auth

| Variable | Description |
|----------|-------------|
| `NEXT_PUBLIC_API_URL` | `https://applivo.in` |
| `NEXT_PUBLIC_GOOGLE_CLIENT_ID` | Google OAuth client ID |
| `GOOGLE_CLIENT_ID` | Same, for backend verification |
| `ALLOWED_ORIGINS` | `["https://applivo.in","https://www.applivo.in"]` |

### Security Defaults Changed in Production

| Variable | Default | Production Value |
|----------|---------|-----------------|
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | 60 | 60 (reduced from 1440) |
| `DEBUG` | false | false |
| `APP_ENV` | development | production |

---

## 19. Installation & Deployment

### Prerequisites

- Docker 24.0+ and Docker Compose 2.24+
- 4 vCPU, 8 GB RAM minimum (VPS)
- Domain with DNS pointing to server IP
- Groq API key (free tier available)

### Quick Start (Production VPS)

```bash
# 1. SSH into server
ssh root@YOUR_SERVER_IP

# 2. Install Docker + Nginx + Certbot
apt update && apt upgrade -y
apt install -y git curl nginx certbot python3-certbot-nginx ufw
curl -fsSL https://get.docker.com | sh

# 3. Firewall
ufw allow 22 && ufw allow 80 && ufw allow 443 && ufw enable

# 4. Clone and configure
cd /opt && git clone https://github.com/YOUR_ORG/applivo.git && cd applivo
cp .env.example .env && nano .env   # fill all required variables

# 5. Generate secrets
openssl rand -hex 32   # SECRET_KEY
openssl rand -hex 32   # JWT_SECRET_KEY
openssl rand -hex 32   # ENCRYPTION_KEY
openssl rand -hex 16   # POSTGRES_PASSWORD / REDIS_PASSWORD

# 6. Build and start
docker compose build --no-cache
docker compose up -d

# 7. Check migrations ran (entrypoint.sh auto-runs alembic upgrade heads)
docker compose logs backend | grep "Migrations complete"

# 8. Create admin user (PostgreSQL production path)
docker compose exec database psql -U applivo -c \
  "UPDATE users SET is_superuser=true WHERE email='your@email.com';"

# Or register first then promote:
curl -X POST https://applivo.in/api/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"admin@applivo.in","password":"StrongPass!","full_name":"Admin"}'
# Then verify OTP from email, then promote in DB

# 9. Nginx config (see Section 17) + SSL
certbot --nginx -d applivo.in -d www.applivo.in

# 10. Set up automated backups
chmod +x scripts/backup_db.sh
(crontab -l; echo "0 2 * * * /opt/applivo/scripts/backup_db.sh") | crontab -

# 11. Verify
curl https://applivo.in/health
# → {"status":"healthy","database":"connected"}
```

### Updating Production

```bash
cd /opt/applivo
git pull origin main
docker compose build --no-cache backend worker-standard worker-browsing frontend
docker compose up -d
# entrypoint.sh auto-runs migrations on backend restart
```

### Scaling Workers

```bash
# Scale Celery concurrency per worker type
# Standard worker: safe to increase (no browser)
# Edit docker-compose.yml worker-standard: --concurrency=4

# Browser worker: keep at 1-2 (each Chromium = ~300MB RAM)
# Monitor with: docker stats
```

---

## 20. Alembic Migrations

Migrations run automatically via `entrypoint.sh` on every backend start (`alembic upgrade heads`). Manual commands:

```bash
# View current state
docker compose exec backend alembic current

# Apply pending
docker compose exec backend alembic upgrade heads

# Rollback one
docker compose exec backend alembic downgrade -1

# Generate new migration after model changes
docker compose exec backend alembic revision --autogenerate -m "add_feature_x"

# History
docker compose exec backend alembic history --verbose
```

### Migration Chain

| Revision | Description |
|----------|-------------|
| `6df4ff846734` | Initial schema — all core tables |
| `security_models_001` | Audit logs, credential vault, consent |
| `add_uq_application_user_job` | Deduplication constraint |
| `cbbc170b5f44` | Chat usage + platform messages |
| `add_production_tables` | Sessions, subscriptions, payments, cookies (IF NOT EXISTS guards) |
| `9a2f4a2c5d91` | Missing user auth columns |
| `1f4e5c7a9b12` | `ai_provider` field on job_analyses |
| `2e6f31d4aa10` | Reconcile user scope columns |
| `c7dc8fa94484` | Branch merge head |
| `f5f6bf535b88` | OTP verification: `is_verified`, `verified_at` |

---

## 21. Security Architecture

### Authentication

- **JWT HS256** signed with `JWT_SECRET_KEY`, 60-minute expiry
- **Refresh tokens** — 30-day lifetime, hashed with bcrypt in `user_sessions`
- **JTI blacklist** in Redis — logout immediately invalidates token
- **Email OTP** — 6-digit code, Redis TTL 10 minutes, required before account activation
- **Device tracking** — `user_sessions` records IP, browser, OS per login

### Password Security

- **bcrypt** via `passlib.CryptContext` (cost factor 12, truncated to 72 bytes)
- `app/core/security.py` is single source of truth — `get_password_hash()` + `verify_password()`
- `startup_checks.py` verifies hashing works correctly on every boot

### File Upload Security

- **MIME validation** via `python-magic` — checks actual file bytes, not just extension
- Extension check `.pdf` is secondary; MIME must be `application/pdf`
- 10MB size limit enforced in handler

### Cookie & Credential Encryption

- **AES-256-GCM** (cryptography library) — authenticated encryption
- Random 12-byte nonce per encryption operation
- Key derived via PBKDF2HMAC-SHA256 (100,000 iterations) from `ENCRYPTION_KEY`

### API Security

- Rate limiting: sliding-window Redis counter per IP
- CORS: explicit origins only in production
- SQL injection: impossible (SQLAlchemy ORM parameterized queries)
- Secrets: all from env vars, `.env` mounted `:ro`, in `.gitignore`
- Admin routes: `require_admin()` dependency on all `/api/admin/*` endpoints

### Payment Security

- **HMAC-SHA256** Razorpay signature verification via `hmac.compare_digest()` (constant-time)
- Webhook secret verified server-to-server
- Payment amounts from server-side plan config — never trusted from client

### Error Tracking

- **Sentry SDK** (`sentry-sdk[fastapi]==2.3.1`) integrated for production error monitoring
- Configurable via `SENTRY_DSN` env var
- 10% trace sample rate to minimize overhead

### Audit Logging

All security-relevant events recorded in `audit_logs`:
- Login attempts (success/failure + IP)
- Subscription creation/expiry
- Payment events
- Cookie connect/disconnect
- Admin actions (user block, refund, data deletion)

---

## 22. Rate Limiting & Quota System

### API Rate Limiting

```
Auth endpoints:   5 requests / 5 minutes per IP
All other:      100 requests / 60 seconds per IP
Response on exceeded: HTTP 429 + Retry-After header
Exempt:         /health, /, /api/docs, /api/redoc
Fail behavior:  Fail-open (logged) if Redis unavailable
```

### Daily Application Quota

| Plan | Daily Limit | Reset |
|------|------------|-------|
| Starter | 150 | Midnight UTC |
| Pro | 250 | Midnight UTC |
| Premium | 500 | Midnight UTC |

Computed from DB count — accurate across worker restarts.

### Monthly AI Token Budget

| Plan | Monthly Tokens |
|------|---------------|
| Starter | 50,000 |
| Pro | 100,000 |
| Premium | Unlimited |
| Admin override | 150,000 / run |

```
GET /api/quotas/me
→ {
    "plan": "pro",
    "daily_limit": 250,
    "daily_used": 47,
    "daily_remaining": 203,
    "monthly_tokens_used": 23400,
    "monthly_tokens_limit": 100000,
    "resets_at": "2026-05-01T00:00:00Z"
  }
```

---

## 23. Priority Queue System

When multiple users have tasks queued simultaneously, `PriorityQueueService` processes by plan tier:

```
Premium (3) → processed first
Pro     (2) → processed second
Starter (1) → processed last
```

Within the same tier: FIFO by creation time.

Backed by Redis sorted sets for multi-worker correctness:

```python
await redis.zadd("applivo:queue:apply", {task_id: -priority})
task_id = await redis.zpopmin("applivo:queue:apply")
```

---

## 24. Monitoring & Logging

### Sentry (Production)

```python
import sentry_sdk
sentry_sdk.init(dsn=settings.SENTRY_DSN, traces_sample_rate=0.1)
```

Real-time error alerts, stack traces, and performance monitoring at [sentry.io](https://sentry.io).

### Structured Logging

All components use `structlog` for JSON-formatted logs:

```
2026-04-21 10:06:58 INFO  scraper  Starting scrape cycle  source=internshala user_id=abc123
2026-04-21 10:07:07 INFO  scraper  Scrape complete  jobs_new=12 budget_tokens=1450
2026-04-21 10:08:15 INFO  apply    Application submitted  company=Google role="ML Intern"
2026-04-21 10:08:16 INFO  notify   Telegram sent  title="✅ Applied — Google"
```

### Celery Flower

Available via SSH tunnel at `http://127.0.0.1:5555/flower`:
```bash
ssh -L 5555:127.0.0.1:5555 root@45.67.216.57
```
Shows: worker status, task history, queue depths, success/failure rates.

### VNC (Browser Worker Debug)

```bash
ssh -L 5900:127.0.0.1:5900 root@45.67.216.57
# VNC viewer → localhost:5900  (no password required)
```

### Health Endpoint

```
GET https://applivo.in/health
→ { "status": "healthy", "database": "connected" }
```

Use with [UptimeRobot](https://uptimerobot.com) for free uptime monitoring + SMS alerts.

### Key Metrics

| Metric | Source |
|--------|--------|
| API response time | Nginx access logs / Sentry |
| Task queue depth | Flower UI |
| Apply success rate | `applications` table status counts |
| Token usage | `chat_usage` table |
| Active subscriptions | `subscriptions` where status=active |
| Cookie expiry | `platform_cookies` where is_valid=false |
| Revenue | `payments` table |

---

## 25. Development Guide

### Local Setup (Without Docker)

```bash
# 1. Install dependencies
pip install -r requirements.txt
playwright install chromium

# 2. Start services
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=dev postgres:16-alpine
docker run -d -p 6379:6379 redis:7-alpine

# 3. Configure .env
APP_ENV=development
DEBUG=true
DATABASE_URL=postgresql+asyncpg://postgres:dev@localhost:5432/applivo
DATABASE_URL_SYNC=postgresql://postgres:dev@localhost:5432/applivo
REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD=

# 4. Run migrations
alembic upgrade heads

# 5. Start services (separate terminals)
uvicorn app.main:app --reload --port 8000
celery -A app.celery_app:celery_app worker --loglevel=info --concurrency=2
celery -A app.celery_app:celery_app beat --loglevel=info
cd frontend && npm install && npm run dev
```

### Code Conventions

- **Python**: PEP 8, type hints on all signatures, `from __future__ import annotations`
- **Async everywhere**: no `requests`, no `time.sleep()` — use `httpx`, `asyncio.sleep()`
- **Logging**: always `structlog.get_logger()`, never `print()`
- **DB sessions**: `get_db()` in route handlers, `get_db_context()` in workers
- **AI calls**: always via `AIRouter`, never direct Groq/Gemini client
- **TypeScript**: strict mode, no `any`, Zod schemas matching backend Pydantic models

### Adding a New Scraper

1. Create `app/agents/scrapers/{platform}.py` extending `BaseScraper`
2. Implement `_get_search_queries()` + `_scrape_query()`
3. Add Celery task in `celery_tasks.py`
4. Add to beat schedule in `celery_app.py`
5. Add platform to `platform.py` supported platforms list

### Adding a New API Route

1. Create `app/api/routes/{feature}.py` with `APIRouter`
2. Register in `app/main.py` `create_app()`
3. Add TypeScript types + API calls in `frontend/lib/api.ts`
4. Create page in `frontend/app/(dashboard)/{feature}/page.tsx`

---

## 26. Troubleshooting

### `Endpoint returned HTML — session not authenticated`

User's Internshala cookies expired. Go to `/connect` → re-export cookies from DevTools → paste as JSON.

### `0 jobs found after scraping`

```bash
# Check session validity for a user
docker compose exec backend python -c "
import asyncio
from app.services.cookie_service import cookie_service
print(asyncio.run(cookie_service.validate_session('USER_ID', 'internshala')))
"
```

### `Database connection failed on startup`

```bash
docker compose ps                          # check database is healthy
docker compose logs database               # check PostgreSQL logs
docker compose exec database psql -U applivo -c "SELECT 1"
```

Migrations run automatically via `entrypoint.sh`. If they fail:
```bash
docker compose logs backend | grep -E "alembic|ERROR|FATAL"
docker compose exec backend alembic upgrade heads   # run manually if needed
```

### `Celery tasks not processing`

```bash
docker compose logs worker-standard        # check for errors
docker compose logs worker-browsing        # check browser worker
docker compose exec redis redis-cli -a $REDIS_PASSWORD ping
docker compose exec redis redis-cli -a $REDIS_PASSWORD llen celery
docker compose restart worker-standard worker-browsing
```

### `Payment verification failing`

Check `RAZORPAY_KEY_SECRET` matches the key shown in Razorpay dashboard exactly. Test vs live keys must match frontend `RAZORPAY_KEY_ID`.

### `OTP not received`

Check SMTP credentials and Gmail App Password (not account password). Test:
```bash
docker compose logs backend | grep -i "otp\|smtp\|email"
```

### `Playwright: browser not found`

Browser is pre-installed in `Dockerfile` during build. If missing after image rebuild:
```bash
docker compose exec worker-browsing playwright install chromium
```

### `AI calls failing / 429 errors`

Check Groq API key and rate limits. Gemini fallback is automatic. Verify:
```bash
docker compose logs worker-browsing | grep -E "groq|gemini|ai_router"
```

Check token budget hasn't been exhausted:
```bash
# For a specific user
curl -H "Authorization: Bearer $TOKEN" https://applivo.in/api/quotas/me
```

### Reset Database (WARNING: destroys all data)

```bash
docker compose down -v
docker compose up -d database
docker compose exec backend alembic upgrade heads
docker compose up -d
```

---

## License

MIT License. See [LICENSE](LICENSE) for details.

---

## Contributing

1. Fork the repository
2. Feature branch: `git checkout -b feature/your-feature`
3. Commit: `git commit -m "feat: add LinkedIn scraper"`
4. Push + open Pull Request

All PRs must pass existing tests, add tests for new functionality, follow code conventions, and include docstrings on public functions.

---

<p align="center">
  Live at <a href="https://applivo.in"><strong>applivo.in</strong></a> · Built with FastAPI, Next.js, PostgreSQL, Redis, Celery, and Playwright<br/>
  AI powered by <a href="https://groq.com">Groq</a> (llama3-70b-8192) with <a href="https://ai.google.dev">Gemini</a> fallback
</p>
