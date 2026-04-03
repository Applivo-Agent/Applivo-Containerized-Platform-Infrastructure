"""
create_superuser.py
───────────────────
Standalone script — directly writes to SQLite without importing app models.
Works on Python 3.9+.

Usage: python3 create_superuser.py
"""
import sqlite3
import uuid
import os
from datetime import datetime, timezone

# ── Config ──────────────────────────────────────────────────
DB_PATH        = "./applivo.db"
ADMIN_EMAIL    = "admin@applivo.com"
ADMIN_PASSWORD = "Admin@1234"
ADMIN_NAME     = "Super Admin"
# ────────────────────────────────────────────────────────────

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
    now = datetime.now(timezone.utc).isoformat()

    print(f"📁 Database: {os.path.abspath(DB_PATH)}")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    ensure_tables(conn)

    # Check if admin exists
    existing = conn.execute(
        "SELECT id, is_superuser FROM users WHERE email = ?", (ADMIN_EMAIL,)
    ).fetchone()

    if existing:
        # Update superuser flag
        conn.execute(
            "UPDATE users SET is_superuser = 1, is_active = 1, updated_at = ? WHERE email = ?",
            (now, ADMIN_EMAIL)
        )
        conn.commit()
        print(f"✅ Admin already exists — superuser flag confirmed!")
        print(f"   Email:    {ADMIN_EMAIL}")
        print(f"   Password: {ADMIN_PASSWORD}")
    else:
        user_id = str(uuid.uuid4())
        profile_id = str(uuid.uuid4())
        hashed = hash_password(ADMIN_PASSWORD)

        conn.execute(
            """INSERT INTO users (id, email, hashed_password, full_name, is_active, is_superuser, created_at, updated_at)
               VALUES (?, ?, ?, ?, 1, 1, ?, ?)""",
            (user_id, ADMIN_EMAIL, hashed, ADMIN_NAME, now, now)
        )
        conn.execute(
            """INSERT INTO user_profiles (id, user_id, created_at, updated_at)
               VALUES (?, ?, ?, ?)""",
            (profile_id, user_id, now, now)
        )
        conn.commit()

        print(f"✅ Superuser created successfully!")
        print(f"   Email:    {ADMIN_EMAIL}")
        print(f"   Password: {ADMIN_PASSWORD}")
        print(f"   User ID:  {user_id}")

    conn.close()

    print("\n" + "="*50)
    print("🚀 Now run these 2 commands in separate terminals:")
    print("="*50)
    print()
    print("  TERMINAL 1 — Backend:")
    print("  PATH=$PATH:$HOME/Library/Python/3.9/bin python3 -m uvicorn app.main:app --reload --port 8000")
    print()
    print("  TERMINAL 2 — Frontend:")
    print("  cd frontend && npm run dev")
    print()
    print("  Then open: http://localhost:3000/login")
    print(f"  Email:     {ADMIN_EMAIL}")
    print(f"  Password:  {ADMIN_PASSWORD}")
    print("="*50)

if __name__ == "__main__":
    main()
