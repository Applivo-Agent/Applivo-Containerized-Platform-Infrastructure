"""
cleanup_users.py
────────────────
Removes all users except the specified admin.
Uses raw sqlite3 to avoid dependency issues.
"""

import sqlite3
import os

DB_PATH = "applivo.db"
ADMIN_EMAIL = "applivoagent@gmail.com"

def cleanup():
    if not os.path.exists(DB_PATH):
        print(f"❌ ERROR: Database file {DB_PATH} not found!")
        return

    print(f"🧹 Starting cleanup. Keeping only {ADMIN_EMAIL}...")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 1. Get the admin ID
        cursor.execute("SELECT id FROM users WHERE email = ?", (ADMIN_EMAIL,))
        admin_row = cursor.fetchone()
        
        if not admin_row:
            print(f"❌ ERROR: Admin user {ADMIN_EMAIL} not found!")
            return
        
        admin_id = admin_row[0]
        print(f"👤 Found admin: {ADMIN_EMAIL} (ID: {admin_id})")

        # 2. Get list of user IDs to delete
        cursor.execute("SELECT id FROM users WHERE id != ?", (admin_id,))
        user_ids = [row[0] for row in cursor.fetchall()]
        
        if not user_ids:
            print("✨ No other users to remove.")
            return

        print(f"🗑️ Deleting {len(user_ids)} users and their related data...")

        # 3. Delete from related tables (Manual cascade)
        tables = [
            "user_profiles", "resumes", "applications", "user_skills", 
            "user_sessions", "credential_vaults", "user_consents", 
            "subscriptions", "payments", "platform_cookies", "notifications",
            "job_analyses", "job_searches", "cover_letters", "interviews",
            "audit_logs", "chat_messages", "chat_usages"
        ]
        
        for table in tables:
            try:
                # Check if table exists
                cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
                if cursor.fetchone():
                    cursor.execute(f"DELETE FROM {table} WHERE user_id != ?", (admin_id,))
                    print(f"  - Cleaned {table}")
            except sqlite3.OperationalError as e:
                # Some tables might use different FK names or not exist
                pass

        # 4. Final step: delete from users table
        cursor.execute("DELETE FROM users WHERE id != ?", (admin_id,))
        
        conn.commit()
        print(f"✅ Cleanup complete. Removed {len(user_ids)} users.")
        
    except Exception as e:
        print(f"❌ ERROR: Cleanup failed: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    cleanup()
