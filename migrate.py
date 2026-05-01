import sqlite3
import psycopg2
import os

sqlite_conn = sqlite3.connect('/app/applivo.db')
sqlite_conn.row_factory = sqlite3.Row
cur = sqlite_conn.cursor()

# Use DATABASE_URL_SYNC from environment, fallback for development
db_url = os.environ.get('DATABASE_URL_SYNC', 'postgresql://applivo:changeme@database:5432/applivo')
pg_conn = psycopg2.connect(db_url)
pg_cur = pg_conn.cursor()

# Migrate users
print('Migrating users...')
users = cur.execute('SELECT * FROM users WHERE is_active = 1').fetchall()
for u in users:
    d = dict(u)
    pg_cur.execute('''INSERT INTO users (id, email, hashed_password, full_name, is_active, is_superuser, is_deleted, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (email) DO NOTHING''',
        (d['id'], d['email'], d['hashed_password'], d['full_name'], bool(d['is_active']), bool(d['is_superuser']), bool(d.get('is_deleted', False)), d['created_at'], d['updated_at']))
print(f'  Migrated {len(users)} users')

# Migrate jobs
print('Migrating jobs...')
jobs = cur.execute('SELECT * FROM jobs').fetchall()
migrated = 0
for j in jobs:
    d = dict(j)
    exp = d.get('experience_level', 'ENTRY')
    exp = exp.upper() if exp.upper() in ['ENTRY', 'MID', 'SENIOR'] else 'ENTRY'
    is_active = bool(d.get('is_active', True))
    easy_apply = bool(d.get('easy_apply', False))
    applicant_count = d.get('applicant_count')
    if applicant_count is not None:
        applicant_count = int(applicant_count)
    pg_cur.execute('''INSERT INTO jobs (id, source, source_job_id, source_url, raw_html, title, company_name, company_logo_url, company_website, description_raw, description_clean, location, country, city, work_mode, job_type, experience_level, salary_min, salary_max, salary_currency, salary_period, posted_at, expires_at, scraped_at, status, is_active, applicant_count, easy_apply, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING''',
        (d.get('id'), d['source'], d['source_job_id'], d['source_url'], d.get('raw_html'), d['title'], d['company_name'], d.get('company_logo_url'), d.get('company_website'), d.get('description_raw'), d.get('description_clean'), d.get('location'), d.get('country'), d.get('city'), d.get('work_mode'), d.get('job_type'), exp, d.get('salary_min'), d.get('salary_max'), d.get('salary_currency'), d.get('salary_period'), d.get('posted_at'), d.get('expires_at'), d.get('scraped_at'), d.get('status'), is_active, applicant_count, easy_apply, d.get('created_at'), d.get('updated_at')))
    migrated += 1
print(f'  Migrated {migrated} jobs')

# Migrate applications - with id
print('Migrating applications...')
apps = cur.execute('SELECT * FROM applications').fetchall()
migrated = 0
for a in apps:
    d = dict(a)
    status = d.get('status', 'QUEUED')
    status_map = {
        'SKIPPED': 'FAILED',
        'QUEUED': 'QUEUED',
        'APPLYING': 'APPLYING',
        'APPLIED': 'APPLIED',
        'SHORTLISTED': 'SHORTLISTED',
        'REJECTED': 'REJECTED',
        'FAILED': 'FAILED',
    }
    status = status_map.get(status.upper(), 'QUEUED')
    method = 'MANUAL'  # Use MANUAL instead of WEBSITE
    app_id = d.get('id')
    if not app_id:
        continue
    pg_cur.execute('''INSERT INTO applications (id, user_id, job_id, resume_id, cover_letter_id, status, method, applied_at, job_title_snapshot, company_snapshot, follow_up_status, follow_up_count, retry_count, is_starred, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING''',
        (app_id, d.get('user_id'), d.get('job_id'), d.get('resume_id'), d.get('cover_letter_id'), status, method, d.get('applied_at'), d.get('job_title_snapshot'), d.get('company_snapshot'), 'PENDING', 0, d.get('retry_count', 0), False, d.get('created_at'), d.get('updated_at')))
    migrated += 1
print(f'  Migrated {migrated} applications')

pg_conn.commit()

# Verify
pg_cur.execute('SELECT COUNT(*) FROM users')
print(f'PostgreSQL users: {pg_cur.fetchone()[0]}')
pg_cur.execute('SELECT COUNT(*) FROM jobs')
print(f'PostgreSQL jobs: {pg_cur.fetchone()[0]}')
pg_cur.execute('SELECT COUNT(*) FROM applications')
print(f'PostgreSQL applications: {pg_cur.fetchone()[0]}')

sqlite_conn.close()
pg_conn.close()
print('Migration complete!')