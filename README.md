# Applivo — Automated Internship & Job Application Platform

> **Production-grade SaaS automation platform** that scrapes, applies, and tracks internships and jobs across platforms using AI-generated answers, Playwright browser automation, Celery background workers, and Razorpay subscription billing.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-16.2-000000?style=flat-square&logo=next.js)](https://nextjs.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=flat-square&logo=postgresql)](https://postgresql.org)
[![Redis](https://img.shields.io/badge/Redis-7-DC382D?style=flat-square&logo=redis)](https://redis.io)
[![Celery](https://img.shields.io/badge/Celery-5.4-37814A?style=flat-square)](https://docs.celeryq.dev)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker)](https://docker.com)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python)](https://python.org)

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

Applivo is a **multi-user SaaS platform** that automates the entire job application workflow. Users subscribe, connect their Internshala account, upload their resume, and the platform continuously scrapes new listings, generates AI-powered answers to screening questions, and submits applications — all without manual effort.

### What Applivo Does

```
User registers → Subscribes → Connects Internshala → Uploads resume
        ↓
Scraper runs every 6 hours → Finds matching internships
        ↓
AI analyzes each opportunity → Match score assigned
        ↓
Apply bot fills forms → Answers screening questions via Groq AI
        ↓
Application submitted → User notified via Email + Telegram
        ↓
Daily digest → Analytics dashboard updated
```

### Design Principles

- **Website-only** — all automation runs server-side. No desktop app, no client-side scripts
- **Multi-tenant** — every user's data, cookies, and automation is fully isolated
- **Subscription-gated** — automation only runs for users with active paid plans
- **Production-first** — structured logging, retry logic, health checks, rate limiting throughout
- **Async I/O** — all database and HTTP operations use async/await for high concurrency

---

## 2. Architecture

### High-Level System Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER (Browser)                           │
│                    Next.js Frontend (React)                     │
│         Dashboard · Jobs · Applications · Analytics             │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTPS / REST API
┌────────────────────────▼────────────────────────────────────────┐
│                    FastAPI Backend                               │
│   Auth · Billing · Profile · Jobs · Applications · Admin        │
│                                                                 │
│   Middleware: Rate Limiter · CORS · JWT Auth · Error Handler    │
└────┬───────────────────┬───────────────────────┬───────────────┘
     │                   │                       │
     ▼                   ▼                       ▼
┌─────────┐       ┌───────────┐         ┌───────────────┐
│ PostgreSQL│      │   Redis   │         │  File Storage │
│ (Primary  │      │  Broker + │         │  /app/storage │
│  Database)│      │  Cache +  │         │  resumes/     │
│           │      │  Results  │         │  screenshots/ │
└─────────┘       └─────┬─────┘         └───────────────┘
                        │ Task Queue
          ┌─────────────▼──────────────────┐
          │          Celery Workers         │
          │  ┌──────────┐  ┌────────────┐  │
          │  │ Scraping  │  │   Apply    │  │
          │  │  Queue    │  │   Queue    │  │
          │  └────┬──────┘  └─────┬──────┘ │
          │       │               │        │
          │  ┌────▼──────┐  ┌─────▼──────┐ │
          │  │Internshala│  │ Playwright  │ │
          │  │ Scraper   │  │  Apply Bot  │ │
          │  └───────────┘  └─────┬──────┘ │
          │                       │        │
          │  ┌────────────┐  ┌────▼──────┐ │
          │  │Notification│  │  Groq AI   │ │
          │  │  Queue     │  │  Answers   │ │
          │  └─────┬──────┘  └───────────┘ │
          └────────┼────────────────────────┘
                   │
          ┌────────▼────────┐
          │ Email + Telegram │
          │  Notifications   │
          └──────────────────┘
                         │
          ┌──────────────▼──────────────┐
          │   Celery Beat (Scheduler)    │
          │  Scrape: every 6h           │
          │  Apply:  every 1h           │
          │  Emails: every 30min        │
          │  Digest: daily at 9AM       │
          │  Expiry: daily at midnight  │
          └─────────────────────────────┘
```

### Container Architecture

```
docker-compose.yml
├── database      (postgres:16-alpine)   — Primary data store
├── redis         (redis:7-alpine)       — Message broker + cache
├── backend       (python:3.11-slim)     — FastAPI API server
├── worker        (python:3.11-slim)     — Celery task workers
├── scheduler     (python:3.11-slim)     — Celery Beat periodic trigger
└── flower        (python:3.11-slim)     — Worker monitoring UI (port 5555)
```

---

## 3. Project Structure

```
applivo/
│
├── app/                              # Backend application
│   ├── main.py                       # FastAPI app factory, middleware, router registration
│   ├── celery_app.py                 # Celery configuration + beat schedule
│   ├── celery_tasks.py               # All background task definitions
│   │
│   ├── core/                         # Cross-cutting concerns
│   │   ├── config.py                 # Pydantic Settings — all env vars
│   │   ├── database.py               # SQLAlchemy async engine + session factory
│   │   └── logging.py                # Structlog configuration
│   │
│   ├── models/                       # SQLAlchemy ORM models
│   │   ├── base.py                   # UUIDMixin, TimestampMixin, SoftDeleteMixin
│   │   ├── user.py                   # User, UserProfile
│   │   ├── subscription.py           # Subscription, Payment, PlanTier enum
│   │   ├── cookie.py                 # PlatformCookie (encrypted session storage)
│   │   ├── job.py                    # Job, JobAnalysis
│   │   ├── application.py            # Application, ApplicationEvent, ApplicationStatus
│   │   ├── resume.py                 # Resume
│   │   ├── interview.py              # Interview, Notification, AgentTask
│   │   ├── audit.py                  # AuditLog
│   │   ├── consent.py                # UserConsent
│   │   └── credential.py             # CredentialVault
│   │
│   ├── api/
│   │   └── routes/
│   │       ├── auth.py               # POST /register, /login, /logout, /me
│   │       ├── profile.py            # GET/PUT /profile, resume upload
│   │       ├── subscriptions.py      # Subscription management
│   │       ├── payments.py           # Razorpay order creation + verification
│   │       ├── platform.py           # Platform cookie connect/validate/disconnect
│   │       ├── jobs.py               # Job listing, apply, analytics
│   │       ├── quotas.py             # Daily quota status
│   │       ├── admin.py              # Admin: user list, stats, revenue
│   │       ├── scheduler.py          # Manual task triggering
│   │       ├── security.py           # Security audit, session management
│   │       ├── onboarding.py         # Onboarding flow
│   │       ├── settings_route.py     # User settings
│   │       └── routes.py             # Applications, resumes, cover letters, analytics
│   │
│   ├── services/                     # Business logic layer
│   │   ├── subscription_service.py   # Plan activation, expiry, access control
│   │   ├── payment_service.py        # Razorpay order + verification
│   │   ├── quota_service.py          # Daily application limit enforcement
│   │   ├── priority_queue.py         # Premium > Pro > Starter task prioritization
│   │   ├── rate_limiter.py           # Sliding window rate limiter (Redis-backed)
│   │   ├── cookie_service.py         # AES-256-GCM cookie encrypt/decrypt/validate
│   │   ├── encryption.py             # Fernet encryption utilities
│   │   ├── notification_service.py   # Email + Telegram dispatch with retry
│   │   ├── ai_assistant.py           # Groq API wrapper for AI answers
│   │   ├── application_service.py    # Application queuing + batch processing
│   │   ├── job_analyzer.py           # Job match scoring + AI analysis
│   │   ├── resume_service.py         # Resume generation + LaTeX rendering
│   │   ├── cover_letter_service.py   # AI cover letter generation
│   │   ├── interview_service.py      # Interview scheduling + prep
│   │   ├── follow_up_service.py      # Automated follow-up emails
│   │   ├── email_monitor_service.py  # IMAP inbox monitoring for recruiter replies
│   │   ├── market_service.py         # Market intelligence + salary benchmarks
│   │   ├── onboarding_service.py     # New user setup wizard
│   │   └── screening_question_service.py  # Application form Q&A
│   │
│   ├── agents/                       # Automation engine
│   │   ├── tasks.py                  # Async task orchestration
│   │   ├── apply_bot.py              # Playwright apply bot dispatcher
│   │   ├── apply_bot_internshala.py  # Internshala-specific form filling
│   │   └── scrapers/
│   │       ├── base.py               # Abstract scraper + DB persistence
│   │       └── internshala.py        # Internshala scraper (API + HTML fallback)
│   │
│   ├── templates/                    # LaTeX resume templates
│   │   ├── resume_professional.tex
│   │   ├── resume_academic.tex
│   │   ├── resume_iiit.tex
│   │   ├── resume_harshibar.tex
│   │   ├── resume_mteck.tex
│   │   └── resume_puneet.tex
│   │
│   └── utils/
│       └── helpers.py                # Shared utilities
│
├── alembic/                          # Database migrations
│   ├── env.py
│   ├── versions/
│   │   ├── 6df4ff846734_initial.py   # Full schema baseline
│   │   └── security_models_001.py    # Audit + credential tables
│   └── script.py.mako
│
├── frontend/                         # Next.js 16 + React 19 frontend
│   ├── app/
│   │   ├── page.tsx                  # Landing page
│   │   ├── login/page.tsx            # Login
│   │   ├── register/page.tsx         # Registration
│   │   ├── pricing/page.tsx          # Pricing plans
│   │   ├── onboarding/page.tsx       # Post-signup wizard
│   │   └── (dashboard)/              # Auth-gated dashboard layout
│   │       ├── layout.tsx            # Sidebar + header shell
│   │       ├── dashboard/page.tsx    # Stats overview
│   │       ├── jobs/page.tsx         # Job listings
│   │       ├── applications/page.tsx # Application tracker
│   │       ├── analytics/page.tsx    # Charts + metrics
│   │       ├── resumes/page.tsx      # Resume management
│   │       ├── cover-letters/page.tsx
│   │       ├── interviews/page.tsx
│   │       ├── skill-gaps/page.tsx
│   │       ├── follow-ups/page.tsx
│   │       ├── connect/page.tsx      # Platform connection
│   │       ├── subscription/page.tsx # Plan + billing
│   │       ├── profile/page.tsx
│   │       ├── settings/page.tsx
│   │       ├── security/page.tsx
│   │       ├── chat/page.tsx         # AI chat
│   │       └── admin/page.tsx        # Admin panel
│   ├── components/
│   │   ├── sidebar.tsx               # Navigation sidebar with plan indicator
│   │   ├── auth-guard.tsx            # Route protection
│   │   └── providers.tsx             # React Query + auth context
│   └── lib/
│       ├── api.ts                    # Axios client + interceptors
│       ├── auth.tsx                  # Auth context + hooks
│       ├── subscription.tsx          # Subscription context + quota hooks
│       └── utils.ts                  # cn(), date formatting
│
├── Dockerfile                        # Multi-stage production build
├── docker-compose.yml                # Full stack orchestration
├── requirements.txt                  # Python dependencies
├── alembic.ini                       # Migration configuration
├── .env.example                      # Environment variable template
└── create_superuser.py               # Admin account bootstrap script
```

---

## 4. Technology Stack

### Backend

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Web Framework | FastAPI | 0.111.0 | Async REST API with automatic OpenAPI docs |
| ASGI Server | Uvicorn | 0.30.1 | Production ASGI server with standard extras |
| Database ORM | SQLAlchemy | 2.0.30 | Async ORM with full type annotations |
| DB Driver | asyncpg | 0.29.0 | Async PostgreSQL driver |
| Migrations | Alembic | 1.13.1 | Schema versioning and migration management |
| Settings | pydantic-settings | 2.3.0 | Type-safe environment variable loading |
| Auth | python-jose | 3.3.0 | JWT token creation and validation |
| Passwords | passlib[bcrypt] | 1.7.4 | Bcrypt password hashing |
| Encryption | cryptography | 42.0.8 | AES-256-GCM cookie encryption |
| Task Queue | Celery | 5.4.0 | Distributed async task processing |
| Broker | Redis | 7 | Celery message broker + result backend |
| AI | openai SDK | 1.30.1 | Points to Groq API (OpenAI-compatible) |
| Browser | Playwright | 1.44.0 | Headless Chromium automation |
| HTTP Client | httpx | 0.27.0 | Async HTTP for scraping |
| HTML Parser | BeautifulSoup4 + lxml | 4.12.3 | HTML scraping and parsing |
| Email | aiosmtplib | 3.0.1 | Async SMTP email delivery |
| Logging | structlog | 24.1.0 | Structured JSON logging |
| Retry | tenacity | 8.3.0 | Retry with exponential backoff |
| PDF | weasyprint + reportlab | 62.1 | Resume PDF generation |
| Monitoring | Flower | 2.0.1 | Celery worker monitoring UI |
| Payment | razorpay (REST) | — | Subscription billing |

### Frontend

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Framework | Next.js | 16.2.2 | React SSR + App Router |
| Language | TypeScript | 5+ | Type-safe frontend |
| UI Components | Radix UI | Various | Accessible headless components |
| Styling | Tailwind CSS | 3.4.19 | Utility-first CSS |
| Data Fetching | TanStack Query | 5.96.1 | Server state management + caching |
| HTTP | Axios | 1.14.0 | API client with interceptors |
| Forms | react-hook-form + zod | 7.72.1 / 4.3 | Form handling + schema validation |
| Charts | Recharts | 3.8.1 | Analytics visualizations |
| Animations | Framer Motion | 12.38.0 | Page transitions |
| Notifications | Sonner | 2.0.7 | Toast notifications |
| Date Utils | date-fns | 4.1.0 | Date formatting |
| Icons | Lucide React | 1.7.0 | Consistent icon set |
| Theming | next-themes | 0.4.6 | Dark/light mode |

### Infrastructure

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Database | PostgreSQL 16 | Primary relational store |
| Cache/Broker | Redis 7 | Celery broker + result backend |
| Containers | Docker + Compose | Service orchestration |
| Build | Multi-stage Dockerfile | Minimal production image |
| Storage | Volume mounts | Resumes, screenshots, celery schedule |

---

## 5. Subscription Plans & Business Model

Applivo uses a **tiered SaaS billing model** with Razorpay payment processing. All prices are in Indian Rupees (INR).

### Plan Comparison

| Feature | Starter | Pro | Premium |
|---------|---------|-----|---------|
| **Price** | ₹200/month | ₹400/month | ₹800/month |
| **Daily Application Limit** | 150 | 250 | 500 |
| **Queue Priority** | Low (1) | Medium (2) | High (3) |
| Job Scraping | ✅ | ✅ | ✅ |
| Auto Apply | ✅ | ✅ | ✅ |
| Basic AI Answers | ✅ | ✅ | ✅ |
| Resume Upload | ✅ | ✅ | ✅ |
| Email Notifications | ✅ | ✅ | ✅ |
| Analytics Dashboard | ✅ | ✅ | ✅ |
| Telegram Notifications | ❌ | ✅ | ✅ |
| AI Cover Letters | ❌ | ✅ | ✅ |
| Interview Tracking | ❌ | ✅ | ✅ |
| Email Inbox Monitoring | ❌ | ✅ | ✅ |
| Follow-up Automation | ❌ | ✅ | ✅ |
| AI Skill Gap Analysis | ❌ | ✅ | ✅ |
| Advanced AI Answers | ❌ | ❌ | ✅ |
| Market Intelligence | ❌ | ❌ | ✅ |
| Advanced Analytics | ❌ | ❌ | ✅ |

### Plan Access Control

Access is enforced at multiple layers:

1. **FastAPI dependency** — `get_active_subscriber()` raises HTTP 402 if subscription is inactive
2. **Quota service** — `QuotaService.check_quota()` blocks applications when daily limit is reached
3. **Priority queue** — `PriorityQueueService` processes Premium tasks before Pro before Starter
4. **Frontend** — Sidebar items marked with `plan: "pro"` or `plan: "premium"` show upgrade prompts

```python
# Enforced in every automation endpoint
async def get_active_subscriber(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> User:
    sub = await subscription_service.get_active_subscription(current_user.id, db)
    if not sub or not sub.is_active():
        raise HTTPException(
            status_code=402,
            detail="Active subscription required"
        )
    return current_user
```

---

## 6. Database Schema

### Entity Relationship Overview

```
users ──────────────────────────────────────────────────┐
  │                                                      │
  ├── profiles (1:1)           ← skills, roles, bio      │
  ├── subscriptions (1:1)      ← plan, status, dates     │
  │     └── payments (1:N)     ← Razorpay records        │
  ├── platform_cookies (1:N)   ← encrypted sessions      │
  ├── resumes (1:N)            ← uploaded PDF files      │
  ├── applications (1:N)       ← per job applications    │
  │     └── application_events ← status history log      │
  ├── notifications (1:N)      ← email/telegram log      │
  └── audit_logs (1:N)         ← security events         │
                                                         │
jobs ────────────────────────────────────────────────────┘
  │   (shared across all users, scraped globally)
  ├── job_analyses             ← AI match scores
  └── applications (1:N)       ← applications per job
```

### Core Tables

#### `users`
```sql
id              UUID PRIMARY KEY
email           VARCHAR(255) UNIQUE NOT NULL
password_hash   VARCHAR(255) NOT NULL          -- bcrypt
full_name       VARCHAR(255) NOT NULL
is_active       BOOLEAN DEFAULT true
is_superuser    BOOLEAN DEFAULT false
created_at      TIMESTAMPTZ NOT NULL
updated_at      TIMESTAMPTZ NOT NULL
deleted_at      TIMESTAMPTZ                    -- soft delete
```

#### `profiles`
```sql
id                    UUID PRIMARY KEY
user_id               UUID REFERENCES users(id) UNIQUE
phone                 VARCHAR(20)
location              VARCHAR(255)
skills                JSONB                    -- ["Python", "ML", ...]
desired_roles         JSONB                    -- ["Data Science", ...]
experience_level      VARCHAR(50)              -- entry | mid | senior
professional_summary  TEXT
linkedin_url          VARCHAR(500)
github_url            VARCHAR(500)
portfolio_url         VARCHAR(500)
telegram_chat_id      VARCHAR(50)              -- per-user Telegram ID
notification_email    VARCHAR(255)
notify_via_telegram   BOOLEAN DEFAULT false
notify_via_email      BOOLEAN DEFAULT true
auto_apply_enabled    BOOLEAN DEFAULT false
require_approval      BOOLEAN DEFAULT true
```

#### `subscriptions`
```sql
id                       UUID PRIMARY KEY
user_id                  UUID REFERENCES users(id) NOT NULL
plan                     ENUM('starter','pro','premium') NOT NULL
status                   ENUM('active','expired','cancelled','pending') NOT NULL
start_date               TIMESTAMPTZ NOT NULL
end_date                 TIMESTAMPTZ
razorpay_subscription_id VARCHAR(255)
created_at               TIMESTAMPTZ NOT NULL
updated_at               TIMESTAMPTZ NOT NULL
```

#### `payments`
```sql
id                    UUID PRIMARY KEY
user_id               UUID REFERENCES users(id) NOT NULL
subscription_id       UUID REFERENCES subscriptions(id)
amount                INTEGER NOT NULL          -- in paise (₹100 = 10000)
currency              VARCHAR(10) DEFAULT 'INR'
status                ENUM('created','authorized','captured','refunded','failed')
razorpay_order_id     VARCHAR(255)
razorpay_payment_id   VARCHAR(255) UNIQUE
razorpay_signature    VARCHAR(500)
plan                  VARCHAR(50)               -- snapshot at payment time
created_at            TIMESTAMPTZ NOT NULL
```

#### `platform_cookies`
```sql
id                UUID PRIMARY KEY
user_id           UUID REFERENCES users(id) NOT NULL
platform          VARCHAR(50) NOT NULL          -- 'internshala'
encrypted_cookies TEXT NOT NULL                 -- AES-256-GCM encrypted JSON
is_valid          BOOLEAN DEFAULT true
expires_at        TIMESTAMPTZ
last_validated    TIMESTAMPTZ
created_at        TIMESTAMPTZ NOT NULL
updated_at        TIMESTAMPTZ NOT NULL
UNIQUE(user_id, platform)
```

#### `jobs`
```sql
id               UUID PRIMARY KEY
source           VARCHAR(50) NOT NULL           -- 'internshala'
source_job_id    VARCHAR(255) NOT NULL
source_url       VARCHAR(1000) NOT NULL
title            VARCHAR(500) NOT NULL
company_name     VARCHAR(500) NOT NULL
company_logo_url VARCHAR(1000)
description_raw  TEXT
description_clean TEXT
location         VARCHAR(500)
work_mode        VARCHAR(50)                    -- remote | onsite | hybrid
job_type         VARCHAR(50)                    -- internship | full_time
salary_min       INTEGER
salary_max       INTEGER
salary_currency  VARCHAR(10) DEFAULT 'INR'
posted_at        TIMESTAMPTZ
scraped_at       TIMESTAMPTZ NOT NULL
is_active        BOOLEAN DEFAULT true
UNIQUE(source, source_job_id)
```

#### `applications`
```sql
id                    UUID PRIMARY KEY
user_id               UUID REFERENCES users(id) NOT NULL
job_id                UUID REFERENCES jobs(id) NOT NULL
resume_id             UUID REFERENCES resumes(id)
status                ENUM('queued','applying','applied','failed','skipped')
applied_at            TIMESTAMPTZ
bot_error             TEXT
retry_count           INTEGER DEFAULT 0
match_score_at_apply  FLOAT
company_snapshot      VARCHAR(500)
job_title_snapshot    VARCHAR(500)
ai_answers            JSONB                     -- answers generated by Groq
created_at            TIMESTAMPTZ NOT NULL
UNIQUE(user_id, job_id)
```

---

## 7. Backend Services

### `SubscriptionService`
**File:** `app/services/subscription_service.py`

Manages the full subscription lifecycle. Key methods:

```python
# Check if user has active subscription
sub = await subscription_service.get_active_subscription(user_id, db)
# sub.is_active() → bool (checks status + end_date)
# sub.daily_limit → int (150/250/500 based on plan)
# sub.priority → int (1/2/3 for queue ordering)

# Activate subscription after payment verification
await subscription_service.create_subscription(
    user_id=user_id,
    plan=PlanTier.PRO,
    duration_days=30,
    razorpay_subscription_id=order_id,
    db=db
)

# Check and auto-expire outdated subscriptions
await subscription_service.expire_old_subscriptions()
```

Auto-expiry logic: when `get_active_subscription()` finds a subscription where `end_date < datetime.utcnow()`, it automatically sets `status = EXPIRED` and commits, then returns `None`.

### `QuotaService`
**File:** `app/services/quota_service.py`

Enforces the daily application limit. Uses direct database counts — no in-memory state, safe across multiple Celery workers.

```python
quota = await QuotaService().check_quota(user_id)
# Returns:
# {
#   "allowed": True,
#   "plan": "pro",
#   "limit": 250,
#   "used": 47,
#   "remaining": 203,
#   "reason": None
# }

# Atomically check + consume
allowed = await QuotaService().consume_quota(user_id, count=1)
# Returns False if quota exhausted
```

The quota is counted by querying `applications` table for `status IN ('applied', 'applying', 'queued')` on the current UTC date. This means the count is persistent, accurate, and crash-safe.

### `PaymentService`
**File:** `app/services/payment_service.py`

Wraps the Razorpay REST API for order creation and HMAC signature verification.

```python
# Create a Razorpay order (frontend opens checkout with this)
order = await PaymentService().create_order(
    user_id=user_id,
    plan=PlanTier.PRO,
)
# Returns: { "order_id": "order_xxx", "amount": 40000, "currency": "INR", ... }

# Verify payment after user completes checkout
result = await PaymentService().verify_payment(
    razorpay_order_id="order_xxx",
    razorpay_payment_id="pay_xxx",
    razorpay_signature="sha256_sig",
    user_id=user_id,
)
# On success: activates subscription, records payment
```

HMAC verification uses `hmac.compare_digest()` (constant-time comparison) to prevent timing attacks.

### `CookieService`
**File:** `app/services/cookie_service.py`

Handles encrypted storage and retrieval of Internshala session cookies per user.

```python
# Save cookies from browser (encrypted at rest)
await cookie_service.save_cookies(
    user_id=user_id,
    platform="internshala",
    cookies=[{"name": "...", "value": "...", ...}]
)

# Retrieve decrypted cookies for the apply bot
cookies = await cookie_service.get_cookies(user_id, platform="internshala")
# Returns: List[dict] or None if no valid session

# Validate session is still active
is_valid = await cookie_service.validate_session(user_id, platform="internshala")
# Hits internshala.com/users/logged_in_check

# Mark cookies as invalid (session expired)
await cookie_service.invalidate(user_id, platform="internshala")
```

Encryption uses AES-256-GCM via the `cryptography` library. The encryption key is stored in `ENCRYPTION_KEY` env variable. If unset, a key is auto-generated on first run (stored in the database or derived from `SECRET_KEY`).

### `NotificationService`
**File:** `app/services/notification_service.py`

Dispatches notifications via Email (SMTP) and Telegram Bot API with retry logic.

```python
# Send to a specific user (uses their profile settings)
await NotificationService().notify(
    user_id=user_id,
    title="✅ Applied — Google",
    body="Role: SWE Intern\nCompany: Google\n\nhttps://internshala.com/...",
    event_type="application_submitted",
)

# Telegram: reads user's telegram_chat_id from profile
# Email: reads user's notification_email from profile
# Both channels triggered if enabled in profile settings

# Send daily digest to all active subscribers
await NotificationService().send_daily_digest()
```

Each notification is logged to the `notifications` table with `status = sent | failed` and `sent_at` timestamp.

### `AIAssistant`
**File:** `app/services/ai_assistant.py`

Wraps the Groq API (OpenAI-compatible SDK) for generating application answers.

```python
answer = await AIAssistant().answer_question(
    question="Why should we hire you?",
    options=[],           # empty → free-text answer
    profile_summary=profile_summary,
    job_context="ML Intern at Zepto, requires Python + TensorFlow",
)
# Returns: concise professional answer string

# For dropdown/radio questions
answer = await AIAssistant().answer_question(
    question="Years of experience with Python",
    options=["< 1 year", "1-2 years", "2-3 years", "3+ years"],
    profile_summary=profile_summary,
)
# Returns: exact matching option text
```

Uses `llama3-70b-8192` for complex multi-paragraph answers and `llama3-8b-8192` for simple option selection to optimize API cost.

### `RateLimiter`
**File:** `app/services/rate_limiter.py`

Sliding-window token bucket limiter applied to every API endpoint.

```python
result = await rate_limiter.is_allowed(
    key=f"rate:{client_ip}",
    max_requests=100,
    window_seconds=60,
)
# Returns: { "allowed": True, "remaining": 87, "limit": 100, "retry_after": 0 }
```

Applied as FastAPI middleware in `main.py`. Returns `HTTP 429` with `Retry-After` header when limit exceeded. Unauthenticated requests keyed by IP; authenticated requests can be keyed by `user_id` for per-user limits.

### `PriorityQueueService`
**File:** `app/services/priority_queue.py`

Ensures Premium and Pro users' tasks are processed before Starter users, using a min-heap keyed by plan priority.

```python
# Enqueue a task with user's plan priority
await priority_queue.enqueue(
    task_id=application_id,
    user_id=user_id,
    task_type="apply",
    plan="pro",      # Premium=3, Pro=2, Starter=1
    payload={"application_id": application_id}
)

# Dequeue highest-priority pending task
task = await priority_queue.dequeue()
```

---

## 8. API Reference

All endpoints are prefixed with `/api`. Full interactive documentation at `/api/docs` (Swagger UI) and `/api/redoc`.

### Authentication

```
POST   /api/auth/register          Register new user
POST   /api/auth/login             Login, receive JWT
GET    /api/auth/me                Current user info
POST   /api/auth/logout            Invalidate token
```

### Subscriptions & Billing

```
GET    /api/subscriptions/plans    List all plans + pricing
GET    /api/subscriptions/me       Current subscription status
POST   /api/payments/create-order  Create Razorpay order → { order_id, amount }
POST   /api/payments/verify        Verify payment + activate subscription
POST   /api/payments/webhook       Razorpay webhook (server-to-server)
```

### Profile & Resume

```
GET    /api/profile                 Get user profile
PUT    /api/profile                 Update profile fields
POST   /api/profile/resume          Upload resume PDF (multipart)
GET    /api/profile/resumes         List uploaded resumes
DELETE /api/profile/resume/{id}     Delete a resume
```

### Platform Connection

```
GET    /api/platform/status         Connection status for all platforms
POST   /api/platform/connect        Save platform cookies (encrypted)
POST   /api/platform/validate       Validate session is still active
DELETE /api/platform/{platform}     Disconnect a platform
```

Request body for `/api/platform/connect`:
```json
{
  "platform": "internshala",
  "cookies": [
    { "name": "session", "value": "abc123", "domain": ".internshala.com" }
  ]
}
```

### Jobs & Applications

```
GET    /api/jobs                    List scraped jobs (paginated)
GET    /api/jobs/{id}               Job detail
POST   /api/jobs/{id}/apply         Queue application for a job
GET    /api/applications            List user's applications
GET    /api/applications/{id}       Application detail + events
DELETE /api/applications/{id}       Cancel queued application
GET    /api/analytics/dashboard     Application statistics + charts
GET    /api/quotas/me               Daily quota status
```

### Scheduler (Manual Trigger)

```
POST   /api/scheduler/trigger/{task}   Manually trigger a background task
GET    /api/scheduler/jobs             List scheduled jobs + next run times
```

Available tasks: `scrape_jobs`, `scrape_internshala`, `check_email_inbox`, `analyze_new_jobs`, `check_follow_ups`, `daily_digest`

### Admin (Superuser only)

```
GET    /api/admin/stats             System statistics
GET    /api/admin/users             User list
GET    /api/admin/payments          Payment history
POST   /api/admin/users/{id}/block  Block a user
GET    /api/admin/tasks             Recent agent task logs
```

### Health

```
GET    /health                      Database + service health check
GET    /                            API info
```

---

## 9. Background Workers & Task Queue

### Celery Configuration

**File:** `app/celery_app.py`

```python
# Task routing — separate queues per task type
task_routes = {
    "app.celery_tasks.scrape_jobs":       {"queue": "scraping"},
    "app.celery_tasks.analyze_jobs":      {"queue": "analysis"},
    "app.celery_tasks.auto_apply":        {"queue": "apply"},
    "app.celery_tasks.send_notification": {"queue": "notifications"},
    "app.celery_tasks.check_emails":      {"queue": "email_monitor"},
    "app.celery_tasks.priority_*":        {"queue": "priority"},
}

# Worker launched with all queues:
# celery -A app.celery_app:celery_app worker --concurrency=4
# -Q default,scraping,analysis,apply,notifications,email_monitor,priority
```

### Beat Schedule

| Task | Schedule | Description |
|------|----------|-------------|
| `scrape_jobs` | Every 6 hours (0,6,12,18) | Scrape all platforms |
| `auto_apply` | Every hour | Process queued applications |
| `check_emails` | Every 30 minutes | IMAP inbox monitor |
| `send_daily_digest` | Daily at 9:00 AM UTC | Email + Telegram summary |
| `check_expired_subscriptions` | Daily at midnight | Auto-expire subscriptions |
| `check_expired_cookies` | Every 4 hours | Validate platform sessions |

### Task Definitions

**`scrape_jobs`** — Triggers `InternshalaScaper().run()` for all categories. Retries 3x with 5-minute delays.

**`analyze_jobs`** — Runs `JobAnalyzerService().analyze_new_batch()` to score new jobs against all active user profiles.

**`auto_apply`** — Calls `ApplicationService().queue_batch_applications()` which:
1. Finds jobs above match threshold for each user
2. Checks daily quota via `QuotaService`
3. Deduplicates (no re-applying to already-applied jobs)
4. Creates `Application` records with `status=QUEUED`
5. Dispatches per-application `run_apply_task` Celery tasks

**`send_notification`** — Dispatches email + Telegram for a specific notification ID. Retries 3x.

**`check_emails`** — IMAP login → fetch unread emails → forward recruiter replies to user.

**`send_daily_digest`** — Aggregates today's application count per active user → sends summary notification.

**`check_expired_subscriptions`** — Finds subscriptions where `end_date < now()` → sets `status = EXPIRED` → notifies user to renew.

**`check_expired_cookies`** — For each user with saved cookies, hits platform session check endpoint → marks invalid if 401.

### Async Execution Pattern

All Celery tasks are synchronous Python functions (Celery requirement) that wrap async code:

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

---

## 10. Scraper Engine

**File:** `app/agents/scrapers/internshala.py`

### Extraction Strategy (Three Layers)

The scraper attempts data extraction in priority order:

```
1. AJAX JSON API (/internships/ajax-new-search-v2-and-a-half/)
   └── Requires authenticated session cookies
   └── Returns structured JSON with all internship metadata
   └── Fastest and most complete

2. __NEXT_DATA__ JSON extraction
   └── Works without authentication (public pages)
   └── Internshala embeds full page data in <script id="__NEXT_DATA__">
   └── Recursive tree search finds internship arrays

3. BeautifulSoup HTML parsing
   └── Last resort fallback
   └── Multi-strategy selectors for each field (resilient to markup changes)
   └── Extracts: job_id, title, company, location, stipend, URL
```

### Session Validation

Before each scrape cycle, the scraper validates the session:

```python
async def _check_session(self, client) -> bool:
    resp = await _http_get_with_retry(
        client,
        "https://internshala.com/users/logged_in_check",
        headers={"Accept": "application/json", "X-Requested-With": "XMLHttpRequest"},
    )
    # Returns {"logged_in": true/false}
    logged_in = resp.json().get("logged_in", False)
    if not logged_in:
        self.log.warning(
            "Session EXPIRED — user must reconnect Internshala",
            user_id=self.user_id,
        )
    return logged_in
```

### Retry Logic

All HTTP requests use exponential backoff:

```python
async def _http_get_with_retry(client, url, *, max_retries=3, **kwargs):
    for attempt in range(max_retries):
        try:
            return await client.get(url, **kwargs)
        except (TimeoutException, ConnectError) as exc:
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)  # 1s, 2s, 4s
            else:
                raise
```

### Deduplication

Jobs are deduplicated before database insertion using `source_job_id` (e.g., `internshala_3086913`):

```python
existing = {row[0] for row in (await db.execute(
    select(Job.source_job_id).where(Job.source == "internshala")
)).all()}

new_jobs = [j for j in scraped if j.source_job_id not in existing]
db.add_all(new_jobs[:settings.MAX_JOBS_PER_CYCLE])
```

### Scraped Categories

```python
CATEGORIES = [
    "Machine Learning", "Data Science", "Python",
    "Web Development", "Software Development",
    "Artificial Intelligence", "Computer Vision",
]
```

Customizable via `USER_DESIRED_ROLES` environment variable (parsed as JSON array).

---

## 11. Apply Bot

**Files:** `app/agents/apply_bot.py`, `app/agents/apply_bot_internshala.py`

### Apply Flow

```
1. Load Application record from DB
2. Load Job, UserProfile, Resume, PlatformCookie
3. Decrypt cookies (AES-256-GCM)
4. Mark Application as APPLYING
5. Launch Playwright Chromium (headless)
6. Inject decrypted cookies into browser context
7. Navigate to https://internshala.com/ → verify login
8. Navigate to job detail page
9. Check already-applied badge → if found, return { success: true, already_applied: true }
10. Find Apply / Easy Apply button
11. Click → wait for modal OR navigate to apply page
12. Fill all form fields:
    - Textareas → Groq AI generates answer
    - Dropdowns → Groq AI selects best option
    - Phone → from user profile
    - Date fields → current date + 30 days
    - File upload → user's default resume PDF
13. Click Submit button
14. Verify success via page content / modal disappearance
15. Update Application status → APPLIED or FAILED
16. Send notification to user
```

### AI-Powered Form Filling

For each textarea (screening question), the bot:

1. Extracts the question label from surrounding DOM elements
2. Builds a profile summary string:
   ```
   Experience level: entry
   Target roles: Machine Learning, Data Science
   Projects: Facial Recognition System, Stock Predictor
   Applying for: ML Intern at Zepto
   Job description excerpt: ...
   ```
3. Calls Groq API with the question + profile context
4. Injects the answer using JavaScript native setter (works on hidden fields)

For dropdown/radio fields, Groq selects the exact option text from the available options.

### Anti-Bot Measures

The apply bot implements several measures to avoid detection:

```python
# Disable webdriver flag
await context.add_init_script("""
    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
""")

# Random typing delay (human-like)
async def _human_type(element, text):
    for char in text:
        await element.type(char, delay=random.uniform(40, 130))
        if random.random() < 0.05:
            await asyncio.sleep(random.uniform(0.1, 0.3))

# User agent rotation
_USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
]

# Random delays between actions
await asyncio.sleep(random.uniform(1.5, 3.0))
```

### CAPTCHA Handling

When CAPTCHA is detected, the application is paused:

```python
async def _has_captcha(page) -> bool:
    if await page.query_selector(".g-recaptcha, [data-sitekey]"):
        return True
    for frame in page.frames:
        if "recaptcha/api2/bframe" in frame.url:
            return True
    return False

# Wait up to 2 minutes for user to solve CAPTCHA manually
async def _wait_for_captcha_resolution(page, timeout_s=120) -> bool:
    for _ in range(timeout_s):
        await asyncio.sleep(1)
        if not await _has_captcha(page):
            return True
    return False
```

The application is set back to `QUEUED` status and the user is notified via Telegram/Email to apply manually.

---

## 12. AI Integration

**File:** `app/services/ai_assistant.py`

### Groq API Configuration

Applivo uses the Groq API (OpenAI-compatible) for fast, cost-effective AI inference:

```python
# All AI calls route through Groq
client = AsyncOpenAI(
    api_key=settings.GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1",
)

# Heavy model for complex answers (multi-paragraph)
HEAVY_MODEL = "llama3-70b-8192"

# Light model for option selection + simple tasks
LIGHT_MODEL = "llama3-8b-8192"
```

### Prompt Engineering

**Screening question (free text):**
```
You are filling a job application form for a candidate.

Candidate profile summary:
{profile_summary}

Job context:
{job_context}

Question: {question}

Write a concise, enthusiastic, professional answer (2-4 sentences).
Be specific about the candidate's actual skills matching the job.
Never use placeholder text like [specific skills] — use real skill names from the profile.
If asked for links or URLs and none are available, say 'Available upon request'.
If asked for a number (e.g. years of experience), reply with just the number.
```

**Screening question (options):**
```
You are filling a job application form for a candidate.

Candidate profile summary:
{profile_summary}

Question: {question}

Available options:
  - {option_1}
  - {option_2}
  ...

Reply with ONLY the exact text of the best option — nothing else.
```

### AI Services Used

| Service | Model | Use Case |
|---------|-------|----------|
| Screening answers (complex) | llama3-70b-8192 | Why should we hire you, cover letters |
| Option selection | llama3-8b-8192 | Dropdown answers, yes/no questions |
| Job match scoring | llama3-70b-8192 | Match score + recommendation |
| Resume tailoring | llama3-70b-8192 | Tailored resume bullet points |
| Cover letter generation | llama3-70b-8192 | Full cover letter per job |
| Skill gap analysis | llama3-8b-8192 | Skills vs job requirements |

---

## 13. Cookie & Session Management

### How Users Connect Their Account

1. User opens Internshala in their browser and logs in
2. User opens browser DevTools → Application → Cookies → copy all cookies for `internshala.com`
3. User pastes the JSON array into Applivo's **Connect** page (`/connect`)
4. Applivo encrypts the cookies and stores them in the `platform_cookies` table
5. The apply bot decrypts and injects them into each Playwright browser context

### Encryption (AES-256-GCM)

```python
# Encrypt before storage
from cryptography.fernet import Fernet

def encrypt_cookies(data: str) -> str:
    f = Fernet(settings.ENCRYPTION_KEY.encode())
    return f.encrypt(data.encode()).decode()

def decrypt_cookies(token: str) -> str:
    f = Fernet(settings.ENCRYPTION_KEY.encode())
    return f.decrypt(token.encode()).decode()
```

### Session Expiry Detection

Every 4 hours, Celery runs `check_expired_cookies` which:

1. For each user with valid cookies, makes a request to `internshala.com/users/logged_in_check`
2. If the session is invalid (returns `{"logged_in": false}` or 401):
   - Sets `PlatformCookie.is_valid = False`
   - Disables `UserProfile.auto_apply_enabled`
   - Sends notification: "Your Internshala session has expired — please reconnect"

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

---

## 14. Notification System

**File:** `app/services/notification_service.py`

### Channels

**Telegram Bot**
- Requires user to set `telegram_chat_id` in their profile
- User must start a conversation with the Applivo bot first
- Messages formatted in Markdown with rich application details

**Email (SMTP)**
- Uses user's `notification_email` from profile, falling back to their account email
- HTML emails with inline CSS styling
- Plain-text fallback for email clients that don't render HTML

### Notification Events

| Event | Title | Channels |
|-------|-------|---------|
| Application submitted | `✅ Applied — {Company}` | Both |
| Application failed | `❌ Failed — {Company}` | Both |
| CAPTCHA detected | `⚠️ CAPTCHA Required` | Both |
| Session expired | `🔑 Session Expired` | Both |
| Subscription expired | `💳 Subscription Expired` | Email |
| Daily digest | `📊 Daily Summary` | Both |
| Interview scheduled | `🗓️ Interview — {Company}` | Both |

### Retry Logic

```python
# Telegram: 3 retries with exponential backoff
for attempt in range(3):
    try:
        response = await http.post(telegram_url, json=payload)
        if response.json().get("ok"):
            break
    except Exception:
        if attempt < 2:
            await asyncio.sleep(2 ** attempt)

# Email: aiosmtplib with 30s timeout, fallback handled by Celery retry
await aiosmtplib.send(msg, hostname=SMTP_HOST, port=587, start_tls=True, timeout=30)
```

---

## 15. Payment Integration (Razorpay)

### Payment Flow

```
Frontend                     Backend                     Razorpay
   │                             │                           │
   │  POST /api/payments/        │                           │
   │  create-order               │                           │
   │  { plan: "pro" }           ─┤─ Create order ──────────►│
   │                             │◄── { order_id, amount } ──│
   │◄── { order_id, key_id } ───│                           │
   │                             │                           │
   │  Open Razorpay Checkout     │                           │
   │  (user enters card)         │                           │
   │─────────────────────────────────────────────────────►  │
   │                             │                           │
   │◄── { payment_id, sig } ─────│────────────────────────── │
   │                             │                           │
   │  POST /api/payments/verify  │                           │
   │  { order_id, payment_id,   ─┤─ Verify HMAC signature    │
   │    signature }              │                           │
   │                             │  Activate subscription    │
   │◄── { status: "success" } ──│                           │
```

### HMAC Verification

```python
import hashlib, hmac

expected = hmac.new(
    settings.RAZORPAY_KEY_SECRET.encode(),
    f"{razorpay_order_id}|{razorpay_payment_id}".encode(),
    hashlib.sha256,
).hexdigest()

if not hmac.compare_digest(expected, razorpay_signature):
    raise HTTPException(status_code=400, detail="Invalid payment signature")
```

### Webhook Handler

`POST /api/payments/webhook` handles server-to-server events from Razorpay (e.g., `payment.captured`, `payment.failed`). Webhook signature is verified using `RAZORPAY_WEBHOOK_SECRET`.

---

## 16. Frontend Architecture

### Technology Decisions

- **Next.js App Router** — server components for initial load, client components for interactivity
- **TanStack Query** — all API calls use `useQuery`/`useMutation` with automatic caching and refetch
- **Axios with interceptors** — JWT token attached to every request automatically; 401 redirects to login
- **Zod schemas** — form validation matches backend Pydantic schemas exactly

### Authentication Flow

```typescript
// lib/auth.tsx
const AuthContext = createContext<AuthContextType>(null!);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem("token"));

  const login = async (email, password) => {
    const { data } = await api.post("/auth/login", { email, password });
    setToken(data.access_token);
    setUser(data);
    localStorage.setItem("token", data.access_token);
  };

  // token auto-attached via axios interceptor in lib/api.ts
}
```

### Route Protection

```typescript
// components/auth-guard.tsx
export function AuthGuard({ children, requiredPlan }) {
  const { user, loading } = useAuth();
  const { plan, subscription } = useSubscription();
  const router = useRouter();

  if (!user) return router.push("/login");
  if (requiredPlan && !hasRequiredPlan(plan, requiredPlan)) {
    return <UpgradePrompt requiredPlan={requiredPlan} />;
  }
  return children;
}
```

### Dashboard Pages

| Route | Component | Description |
|-------|-----------|-------------|
| `/dashboard` | Dashboard | Stats cards, recent applications, quota bar |
| `/jobs` | Jobs | Paginated job listings with apply button |
| `/applications` | Applications | Application tracker with status filters |
| `/analytics` | Analytics | Recharts: applications over time, success rate |
| `/resumes` | Resumes | Upload + manage resume PDFs |
| `/connect` | Connections | Platform connection wizard |
| `/subscription` | Subscription | Current plan, upgrade, payment history |
| `/cover-letters` | CoverLetters | (Pro+) AI-generated cover letters |
| `/interviews` | Interviews | (Pro+) Interview scheduling + prep |
| `/skill-gaps` | SkillGaps | (Pro+) Skills analysis |
| `/follow-ups` | FollowUps | (Pro+) Automated follow-up management |
| `/chat` | AIChat | Direct AI assistant conversation |
| `/admin` | Admin | (Superuser) User management + stats |

### Subscription Context

```typescript
// lib/subscription.tsx
export function useSubscription() {
  const { data } = useQuery({
    queryKey: ["subscription"],
    queryFn: () => api.get("/subscriptions/me").then(r => r.data),
    staleTime: 5 * 60 * 1000,
  });

  return {
    plan: data?.plan ?? null,       // "starter" | "pro" | "premium" | null
    isActive: data?.is_active,
    quota: data?.quota,             // { used, limit, remaining }
    subscription: data,
  };
}
```

---

## 17. Infrastructure & Docker

### Dockerfile (Multi-Stage Build)

```dockerfile
# Stage 1: Build dependencies
FROM python:3.11-slim AS builder
WORKDIR /build
RUN apt-get install -y gcc g++ libpq-dev
COPY requirements.txt .
RUN pip install --prefix=/install -r requirements.txt

# Stage 2: Runtime image
FROM python:3.11-slim
WORKDIR /app
RUN apt-get install -y libpq5 libnss3 libatk1.0-0 ...  # Playwright deps
COPY --from=builder /install /usr/local
COPY . .
RUN useradd -m -u 1000 applivo && chown -R applivo:applivo /app
USER applivo
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Container Services

| Container | Image | Port | Command |
|-----------|-------|------|---------|
| `applivo-database` | postgres:16-alpine | 5433→5432 | Default PostgreSQL |
| `applivo-redis` | redis:7-alpine | 6379→6379 | With AOF persistence |
| `applivo-backend` | (built) | 8000→8000 | uvicorn app.main:app |
| `applivo-worker` | (built) | — | celery worker -Q all |
| `applivo-scheduler` | (built) | — | celery beat |
| `applivo-flower` | (built) | 5555→5555 | celery flower |

### Volume Mounts

```yaml
volumes:
  postgres-data:    # PostgreSQL data files
  redis-data:       # Redis persistence (AOF)
  applivo-storage:  # Shared storage (resumes, screenshots, celerybeat schedule)
```

All containers mount the same `applivo-storage` volume so the API, worker, and scheduler all see the same file system.

### Health Checks

```yaml
# PostgreSQL
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U applivo"]
  interval: 10s
  retries: 5

# Redis
healthcheck:
  test: ["CMD", "redis-cli", "ping"]
  interval: 10s

# Backend API
healthcheck:
  test: ["CMD", "python", "-c", "import httpx; httpx.get('http://localhost:8000/health')"]
  interval: 30s
  start_period: 40s
```

### Logging

All containers use the `json-file` log driver with rotation:
```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

---

## 18. Environment Variables

Copy `.env.example` to `.env` and configure all required variables before starting.

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | JWT signing secret (min 32 chars) | `your-random-32-char-secret-here` |
| `DATABASE_URL` | PostgreSQL async connection string | `postgresql+asyncpg://applivo:pass@database:5432/applivo` |
| `DATABASE_URL_SYNC` | PostgreSQL sync string (Alembic) | `postgresql://applivo:pass@database:5432/applivo` |
| `POSTGRES_PASSWORD` | PostgreSQL container password | `securepassword123` |
| `REDIS_URL` | Redis connection URL | `redis://redis:6379/0` |
| `GROQ_API_KEY` | Groq API key for AI | `gsk_xxxxxxxxxxxxxxxxxxxx` |
| `JWT_SECRET_KEY` | JWT signing secret | `jwt-secret-32-chars-minimum` |

### Optional — Payment

| Variable | Description |
|----------|-------------|
| `RAZORPAY_KEY_ID` | Razorpay API key ID (`rzp_test_...` or `rzp_live_...`) |
| `RAZORPAY_KEY_SECRET` | Razorpay API secret |
| `RAZORPAY_WEBHOOK_SECRET` | Webhook signature verification secret |

### Optional — Notifications

| Variable | Description | Example |
|----------|-------------|---------|
| `TELEGRAM_BOT_TOKEN` | Bot token from @BotFather | `123456789:ABC-...` |
| `SMTP_HOST` | SMTP server hostname | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP port (587 for TLS) | `587` |
| `SMTP_USERNAME` | SMTP login email | `yourapp@gmail.com` |
| `SMTP_PASSWORD` | SMTP app password | `abcd efgh ijkl mnop` |
| `SMTP_FROM_EMAIL` | From address in sent emails | `noreply@applivo.in` |

### Optional — Internshala Credentials

| Variable | Description |
|----------|-------------|
| `INTERNShALA_EMAIL` | Internshala login email (fallback if no cookies) |
| `INTERNShALA_PASSWORD` | Internshala password (fallback) |

### Optional — Auto Apply

| Variable | Default | Description |
|----------|---------|-------------|
| `AUTO_APPLY_ENABLED` | `false` | Enable auto-apply globally |
| `AUTO_APPLY_MATCH_THRESHOLD` | `75` | Minimum AI match score (0-100) |
| `AUTO_APPLY_DAILY_LIMIT` | `10` | Global daily limit (overridden by plan) |
| `AUTO_APPLY_REQUIRE_APPROVAL` | `true` | Require manual approval per application |

### Optional — Rate Limiting & Scraping

| Variable | Default | Description |
|----------|---------|-------------|
| `RATE_LIMIT_REQUESTS` | `100` | Requests per window |
| `RATE_LIMIT_WINDOW_SECONDS` | `60` | Rate limit window size |
| `SCRAPE_INTERVAL_HOURS` | `6` | Hours between scrape cycles |
| `MAX_JOBS_PER_CYCLE` | `200` | Max jobs to save per scrape |

### Security Variables

| Variable | Description |
|----------|-------------|
| `ENCRYPTION_KEY` | Fernet key for cookie encryption (base64, 32 bytes) |
| `JWT_ALGORITHM` | JWT algorithm (default: `HS256`) |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiry (default: `1440` = 24h) |

---

## 19. Installation & Deployment

### Prerequisites

- Docker 24.0+ and Docker Compose 2.24+
- At minimum 2GB RAM for all containers
- Groq API key (free tier available at [console.groq.com](https://console.groq.com))

### Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/your-org/applivo.git
cd applivo

# 2. Configure environment
cp .env.example .env
# Edit .env — set SECRET_KEY, JWT_SECRET_KEY, POSTGRES_PASSWORD, GROQ_API_KEY

# 3. Generate an encryption key for cookies
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# Add the output as ENCRYPTION_KEY in .env

# 4. Start all containers
docker-compose up -d

# 5. Run database migrations
docker-compose exec backend python -m alembic upgrade head

# 6. Create admin user
docker-compose exec backend python create_superuser.py \
  --email admin@example.com \
  --password securepassword \
  --name "Admin User"

# 7. Install Playwright browser (Chromium)
docker-compose exec worker playwright install chromium

# 8. Verify everything is running
curl http://localhost:8000/health
# Expected: {"status": "healthy", "database": "connected", ...}

# 9. Start the frontend (optional — separate deployment)
cd frontend
npm install
npm run dev    # or: npm run build && npm start
```

### Production Deployment Checklist

```bash
# Required .env changes for production:
APP_ENV=production
DEBUG=false
SECRET_KEY=<cryptographically-random-64-char-string>
JWT_SECRET_KEY=<cryptographically-random-64-char-string>
POSTGRES_PASSWORD=<strong-database-password>
ENCRYPTION_KEY=<fernet-key-from-generation-step>

# Razorpay live keys
RAZORPAY_KEY_ID=rzp_live_xxxxxxxxxxxxx
RAZORPAY_KEY_SECRET=<live-secret>

# CORS (replace with your actual domain)
# Add ALLOWED_ORIGINS to config if deploying with CORS restrictions
```

### Scaling Workers

To handle more users, scale the Celery worker:

```bash
# Run 8 concurrent workers
docker-compose up -d --scale worker=3

# Or adjust concurrency per worker
docker-compose exec worker celery -A app.celery_app:celery_app \
  worker --concurrency=8 -Q default,scraping,analysis,apply,notifications
```

### Monitoring Celery

Flower is available at `http://localhost:5555` — shows:
- Active workers and their tasks
- Task history (success/failure rates)
- Queue depths
- Task result inspection

---

## 20. Alembic Migrations

**Config file:** `alembic.ini`
**Migrations directory:** `alembic/versions/`

### Commands

```bash
# Apply all pending migrations
docker-compose exec backend python -m alembic upgrade head

# Rollback one migration
docker-compose exec backend python -m alembic downgrade -1

# Create a new migration after model changes
docker-compose exec backend python -m alembic revision --autogenerate \
  -m "add_skill_tags_column"

# View current migration status
docker-compose exec backend python -m alembic current

# View migration history
docker-compose exec backend python -m alembic history --verbose
```

### Existing Migrations

| Revision | Description |
|----------|-------------|
| `6df4ff846734` | Initial schema — all core tables |
| `security_models_001` | Audit logs, credential vault, consent records |

---

## 21. Security Architecture

### Authentication

- **JWT tokens** signed with `HS256` algorithm and `JWT_SECRET_KEY`
- Tokens expire after 24 hours (configurable via `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`)
- Stored in `localStorage` on the frontend, attached as `Authorization: Bearer <token>` header
- Every protected endpoint validates the token via `get_current_user()` FastAPI dependency

### Password Storage

- **bcrypt** with adaptive cost factor (passlib default: cost 12)
- Passwords never stored in plaintext or logged
- No password reset without email verification

### Cookie Encryption

- Session cookies encrypted with **Fernet (AES-128-CBC + HMAC-SHA256)**
- Unique key per deployment, stored in `ENCRYPTION_KEY` env variable
- Cookies are opaque blobs in the database — no plaintext storage

### API Security

- Rate limiting: 100 requests/minute per IP (configurable)
- CORS: wildcard in development, explicit origins in production
- Input validation: all request bodies validated by Pydantic
- SQL injection: impossible via SQLAlchemy ORM parameterized queries
- Secret exposure: all sensitive config read from env vars, never hardcoded

### Payment Security

- Razorpay HMAC signature verified using `hmac.compare_digest()` (constant-time, prevents timing attacks)
- Webhook secret verified server-to-server
- Payment amounts always fetched from server-side plan definition — never trusted from client

### Audit Logging

The `audit_logs` table records:
- Login attempts (success/failure)
- Subscription changes
- Payment events
- Cookie connect/disconnect
- Admin actions

---

## 22. Rate Limiting & Quota System

### API Rate Limiting

Implemented as FastAPI middleware in `main.py`. Uses a sliding-window counter stored in memory (or Redis in production).

```
Limit: 100 requests per 60 seconds per IP
Response on exceeded: HTTP 429 + Retry-After header
```

Certain paths are exempt: `/health`, `/`, `/api/docs`, `/api/redoc`

### Daily Application Quota

Enforced by `QuotaService` before every application submission:

| Plan | Daily Limit | Reset |
|------|------------|-------|
| Starter | 150 | Midnight UTC |
| Pro | 250 | Midnight UTC |
| Premium | 500 | Midnight UTC |

The quota is computed by counting `applications` records for the current UTC date, making it accurate even after worker restarts or crashes.

```
GET /api/quotas/me
→ {
    "plan": "pro",
    "limit": 250,
    "used": 47,
    "remaining": 203,
    "resets_at": "2026-04-05T00:00:00Z"
  }
```

---

## 23. Priority Queue System

**File:** `app/services/priority_queue.py`

When multiple users have applications queued simultaneously, the system processes them in plan priority order:

```
Premium (priority=3) → processed first
Pro     (priority=2) → processed second
Starter (priority=1) → processed last
```

Within the same priority tier, tasks are ordered by creation time (FIFO).

The priority queue is implemented as a min-heap (`heapq`) with negated priority values so the highest-priority task is at the head. Tasks are inserted via `enqueue()` and consumed by Celery workers via `dequeue()`.

For multi-worker deployments, the queue is backed by Redis sorted sets:

```python
# Redis sorted set: key=task_id, score=priority
await redis.zadd("applivo:queue:apply", {task_id: -priority})
task_id = await redis.zpopmin("applivo:queue:apply")
```

---

## 24. Monitoring & Logging

### Structured Logging

All components use `structlog` for JSON-formatted logs:

```
2026-04-02 10:06:58 INFO  scraper  Starting scrape cycle  source=internshala
2026-04-02 10:07:02 INFO  scraper  HTML parse  cards_found=101 category=Machine Learning
2026-04-02 10:07:07 INFO  scraper  Scrape complete  jobs_found=45 jobs_new=12 errors=0
2026-04-02 10:08:15 INFO  apply    Application submitted  user=abc123 job=Google company=Google
2026-04-02 10:08:16 INFO  notify   Telegram sent  user=abc123 title="✅ Applied — Google"
```

Log levels configurable via `LOG_LEVEL` environment variable.

### Celery Flower (Task Monitoring)

Available at `http://localhost:5555`:
- Real-time worker status
- Task success/failure rates
- Queue depths per queue
- Task result inspection
- Historical task logs

### Health Check Endpoint

```
GET /health
→ {
    "status": "healthy",
    "database": "connected",
    "app": "Applivo",
    "version": "2.0.0",
    "env": "production",
    "mode": "saas"
  }
```

Use this endpoint with your load balancer or uptime monitor (UptimeRobot, Better Uptime, etc.).

### Key Metrics to Monitor

| Metric | How to Monitor |
|--------|---------------|
| API response time | Nginx access logs / APM |
| Task queue depth | Flower UI / Redis LLEN |
| Scrape job count | Application DB analytics |
| Apply success rate | `applications` table status counts |
| Subscription revenue | `payments` table |
| Active users | `subscriptions` where status=active |
| Error rate | structlog ERROR level |
| Cookie expiry | `platform_cookies` where is_valid=false |

---

## 25. Development Guide

### Running Locally (Without Docker)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Install Playwright browser
playwright install chromium

# 3. Start PostgreSQL and Redis (via Docker or local install)
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=dev postgres:16-alpine
docker run -d -p 6379:6379 redis:7-alpine

# 4. Configure .env for local dev
DATABASE_URL=postgresql+asyncpg://postgres:dev@localhost:5432/applivo
DATABASE_URL_SYNC=postgresql://postgres:dev@localhost:5432/applivo
REDIS_URL=redis://localhost:6379/0
APP_ENV=development
DEBUG=true

# 5. Run migrations
python -m alembic upgrade head

# 6. Start the API
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 7. Start a Celery worker (separate terminal)
celery -A app.celery_app:celery_app worker --loglevel=info --concurrency=2

# 8. Start Celery Beat (separate terminal)
celery -A app.celery_app:celery_app beat --loglevel=info

# 9. Start frontend (separate terminal)
cd frontend && npm install && npm run dev
```

### Code Style & Conventions

- **Python**: PEP 8, type hints on all function signatures, async/await throughout
- **Imports**: `from __future__ import annotations` in all files
- **Logging**: always use `structlog.get_logger()`, never `print()`
- **Error handling**: all external calls wrapped in `try/except`, errors logged before re-raising
- **DB sessions**: always use `get_db()` dependency in routes, `get_db_context()` in workers
- **No blocking I/O**: all I/O must be async — no `requests`, no `time.sleep()`
- **TypeScript**: strict mode enabled, no `any` types, Zod schemas for all forms

### Adding a New Scraper

1. Create `app/agents/scrapers/{platform}.py` extending `BaseScraper`
2. Implement `_get_search_queries()` and `_scrape_query()`
3. Add a Celery task in `celery_tasks.py`
4. Add to beat schedule in `celery_app.py`
5. Add platform to `platform.py` API route supported platforms list

### Adding a New API Route

1. Create `app/api/routes/{feature}.py` with `APIRouter`
2. Register in `app/main.py` `create_app()` function
3. Add TypeScript API calls in `frontend/lib/api.ts`
4. Create the frontend page in `frontend/app/(dashboard)/{feature}/page.tsx`

---

## 26. Troubleshooting

### `Endpoint returned HTML — session not authenticated`

**Cause:** Internshala AJAX API returns HTML when cookies are expired or not authenticated.

**Fix:**
1. Go to `/connect` in the dashboard
2. Log into Internshala in another browser tab
3. Copy cookies from DevTools → Network → any request → Cookie header
4. Paste into the Connect page as JSON array

### `0 jobs found after scraping`

**Cause:** HTML fallback parser returns 0 results when markup has changed or session is invalid.

**Diagnosis:**
```bash
# Check session validity
docker-compose exec backend python -c "
import asyncio
from app.services.cookie_service import cookie_service
result = asyncio.run(cookie_service.validate_session('USER_ID', 'internshala'))
print(result)
"
```

### `Database connection failed`

**Cause:** PostgreSQL container not ready, wrong credentials, or network issue.

**Fix:**
```bash
# Check container status
docker-compose ps

# Check PostgreSQL logs
docker-compose logs database

# Test connection manually
docker-compose exec database psql -U applivo -c "SELECT 1"
```

### `Celery worker not processing tasks`

**Fix:**
```bash
# Check worker logs
docker-compose logs worker

# Check Redis connection
docker-compose exec redis redis-cli ping

# Restart worker
docker-compose restart worker

# Inspect queue contents
docker-compose exec redis redis-cli llen celery
```

### `Payment verification failing`

**Cause:** HMAC signature mismatch — usually wrong `RAZORPAY_KEY_SECRET`.

**Verify:** The key used for signing in `PaymentService.verify_payment()` must exactly match the secret in the Razorpay dashboard.

### `Playwright: browser not found`

**Fix:**
```bash
docker-compose exec worker playwright install chromium
# or for all browsers:
docker-compose exec worker playwright install
```

### `ImportError: No module named 'razorpay'`

**Fix:**
```bash
pip install razorpay
# or add to requirements.txt and rebuild Docker image
docker-compose build --no-cache backend worker
```

### Resetting the Database

```bash
# WARNING: Destroys all data
docker-compose down -v            # Remove containers + volumes
docker-compose up -d database     # Restart DB
docker-compose exec backend python -m alembic upgrade head
docker-compose exec backend python create_superuser.py ...
docker-compose up -d              # Start all services
```

---

## License

MIT License. See [LICENSE](LICENSE) for details.

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit with clear messages: `git commit -m "feat: add LinkedIn scraper"`
4. Push and open a Pull Request

All PRs must:
- Pass existing tests
- Add tests for new functionality
- Follow the code style conventions
- Include docstrings on all public functions

---

*Built with FastAPI, Next.js, PostgreSQL, Redis, Celery, and Playwright.*
*AI powered by [Groq](https://groq.com) — llama3-70b-8192 and llama3-8b-8192.*