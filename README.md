# Applivo - AI-Powered Job Automation Platform

<p align="center">
  <img src="https://applivo.com/logo.png" alt="Applivo Logo" width="200"/>
</p>

<p align="center">
  <a href="https://github.com/Applivo-Agent/Applivo-Containerized-Platform-Infrastructure">
    <img src="https://img.shields.io/github/stars/Applivo-Agent/Applivo-Containerized-Platform-Infrastructure?style=social" alt="GitHub Stars"/>
  </a>
  <a href="https://github.com/Applivo-Agent/Applivo-Containerized-Platform-Infrastructure/actions">
    <img src="https://img.shields.io/github/actions/workflow/status/Applivo-Agent/Applivo-Containerized-Platform-Infrastructure/deploy.yml" alt="Build Status"/>
  </a>
  <a href="https://github.com/Applivo-Agent/Applivo-Containerized-Platform-Infrastructure/blob/main/LICENSE">
    <img src="https://img.shields.io/github/license/Applivo-Agent/Applivo-Containerized-Platform-Infrastructure" alt="License"/>
  </a>
  <img src="https://img.shields.io/badge/Python-3.11+-blue" alt="Python Version"/>
  <img src="https://img.shields.io/badge/FastAPI-0.111.0-green" alt="FastAPI Version"/>
</p>

---

## Table of Contents

