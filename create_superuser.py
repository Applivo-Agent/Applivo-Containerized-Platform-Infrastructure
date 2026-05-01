"""
create_superuser.py
───────────────────
Create admin user via API registration + database flag.
Supports both SQLite (dev) and PostgreSQL (production).

Usage: 
  Development: python3 create_superuser.py
  Production (VPS): Register via API, then flag as admin in PostgreSQL

For VPS/Production:
  1. Start containers: docker compose up -d
  2. Register via API:
     curl -X POST http://localhost:8000/api/auth/register \
       -H 'Content-Type: application/json' \
       -d '{"email":"admin@yourdomain.com","password":"YourStrongPassword!","full_name":"Admin"}'
  3. Make admin in PostgreSQL:
     docker compose exec database psql -U applivo -c \
       "UPDATE users SET is_superuser=true WHERE email='admin@yourdomain.com';"
"""
import os
import sys
import sqlite3
import uuid
from datetime import datetime, timezone

DB_PATH = os.environ.get("DATABASE_URL_SYNC", "sqlite:///./applivo.db")

ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")
ADMIN_NAME = os.environ.get("ADMIN_NAME", "Super Admin")

if not ADMIN_EMAIL or not ADMIN_PASSWORD:
    print("❌ ERROR: ADMIN_EMAIL and ADMIN_PASSWORD environment variables MUST be set.")
    print("   Example: ADMIN_EMAIL=admin@applivo.in ADMIN_PASSWORD=StrongPassword123 python3 create_superuser.py")
    sys.exit(1)


def is_postgres(url: str) -> bool:
    return "postgresql" in url.lower()


def hash_password(password: str) -> str:
    import bcrypt
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def ensure_tables(conn):
    """Create tables if they don't exist (minimal schema for users)."""
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL,
            full_name TEXT NOT NULL,
            is_active INTEGER DEFAULT 1,
            is_superuser INTEGER DEFAULT 0,
            is_deleted INTEGER DEFAULT 0,
            deleted_at TEXT,
            last_login_at TEXT,
            created_at TEXT,
            updated_at TEXT
        );

        CREATE TABLE IF NOT EXISTS user_profiles (
            id TEXT PRIMARY KEY,
            user_id TEXT UNIQUE NOT NULL REFERENCES users(id),
            phone TEXT,
            location TEXT,
            linkedin_url TEXT,
            github_url TEXT,
            portfolio_url TEXT,
            experience_level TEXT DEFAULT 'entry',
            desired_roles TEXT DEFAULT '[]',
            desired_locations TEXT DEFAULT '[]',
            open_to_remote INTEGER DEFAULT 1,
            open_to_hybrid INTEGER DEFAULT 1,
            min_salary INTEGER DEFAULT 0,
            preferred_company_size TEXT DEFAULT '[]',
            preferred_industries TEXT DEFAULT '[]',
            avoid_companies TEXT DEFAULT '[]',
            professional_summary TEXT,
            career_goals TEXT,
            unique_value_proposition TEXT,
            education TEXT DEFAULT '[]',
            work_experience TEXT DEFAULT '[]',
            projects TEXT DEFAULT '[]',
            certifications TEXT DEFAULT '[]',
            awards TEXT DEFAULT '[]',
            publications TEXT DEFAULT '[]',
            auto_apply_enabled INTEGER DEFAULT 0,
            auto_apply_threshold INTEGER DEFAULT 75,
            auto_apply_daily_limit INTEGER DEFAULT 10,
            require_apply_approval INTEGER DEFAULT 1,
            notify_new_jobs INTEGER DEFAULT 1,
            notify_applications INTEGER DEFAULT 1,
            notify_interviews INTEGER DEFAULT 1,
            notify_via_telegram INTEGER DEFAULT 1,
            notify_via_email INTEGER DEFAULT 1,
            telegram_chat_id TEXT,
            notification_email TEXT,
            linkedin_session_cookie TEXT,
            indeed_session_cookie TEXT,
            created_at TEXT,
            updated_at TEXT
        );
    """)
    conn.commit()


def main():
    if is_postgres(DB_PATH):
        print("⚠️  PostgreSQL detected.")
        print("   For production/VPS, create admin via API + direct DB flag.")
        print("   See instructions in the docstring above.")
        print()
        print("   Quick command after registering:")
        print(f"   docker compose exec database psql -U applivo -c \"UPDATE users SET is_superuser=true WHERE email='{ADMIN_EMAIL}';\"")
        sys.exit(0)
    
    now = datetime.now(timezone.utc).isoformat()

    db_file = DB_PATH.replace("sqlite:///", "")
    print(f"📁 Database: {os.path.abspath(db_file)}")

    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row

    ensure_tables(conn)

    existing = conn.execute(
        "SELECT id, is_superuser FROM users WHERE email = ?", (ADMIN_EMAIL,)
    ).fetchone()

    if existing:
        conn.execute(
            "UPDATE users SET is_superuser = 1, is_active = 1, updated_at = ? WHERE email = ?",
            (now, ADMIN_EMAIL)
        )
        conn.commit()
        print(f"✅ Admin already exists — superuser flag confirmed!")
        print(f"   Email:    {ADMIN_EMAIL}")
    else:
        user_id = str(uuid.uuid4())
        profile_id = str(uuid.uuid4())
        hashed = hash_password(ADMIN_PASSWORD)

        conn.execute(
            """INSERT INTO users (
                id, email, hashed_password, full_name, is_active, is_superuser, 
                is_deleted, is_verified, created_at, updated_at
               ) VALUES (?, ?, ?, ?, 1, 1, 0, 1, ?, ?)""",
            (user_id, ADMIN_EMAIL, hashed, ADMIN_NAME, now, now)
        )
        conn.execute(
            """INSERT INTO user_profiles (
                id, user_id, experience_level, desired_roles, desired_locations,
                open_to_remote, open_to_hybrid, min_salary, preferred_company_size,
                preferred_industries, avoid_companies, education, work_experience,
                projects, certifications, awards, publications, auto_apply_enabled,
                auto_apply_threshold, auto_apply_daily_limit, require_apply_approval,
                notify_new_jobs, notify_applications, notify_interviews,
                notify_via_telegram, notify_via_email, created_at, updated_at
               ) VALUES (
                ?, ?, 'entry', '[]', '[]',
                1, 1, 0, '[]',
                '[]', '[]', '[]', '[]',
                '[]', '[]', '[]', '[]', 0,
                75, 10, 1,
                1, 1, 1,
                1, 1, ?, ?
               )""",
            (profile_id, user_id, now, now)
        )
        conn.commit()

        print(f"✅ Superuser created successfully!")
        print(f"   Email:    {ADMIN_EMAIL}")
        print(f"   Password: ******** (masked for security)")
        print(f"   User ID:  {user_id}")

    conn.close()

    print("\n" + "="*50)
    print("🚀 Now run these commands:")
    print("="*50)
    print()
    print("  Backend: python3 -m uvicorn app.main:app --reload --port 8000")
    print("  Frontend: cd frontend && npm run dev")
    print()
    print("  Open: http://localhost:3000/login")
    print(f"  Email:     {ADMIN_EMAIL}")
    print(f"  Password:  ********")
    print("="*50)


if __name__ == "__main__":
    main()