1. [Introduction](#introduction)
2. [Features](#features)
3. [Architecture](#architecture)
4. [Tech Stack](#tech-stack)
5. [Project Structure](#project-structure)
6. [Getting Started](#getting-started)
7. [API Documentation](#api-documentation)
8. [Services Overview](#services-overview)
9. [Subscription Plans](#subscription-plans)
10. [Security](#security)
11. [Deployment](#deployment)
12. [Development](#development)
13. [Troubleshooting](#troubleshooting)
14. [Roadmap](#roadmap)
15. [License](#license)

---

## Introduction

Applivo is a production-grade SaaS platform designed to automate the job search process using AI. It enables users to:

- **Scrape Jobs Automatically** - Collect job listings from Internshala and other platforms
- **AI-Powered Analysis** - Get match scores based on your profile, skills, and preferences
- **Auto-Apply to Jobs** - Queue and apply to jobs automatically based on threshold settings
- **Generate Custom Resumes** - AI creates tailored resumes for specific job applications
- **Cover Letter Generation** - AI generates personalized cover letters
- **Track Applications** - Monitor application status, interviews, and offers

The platform is built as a multi-tenant SaaS with subscription-based access control, secure payment processing via Razorpay, and comprehensive audit logging for compliance.

---

## Features

### Core Features

| Feature | Description |
|---------|-------------|
| **Job Scraping** | Automated scraping from Internshala with configurable schedules |
| **AI Job Analysis** | Match score calculation based on user profile vs job requirements |
| **Auto-Apply** | Automatic job application with approval workflow |
| **Resume Builder** | AI-generated tailored resumes using LaTeX templates |
| **Cover Letters** | AI-generated personalized cover letters |
| **Application Tracking** | Full pipeline tracking (Applied → Viewed → Shortlisted → Interview → Offer) |
| **Multi-Platform Support** | Extensible architecture for LinkedIn, Indeed, Naukri |
| **Telegram Notifications** | Real-time job alerts and application updates |
| **Email Notifications** | Weekly digest and interview schedule reminders |

### Admin Features

| Feature | Description |
|---------|-------------|
| **User Management** | View, activate/deactivate, delete users |
| **Subscription Management** | Change user plans, view subscription status |
| **Payment History** | View all payments, process refunds |
| **System Health** | Monitor database, Redis, Celery workers |
| **Automation Control** | Enable/disable auto-apply per user |
| **Audit Logs** | Full audit trail of all system actions |

### SaaS Features

| Feature | Description |
|---------|-------------|
| **Multi-Tenancy** | JWT-based authentication for multiple users |
| **Subscription Tiers** | Starter (₹200), Pro (₹400), Premium (₹800) |
| **Usage Quotas** | Daily application limits based on plan |
| **Priority Queue** | Higher-tier users get faster processing |
| **Rate Limiting** | API request limits per user tier |
| **Encrypted Storage** | AES-256-GCM encryption for platform cookies |

---

## Architecture

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              EXTERNAL CLIENTS                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Web App   │  │   Mobile    │  │   Admin     │  │  Telegram   │        │
│  │   (React)   │  │     App     │  │   Panel     │  │    Bot      │        │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘        │
└─────────┼────────────────┼────────────────┼────────────────┼─────────────────┘
          │                │                │                │
          └────────────────┴────────┬───────┴────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              LOAD BALANCER / REVERSE PROXY                   │
│                            (Nginx / Cloudflare / Traefik)                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           BACKEND API (FastAPI)                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  FastAPI Server (Port 8000)                                        │    │
│  │  • JWT Authentication                                              │    │
│  │  • Rate Limiting (Redis)                                          │    │
│  │  • Request Validation (Pydantic)                                  │    │
│  │  • CORS Middleware                                                 │    │
│  │  • Static File Serving (Resumes, Cover Letters)                   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
          ┌──────────────────────────┼──────────────────────────┐
          │                          │                          │
          ▼                          ▼                          ▼
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│  PostgreSQL     │      │      Redis      │      │   Celery        │
│  (Port 5432)   │      │   (Port 6379)   │      │   Workers       │
│                 │      │                  │      │                 │
│ • Users         │      │ • Cache         │      │ • scraping      │
│ • Jobs          │      │ • Rate Limits   │      │ • analysis      │
│ • Applications │      │ • Session Data  │      │ • apply         │
│ • Subscriptions│      │ • Celery Broker │      │ • notifications │
│ • Payments     │      │ • Result Backend│      │                 │
│ • Audit Logs   │      │                  │      │                 │
└─────────────────┘      └─────────────────┘      └─────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         BACKGROUND SERVICES                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Scraper    │  │   Job        │  │   Apply      │  │   Notification│ │
│  │   Worker     │  │   Analyzer   │  │   Bot        │  │   Service     │ │
│  │              │  │   (AI/LLM)    │  │              │  │               │ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                     │
│  │   Resume     │  │   Cover      │  │   Email      │                     │
│  │   Generator  │  │   Letter     │  │   Monitor    │                     │
│  │   (AI/LLM)   │  │   Generator  │  │   Service    │                     │
│  └──────────────┘  └──────────────┘  └──────────────┘                     │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         EXTERNAL SERVICES                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │  Internshala │  │   Razorpay   │  │    OpenAI    │  │   Telegram   │    │
│  │   (Scraping) │  │  (Payments) │  │   (AI/LLM)   │  │   (Notify)   │    │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘    │
│                                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                       │
│  │    Gmail/    │  │   Overleaf   │  │    LinkedIn │                       │
│  │   SMTP       │  │  (LaTeX)     │  │   (Future)   │                       │
│  └──────────────┘  └──────────────┘  └──────────────┘                       │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Data Flow Diagram

```
User Registration & Subscription Flow:
────────────────────────────────────────

    ┌──────────┐     ┌─────────────┐     ┌─────────────┐     ┌────────────┐
    │  User    │────▶│   Register  │────▶│  Create     │────▶│  Razorpay  │
    │  Signs   │     │   Account   │     │  Order      │     │  Checkout  │
    │  Up      │     │             │     │             │     │            │
    └──────────┘     └─────────────┘     └─────────────┘     └────────────┘
                                                                     │
                                                                     ▼
    ┌──────────┐     ┌─────────────┐     ┌─────────────┐     ┌────────────┐
    │  Webhook │◀────│   Payment   │◀────│  Verify     │◀────│  Payment   │
    │  Handler │     │   Success   │     │  Signature  │     │  Captured  │
    └──────────┘     └─────────────┘     └─────────────┘     └────────────┘
                                                                     │
                                                                     ▼
    ┌──────────┐     ┌─────────────┐     ┌─────────────┐
    │  Active  │────▶│  Quota      │────▶│  Access     │
    │  Sub     │     │  Enabled    │     │  Granted    │
    └──────────┘     └─────────────┘     └─────────────┘


Job Scraping & Application Flow:
─────────────────────────────────

    ┌──────────┐     ┌─────────────┐     ┌─────────────┐     ┌────────────┐
    │ Schedule │────▶│  Scrape     │────▶│   Store     │────▶│  AI        │
    │  Trigger │     │  Jobs       │     │  Jobs       │     │  Analysis  │
    │          │     │             │     │             │     │            │
    └──────────┘     └─────────────┘     └─────────────┘     └────────────┘
                                                                     │
                                                                     ▼
    ┌──────────┐     ┌─────────────┐     ┌─────────────┐     ┌────────────┐
    │  Match   │────▶│  Create     │────▶│  Queue      │────▶│  Auto      │
    │  Score   │     │  Application│     │  for Apply  │     │  Apply     │
    │  > 75%   │     │  Records    │     │             │     │            │
    └──────────┘     └─────────────┘     └─────────────┘     └────────────┘
                                                                     │
                                                                     ▼
    ┌──────────┐     ┌─────────────┐     ┌─────────────┐
    │  Update  │────▶│  Send       │────▶│  Log        │
    │  Status  │     │  Telegram   │     │  Audit      │
    │          │     │  Notify     │     │  Event      │
    └──────────┘     └─────────────┘     └─────────────┘
```

### Component Interaction Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          API Request Flow                                    │
│                                                                              │
│  Client                                                                        │
│    │                                                                          │
│    ▼                                                                          │
│  [JWT Token] ──▶ Authentication Middleware                                   │
│    │                                                                          │
│    ▼                                                                          │
│  Rate Limiter (Redis) ──▶ Block if exceeded                                  │
│    │                                                                          │
│    ▼                                                                          │
│  Route Handler                                                                │
│    │                                                                          │
│    ├─▶ Database (PostgreSQL)                                                 │
│    │                                                                          │
│    ├─▶ External APIs (Razorpay, OpenAI, Telegram)                            │
│    │                                                                          │
│    └─▶ Celery Task (async)                                                    │
│         │                                                                     │
│         ▼                                                                     │
│      Worker                                                                   │
│         │                                                                     │
│         ├─▶ Scrape Jobs                                                       │
│         ├─▶ AI Analysis                                                       │
│         ├─▶ Apply to Jobs                                                     │
│         └─▶ Send Notifications                                                │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Tech Stack

### Backend Technologies

| Category | Technology | Version |
|----------|------------|---------|
| **Web Framework** | FastAPI | 0.111.0 |
| **ASGI Server** | Uvicorn | 0.30.1 |
| **Language** | Python | 3.11+ |
| **ORM** | SQLAlchemy | 2.0.30 |
| **Async Driver** | asyncpg | 0.29.0 |
| **Migration** | Alembic | 1.13.1 |
| **Validation** | Pydantic | 2.7.1 |
| **Authentication** | python-jose | 3.3.0 |
| **Password Hashing** | bcrypt | 4.0.1+ |
| **Encryption** | cryptography (AES-256-GCM) | 42.0.8 |

### Task Queue & Caching

| Category | Technology | Version |
|----------|------------|---------|
| **Task Queue** | Celery | 5.4.0 |
| **Message Broker** | Redis | 7 |
| **Scheduler** | Celery Beat | (bundled) |
| **Monitoring** | Flower | 2.0.1 |

### AI & ML

| Category | Technology | Version |
|----------|------------|---------|
| **LLM Client** | OpenAI | 1.30.1 |
| **Tokenization** | tiktoken | 0.7.0 |
| **Framework** | LangChain | 0.2.1 |
| **Vector DB** | ChromaDB | 0.5.0 |

### Infrastructure

| Category | Technology |
|----------|------------|
| **Database** | PostgreSQL 16 |
| **Cache** | Redis 7 |
| **Container** | Docker & Docker Compose |
| **Runtime** | Python 3.11 |

### Additional Libraries

| Category | Libraries |
|----------|-----------|
| **HTTP Client** | httpx, aiohttp, BeautifulSoup4 |
| **Notifications** | python-telegram-bot |
| **Email** | aiosmtplib, Jinja2 |
| **PDF** | WeasyPrint, reportlab |
| **Storage** | boto3 (S3), aiofiles |
| **Utilities** | structlog, tenacity, python-dotenv |

---

## Project Structure

```
applivo-fixed/
├── app/                          # Main application package
│   ├── __init__.py              # Package initialization
│   │
│   ├── main.py                  # FastAPI application factory
│   │                           # - Router registration
│   │                           # - Middleware setup
│   │                           # - Lifespan events
│   │
│   ├── celery_app.py            # Celery application configuration
│   │                           # - Broker setup
│   │                           # - Task routes
│   │                           # - Beat schedule
│   │
│   ├── celery_tasks.py          # Celery task definitions
│   │                           # - Periodic tasks
│   │                           # - Task wrappers
│   │
│   ├── core/                    # Core infrastructure
│   │   ├── config.py           # Settings & configuration
│   │   ├── database.py         # Database connection & session
│   │   ├── logging.py          # Structured logging setup
│   │   └── __init__.py
│   │
│   ├── api/                     # API layer
│   │   ├── routes/             # API endpoints
│   │   │   ├── __init__.py
│   │   │   ├── auth.py         # Authentication (register, login, JWT)
│   │   │   ├── jobs.py         # Job scraping & analysis
│   │   │   ├── profile.py     # User profile management
│   │   │   ├── subscriptions.py # Subscription management
│   │   │   ├── payments.py     # Payment processing
│   │   │   ├── platform.py    # Platform cookie management
│   │   │   ├── quotas.py      # Usage quota management
│   │   │   ├── admin.py       # Admin service (NEW)
│   │   │   ├── security.py    # Security & audit logs
│   │   │   ├── scheduler.py   # Job scheduling
│   │   │   ├── onboarding.py  # User onboarding
│   │   │   ├── settings_route.py # User settings
│   │   │   └── routes.py      # Combined routes (applications, resumes, etc.)
│   │   │
│   │   └── __init__.py
│   │
│   ├── models/                  # Database models
│   │   ├── __init__.py         # Model exports
│   │   ├── base.py            # Base classes (UUIDMixin, TimestampMixin, etc.)
│   │   ├── user.py            # User & UserProfile models
│   │   ├── job.py             # Job & JobAnalysis models
│   │   ├── application.py     # Application & ApplicationEvent models
│   │   ├── subscription.py    # Subscription & Payment models
│   │   ├── resume.py          # Resume & CoverLetter models
│   │   ├── credential.py     # CredentialVault model
│   │   ├── consent.py         # UserConsent model
│   │   ├── cookie.py          # PlatformCookie model
│   │   ├── interview.py      # Interview & AgentTask models
│   │   ├── audit.py           # AuditLog model
│   │   └── base.py
│   │
│   ├── services/               # Business logic services
│   │   ├── __init__.py
│   │   ├── subscription_service.py  # Plan management
│   │   ├── payment_service.py       # Razorpay integration
│   │   ├── quota_service.py         # Daily limits enforcement
│   │   ├── rate_limiter.py          # Redis-based rate limiting
│   │   ├── priority_queue.py       # Celery priority routing
│   │   ├── cookie_service.py        # Encrypted cookie management
│   │   ├── application_service.py  # Auto-apply logic
│   │   ├── job_analyzer.py           # AI job analysis
│   │   ├── ai_assistant.py          # Career chatbot
│   │   ├── notification_service.py  # Telegram/Email notifications
│   │   ├── resume_service.py        # Resume management
│   │   ├── cover_letter_service.py  # Cover letter generation
│   │   ├── overleaf_service.py      # LaTeX resume generation
│   │   ├── scheduler_service.py    # Job scheduling logic
│   │   ├── screening_question_service.py
│   │   ├── interview_service.py
│   │   ├── follow_up_service.py
│   │   ├── onboarding_service.py
│   │   ├── market_service.py
│   │   ├── email_monitor_service.py
│   │   └── encryption.py            # AES-256-GCM encryption
│   │
│   ├── agents/                 # AI agents & automation
│   │   ├── __init__.py
│   │   ├── tasks.py           # Celery task definitions for agents
│   │   ├── apply_bot.py       # Auto-apply automation bot
│   │   ├── apply_bot_internshala.py # Internshala-specific apply logic
│   │   └── scrapers/         # Job scrapers
│   │       ├── __init__.py
│   │       ├── base.py       # Base scraper class
│   │       └── internshala.py # Internshala scraper
│   │
│   ├── schemas/               # Pydantic schemas
│   │   ├── __init__.py
│   │   └── (various schema files)
│   │
│   ├── utils/                # Utility functions
│   │   ├── __init__.py
│   │   └── helpers.py
│   │
│   └── storage/             # Local file storage (not in git)
│       ├── resumes/
│       ├── cover_letters/
│       └── logs/
│
├── alembic/                 # Database migrations
│   ├── versions/
│   │   └── (migration files)
│   ├── env.py
│   └── script.py.mako
│
├── docker-compose.yml       # Multi-container Docker setup
├── Dockerfile              # Multi-stage build for production
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── .gitignore
├── LICENSE
└── README.md
```

---

## Getting Started

### Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| **Docker** | 20.10+ | Required for containerized deployment |
| **Docker Compose** | 2.0+ | Required for multi-container setup |
| **Python** | 3.11+ | Required for local development |
| **PostgreSQL** | 16 | Included in Docker Compose |
| **Redis** | 7 | Included in Docker Compose |

### Environment Setup

1. **Clone the Repository**

```bash
git clone https://github.com/Applivo-Agent/Applivo-Containerized-Platform-Infrastructure.git
cd Applivo-Containerized-Platform-Infrastructure
```

2. **Create Environment File**

```bash
cp .env.example .env
```

3. **Configure Environment Variables**

Edit `.env` with your settings:

```env
# Application
APP_NAME=Applivo
APP_ENV=production
APP_HOST=0.0.0.0
APP_PORT=8000

# Database
POSTGRES_PASSWORD=your_secure_password_here
DATABASE_URL=postgresql+asyncpg://applivo:your_secure_password_here@database:5432/applivo
DATABASE_URL_SYNC=postgresql://applivo:your_secure_password_here@database:5432/applivo

# Redis
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/1

# JWT Authentication
SECRET_KEY=your_jwt_secret_key_min_32_chars
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# OpenAI (for AI features)
OPENAI_API_KEY=sk-your-openai-api-key

# Razorpay (for payments)
RAZORPAY_KEY_ID=your_razorpay_key_id
RAZORPAY_KEY_SECRET=your_razorpay_key_secret

# Telegram (for notifications)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
```

### Quick Start (Docker)

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend

# Access the API
curl http://localhost:8000/health
```

### Local Development Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start the development server
uvicorn app.main:app --reload --port 8000

# In another terminal, start Celery worker
celery -A app.celery_app:celery_app worker --loglevel=info
```

---

## API Documentation

### Base URL

```
Production: https://api.applivo.com/api
Development: http://localhost:8000/api
```

### Authentication

All protected endpoints require a JWT token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

### Public Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register a new user |
| POST | `/auth/login` | Login and get JWT token |
| GET | `/health` | Health check |

### Protected Endpoints

#### Jobs

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/jobs` | List scraped jobs |
| GET | `/jobs/{id}` | Get job details |
| GET | `/jobs/{id}/analysis` | Get AI analysis |
| POST | `/jobs/scrape` | Trigger job scraping |

#### Applications

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/applications` | List applications |
| POST | `/applications` | Create application |
| PATCH | `/applications/{id}/status` | Update status |
| POST | `/applications/{id}/approve` | Approve for auto-apply |
| GET | `/applications/stats` | Application funnel stats |

#### Profile

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/profile` | Get current user profile |
| PUT | `/profile` | Update profile |
| GET | `/profile/skills` | List user skills |
| POST | `/profile/skills` | Add skill |

#### Subscriptions

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/subscriptions/plans` | Get available plans |
| POST | `/subscriptions/create-order` | Create Razorpay order |
| POST | `/subscriptions/webhook` | Razorpay webhook handler |
| GET | `/subscriptions/current` | Get current subscription |

#### Payments

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/payments/history` | Payment history |
| GET | `/payments/{id}` | Payment details |

#### Admin (Superuser Only)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/admin/stats` | System-wide statistics |
| GET | `/admin/users` | List all users |
| GET | `/admin/users/{id}` | User details |
| PATCH | `/admin/users/{id}` | Update user |
| DELETE | `/admin/users/{id}` | Deactivate user |
| GET | `/admin/subscriptions` | List subscriptions |
| GET | `/admin/payments` | List payments |
| POST | `/admin/payments/{id}/refund` | Refund payment |
| GET | `/admin/audit-logs` | System audit logs |
| GET | `/admin/system/health` | Health check |
| GET | `/admin/automation/status` | Automation metrics |
| POST | `/admin/automation/disable/{id}` | Disable automation |
| GET | `/admin/settings` | Platform settings |

### Example API Calls

#### Register a New User

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123",
    "full_name": "John Doe"
  }'
```

#### Login

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

#### Get Current User Profile

```bash
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### Get Admin Stats

```bash
curl http://localhost:8000/api/admin/stats \
  -H "Authorization: Bearer YOUR_ADMIN_JWT_TOKEN"
```

---

## Services Overview

### Core Services

#### 1. Subscription Service (`app/services/subscription_service.py`)

Manages user subscription tiers and plan benefits.

```python
# Plan Tiers
PlanTier.STARTER = "starter"   # ₹200/month, 150 apps/day
PlanTier.PRO = "pro"           # ₹400/month, 250 apps/day
PlanTier.PREMIUM = "premium"   # ₹800/month, 500 apps/day
```

#### 2. Payment Service (`app/services/payment_service.py`)

Handles Razorpay integration for subscription payments.

- Creates payment orders
- Verifies payment signatures
- Processes webhooks
- Handles refunds

#### 3. Quota Service (`app/services/quota_service.py`)

Enforces daily application limits based on subscription tier.

- Tracks daily usage
- Resets at midnight
- Blocks when limit reached

#### 4. Rate Limiter Service (`app/services/rate_limiter.py`)

Redis-based API rate limiting.

```python
# Limits per tier
STARTER: 100 requests/minute
PRO: 200 requests/minute
PREMIUM: 500 requests/minute
```

#### 5. Priority Queue Service (`app/services/priority_queue.py`)

Celery task prioritization based on subscription tier.

```python
# Priority mapping
PREMIUM: High priority (3)
PRO: Medium priority (2)
STARTER: Normal priority (1)
```

#### 6. Cookie Service (`app/services/cookie_service.py`)

Encrypted storage for platform cookies (AES-256-GCM).

- Encrypt/decrypt cookies
- Validate session status
- Detect expired sessions

#### 7. Application Service (`app/services/application_service.py`)

Auto-apply logic and job application management.

- Queue applications
- Execute apply bots
- Track application status

#### 8. Job Analyzer Service (`app/services/job_analyzer.py`)

AI-powered job analysis with match scoring.

- Extract job requirements
- Compare with user profile
- Calculate match score (0-100%)
- Generate improvement suggestions

### Notification Services

#### Notification Service

Sends Telegram and Email notifications.

#### Email Monitor Service

Monitors email for interview responses.

---

## Subscription Plans

### Plan Comparison

| Feature | Starter | Pro | Premium |
|---------|---------|-----|---------|
| **Price** | ₹200/month | ₹400/month | ₹800/month |
| **Daily Applications** | 150 | 250 | 500 |
| **AI Job Analysis** | ✅ | ✅ | ✅ |
| **Auto-Apply** | ✅ | ✅ | ✅ |
| **Resume Generation** | 5/month | 20/month | Unlimited |
| **Cover Letters** | 5/month | 20/month | Unlimited |
| **Priority Support** | ❌ | Email | Priority |
| **API Rate Limit** | 100/min | 200/min | 500/min |
| **Task Priority** | Normal | Medium | High |

### Payment Flow

1. User selects plan
2. Backend creates Razorpay order
3. User completes payment on Razorpay
4. Razorpay sends webhook to backend
5. Backend verifies and activates subscription
6. User gets access to features

---

## Security

### Authentication

- JWT-based authentication with RSA256
- Token expiration: 24 hours
- Secure password hashing with bcrypt

### Data Encryption

- Platform cookies: AES-256-GCM
- Database at rest: PostgreSQL encryption
- SSL/TLS for data in transit

### Rate Limiting

- Per-user rate limits based on tier
- Redis-based distributed rate limiting
- Login attempt limiting (prevent brute force)

### Audit Logging

All important actions are logged:

```python
# Example audit actions
USER_LOGIN = "user.login"
USER_REGISTERED = "user.registered"
PROFILE_UPDATED = "profile.updated"
PAYMENT_SUCCESS = "payment.success"
ADMIN_USER_UPDATED = "admin.user_updated"
```

---

## Deployment

### Production Deployment (Docker)

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Scale workers (optional)
docker-compose up -d --scale worker=3
```

### Environment-Specific Configuration

| Environment | Configuration |
|-------------|---------------|
| **Development** | Local Docker, debug mode |
| **Staging** | Cloud Docker, minimal resources |
| **Production** | Kubernetes or cloud-managed services |

### Health Checks

```bash
# Backend health
curl http://localhost:8000/health

# Database connection
curl http://localhost:8000/api/health/db

# Celery workers
curl http://localhost:5555  # Flower UI
```

---

## Development

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html
```

### Code Quality

```bash
# Linting
ruff check app/

# Type checking
mypy app/

# Format code
ruff format app/
```

### Adding New Features

1. Create model in `app/models/`
2. Add schema in `app/schemas/`
3. Add service logic in `app/services/`
4. Add endpoint in `app/api/routes/`
5. Register router in `app/main.py`
6. Add tests

---

## Troubleshooting

### Common Issues

#### 1. Database Connection Failed

```bash
# Check PostgreSQL is running
docker-compose ps database

# Check connection
docker exec applivo-database psql -U applivo -d applivo -c "SELECT 1"
```

#### 2. Redis Connection Failed

```bash
# Check Redis is running
docker-compose ps redis

# Test connection
docker exec applivo-redis redis-cli ping
```

#### 3. Celery Worker Not Starting

```bash
# Check worker logs
docker-compose logs worker

# Check broker connection
docker exec applivo-worker celery -A app.celery_app:celery_app inspect ping
```

#### 4. Job Scraping Not Working

```bash
# Check scraper logs
docker-compose logs worker | grep scraper

# Test scraper manually
docker exec -it applivo-backend python -c "from app.agents.scrapers.internshala import IntershalaScraper; import asyncio; asyncio.run(IntershalaScraper().run())"
```

#### 5. Payment Webhook Not Received

```bash
# Verify webhook URL is correct in Razorpay dashboard
# Check logs for webhook errors
docker-compose logs backend | grep webhook
```

### Debug Mode

Set in `.env`:

```env
APP_ENV=development
DEBUG=true
LOG_LEVEL=DEBUG
```

---

## Roadmap

### Phase 1 (Completed ✅)

- [x] User authentication (JWT)
- [x] Job scraping from Internshala
- [x] AI job analysis with match scores
- [x] Application tracking
- [x] Multi-container Docker setup
- [x] Admin service implementation

### Phase 2 (In Progress)

- [ ] LinkedIn integration
- [ ] Naukri integration
- [ ] Indeed integration
- [ ] Resume parsing with AI
- [ ] Interview scheduling

### Phase 3 (Planned)

- [ ] LinkedIn Easy Apply automation
- [ ] Email integration (Gmail, Outlook)
- [ ] Advanced analytics dashboard
- [ ] Team features (multi-user orgs)
- [ ] Custom integrations API

---

## Contributing

Contributions are welcome! Please read our contributing guidelines before submitting PRs.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

---

## Support

- **Documentation**: https://docs.applivo.com
- **Email**: support@applivo.com
- **Telegram**: https://t.me/applivo_support

---

## License

MIT License - See [LICENSE](LICENSE) for details.

---

## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Web framework
- [SQLAlchemy](https://www.sqlalchemy.org/) - ORM
- [Celery](https://docs.celeryproject.org/) - Task queue
- [OpenAI](https://openai.com/) - AI/LLM
- [Internshala](https://internshala.com/) - Job listings

---

<p align="center">
  <strong>Built with ❤️ by the Applivo Team</strong>
</p>