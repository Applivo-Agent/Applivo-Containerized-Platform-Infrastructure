.dbconfig defensive off
BEGIN;
PRAGMA writable_schema = on;
PRAGMA foreign_keys = off;
PRAGMA encoding = 'UTF-8';
PRAGMA page_size = '4096';
PRAGMA auto_vacuum = '0';
PRAGMA user_version = '0';
PRAGMA application_id = '0';
CREATE TABLE users (
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
CREATE TABLE user_profiles (
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
CREATE TABLE user_skills (
	user_id VARCHAR(36) NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	category VARCHAR(50), 
	proficiency VARCHAR(20), 
	years_experience FLOAT, 
	is_primary BOOLEAN NOT NULL, 
	id VARCHAR(36) NOT NULL, 
	created_at DATETIME DEFAULT (CURRENT_TIMESTAMP) NOT NULL, 
	updated_at DATETIME DEFAULT (CURRENT_TIMESTAMP) NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_user_skill UNIQUE (user_id, name), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);
CREATE TABLE resumes (
	user_id VARCHAR(36) NOT NULL, 
	name VARCHAR(255) NOT NULL, 
	version INTEGER NOT NULL, 
	resume_type VARCHAR(12) NOT NULL, 
	role_category VARCHAR(100), 
	content_json JSON, 
	content_markdown TEXT, 
	file_path VARCHAR(1000), 
	file_size_bytes INTEGER, 
	ats_score FLOAT, 
	keyword_coverage FLOAT, 
	times_used INTEGER NOT NULL, 
	response_count INTEGER NOT NULL, 
	response_rate FLOAT, 
	target_job_id VARCHAR(36), 
	keywords_injected JSON NOT NULL, 
	is_active BOOLEAN NOT NULL, 
	is_default BOOLEAN NOT NULL, 
	id VARCHAR(36) NOT NULL, 
	created_at DATETIME DEFAULT (CURRENT_TIMESTAMP) NOT NULL, 
	updated_at DATETIME DEFAULT (CURRENT_TIMESTAMP) NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);
CREATE TABLE recruiters (
	user_id VARCHAR(36) NOT NULL, 
	name VARCHAR(255) NOT NULL, 
	email VARCHAR(255), 
	linkedin_url VARCHAR(500), 
	company VARCHAR(255), 
	title VARCHAR(255), 
	interest_level VARCHAR(20), 
	last_contact_at DATETIME, 
	next_follow_up_at DATETIME, 
	notes TEXT, 
	id VARCHAR(36) NOT NULL, 
	created_at DATETIME DEFAULT (CURRENT_TIMESTAMP) NOT NULL, 
	updated_at DATETIME DEFAULT (CURRENT_TIMESTAMP) NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);
CREATE TABLE notifications (
	user_id VARCHAR(36) NOT NULL, 
	channel VARCHAR(8) NOT NULL, 
	status VARCHAR(7) NOT NULL, 
	title VARCHAR(500) NOT NULL, 
	body TEXT NOT NULL, 
	data JSON, 
	event_type VARCHAR(100), 
	telegram_message_id VARCHAR(50), 
	telegram_reply_markup JSON, 
	sent_at DATETIME, 
	read_at DATETIME, 
	error_message TEXT, 
	id VARCHAR(36) NOT NULL, 
	created_at DATETIME DEFAULT (CURRENT_TIMESTAMP) NOT NULL, 
	updated_at DATETIME DEFAULT (CURRENT_TIMESTAMP) NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);
CREATE TABLE agent_tasks (
	task_type VARCHAR(21) NOT NULL, 
	status VARCHAR(9) NOT NULL, 
	celery_task_id VARCHAR(100), 
	payload JSON, 
	result JSON, 
	error TEXT, 
	scheduled_at DATETIME, 
	started_at DATETIME, 
	completed_at DATETIME, 
	duration_ms INTEGER, 
	retry_count INTEGER NOT NULL, 
	max_retries INTEGER NOT NULL, 
	related_job_id VARCHAR(36), 
	related_application_id VARCHAR(36), 
	triggered_by VARCHAR(50) NOT NULL, 
	id VARCHAR(36) NOT NULL, 
	created_at DATETIME DEFAULT (CURRENT_TIMESTAMP) NOT NULL, 
	updated_at DATETIME DEFAULT (CURRENT_TIMESTAMP) NOT NULL, user_id TEXT, 
	PRIMARY KEY (id), 
	UNIQUE (celery_task_id)
);
CREATE TABLE skill_gaps (
	user_id VARCHAR(36) NOT NULL, 
	skill_name VARCHAR(100) NOT NULL, 
	category VARCHAR(50), 
	demand_count INTEGER NOT NULL, 
	demand_percentage FLOAT, 
	priority VARCHAR(20) NOT NULL, 
	user_has_skill BOOLEAN NOT NULL, 
	user_proficiency VARCHAR(20), 
	learning_plan_generated BOOLEAN NOT NULL, 
	resolved BOOLEAN NOT NULL, 
	id VARCHAR(36) NOT NULL, 
	created_at DATETIME DEFAULT (CURRENT_TIMESTAMP) NOT NULL, 
	updated_at DATETIME DEFAULT (CURRENT_TIMESTAMP) NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);
CREATE TABLE market_snapshots (
	snapshot_date DATETIME NOT NULL, 
	total_jobs_scraped INTEGER NOT NULL, 
	total_jobs_analyzed INTEGER NOT NULL, 
	top_skills JSON NOT NULL, 
	top_companies_hiring JSON NOT NULL, 
	emerging_roles JSON NOT NULL, 
	salary_data JSON, 
	by_source JSON, 
	by_location JSON, 
	by_work_mode JSON, 
	id VARCHAR(36) NOT NULL, 
	created_at DATETIME DEFAULT (CURRENT_TIMESTAMP) NOT NULL, 
	updated_at DATETIME DEFAULT (CURRENT_TIMESTAMP) NOT NULL, 
	PRIMARY KEY (id)
);
CREATE TABLE learning_plans (
	user_id VARCHAR(36) NOT NULL, 
	title VARCHAR(255) NOT NULL, 
	target_role VARCHAR(255), 
	total_weeks INTEGER NOT NULL, 
	weekly_plans JSON NOT NULL, 
	skills_addressed JSON NOT NULL, 
	is_active BOOLEAN NOT NULL, 
	progress_percentage FLOAT NOT NULL, 
	id VARCHAR(36) NOT NULL, 
	created_at DATETIME DEFAULT (CURRENT_TIMESTAMP) NOT NULL, 
	updated_at DATETIME DEFAULT (CURRENT_TIMESTAMP) NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);
CREATE TABLE generated_projects (
	user_id VARCHAR(36) NOT NULL, 
	skill_gap_id VARCHAR(36), 
	title VARCHAR(255) NOT NULL, 
	description TEXT NOT NULL, 
	tech_stack JSON NOT NULL, 
	difficulty VARCHAR(20) NOT NULL, 
	github_structure JSON, 
	readme_content TEXT, 
	starter_code TEXT, 
	github_repo_url VARCHAR(500), 
	status VARCHAR(30) NOT NULL, 
	id VARCHAR(36) NOT NULL, 
	created_at DATETIME DEFAULT (CURRENT_TIMESTAMP) NOT NULL, 
	updated_at DATETIME DEFAULT (CURRENT_TIMESTAMP) NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);
CREATE TABLE credential_vaults (
	user_id VARCHAR(36) NOT NULL, 
	credential_type VARCHAR(50) NOT NULL, 
	display_name VARCHAR(255) NOT NULL, 
	is_active BOOLEAN NOT NULL, 
	encrypted_data TEXT NOT NULL, 
	consent_given BOOLEAN NOT NULL, 
	consent_timestamp DATETIME, 
	consent_purpose VARCHAR(500) NOT NULL, 
	last_used_at DATETIME, 
	use_count INTEGER NOT NULL, 
	expires_at DATETIME, 
	scope VARCHAR(1000), 
	id VARCHAR(36) NOT NULL, 
	created_at DATETIME DEFAULT (CURRENT_TIMESTAMP) NOT NULL, 
	updated_at DATETIME DEFAULT (CURRENT_TIMESTAMP) NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);
CREATE TABLE user_consents (
	user_id VARCHAR(36) NOT NULL, 
	consent_type VARCHAR(50) NOT NULL, 
	scope VARCHAR(50) NOT NULL, 
	granted BOOLEAN NOT NULL, 
	revoked DATETIME, 
	granted_at DATETIME, 
	ip_address VARCHAR(45), 
	user_agent TEXT, 
	policy_version VARCHAR(20) NOT NULL, 
	purpose VARCHAR(500) NOT NULL, 
	data_categories JSON, 
	extra_data JSON, 
	id VARCHAR(36) NOT NULL, 
	created_at DATETIME DEFAULT (CURRENT_TIMESTAMP) NOT NULL, 
	updated_at DATETIME DEFAULT (CURRENT_TIMESTAMP) NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);
CREATE TABLE consent_versions (
	version VARCHAR(20) NOT NULL, 
	effective_from DATETIME NOT NULL, 
	consent_requirements JSON NOT NULL, 
	changes TEXT, 
	id VARCHAR(36) NOT NULL, 
	created_at DATETIME DEFAULT (CURRENT_TIMESTAMP) NOT NULL, 
	updated_at DATETIME DEFAULT (CURRENT_TIMESTAMP) NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (version)
);
CREATE TABLE audit_logs (
	user_id VARCHAR(36), 
	user_email VARCHAR(255), 
	action VARCHAR(100) NOT NULL, 
	resource_type VARCHAR(50) NOT NULL, 
	resource_id VARCHAR(36), 
	ip_address VARCHAR(45), 
	user_agent TEXT, 
	request_method VARCHAR(10), 
	request_path VARCHAR(500), 
	request_id VARCHAR(36), 
	details JSON, 
	changes JSON, 
	success BOOLEAN NOT NULL, 
	error_code VARCHAR(50), 
	error_message TEXT, 
	timestamp DATETIME NOT NULL, 
	id VARCHAR(36) NOT NULL, 
	PRIMARY KEY (id)
);
CREATE TABLE subscriptions (
	user_id VARCHAR(36) NOT NULL, 
	"plan" VARCHAR(7) NOT NULL, 
	status VARCHAR(9) NOT NULL, 
	start_date DATETIME NOT NULL, 
	end_date DATETIME, 
	razorpay_subscription_id VARCHAR(255), 
	id VARCHAR(36) NOT NULL, 
	created_at DATETIME DEFAULT (CURRENT_TIMESTAMP) NOT NULL, 
	updated_at DATETIME DEFAULT (CURRENT_TIMESTAMP) NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);
CREATE TABLE platform_cookies (
	user_id VARCHAR(36) NOT NULL, 
	platform VARCHAR(50) NOT NULL, 
	encrypted_cookies TEXT NOT NULL, 
	is_valid BOOLEAN NOT NULL, 
	expires_at DATETIME, 
	last_validated_at DATETIME, 
	last_used_at DATETIME, 
	id VARCHAR(36) NOT NULL, 
	created_at DATETIME DEFAULT (CURRENT_TIMESTAMP) NOT NULL, 
	updated_at DATETIME DEFAULT (CURRENT_TIMESTAMP) NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);
CREATE TABLE job_analyses (
	job_id VARCHAR(36) NOT NULL, 
	required_skills JSON NOT NULL, 
	preferred_skills JSON NOT NULL, 
	tech_stack JSON NOT NULL, 
	ats_keywords JSON NOT NULL, 
	min_years_experience FLOAT, 
	max_years_experience FLOAT, 
	education_requirement VARCHAR(100), 
	key_responsibilities JSON NOT NULL, 
	role_category VARCHAR(100), 
	seniority_detected VARCHAR(50), 
	is_internship BOOLEAN NOT NULL, 
	match_score FLOAT, 
	skill_match_score FLOAT, 
	experience_match_score FLOAT, 
	semantic_similarity_score FLOAT, 
	matching_skills JSON NOT NULL, 
	missing_skills JSON NOT NULL, 
	skill_gap_count INTEGER NOT NULL, 
	estimated_applicants INTEGER, 
	competition_level VARCHAR(20), 
	interview_probability FLOAT, 
	job_difficulty VARCHAR(20), 
	priority_score FLOAT, 
	estimated_salary_min INTEGER, 
	estimated_salary_max INTEGER, 
	ai_summary TEXT, 
	ai_recommendation TEXT, 
	model_used VARCHAR(50), 
	tokens_used INTEGER, 
	processing_time_ms INTEGER, 
	id VARCHAR(36) NOT NULL, 
	created_at DATETIME DEFAULT (CURRENT_TIMESTAMP) NOT NULL, 
	updated_at DATETIME DEFAULT (CURRENT_TIMESTAMP) NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(job_id) REFERENCES jobs (id)
);
CREATE TABLE applications (
	user_id VARCHAR(36) NOT NULL, 
	job_id VARCHAR(36) NOT NULL, 
	resume_id VARCHAR(36), 
	cover_letter_id VARCHAR(36), 
	status VARCHAR(19) NOT NULL, 
	method VARCHAR(10) NOT NULL, 
	applied_at DATETIME, 
	viewed_at DATETIME, 
	shortlisted_at DATETIME, 
	interview_scheduled_at DATETIME, 
	offer_received_at DATETIME, 
	rejected_at DATETIME, 
	match_score_at_apply FLOAT, 
	job_title_snapshot VARCHAR(500), 
	company_snapshot VARCHAR(255), 
	recruiter_id VARCHAR(36), 
	recruiter_name VARCHAR(255), 
	recruiter_email VARCHAR(255), 
	recruiter_linkedin VARCHAR(500), 
	follow_up_status VARCHAR(9) NOT NULL, 
	follow_up_date DATETIME, 
	follow_up_count INTEGER NOT NULL, 
	last_follow_up_at DATETIME, 
	interview_date DATETIME, 
	interview_type VARCHAR(50), 
	interview_notes TEXT, 
	interview_feedback TEXT, 
	offer_salary INTEGER, 
	offer_details JSON, 
	bot_session_id VARCHAR(100), 
	bot_error TEXT, 
	bot_screenshot_path VARCHAR(1000), 
	retry_count INTEGER NOT NULL, 
	notes TEXT, 
	is_starred BOOLEAN NOT NULL, 
	id VARCHAR(36) NOT NULL, 
	created_at DATETIME DEFAULT (CURRENT_TIMESTAMP) NOT NULL, 
	updated_at DATETIME DEFAULT (CURRENT_TIMESTAMP) NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id), 
	FOREIGN KEY(job_id) REFERENCES jobs (id), 
	FOREIGN KEY(resume_id) REFERENCES resumes (id)
);
CREATE TABLE recruiter_messages (
	recruiter_id VARCHAR(36) NOT NULL, 
	direction VARCHAR(10) NOT NULL, 
	channel VARCHAR(20) NOT NULL, 
	subject VARCHAR(500), 
	body TEXT NOT NULL, 
	sent_at DATETIME, 
	id VARCHAR(36) NOT NULL, 
	created_at DATETIME DEFAULT (CURRENT_TIMESTAMP) NOT NULL, 
	updated_at DATETIME DEFAULT (CURRENT_TIMESTAMP) NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(recruiter_id) REFERENCES recruiters (id)
);
CREATE TABLE credential_use_logs (
	credential_id VARCHAR(36) NOT NULL, 
	user_id VARCHAR(36) NOT NULL, 
	action VARCHAR(100) NOT NULL, 
	ip_address VARCHAR(45), 
	user_agent TEXT, 
	success BOOLEAN NOT NULL, 
	error_message TEXT, 
	id VARCHAR(36) NOT NULL, 
	created_at DATETIME DEFAULT (CURRENT_TIMESTAMP) NOT NULL, 
	updated_at DATETIME DEFAULT (CURRENT_TIMESTAMP) NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(credential_id) REFERENCES credential_vaults (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);
CREATE TABLE payments (
	user_id VARCHAR(36) NOT NULL, 
	subscription_id VARCHAR(36), 
	amount INTEGER NOT NULL, 
	currency VARCHAR(10) NOT NULL, 
	status VARCHAR(10) NOT NULL, 
	razorpay_order_id VARCHAR(255), 
	razorpay_payment_id VARCHAR(255), 
	razorpay_signature VARCHAR(500), 
	"plan" VARCHAR(50), 
	id VARCHAR(36) NOT NULL, 
	created_at DATETIME DEFAULT (CURRENT_TIMESTAMP) NOT NULL, 
	updated_at DATETIME DEFAULT (CURRENT_TIMESTAMP) NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id), 
	FOREIGN KEY(subscription_id) REFERENCES subscriptions (id)
);
CREATE TABLE cover_letters (
	user_id VARCHAR(36) NOT NULL, 
	job_id VARCHAR(36), 
	application_id VARCHAR(36), 
	content TEXT NOT NULL, 
	tone VARCHAR(50) NOT NULL, 
	target_company VARCHAR(255), 
	target_role VARCHAR(255), 
	highlighted_skills JSON NOT NULL, 
	file_path VARCHAR(1000), 
	model_used VARCHAR(50), 
	tokens_used INTEGER, 
	word_count INTEGER, 
	id VARCHAR(36) NOT NULL, 
	created_at DATETIME DEFAULT (CURRENT_TIMESTAMP) NOT NULL, 
	updated_at DATETIME DEFAULT (CURRENT_TIMESTAMP) NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id), 
	FOREIGN KEY(job_id) REFERENCES jobs (id), 
	FOREIGN KEY(application_id) REFERENCES applications (id)
);
CREATE TABLE application_events (
	application_id VARCHAR(36) NOT NULL, 
	event_type VARCHAR(100) NOT NULL, 
	from_status VARCHAR(50), 
	to_status VARCHAR(50), 
	triggered_by VARCHAR(50) NOT NULL, 
	details JSON, 
	id VARCHAR(36) NOT NULL, 
	created_at DATETIME DEFAULT (CURRENT_TIMESTAMP) NOT NULL, 
	updated_at DATETIME DEFAULT (CURRENT_TIMESTAMP) NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(application_id) REFERENCES applications (id)
);
CREATE TABLE interviews (
	application_id VARCHAR(36) NOT NULL, 
	user_id VARCHAR(36) NOT NULL, 
	interview_type VARCHAR(13) NOT NULL, 
	scheduled_at DATETIME, 
	duration_minutes INTEGER, 
	platform VARCHAR(100), 
	meeting_link VARCHAR(2000), 
	company_report JSON, 
	technical_questions JSON NOT NULL, 
	behavioral_questions JSON NOT NULL, 
	study_topics JSON NOT NULL, 
	completed_at DATETIME, 
	outcome VARCHAR(50), 
	user_notes TEXT, 
	ai_feedback TEXT, 
	id VARCHAR(36) NOT NULL, 
	created_at DATETIME DEFAULT (CURRENT_TIMESTAMP) NOT NULL, 
	updated_at DATETIME DEFAULT (CURRENT_TIMESTAMP) NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(application_id) REFERENCES applications (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);
CREATE TABLE mock_interview_sessions (
	interview_id VARCHAR(36) NOT NULL, 
	user_id VARCHAR(36) NOT NULL, 
	transcript JSON NOT NULL, 
	duration_seconds INTEGER, 
	overall_score FLOAT, 
	technical_depth_score FLOAT, 
	communication_score FLOAT, 
	confidence_score FLOAT, 
	improvement_suggestions JSON NOT NULL, 
	recording_path VARCHAR(1000), 
	transcription TEXT, 
	filler_word_count INTEGER, 
	filler_words_detected JSON NOT NULL, 
	speech_pace_wpm FLOAT, 
	id VARCHAR(36) NOT NULL, 
	created_at DATETIME DEFAULT (CURRENT_TIMESTAMP) NOT NULL, 
	updated_at DATETIME DEFAULT (CURRENT_TIMESTAMP) NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(interview_id) REFERENCES interviews (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);
CREATE TABLE lost_and_found(rootpgno INTEGER, pgno INTEGER, nfield INTEGER, id INTEGER, c0, c1);
CREATE TABLE user_sessions (
	user_id VARCHAR(36) NOT NULL, 
	device_id VARCHAR(255) NOT NULL, 
	device_name VARCHAR(255), 
	device_type VARCHAR(50), 
	browser VARCHAR(100), 
	os VARCHAR(100), 
	ip_address VARCHAR(45), 
	location VARCHAR(255), 
	user_agent TEXT, 
	refresh_token_hash VARCHAR(255), 
	refresh_token_expires_at DATETIME, 
	access_token_jti VARCHAR(255), 
	last_used_at DATETIME, 
	is_current BOOLEAN NOT NULL, 
	is_active BOOLEAN NOT NULL, 
	id VARCHAR(36) NOT NULL, 
	created_at DATETIME DEFAULT (CURRENT_TIMESTAMP) NOT NULL, 
	updated_at DATETIME DEFAULT (CURRENT_TIMESTAMP) NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_user_device_session UNIQUE (user_id, device_id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);
CREATE UNIQUE INDEX ix_job_analyses_job_id ON job_analyses (job_id);
INSERT OR IGNORE INTO 'users'(_rowid_, 'id', 'email', 'hashed_password', 'full_name', 'is_active', 'is_superuser', 'is_deleted', 'deleted_at', 'last_login_at', 'created_at', 'updated_at') VALUES (1, '186abe6d-ed82-4ac6-882e-9d0acb5f3192', 'admin@applivo.com', '$2b$12$qKtKoPuIH4h/6s6.H0f8Oe6WN3c3GBwA6xiYyCuXFoqe3TB57TpWq', 'Super Admin', 1, 1, 0, NULL, '2026-04-15 16:55:09.933870', '2026-04-03T13:03:19.893725+00:00', '2026-04-15 16:55:09.939385');
INSERT OR IGNORE INTO 'users'(_rowid_, 'id', 'email', 'hashed_password', 'full_name', 'is_active', 'is_superuser', 'is_deleted', 'deleted_at', 'last_login_at', 'created_at', 'updated_at') VALUES (2, '364c6ba3-8669-4f9a-bd50-577322459d4d', 'user@applivo.com', '$2b$12$acJsYOgDApUknfA4sp4RuOAQoQcMfu01RDmmKV8KNiy4H6b4OmE4O', 'Test User', 1, 0, 0, NULL, '2026-04-05 04:38:23.996727', '2026-04-03 15:31:32.280181', '2026-04-05 04:38:24.015475');
INSERT OR IGNORE INTO 'users'(_rowid_, 'id', 'email', 'hashed_password', 'full_name', 'is_active', 'is_superuser', 'is_deleted', 'deleted_at', 'last_login_at', 'created_at', 'updated_at') VALUES (3, '97b1df0e-5487-40a0-9e70-eddd1f3c67aa', 'dhruvxpnt@gmail.com', '$2b$12$XjmGBHPQSt5dMZhbxW/h0.FqqCaDn/9F/Orj8hhc00npnnemHKSO6', 'dhruvx', 1, 0, 0, NULL, '2026-04-04 13:27:00.564853', '2026-04-04 13:20:11.781578', '2026-04-04 13:27:00.571581');
INSERT OR IGNORE INTO 'users'(_rowid_, 'id', 'email', 'hashed_password', 'full_name', 'is_active', 'is_superuser', 'is_deleted', 'deleted_at', 'last_login_at', 'created_at', 'updated_at') VALUES (4, 'cee75610-ee7e-49bf-878b-eeef72650576', 'sudhu@gmail.com', '$2b$12$/CuPnyIp5R3MPBXkKfPiKO1sfBKrE5blkNW6q5810FRCkLaL5zUS.', 'sudharsan', 1, 0, 0, NULL, '2026-04-04 16:07:42.866602', '2026-04-04 13:28:26.725782', '2026-04-04 16:07:42.879997');
INSERT OR IGNORE INTO 'users'(_rowid_, 'id', 'email', 'hashed_password', 'full_name', 'is_active', 'is_superuser', 'is_deleted', 'deleted_at', 'last_login_at', 'created_at', 'updated_at') VALUES (5, 'fecf1cde-739e-4c99-82ea-db6915e226fe', 'ss0856@srmist.edu.in', '$2b$12$NzWExEk/ozd6g3/orfQSp.Xy1BbIHoooAWD0SImRJy0YUMwsBW5Wy', 'sudharsan', 1, 0, 0, NULL, '2026-04-15 14:53:04.101322', '2026-04-04 13:39:54.958919', '2026-04-15 14:53:04.109085');
INSERT OR IGNORE INTO 'users'(_rowid_, 'id', 'email', 'hashed_password', 'full_name', 'is_active', 'is_superuser', 'is_deleted', 'deleted_at', 'last_login_at', 'created_at', 'updated_at') VALUES (6, '8cafcc85-c0e5-4c75-af1f-b1f40a94866b', 'newadmin@test.com', '$2b$12$PaZvASoQNlzn//dpgGBL..6DoQUlzHOaWXf8lbb/5yjGiYIQdlYXy', 'New Admin', 1, 1, 0, NULL, NULL, '2026-04-05 12:41:00', '2026-04-05 12:41:00');
INSERT OR IGNORE INTO 'user_profiles'(_rowid_, 'id', 'user_id', 'phone', 'location', 'linkedin_url', 'github_url', 'portfolio_url', 'experience_level', 'desired_roles', 'desired_locations', 'open_to_remote', 'open_to_hybrid', 'min_salary', 'preferred_company_size', 'preferred_industries', 'avoid_companies', 'professional_summary', 'career_goals', 'unique_value_proposition', 'education', 'work_experience', 'projects', 'certifications', 'awards', 'publications', 'auto_apply_enabled', 'auto_apply_threshold', 'auto_apply_daily_limit', 'require_apply_approval', 'notify_new_jobs', 'notify_applications', 'notify_interviews', 'notify_via_telegram', 'notify_via_email', 'telegram_chat_id', 'notification_email', 'linkedin_session_cookie', 'indeed_session_cookie', 'created_at', 'updated_at') VALUES (1, '46f83bf2-d8fd-4989-91a3-32e9837aecba', '186abe6d-ed82-4ac6-882e-9d0acb5f3192', '9751120169', 'dindigul ', '', '', '', 'entry', '["ml engineer"]', '["remote"]', 1, 1, 0, '[]', '[]', '[]', 'ml', 'ml', replace('ml\n','\n', char(10)), '[{"degree": "b.tech cse ", "field": "cse", "institution": "srm", "year": null, "gpa": 9.3, "description": null}]', '[]', '[]', '[]', '[]', '[]', 1, 19, 10, 1, 1, 1, 1, 1, 1, '', '', NULL, NULL, '2026-04-03T13:03:19.893725+00:00', '2026-04-08 09:15:37.523939');
INSERT OR IGNORE INTO 'user_profiles'(_rowid_, 'id', 'user_id', 'phone', 'location', 'linkedin_url', 'github_url', 'portfolio_url', 'experience_level', 'desired_roles', 'desired_locations', 'open_to_remote', 'open_to_hybrid', 'min_salary', 'preferred_company_size', 'preferred_industries', 'avoid_companies', 'professional_summary', 'career_goals', 'unique_value_proposition', 'education', 'work_experience', 'projects', 'certifications', 'awards', 'publications', 'auto_apply_enabled', 'auto_apply_threshold', 'auto_apply_daily_limit', 'require_apply_approval', 'notify_new_jobs', 'notify_applications', 'notify_interviews', 'notify_via_telegram', 'notify_via_email', 'telegram_chat_id', 'notification_email', 'linkedin_session_cookie', 'indeed_session_cookie', 'created_at', 'updated_at') VALUES (2, '7ad430ba-3d79-44bc-96d2-3428ed72e52d', '364c6ba3-8669-4f9a-bd50-577322459d4d', '+919999999999', 'Bangalore', NULL, NULL, NULL, 'entry', '["Software Developer", "Machine Learning"]', '["Remote", "Work from home", "Bangalore", "Chennai"]', 1, 1, 0, '[]', '[]', '[]', NULL, NULL, NULL, '[]', '[]', '[]', '[]', '[]', '[]', 1, 50, 5, 1, 1, 1, 1, 1, 1, NULL, NULL, NULL, NULL, '2026-04-03 15:31:32.281470', '2026-04-03 16:20:58.256196');
INSERT OR IGNORE INTO 'user_profiles'(_rowid_, 'id', 'user_id', 'phone', 'location', 'linkedin_url', 'github_url', 'portfolio_url', 'experience_level', 'desired_roles', 'desired_locations', 'open_to_remote', 'open_to_hybrid', 'min_salary', 'preferred_company_size', 'preferred_industries', 'avoid_companies', 'professional_summary', 'career_goals', 'unique_value_proposition', 'education', 'work_experience', 'projects', 'certifications', 'awards', 'publications', 'auto_apply_enabled', 'auto_apply_threshold', 'auto_apply_daily_limit', 'require_apply_approval', 'notify_new_jobs', 'notify_applications', 'notify_interviews', 'notify_via_telegram', 'notify_via_email', 'telegram_chat_id', 'notification_email', 'linkedin_session_cookie', 'indeed_session_cookie', 'created_at', 'updated_at') VALUES (3, 'fbccc07a-d8ae-4e07-9947-ca6852ce5261', '97b1df0e-5487-40a0-9e70-eddd1f3c67aa', NULL, NULL, NULL, NULL, NULL, 'entry', '[]', '[]', 1, 1, 0, '[]', '[]', '[]', NULL, NULL, NULL, '[]', '[]', '[]', '[]', '[]', '[]', 0, 75, 10, 1, 1, 1, 1, 1, 1, NULL, NULL, NULL, NULL, '2026-04-04 13:20:11.782920', '2026-04-04 13:20:11.782923');
INSERT OR IGNORE INTO 'user_profiles'(_rowid_, 'id', 'user_id', 'phone', 'location', 'linkedin_url', 'github_url', 'portfolio_url', 'experience_level', 'desired_roles', 'desired_locations', 'open_to_remote', 'open_to_hybrid', 'min_salary', 'preferred_company_size', 'preferred_industries', 'avoid_companies', 'professional_summary', 'career_goals', 'unique_value_proposition', 'education', 'work_experience', 'projects', 'certifications', 'awards', 'publications', 'auto_apply_enabled', 'auto_apply_threshold', 'auto_apply_daily_limit', 'require_apply_approval', 'notify_new_jobs', 'notify_applications', 'notify_interviews', 'notify_via_telegram', 'notify_via_email', 'telegram_chat_id', 'notification_email', 'linkedin_session_cookie', 'indeed_session_cookie', 'created_at', 'updated_at') VALUES (4, '3d14eafc-708c-45d1-890f-73a03aed5ecc', 'cee75610-ee7e-49bf-878b-eeef72650576', NULL, NULL, NULL, NULL, NULL, 'entry', '[]', '[]', 1, 1, 0, '[]', '[]', '[]', NULL, NULL, NULL, '[]', '[]', '[]', '[]', '[]', '[]', 0, 75, 10, 1, 1, 1, 1, 1, 1, NULL, NULL, NULL, NULL, '2026-04-04 13:28:26.726975', '2026-04-04 13:28:26.726976');
INSERT OR IGNORE INTO 'user_profiles'(_rowid_, 'id', 'user_id', 'phone', 'location', 'linkedin_url', 'github_url', 'portfolio_url', 'experience_level', 'desired_roles', 'desired_locations', 'open_to_remote', 'open_to_hybrid', 'min_salary', 'preferred_company_size', 'preferred_industries', 'avoid_companies', 'professional_summary', 'career_goals', 'unique_value_proposition', 'education', 'work_experience', 'projects', 'certifications', 'awards', 'publications', 'auto_apply_enabled', 'auto_apply_threshold', 'auto_apply_daily_limit', 'require_apply_approval', 'notify_new_jobs', 'notify_applications', 'notify_interviews', 'notify_via_telegram', 'notify_via_email', 'telegram_chat_id', 'notification_email', 'linkedin_session_cookie', 'indeed_session_cookie', 'created_at', 'updated_at') VALUES (5, '9ea0c87e-fbcf-4ede-a9a9-a71444856a96', 'fecf1cde-739e-4c99-82ea-db6915e226fe', NULL, NULL, NULL, NULL, NULL, 'entry', '[]', '[]', 1, 1, 0, '[]', '[]', '[]', NULL, NULL, NULL, '[]', '[]', '[]', '[]', '[]', '[]', 0, 15, 10, 1, 1, 1, 1, 1, 1, NULL, NULL, NULL, NULL, '2026-04-04 13:39:54.960358', '2026-04-12 16:41:26.783807');
INSERT OR IGNORE INTO 'user_skills'(_rowid_, 'user_id', 'name', 'category', 'proficiency', 'years_experience', 'is_primary', 'id', 'created_at', 'updated_at') VALUES (1, '186abe6d-ed82-4ac6-882e-9d0acb5f3192', 'python', 'programming', 'intermediate', 1, 0, '7643a41f-75a1-4f6c-a583-8706613d5827', '2026-04-04 13:47:31.376627', '2026-04-04 13:47:31.376632');
INSERT OR IGNORE INTO 'resumes'(_rowid_, 'user_id', 'name', 'version', 'resume_type', 'role_category', 'content_json', 'content_markdown', 'file_path', 'file_size_bytes', 'ats_score', 'keyword_coverage', 'times_used', 'response_count', 'response_rate', 'target_job_id', 'keywords_injected', 'is_active', 'is_default', 'id', 'created_at', 'updated_at') VALUES (1, '364c6ba3-8669-4f9a-bd50-577322459d4d', 'resume_lawdocs_artificial_intellige', 1, 'TAILORED', 'other', '{"summary": "Ambitious AI/ML student and developer seeking an entry-level role in Artificial Intelligence, eager to apply theoretical knowledge in a practical setting and contribute to innovative projects", "experience_bullets": {}, "project_bullets": {}, "skills_to_highlight": ["Artificial Intelligence", "Machine Learning"], "keywords_injected": ["AI", "ML", "Innovation"], "ats_score_estimate": 60}', NULL, 'resumes/ac54b102-4eec-452b-8cab-0d0ff1438bf0.html', NULL, 60, NULL, 2, 0, NULL, '0cfe99bd-93a4-4623-be1e-ab404329f848', '["AI", "ML", "Innovation"]', 1, 1, 'f1ae23da-b6a9-4ad3-9bd9-9e19b846d2da', '2026-04-04 09:55:38.337170', '2026-04-04 09:56:58.876696');
INSERT OR IGNORE INTO 'resumes'(_rowid_, 'user_id', 'name', 'version', 'resume_type', 'role_category', 'content_json', 'content_markdown', 'file_path', 'file_size_bytes', 'ats_score', 'keyword_coverage', 'times_used', 'response_count', 'response_rate', 'target_job_id', 'keywords_injected', 'is_active', 'is_default', 'id', 'created_at', 'updated_at') VALUES (2, '186abe6d-ed82-4ac6-882e-9d0acb5f3192', 'Sudharsan Resume', 1, 'BASE', NULL, NULL, NULL, 'resumes/095a811a-82c2-4882-8eda-b2aa7625792a.pdf', 81728, NULL, NULL, 23, 0, NULL, NULL, '[]', 1, 1, 'ff2e4b7e-f5af-4e54-9051-48f631937cfa', '2026-04-04 12:18:27.187732', '2026-04-14 16:59:21.673924');
INSERT OR IGNORE INTO 'resumes'(_rowid_, 'user_id', 'name', 'version', 'resume_type', 'role_category', 'content_json', 'content_markdown', 'file_path', 'file_size_bytes', 'ats_score', 'keyword_coverage', 'times_used', 'response_count', 'response_rate', 'target_job_id', 'keywords_injected', 'is_active', 'is_default', 'id', 'created_at', 'updated_at') VALUES (3, 'fecf1cde-739e-4c99-82ea-db6915e226fe', 'Sudharsan Resume', 1, 'BASE', NULL, NULL, NULL, 'resumes/2b4fe5c6-644b-4c67-a490-5c74e4b749cc.pdf', 81728, NULL, NULL, 0, 0, NULL, NULL, '[]', 1, 0, 'cceabfcf-6d1e-4b5f-a909-299e572237f7', '2026-04-04 13:47:39.761381', '2026-04-04 13:47:39.761383');
INSERT OR IGNORE INTO 'notifications'(_rowid_, 'user_id', 'channel', 'status', 'title', 'body', 'data', 'event_type', 'telegram_message_id', 'telegram_reply_markup', 'sent_at', 'read_at', 'error_message', 'id', 'created_at', 'updated_at') VALUES (485, '186abe6d-ed82-4ac6-882e-9d0acb5f3192', 'EMAIL', 'SENT', 'Important message: Mindenious Edutech. Accept our invite to', replace('Subject: Interview Invitation\n\nKeywords: interview, assessment','\n', char(10)), 'null', 'platform_message', NULL, NULL, '2026-04-15 12:23:56.447672', NULL, NULL, 'f69f4fdd-4d62-4b70-8b8e-cd4dd410b960', '2026-04-15 12:23:52.499019', '2026-04-15 12:23:56.448173');
INSERT OR IGNORE INTO 'notifications'(_rowid_, 'user_id', 'channel', 'status', 'title', 'body', 'data', 'event_type', 'telegram_message_id', 'telegram_reply_markup', 'sent_at', 'read_at', 'error_message', 'id', 'created_at', 'updated_at') VALUES (486, '186abe6d-ed82-4ac6-882e-9d0acb5f3192', 'TELEGRAM', 'FAILED', 'Important message: Mindenious Edutech. Accept our invite to', replace('Subject: Assessment / Assignment\n\nKeywords: assignment','\n', char(10)), 'null', 'platform_message', NULL, 'null', NULL, NULL, '{''ok'': False, ''error_code'': 403, ''description'': "Forbidden: bots can''t send messages to bots"}', '8c8bdcc1-4a21-42f9-974e-b34ef8b1312b', '2026-04-15 12:23:56.465244', '2026-04-15 12:23:57.455680');
INSERT OR IGNORE INTO 'notifications'(_rowid_, 'user_id', 'channel', 'status', 'title', 'body', 'data', 'event_type', 'telegram_message_id', 'telegram_reply_markup', 'sent_at', 'read_at', 'error_message', 'id', 'created_at', 'updated_at') VALUES (487, '186abe6d-ed82-4ac6-882e-9d0acb5f3192', 'EMAIL', 'SENT', 'Important message: Mindenious Edutech. Accept our invite to', replace('Subject: Assessment / Assignment\n\nKeywords: assignment','\n', char(10)), 'null', 'platform_message', NULL, NULL, '2026-04-15 12:24:01.190945', NULL, NULL, 'ea13edbc-58bf-4d7a-aa4a-31436890d913', '2026-04-15 12:23:57.456209', '2026-04-15 12:24:01.191964');
INSERT OR IGNORE INTO 'notifications'(_rowid_, 'user_id', 'channel', 'status', 'title', 'body', 'data', 'event_type', 'telegram_message_id', 'telegram_reply_markup', 'sent_at', 'read_at', 'error_message', 'id', 'created_at', 'updated_at') VALUES (488, 'fecf1cde-739e-4c99-82ea-db6915e226fe', 'TELEGRAM', 'FAILED', 'Welcome back, sudharsan! 👋', replace('It''s great to have you here again. New opportunities are waiting, and Applivo is ready to help you apply smarter, prepare better, and move one step closer to your next career milestone.\n\nLet''s get started!','\n', char(10)), 'null', 'user_login', NULL, 'null', NULL, NULL, '{''ok'': False, ''error_code'': 403, ''description'': "Forbidden: bots can''t send messages to bots"}', '2bebfdcc-38ad-44ff-9caf-964e4367d1f3', '2026-04-15 14:04:16.588096', '2026-04-15 14:04:17.889598');
INSERT OR IGNORE INTO 'notifications'(_rowid_, 'user_id', 'channel', 'status', 'title', 'body', 'data', 'event_type', 'telegram_message_id', 'telegram_reply_markup', 'sent_at', 'read_at', 'error_message', 'id', 'created_at', 'updated_at') VALUES (489, 'fecf1cde-739e-4c99-82ea-db6915e226fe', 'EMAIL', 'SENT', 'Welcome back, sudharsan! 👋', replace('It''s great to have you here again. New opportunities are waiting, and Applivo is ready to help you apply smarter, prepare better, and move one step closer to your next career milestone.\n\nLet''s get started!','\n', char(10)), 'null', 'user_login', NULL, NULL, '2026-04-15 14:04:22.575048', NULL, NULL, 'b35665a2-a7da-4440-abd4-a99bec990c2b', '2026-04-15 14:04:17.890182', '2026-04-15 14:04:22.576418');
INSERT OR IGNORE INTO 'notifications'(_rowid_, 'user_id', 'channel', 'status', 'title', 'body', 'data', 'event_type', 'telegram_message_id', 'telegram_reply_markup', 'sent_at', 'read_at', 'error_message', 'id', 'created_at', 'updated_at') VALUES (490, '186abe6d-ed82-4ac6-882e-9d0acb5f3192', 'TELEGRAM', 'FAILED', 'Welcome back, Super! 👋', replace('It''s great to have you here again. New opportunities are waiting, and Applivo is ready to help you apply smarter, prepare better, and move one step closer to your next career milestone.\n\nLet''s get started!','\n', char(10)), 'null', 'user_login', NULL, 'null', NULL, NULL, '{''ok'': False, ''error_code'': 403, ''description'': "Forbidden: bots can''t send messages to bots"}', '09341f65-b3d3-4493-9954-3191ee559830', '2026-04-15 14:53:22.709497', '2026-04-15 14:53:23.905080');
INSERT OR IGNORE INTO 'notifications'(_rowid_, 'user_id', 'channel', 'status', 'title', 'body', 'data', 'event_type', 'telegram_message_id', 'telegram_reply_markup', 'sent_at', 'read_at', 'error_message', 'id', 'created_at', 'updated_at') VALUES (491, '186abe6d-ed82-4ac6-882e-9d0acb5f3192', 'EMAIL', 'SENT', 'Welcome back, Super! 👋', replace('It''s great to have you here again. New opportunities are waiting, and Applivo is ready to help you apply smarter, prepare better, and move one step closer to your next career milestone.\n\nLet''s get started!','\n', char(10)), 'null', 'user_login', NULL, NULL, '2026-04-15 14:53:28.440356', NULL, NULL, 'a964ec9d-59a4-4134-9022-35e8f6d825f2', '2026-04-15 14:53:23.905518', '2026-04-15 14:53:28.440904');
INSERT OR IGNORE INTO 'notifications'(_rowid_, 'user_id', 'channel', 'status', 'title', 'body', 'data', 'event_type', 'telegram_message_id', 'telegram_reply_markup', 'sent_at', 'read_at', 'error_message', 'id', 'created_at', 'updated_at') VALUES (492, '186abe6d-ed82-4ac6-882e-9d0acb5f3192', 'TELEGRAM', 'FAILED', 'Welcome back, Super! 👋', replace('It''s great to have you here again. New opportunities are waiting, and Applivo is ready to help you apply smarter, prepare better, and move one step closer to your next career milestone.\n\nLet''s get started!','\n', char(10)), 'null', 'user_login', NULL, 'null', NULL, NULL, '{''ok'': False, ''error_code'': 403, ''description'': "Forbidden: bots can''t send messages to bots"}', '6796ee06-da15-4ff3-b3cf-5c2832d3b687', '2026-04-15 16:34:22.559975', '2026-04-15 16:34:23.524496');
INSERT OR IGNORE INTO 'notifications'(_rowid_, 'user_id', 'channel', 'status', 'title', 'body', 'data', 'event_type', 'telegram_message_id', 'telegram_reply_markup', 'sent_at', 'read_at', 'error_message', 'id', 'created_at', 'updated_at') VALUES (493, '186abe6d-ed82-4ac6-882e-9d0acb5f3192', 'EMAIL', 'SENT', 'Welcome back, Super! 👋', replace('It''s great to have you here again. New opportunities are waiting, and Applivo is ready to help you apply smarter, prepare better, and move one step closer to your next career milestone.\n\nLet''s get started!','\n', char(10)), 'null', 'user_login', NULL, NULL, '2026-04-15 16:34:28.193013', NULL, NULL, '529bbf5b-bd50-409e-87bf-db3cb9cf13d5', '2026-04-15 16:34:23.525260', '2026-04-15 16:34:28.194750');
INSERT OR IGNORE INTO 'agent_tasks'(_rowid_, 'task_type', 'status', 'celery_task_id', 'payload', 'result', 'error', 'scheduled_at', 'started_at', 'completed_at', 'duration_ms', 'retry_count', 'max_retries', 'related_job_id', 'related_application_id', 'triggered_by', 'id', 'created_at', 'updated_at', 'user_id') VALUES (1, 'scrape_jobs', 'SUCCESS', NULL, '{"task_type": "scrape_jobs", "payload": null, "scrape_linkedin": true, "scrape_indeed": true, "scrape_internshala": true, "scrape_wellfound": true, "analyze_jobs": true, "max_jobs": null}', '{"jobs_found": 90, "jobs_new": 90}', NULL, NULL, '2026-04-15 15:02:13.286819', '2026-04-15 15:02:33.160035', 19900, 0, 3, NULL, NULL, 'user', '3f763bae-2e67-4183-92da-7f36294c61bf', '2026-04-15 15:02:13.291848', '2026-04-15 15:02:33.160364', '186abe6d-ed82-4ac6-882e-9d0acb5f3192');
INSERT OR IGNORE INTO 'subscriptions'(_rowid_, 'user_id', 'plan', 'status', 'start_date', 'end_date', 'razorpay_subscription_id', 'id', 'created_at', 'updated_at') VALUES (1, '364c6ba3-8669-4f9a-bd50-577322459d4d', 'STARTER', 'ACTIVE', '2026-04-03 16:05:11.978901', '2026-05-03 16:05:11.978902', NULL, '6047a7ab-0571-4653-b2f6-bc485190d30b', '2026-04-03 16:05:11.979552', '2026-04-03 16:05:11.979553');
INSERT OR IGNORE INTO 'platform_cookies'(_rowid_, 'user_id', 'platform', 'encrypted_cookies', 'is_valid', 'expires_at', 'last_validated_at', 'last_used_at', 'id', 'created_at', 'updated_at') VALUES (1, '364c6ba3-8669-4f9a-bd50-577322459d4d', 'internshala', '', 0, NULL, '', NULL, '', '', '');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (83, '738a1e16-6fa2-4879-84da-18d96ff8fd3b', '[]', '[]', '[]', '[]', 0, NULL, 'bachelor', '[]', 'other', 'entry', 0, 58, 50, 70, NULL, '[]', '[]', 0, NULL, 'medium', 0.29, 'easy', 40.6, NULL, NULL, '', 'Good match (50% skill). Missing: none', 'llama-3.1-8b-instant', 411, 4395, '0b44ed4a-ce7a-4bd8-b774-a2ee19822ade', '2026-04-03 17:00:06.265912', '2026-04-15 04:24:23.385431');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (84, '846d9989-d31c-4d0f-989b-a6fba2ae4a4a', '[]', '[]', '[]', '[]', 0, NULL, 'bachelor', '[]', 'software_engineering', 'entry', 0, 58, 50, 70, NULL, '[]', '[]', 0, NULL, 'medium', 0.29, 'easy', 40.6, NULL, NULL, 'No job description provided.', 'Good match (50% skill). Missing: none', 'llama-3.1-8b-instant', 393, 3374, '17248108-2511-4376-9e31-9f3a8ff49998', '2026-04-03 17:00:09.080139', '2026-04-15 04:24:26.767425');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (85, '25714984-ea0b-4974-add0-abd485ae2a3e', '[]', '[]', '[]', '[]', 0, NULL, 'bachelor', '[]', 'other', 'entry', 0, 58, 50, 70, NULL, '[]', '[]', 0, NULL, 'medium', 0.29, 'easy', 40.6, NULL, NULL, '', 'Good match (50% skill). Missing: none', 'llama-3.1-8b-instant', 414, 4452, '9ff8843c-8917-4f11-929d-2a01c4cd3d22', '2026-04-03 17:00:12.047783', '2026-04-15 04:24:31.228571');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (86, '8d5d7564-6ed6-47a9-830d-639a435e1a9b', '[]', '[]', '[]', '[]', 0, NULL, 'none', '[]', 'other', 'entry', 0, 58, 50, 70, NULL, '[]', '[]', 0, NULL, 'medium', 0.29, 'easy', 40.6, NULL, NULL, 'No job description provided.', 'Good match (50% skill). Missing: none', 'llama-3.1-8b-instant', 399, 4539, '4c66da03-9ccb-48e7-b5ed-e48f07dda3a5', '2026-04-03 17:00:15.015215', '2026-04-15 04:24:35.775279');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (87, 'd9b081d3-71eb-40cf-872a-7893d8906043', '[]', '[]', '[]', '[]', 0, NULL, 'none', '[]', 'other', 'none', 0, 58, 50, 70, NULL, '[]', '[]', 0, NULL, 'medium', 0.29, 'none', 40.6, NULL, NULL, 'No job description provided.', 'Good match (50% skill). Missing: none', 'llama-3.1-8b-instant', 378, 3575, '9ba529db-473c-4c1b-aa9e-aac7a0064ba1', '2026-04-03 17:20:54.671450', '2026-04-15 04:24:39.357910');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (88, 'd80f53fa-829b-42a1-83de-f04e8a6d698f', '[]', '[]', '[]', '[]', 0, NULL, 'bachelor|master|phd|none', '[]', 'computer_vision|nlp|mlops|data_science|software_engineering|other', 'entry|mid|senior|lead', 1, 58, 50, 70, NULL, '[]', '[]', 0, NULL, 'medium', 0.29, 'easy|medium|hard', 40.6, NULL, NULL, '', 'Good match (50% skill). Missing: none', 'llama-3.1-8b-instant', 439, 3473, '3ab29817-e4e9-4502-9b0b-58e36b1e3e82', '2026-04-03 17:20:55.460361', '2026-04-15 04:24:42.838497');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (89, '663bcbe2-239e-4666-850a-ca3504a5554a', '[]', '[]', '[]', '[]', 0, NULL, 'none', '[]', 'other', 'entry', 0, 58, 50, 70, NULL, '[]', '[]', 0, NULL, 'medium', 0.29, 'easy', 40.6, NULL, NULL, 'No job description provided.', 'Good match (50% skill). Missing: none', 'llama-3.1-8b-instant', 401, 4337, 'b38cf6be-c642-410f-a75d-f55246ec9a58', '2026-04-03 17:20:56.122512', '2026-04-15 04:24:47.181494');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (90, '2a5cf452-0331-4447-9ada-913608e7649f', '[]', '[]', '[]', '[]', 0, NULL, 'bachelor', '[]', 'other', 'entry', 0, 58, 50, 70, NULL, '[]', '[]', 0, NULL, 'medium', 0.29, 'easy', 40.6, NULL, NULL, 'No job description provided.', 'Good match (50% skill). Missing: none', 'llama-3.1-8b-instant', 410, 4384, '5cf4b440-3b58-42a9-a344-ea4ecb007cb5', '2026-04-03 17:20:56.602207', '2026-04-15 04:24:51.574160');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (91, 'fd7d6f3b-68e7-4a81-89a9-14793e0f8b13', '[]', '[]', '[]', '[]', 0, NULL, 'none', '[]', 'software_engineering', 'none', 0, 58, 50, 70, NULL, '[]', '[]', 0, NULL, 'medium', 0.29, 'none', 40.6, NULL, NULL, 'No job description provided.', 'Good match (50% skill). Missing: none', 'llama-3.1-8b-instant', 407, 4510, '4c514254-8e91-4b8a-aafe-7a06ba64481d', '2026-04-03 17:20:57.459004', '2026-04-15 04:24:56.092677');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (92, '8a8eccc3-086f-42d6-9449-2096738d9010', '[]', '[]', '[]', '[]', 0, NULL, 'none', '[]', 'software_engineering', 'none', 0, 58, 50, 70, NULL, '[]', '[]', 0, NULL, 'medium', 0.29, 'none', 40.6, NULL, NULL, 'No job description provided.', 'Good match (50% skill). Missing: none', 'llama-3.1-8b-instant', 409, 3741, 'c9da391a-fbb3-4665-ad00-a37705e42e5b', '2026-04-03 17:20:58.139695', '2026-04-15 04:24:59.841636');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (1, '0cfe99bd-93a4-4623-be1e-ab404329f848', '[]', '[]', '[]', '[]', 0, NULL, 'none', '[]', 'other', 'none', 0, 58, 50, 70, NULL, '[]', '[]', 0, NULL, 'medium', 0.29, 'none', 40.6, NULL, NULL, 'No job description provided', 'Good match (50% skill). Missing: none', 'llama-3.1-8b-instant', 406, 1222, '7d72bdb3-6de5-4931-8d17-97dda2ed890f', '2026-04-03 16:56:54.106906', '2026-04-15 04:19:13.488350');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (2, '058354ec-0eda-4387-9847-7c9ad97ccbfe', '[]', '[]', '[]', '[]', 0, NULL, 'bachelor', '[]', 'other', 'senior', 0, 46, 50, 40, NULL, '[]', '[]', 0, NULL, 'medium', 0.23, 'hard', 23, NULL, NULL, 'No job description provided.', 'Partial match (50%). Consider if desperate.', 'llama-3.1-8b-instant', 412, 555, '2e40a7b5-c890-48f2-ab10-f896bb19d231', '2026-04-03 16:57:16.635838', '2026-04-15 04:19:14.049319');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (3, '769910c5-0560-481f-afec-b05b60ef97d3', '[]', '[]', '[]', '[]', 0, NULL, 'bachelor', '[]', 'data_science', 'entry', 1, 58, 50, 70, NULL, '[]', '[]', 0, NULL, 'medium', 0.29, 'easy', 40.6, NULL, NULL, 'No job description provided.', 'Good match (50% skill). Missing: none', 'llama-3.1-8b-instant', 408, 411, 'e13cce12-4ddc-4a1d-917c-fe6f7dcc8a33', '2026-04-03 16:57:17.555981', '2026-04-15 04:19:14.468919');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (4, 'cd9392bb-e927-4f13-b3e9-38b5b1441f20', '[]', '[]', '[]', '[]', 0, NULL, 'none', '[]', 'other', 'entry', 1, 58, 50, 70, NULL, '[]', '[]', 0, NULL, 'medium', 0.29, 'easy', 40.6, NULL, NULL, '', 'Good match (50% skill). Missing: none', 'llama-3.1-8b-instant', 402, 377, 'f872887a-25a8-49cc-86f4-dc44b434ff7d', '2026-04-03 16:57:18.189469', '2026-04-15 04:19:14.854386');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (5, '1ef0f01a-e764-483f-8f56-09f2d69304bf', '[]', '[]', '[]', '[]', 0, NULL, 'bachelor', '[]', 'other', 'entry', 1, 58, 50, 70, NULL, '[]', '[]', 0, NULL, 'medium', 0.29, 'easy', 40.6, NULL, NULL, '', 'Good match (50% skill). Missing: none', 'llama-3.1-8b-instant', 418, 415, 'da4e4b84-47e9-45a6-93e8-7161a608130d', '2026-04-03 16:57:19.194167', '2026-04-15 04:19:15.277917');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (6, '99138747-d070-4c7f-94a1-4ed6c2ae7b59', '[]', '[]', '[]', '[]', 0, NULL, 'none', '[]', 'other', 'none', 0, 58, 50, 70, NULL, '[]', '[]', 0, NULL, 'medium', 0.29, 'none', 40.6, NULL, NULL, 'No job description provided', 'Good match (50% skill). Missing: none', 'llama-3.1-8b-instant', 408, 498, '3b43f310-4479-4900-818a-56ace2cfff31', '2026-04-03 16:57:19.807993', '2026-04-15 04:19:15.782903');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (7, '7f080d3e-16d3-42d4-965f-266c46165c35', '[]', '[]', '[]', '[]', 0, NULL, 'bachelor', '[]', 'other', 'senior', 0, 46, 50, 40, NULL, '[]', '[]', 0, NULL, 'medium', 0.23, 'hard', 23, NULL, NULL, '', 'Partial match (50%). Consider if desperate.', 'llama-3.1-8b-instant', 409, 408, '63337a2b-86df-4c4d-b156-abe391ae816c', '2026-04-03 16:57:20.612036', '2026-04-15 04:19:16.199309');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (8, 'a6d39891-deb9-443c-af34-2cbfdc3969aa', '[]', '[]', '[]', '[]', 0, NULL, 'bachelor', '[]', 'other', 'unknown', 0, 58, 50, 70, NULL, '[]', '[]', 0, NULL, 'medium', 0.29, 'unknown', 40.6, NULL, NULL, 'unknown', 'Good match (50% skill). Missing: none', 'llama-3.1-8b-instant', 409, 403, '600284f9-8b45-4315-bfb5-d1f4433daff3', '2026-04-03 16:57:21.378126', '2026-04-15 04:19:16.610920');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (9, 'aa90aee3-119b-4707-b8ca-1942df261edc', '[]', '[]', '[]', '[]', 0, NULL, 'bachelor', '[]', 'computer_vision', 'unknown', 0, 58, 50, 70, NULL, '[]', '[]', 0, NULL, 'medium', 0.29, 'unknown', 40.6, NULL, NULL, 'unknown', 'Good match (50% skill). Missing: none', 'llama-3.1-8b-instant', 400, 7397, '6104455c-e2cb-4d31-bf2d-232a91219a07', '2026-04-03 16:57:22.118112', '2026-04-15 04:19:24.015824');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (10, '42ac7894-d380-46e2-aa9f-73eea07b6297', '[]', '[]', '[]', '[]', 0, NULL, 'none', '[]', 'other', 'none', 0, 58, 50, 70, NULL, '[]', '[]', 0, NULL, 'medium', 0.29, 'none', 40.6, NULL, NULL, 'none', 'Good match (50% skill). Missing: none', 'llama-3.1-8b-instant', 405, 1518, '2cb48ee8-4dd7-4049-bdc6-625c8027cb1f', '2026-04-03 16:57:22.791363', '2026-04-15 04:19:25.541744');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (11, 'c2aff95f-854e-4ac7-9f3b-0db32913c41e', '[]', '[]', '[]', '[]', 0, NULL, 'bachelor', '[]', 'data_science', 'mid', 0, 58, 50, 70, NULL, '[]', '[]', 0, NULL, 'medium', 0.29, 'medium', 40.6, NULL, NULL, 'No job description provided.', 'Good match (50% skill). Missing: none', 'llama-3.1-8b-instant', 408, 4805, 'e2da927f-9ff5-4216-b47a-1bf94028b846', '2026-04-03 16:57:23.497172', '2026-04-15 04:19:30.354199');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (12, '3487a4cf-2f1a-4ef0-ad9c-ad26c5072a15', '[]', '[]', '[]', '[]', 0, NULL, 'none', '[]', 'other', 'none', 0, 58, 50, 70, NULL, '[]', '[]', 0, NULL, 'medium', 0.29, 'none', 40.6, NULL, NULL, 'No job description provided', 'Good match (50% skill). Missing: none', 'llama-3.1-8b-instant', 413, 3457, '05fc107a-16e5-46ba-9414-e2ccdf99564c', '2026-04-03 16:57:24.043439', '2026-04-15 04:19:33.819774');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (13, 'd2af74a3-439e-4cc4-b259-f1f65691269f', '[]', '[]', '[]', '[]', 0, NULL, 'none', '[]', 'other', 'none', 0, 58, 50, 70, NULL, '[]', '[]', 0, NULL, 'medium', 0.29, 'none', 40.6, NULL, NULL, 'none', 'Good match (50% skill). Missing: none', 'llama-3.1-8b-instant', 422, 4490, '9246de96-1d97-49a0-8f74-77ddcf0a0e04', '2026-04-03 16:57:24.874792', '2026-04-15 04:19:38.318100');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (14, '77be3aa2-ae1e-46b9-a8c7-ffbfee39929d', '[]', '[]', '[]', '[]', 0, NULL, 'none', '[]', 'other', 'none', 0, 58, 50, 70, NULL, '[]', '[]', 0, NULL, 'medium', 0.29, 'none', 40.6, NULL, NULL, 'none', 'Good match (50% skill). Missing: none', 'llama-3.1-8b-instant', 405, 3477, '706f0d1f-412a-435a-8f1a-9ec448102bcc', '2026-04-03 16:57:25.461796', '2026-04-15 04:19:41.802242');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (15, '92cc66af-11f2-4c2a-b425-71dfc9587d96', '[]', '[]', '[]', '[]', 0, NULL, 'bachelor|master|phd|none', '[]', 'other', 'unknown', 0, 58, 50, 70, NULL, '[]', '[]', 0, NULL, 'medium', 0.29, 'unknown', 40.6, NULL, NULL, 'No job description provided', 'Good match (50% skill). Missing: none', 'llama-3.1-8b-instant', 414, 4393, '428a22f6-e5e1-497a-91cf-06a1d748a6ea', '2026-04-03 16:57:25.971941', '2026-04-15 04:19:46.202396');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (16, '20b6ef13-6b70-4b8b-815b-44ef9870fd1a', '[]', '[]', '[]', '[]', 0, NULL, 'bachelor', '[]', 'other', 'mid', 0, 58, 50, 70, NULL, '[]', '[]', 0, NULL, 'medium', 0.29, 'medium', 40.6, NULL, NULL, '', 'Good match (50% skill). Missing: none', 'llama-3.1-8b-instant', 427, 4477, 'c9afe31c-31b2-4617-af63-503876ec2bbf', '2026-04-03 16:57:26.874449', '2026-04-15 04:19:50.685481');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (17, 'f64ba568-5424-4292-b434-5548dc79687e', '[]', '[]', '[]', '[]', 0, NULL, 'bachelor', '[]', 'other', 'senior', 0, 46, 50, 40, NULL, '[]', '[]', 0, NULL, 'medium', 0.23, 'hard', 23, NULL, NULL, '', 'Partial match (50%). Consider if desperate.', 'llama-3.1-8b-instant', 409, 4610, 'bc95efab-3762-4299-b607-6b7f84c735b9', '2026-04-03 16:57:27.691274', '2026-04-15 04:19:55.300854');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (18, 'e671f1af-3593-4b62-9060-41a6c8e98818', '["AWS", "SageMaker", "Machine Learning"]', '[]', '["AWS", "SageMaker"]', '["Cloud", "Machine Learning", "AWS SageMaker"]', 2, NULL, 'bachelor', '["Develop and deploy machine learning models on AWS SageMaker"]', 'mlops', 'mid', 0, 37, 15, 70, NULL, '[]', '["aws", "sagemaker", "machine learning"]', 3, NULL, 'high', 0.185, 'medium', 18.5, NULL, NULL, 'Develop and deploy machine learning models on AWS SageMaker. Collaborate with cross-functional teams to integrate machine learning solutions into the product.', 'Partial match (15%). Consider if desperate.', 'llama-3.1-8b-instant', 459, 4688, '6a54c2dd-9460-4903-9905-01bec4c08257', '2026-04-03 16:57:28.427445', '2026-04-14 15:54:48.791773');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (19, '5f1fb82e-143d-4b35-86ce-4d77a15ac4e3', '[]', '[]', '[]', '[]', 0, NULL, 'none', '[]', 'other', 'none', 0, 58, 50, 70, NULL, '[]', '[]', 0, NULL, 'medium', 0.29, 'none', 40.6, NULL, NULL, 'No job description provided', 'Good match (50% skill). Missing: none', 'llama-3.1-8b-instant', 403, 3414, '41712959-6f11-4138-b804-91d44ec5a5de', '2026-04-03 16:57:28.922367', '2026-04-15 04:20:03.017981');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (20, 'bcd7218f-2527-4412-ba8d-3460caefd5f0', '[]', '[]', '[]', '[]', 0, NULL, 'none', '[]', 'software_engineering', 'none', 0, 58, 50, 70, NULL, '[]', '[]', 0, NULL, 'medium', 0.29, 'none', 40.6, NULL, NULL, 'No job description provided.', 'Good match (50% skill). Missing: none', 'llama-3.1-8b-instant', 406, 4462, '8c20f5d3-9e08-46ca-8cc5-cc798e7957fb', '2026-04-03 16:57:29.536675', '2026-04-15 04:20:07.487418');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (21, 'b5bf7690-5f76-4955-ac34-9b70e52f1529', '[]', '[]', '[]', '[]', 0, NULL, 'none', '[]', 'other', 'lead', 0, 46, 50, 40, NULL, '[]', '[]', 0, NULL, 'medium', 0.23, 'hard', 23, NULL, NULL, 'No job description provided.', 'Partial match (50%). Consider if desperate.', 'llama-3.1-8b-instant', 407, 4618, 'b7a205fc-3944-4dca-90ed-20db5d5d0d41', '2026-04-03 16:57:30.050123', '2026-04-15 04:20:12.113010');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (22, '350726b2-86d5-402b-90e4-a0c7613d9fe6', '[]', '[]', '[]', '[]', 0, NULL, 'bachelor|master|phd|none', '[]', 'data_science', 'unknown', 0, 58, 50, 70, NULL, '[]', '[]', 0, NULL, 'medium', 0.29, 'unknown', 40.6, NULL, NULL, 'unknown', 'Good match (50% skill). Missing: none', 'llama-3.1-8b-instant', 406, 3447, '80b3ab70-39b3-41b6-b9e1-3138d23ef374', '2026-04-03 16:57:30.867595', '2026-04-15 04:20:15.565736');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (23, 'ef6c98cd-0a22-4243-a39e-8bb3e64ddb0a', '[]', '[]', '[]', '[]', 0, NULL, 'bachelor', '[]', 'other', 'senior', 0, 46, 50, 40, NULL, '[]', '[]', 0, NULL, 'medium', 0.23, 'hard', 23, NULL, NULL, 'No job description provided.', 'Partial match (50%). Consider if desperate.', 'llama-3.1-8b-instant', 412, 4658, '00c84a16-a207-49d1-b2c8-5a3cdd646af9', '2026-04-03 16:57:31.760836', '2026-04-15 04:20:20.230209');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (24, '06759dd8-7d7c-4d3f-b125-d7fef40399fb', '[]', '[]', '[]', '[]', 0, NULL, 'bachelor', '[]', 'software_engineering', 'mid', 0, 58, 50, 70, NULL, '[]', '[]', 0, NULL, 'medium', 0.29, 'medium', 40.6, NULL, NULL, 'No job description provided.', 'Good match (50% skill). Missing: none', 'llama-3.1-8b-instant', 411, 3364, 'b697c6ca-8ac2-4f05-9062-ed9260c2d7d0', '2026-04-03 16:57:32.814614', '2026-04-15 04:20:23.601332');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (25, '001f713e-b1d2-4fd5-8f34-5789fb5b710e', '[]', '[]', '[]', '[]', 0, NULL, 'bachelor|master|phd|none', '[]', 'data_science', 'unknown', 0, 58, 50, 70, NULL, '[]', '[]', 0, NULL, 'medium', 0.29, 'unknown', 40.6, NULL, NULL, 'unknown', 'Good match (50% skill). Missing: none', 'llama-3.1-8b-instant', 414, 4372, 'c8458f18-8c98-483e-a1ed-586f107c7e98', '2026-04-03 16:57:33.327706', '2026-04-15 04:20:27.979804');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (26, 'f983c546-f677-4b6c-8296-23b4111025ce', '[]', '[]', '[]', '[]', 0, NULL, 'bachelor|master|phd|none', '[]', 'data_science', 'unknown', 0, 58, 50, 70, NULL, '[]', '[]', 0, NULL, 'medium', 0.29, 'unknown', 40.6, NULL, NULL, 'No job description provided.', 'Good match (50% skill). Missing: none', 'llama-3.1-8b-instant', 427, 4573, '598955bf-732c-498f-8c51-93b426034b18', '2026-04-03 16:57:34.000771', '2026-04-15 04:20:32.560673');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (27, '87224bf9-90e0-41cf-8377-c1cca6e97d0b', '[]', '[]', '[]', '[]', 0, NULL, 'none', '[]', 'software_engineering', 'none', 0, 58, 50, 70, NULL, '[]', '[]', 0, NULL, 'medium', 0.29, 'none', 40.6, NULL, NULL, 'No job description provided.', 'Good match (50% skill). Missing: none', 'llama-3.1-8b-instant', 405, 3809, '9b1a5744-a23e-4961-9c72-155247fedf0a', '2026-04-03 16:57:34.860959', '2026-04-15 04:20:36.377638');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (28, '51895afe-478b-4bed-b585-a1230cc8cbaa', '[]', '[]', '[]', '[]', 0, NULL, 'none', '[]', 'other', 'none', 0, 58, 50, 70, NULL, '[]', '[]', 0, NULL, 'medium', 0.29, 'none', 40.6, NULL, NULL, 'No job description provided', 'Good match (50% skill). Missing: none', 'llama-3.1-8b-instant', 407, 4494, '6a3d4bc9-d08e-4156-8f99-911a1d1b140e', '2026-04-03 16:57:35.626888', '2026-04-15 04:20:40.880303');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (29, 'e0b54ad2-f432-46bc-a4d9-615b779de21a', '[]', '[]', '[]', '[]', 0, NULL, 'none', '[]', 'other', 'none', 0, 58, 50, 70, NULL, '[]', '[]', 0, NULL, 'medium', 0.29, 'none', 40.6, NULL, NULL, 'No job description provided', 'Good match (50% skill). Missing: none', 'llama-3.1-8b-instant', 404, 3356, '7434f14e-1058-40b1-ae67-9406a69e259a', '2026-04-03 16:57:36.203821', '2026-04-15 04:20:44.244526');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (30, '1b868b4d-457d-4ea9-bfa3-e5821bfa62a7', '[]', '[]', '[]', '[]', 0, NULL, 'bachelor|master|phd|none', '[]', 'data_science', 'unknown', 0, 58, 50, 70, NULL, '[]', '[]', 0, NULL, 'medium', 0.29, 'unknown', 40.6, NULL, NULL, 'No job description provided.', 'Good match (50% skill). Missing: none', 'llama-3.1-8b-instant', 406, 4524, '7bda2929-c1db-40e1-bc2a-2ba6b554efb1', '2026-04-03 16:57:36.907895', '2026-04-15 04:20:48.776063');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (31, '1893ee73-a045-42bd-868b-f6362b340b66', '[]', '[]', '[]', '[]', 0, NULL, 'none', '[]', 'other', 'none', 0, 58, 50, 70, NULL, '[]', '[]', 0, NULL, 'medium', 0.29, 'none', 40.6, NULL, NULL, 'No job description provided.', 'Good match (50% skill). Missing: none', 'llama-3.1-8b-instant', 388, 3565, '01c5273b-752f-45ac-92fa-e409a99d9bf1', '2026-04-03 16:57:37.932654', '2026-04-15 04:20:52.349035');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (32, 'be7c027d-abca-4214-b3f8-b3de0adef08c', '[]', '[]', '[]', '[]', 0, NULL, 'none', '[]', 'other', 'none', 0, 58, 50, 70, NULL, '[]', '[]', 0, NULL, 'medium', 0.29, 'none', 40.6, NULL, NULL, 'No job description provided.', 'Good match (50% skill). Missing: none', 'llama-3.1-8b-instant', 386, 4496, '475ba12c-5ad2-498d-a736-db68119c3a1b', '2026-04-03 16:57:40.800803', '2026-04-15 04:20:56.851717');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (33, '9dff419b-3188-411b-86ac-bde2f9232649', '[]', '[]', '[]', '[]', 0, NULL, 'none', '[]', 'other', 'none', 0, 58, 50, 70, NULL, '[]', '[]', 0, NULL, 'medium', 0.29, 'none', 40.6, NULL, NULL, 'No job description provided', 'Good match (50% skill). Missing: none', 'llama-3.1-8b-instant', 410, 3428, 'e09a3059-e1a3-4041-be9c-9db8f0274655', '2026-04-03 16:57:43.668048', '2026-04-15 04:21:00.287821');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (34, '7a8f7b54-f044-4ac7-92d1-8aa8462c521c', '[]', '[]', '[]', '[]', 0, NULL, 'bachelor', '[]', 'software_engineering', 'entry', 0, 58, 50, 70, NULL, '[]', '[]', 0, NULL, 'medium', 0.29, 'hard', 40.6, NULL, NULL, 'Data Platform Engineering role for 2026 graduates at Primenumbers Technologies.', 'Good match (50% skill). Missing: none', 'llama-3.1-8b-instant', 406, 5555, '794e1243-eecb-4ec8-a4e0-a1b2c846ea57', '2026-04-03 16:57:46.536599', '2026-04-15 04:21:05.850938');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (35, '10a143f5-8664-45a0-bccf-79c1565e037c', '[]', '[]', '[]', '[]', 0, NULL, 'bachelor', '[]', 'other', 'entry', 0, 58, 50, 70, NULL, '[]', '[]', 0, NULL, 'medium', 0.29, 'easy', 40.6, NULL, NULL, '', 'Good match (50% skill). Missing: none', 'llama-3.1-8b-instant', 382, 2388, '45a0b03c-df28-4bdd-ac5d-6dde2e4ee6c1', '2026-04-03 16:57:49.160869', '2026-04-15 04:21:08.247433');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (36, '3620bb0f-25e5-448c-85b0-a630fdc28db4', '[]', '[]', '[]', '[]', 0, NULL, 'bachelor|master|phd|none', '[]', 'other', 'unknown', 0, 58, 50, 70, NULL, '[]', '[]', 0, NULL, 'medium', 0.29, 'unknown', 40.6, NULL, NULL, 'unknown', 'Good match (50% skill). Missing: none', 'llama-3.1-8b-instant', 420, 4676, '515c9f46-2e2b-49e0-a234-fc54fb5280d5', '2026-04-03 16:57:51.717699', '2026-04-15 04:21:12.930597');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (37, '3a9fe65c-ac49-400e-8ce3-ff099644df76', '[]', '[]', '[]', '[]', 0, NULL, 'bachelor|master|phd|none', '[]', 'other', 'unknown', 0, 58, 50, 70, NULL, '[]', '[]', 0, NULL, 'medium', 0.29, 'unknown', 40.6, NULL, NULL, 'No AI summary available', 'Good match (50% skill). Missing: none', 'llama-3.1-8b-instant', 423, 3473, 'f16a4f70-c85d-461c-b465-2e9972d1ea12', '2026-04-03 16:57:54.727514', '2026-04-15 04:21:16.411667');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (38, '7722e288-cb9a-426a-aeeb-0d6aefb68500', '[]', '[]', '[]', '[]', 0, NULL, 'bachelor', '[]', 'other', 'senior', 0, 46, 50, 40, NULL, '[]', '[]', 0, NULL, 'medium', 0.23, 'hard', 23, NULL, NULL, '', 'Partial match (50%). Consider if desperate.', 'llama-3.1-8b-instant', 408, 4393, '3439b679-9b13-4652-9bac-a866a035d5a2', '2026-04-03 16:57:57.594440', '2026-04-15 04:21:20.812435');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (39, '04fed8ab-4db5-42a8-b3a8-8d8845a104b6', '[]', '[]', '[]', '[]', 0, NULL, 'none', '[]', 'other', 'none', 0, 58, 50, 70, NULL, '[]', '[]', 0, NULL, 'medium', 0.29, 'none', 40.6, NULL, NULL, 'No job description provided', 'Good match (50% skill). Missing: none', 'llama-3.1-8b-instant', 396, 4502, '7258a4a1-341e-4bdf-86e0-92e002fc7f00', '2026-04-03 16:58:00.461378', '2026-04-15 04:21:25.322984');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (40, '2a4a41ed-f71a-4113-942b-244e8e88b269', '[]', '[]', '[]', '[]', 0, NULL, 'none', '[]', 'other', 'none', 0, 58, 50, 70, NULL, '[]', '[]', 0, NULL, 'medium', 0.29, 'none', 40.6, NULL, NULL, 'none', 'Good match (50% skill). Missing: none', 'llama-3.1-8b-instant', 409, 3368, '13822903-6c23-4ae6-a5bd-3a9528a81140', '2026-04-03 16:58:03.121875', '2026-04-15 04:21:28.699221');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (41, '35089a00-236e-4633-8fec-d4da81abaa22', '[]', '[]', '[]', '[]', 0, NULL, 'bachelor', '[]', 'other', 'senior', 0, 46, 50, 40, NULL, '[]', '[]', 0, NULL, 'medium', 0.23, 'hard', 23, NULL, NULL, 'No AI summary found', 'Partial match (50%). Consider if desperate.', 'llama-3.1-8b-instant', 416, 4749, '96d891f8-ff3a-4a6a-acee-69c4044d0e01', '2026-04-03 16:58:05.942465', '2026-04-15 04:21:33.457069');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (42, '57c48526-d2a0-447f-8a2b-7d2289c9c58f', '[]', '[]', '[]', '[]', 0, NULL, 'bachelor', '[]', 'software_engineering', 'mid', 0, 58, 50, 70, NULL, '[]', '[]', 0, NULL, 'medium', 0.29, 'medium', 40.6, NULL, NULL, 'No job description provided.', 'Good match (50% skill). Missing: none', 'llama-3.1-8b-instant', 404, 3427, '078f347f-0686-430f-9b4c-00c68141edab', '2026-04-03 16:58:08.656685', '2026-04-15 04:21:36.891612');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (43, '25d22dea-b1db-4111-82f6-fa227a7f55e3', '[]', '[]', '[]', '[]', 0, NULL, 'bachelor', '[]', 'other', 'unknown', 0, 58, 50, 70, NULL, '[]', '[]', 0, NULL, 'medium', 0.29, 'unknown', 40.6, NULL, NULL, 'unknown', 'Good match (50% skill). Missing: none', 'llama-3.1-8b-instant', 425, 4499, 'c1f16a7e-0a2c-4c53-a5d9-3edebc5ae2b7', '2026-04-03 16:58:11.533123', '2026-04-15 04:21:41.398474');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (44, '6d7c697b-a269-4f74-baf9-c0eaada5e643', '[]', '[]', '[]', '[]', 0, NULL, 'none', '[]', 'other', 'none', 0, 58, 50, 70, NULL, '[]', '[]', 0, NULL, 'medium', 0.29, 'unknown', 40.6, NULL, NULL, 'No job description provided.', 'Good match (50% skill). Missing: none', 'llama-3.1-8b-instant', 406, 4463, '8401739b-fbf0-4e55-a86a-cecd826e107a', '2026-04-03 16:58:14.506219', '2026-04-15 04:21:45.869451');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (45, '75eb21cb-5f45-433c-b56d-f2a1a1566516', '[]', '[]', '[]', '[]', 0, NULL, 'none', '[]', 'software_engineering', 'none', 0, 58, 50, 70, NULL, '[]', '[]', 0, NULL, 'medium', 0.29, 'none', 40.6, NULL, NULL, 'No job description provided.', 'Good match (50% skill). Missing: none', 'llama-3.1-8b-instant', 387, 4023, 'cac7ea8e-75e0-4679-85a9-309c574fe7de', '2026-04-03 16:58:17.394476', '2026-04-15 04:21:49.901082');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (46, '692aba8a-9059-4bee-a7e0-2fcb9ef6f8d5', '[]', '[]', '[]', '[]', 0, NULL, 'bachelor|master|phd|none', '[]', 'data_science', 'unknown', 0, 58, 50, 70, NULL, '[]', '[]', 0, NULL, 'medium', 0.29, 'unknown', 40.6, NULL, NULL, 'unknown', 'Good match (50% skill). Missing: none', 'llama-3.1-8b-instant', 418, 3372, '95a3cbb7-4faf-46ce-8d6c-33f13c307b9d', '2026-04-03 16:58:20.197639', '2026-04-15 04:21:53.281622');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (47, 'a79f2934-37ac-4870-b39d-c5607e2114d2', '[]', '[]', '[]', '[]', 0, NULL, 'none', '[]', 'other', 'none', 0, 58, 50, 70, NULL, '[]', '[]', 0, NULL, 'medium', 0.29, 'none', 40.6, NULL, NULL, 'No job description provided.', 'Good match (50% skill). Missing: none', 'llama-3.1-8b-instant', 410, 5512, '6e1dc9df-bb99-417b-98c6-bebcfa75eb8a', '2026-04-03 16:58:22.888419', '2026-04-15 04:21:58.801675');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (48, '9657497a-e096-4c75-bfab-7707d6329854', '[]', '[]', '[]', '[]', 0, NULL, 'none', '[]', 'software_engineering', 'none', 0, 58, 50, 70, NULL, '[]', '[]', 0, NULL, 'medium', 0.29, 'none', 40.6, NULL, NULL, 'No job description provided.', 'Good match (50% skill). Missing: none', 'llama-3.1-8b-instant', 418, 2655, 'c885b35c-895c-4303-99b9-463cfcfa4f8b', '2026-04-03 16:58:25.597979', '2026-04-15 04:22:01.464765');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (49, 'ad851170-f051-4955-817b-a9cb561e6ccb', '[]', '[]', '[]', '[]', 0, NULL, 'bachelor', '[]', 'software_engineering', 'mid', 0, 58, 50, 70, NULL, '[]', '[]', 0, NULL, 'medium', 0.29, 'medium', 40.6, NULL, NULL, 'No job description provided.', 'Good match (50% skill). Missing: none', 'llama-3.1-8b-instant', 411, 4487, '36f297f0-a096-40df-b64a-cf0da526d598', '2026-04-03 16:58:28.622484', '2026-04-15 04:22:05.956668');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (50, '60b22641-393b-4b2b-a569-68e7c1d99e85', '[]', '[]', '[]', '[]', 0, NULL, 'none', '[]', 'software_engineering', 'unknown', 0, 58, 50, 70, NULL, '[]', '[]', 0, NULL, 'medium', 0.29, 'unknown', 40.6, NULL, NULL, 'No job description provided', 'Good match (50% skill). Missing: none', 'llama-3.1-8b-instant', 391, 3387, '9830cc8d-48d9-4cfd-a608-f079e88f5be7', '2026-04-03 16:58:31.693284', '2026-04-15 04:22:09.351564');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (51, 'e796fa36-092e-4098-ac22-50d4aedfb1ce', '[]', '[]', '[]', '[]', 0, NULL, 'none', '[]', 'other', 'entry', 1, 58, 50, 70, NULL, '[]', '[]', 0, NULL, 'medium', 0.29, 'easy', 40.6, NULL, NULL, '', 'Good match (50% skill). Missing: none', 'llama-3.1-8b-instant', 402, 4417, '3cb868b0-92c7-4800-9e2b-f5d007ed097f', '2026-04-03 16:58:34.356468', '2026-04-15 04:22:13.777723');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (52, '8961dff8-f575-4cf5-a1c9-5bbca71fec6f', '[]', '[]', '[]', '[]', 0, NULL, 'none', '[]', 'data_science', 'none', 0, 58, 50, 70, NULL, '[]', '[]', 0, NULL, 'medium', 0.29, 'none', 40.6, NULL, NULL, 'No job description provided.', 'Good match (50% skill). Missing: none', 'llama-3.1-8b-instant', 408, 4520, '210776d5-9cef-4d27-b081-6d4fa3e84a01', '2026-04-03 16:58:37.544589', '2026-04-15 04:22:18.306609');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (53, 'dae8a51f-8455-4573-b0b1-0d26f072ebc1', '[]', '[]', '[]', '[]', NULL, NULL, NULL, '[]', 'other', 'unknown', 0, 58, 50, 70, NULL, '[]', '[]', 0, NULL, 'medium', 0.29, 'medium', 40.6, NULL, NULL, '', 'Good match (50% skill). Missing: none', 'llama-3.1-8b-instant', 405, 3461, 'aca9623b-ca3a-43f4-ad38-70ec1266a1b9', '2026-04-03 16:58:40.501429', '2026-04-15 04:22:21.776691');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (54, 'd39cf6e2-1a24-4b12-ba00-effeef424d4d', '[]', '[]', '[]', '[]', 0, NULL, 'none', '[]', 'other', 'none', 0, 58, 50, 70, NULL, '[]', '[]', 0, NULL, 'medium', 0.29, 'easy', 40.6, NULL, NULL, 'No AI summary available', 'Good match (50% skill). Missing: none', 'llama-3.1-8b-instant', 378, 4460, '12cb3543-92b5-4216-8a95-0f54e88f7655', '2026-04-03 16:58:43.162504', '2026-04-15 04:22:26.245111');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (55, 'c1b3bbe5-e0d2-45de-96de-62e6adf1d4cc', '[]', '[]', '[]', '[]', 0, NULL, 'bachelor', '[]', 'software_engineering', 'mid', 0, 58, 50, 70, NULL, '[]', '[]', 0, NULL, 'medium', 0.29, 'medium', 40.6, NULL, NULL, 'An AI model to analyze financial data for intraday trading decisions. The model should be able to process large amounts of data in real-time.', 'Good match (50% skill). Missing: none', 'llama-3.1-8b-instant', 454, 3702, 'fff78d5e-ab3c-4aed-805e-60ab6c937c8d', '2026-04-03 16:58:46.028007', '2026-04-15 04:22:29.956095');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (56, '25ffe596-d016-4628-96c0-a3af4fe8e9a8', '[]', '[]', '[]', '[]', 0, NULL, 'none', '[]', 'other', 'none', 0, 58, 50, 70, NULL, '[]', '[]', 0, NULL, 'medium', 0.29, 'none', 40.6, NULL, NULL, 'No job description provided', 'Good match (50% skill). Missing: none', 'llama-3.1-8b-instant', 384, 4998, '470756ed-366b-49f3-8801-4562d369243c', '2026-04-03 16:58:48.900000', '2026-04-15 04:22:34.962329');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (57, '3a612b95-3a78-4535-ae86-8ebe4e95cc14', '[]', '[]', '[]', '[]', 0, NULL, 'bachelor', '[]', 'data_science', 'mid', 0, 58, 50, 70, NULL, '[]', '[]', 0, NULL, 'medium', 0.29, 'medium', 40.6, NULL, NULL, 'No job description provided.', 'Good match (50% skill). Missing: none', 'llama-3.1-8b-instant', 407, 3491, 'f3436c8b-b702-4583-a81f-34c57c856646', '2026-04-03 16:58:51.765346', '2026-04-15 04:22:38.462319');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (58, 'a831ecbf-c7c4-46b2-9a48-18c95c76e95a', '[]', '[]', '[]', '[]', 0, NULL, 'bachelor', '[]', 'other', 'mid', 0, 58, 50, 70, NULL, '[]', '[]', 0, NULL, 'medium', 0.29, 'medium', 40.6, NULL, NULL, 'No job description provided.', 'Good match (50% skill). Missing: none', 'llama-3.1-8b-instant', 391, 3747, '090d40f7-60d0-4541-bf8b-1a28a3bf08a4', '2026-04-03 16:58:54.528839', '2026-04-15 04:22:42.218651');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (59, '90dae3b4-6cf1-44d3-89d2-1ce8ad20a497', '[]', '[]', '[]', '[]', 0, NULL, 'none', '[]', 'other', 'none', 0, 58, 50, 70, NULL, '[]', '[]', 0, NULL, 'medium', 0.29, 'none', 40.6, NULL, NULL, 'No job description provided', 'Good match (50% skill). Missing: none', 'llama-3.1-8b-instant', 408, 5113, '44f78a6c-65c4-4605-9522-ac73c3f98eb7', '2026-04-03 16:58:57.600803', '2026-04-15 04:22:47.339077');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (60, 'f9f6657e-3aa5-4402-9b29-40b7debeed09', '[]', '[]', '[]', '[]', 0, NULL, 'none', '[]', 'other', 'none', 0, 58, 50, 70, NULL, '[]', '[]', 0, NULL, 'medium', 0.29, 'none', 40.6, NULL, NULL, 'none', 'Good match (50% skill). Missing: none', 'llama-3.1-8b-instant', 394, 3474, '99841c8c-2baa-4804-a59b-24e80e605954', '2026-04-03 16:59:00.673812', '2026-04-15 04:22:50.820244');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (61, '85591004-927b-4028-b583-8810f7a74172', '[]', '[]', '[]', '[]', 0, NULL, 'bachelor', '[]', 'data_science', 'mid', 0, 58, 50, 70, NULL, '[]', '[]', 0, NULL, 'medium', 0.29, 'medium', 40.6, NULL, NULL, 'No job description provided.', 'Good match (50% skill). Missing: none', 'llama-3.1-8b-instant', 408, 3473, '4beca5f9-39ad-4dfc-8bf2-916ee0248209', '2026-04-03 16:59:03.439217', '2026-04-15 04:22:54.301535');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (62, 'b814049b-cbac-455f-a0ab-5b2b228bd5b6', '[]', '[]', '[]', '[]', 0, NULL, 'none', '[]', 'other', 'none', 0, 58, 50, 70, NULL, '[]', '[]', 0, NULL, 'medium', 0.29, 'easy', 40.6, NULL, NULL, 'No job description provided.', 'Good match (50% skill). Missing: none', 'llama-3.1-8b-instant', 385, 4397, 'e45fe79b-cfc5-4284-a278-5eb530aa0704', '2026-04-03 16:59:06.407249', '2026-04-15 04:22:58.705357');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (69, '151bfabe-aafd-42b3-88fa-776aa75d504c', '[]', '[]', '[]', '[]', 0, NULL, 'none', '[]', 'other', 'entry', 0, 58, 50, 70, NULL, '[]', '[]', 0, NULL, 'medium', 0.29, 'easy', 40.6, NULL, NULL, '', 'Good match (50% skill). Missing: none', 'llama-3.1-8b-instant', 434, 3578, '816b79d8-db82-480a-8a58-2b405e43ca69', '2026-04-03 16:59:26.302784', '2026-04-15 04:23:26.044186');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (70, '3b8beb43-9915-425e-b193-b50fd73df0b5', '[]', '[]', '[]', '[]', 0, NULL, 'none', '[]', 'software_engineering', 'entry', 0, 58, 50, 70, NULL, '[]', '[]', 0, NULL, 'medium', 0.29, 'easy', 40.6, NULL, NULL, 'No job description provided.', 'Good match (50% skill). Missing: none', 'llama-3.1-8b-instant', 382, 4571, '9773f286-c366-4522-bb0e-ed94fdf3321a', '2026-04-03 16:59:29.242501', '2026-04-15 04:23:30.623734');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (71, '83595046-eb44-490d-9ca2-c5211a92f967', '[]', '[]', '[]', '[]', 0, NULL, 'none', '[]', 'data_science', 'none', 0, 58, 50, 70, NULL, '[]', '[]', 0, NULL, 'medium', 0.29, 'easy', 40.6, NULL, NULL, 'No job description provided.', 'Good match (50% skill). Missing: none', 'llama-3.1-8b-instant', 419, 3707, 'ba0a3bed-d938-4fff-a3ff-e8ce0a6a9ed3', '2026-04-03 16:59:32.110106', '2026-04-15 04:23:34.338336');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (72, '8c1572e0-54a0-48f3-b6c8-a74bddc1a228', '[]', '[]', '[]', '[]', 0, NULL, 'none', '[]', 'other', 'senior', 0, 46, 50, 40, NULL, '[]', '[]', 0, NULL, 'medium', 0.23, 'medium', 23, NULL, NULL, 'No job description provided.', 'Partial match (50%). Consider if desperate.', 'llama-3.1-8b-instant', 410, 4393, '5a9a5823-d7f1-4acd-b8e2-5302677dca1a', '2026-04-03 16:59:35.257639', '2026-04-15 04:23:38.739436');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (73, '9258f784-17da-4c7b-bb7f-92629b42004f', '[]', '[]', '[]', '[]', 0, NULL, 'none', '[]', 'other', 'none', 0, 58, 50, 70, NULL, '[]', '[]', 0, NULL, 'medium', 0.29, 'none', 40.6, NULL, NULL, 'No job description provided.', 'Good match (50% skill). Missing: none', 'llama-3.1-8b-instant', 386, 3684, '1254197e-9496-4f9a-8f25-1dec1c0a2bbb', '2026-04-03 16:59:38.254821', '2026-04-15 04:23:42.432331');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (74, '934042c2-7370-4e6e-98f3-c0710c0ed612', '[]', '[]', '[]', '[]', 0, NULL, 'none', '[]', 'software_engineering', 'entry', 0, 58, 50, 70, NULL, '[]', '[]', 0, NULL, 'medium', 0.29, 'easy', 40.6, NULL, NULL, '', 'Good match (50% skill). Missing: none', 'llama-3.1-8b-instant', 409, 4493, '417121b8-b8fb-42af-8785-5bb5c2d8ca5f', '2026-04-03 16:59:40.916831', '2026-04-15 04:23:46.933824');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (75, '68eb5bcc-a67c-4912-af78-5ac3139d535b', '[]', '[]', '[]', '[]', 0, NULL, 'none', '[]', 'other', 'none', 0, 58, 50, 70, NULL, '[]', '[]', 0, NULL, 'medium', 0.29, 'none', 40.6, NULL, NULL, 'No job description provided', 'Good match (50% skill). Missing: none', 'llama-3.1-8b-instant', 410, 3576, 'a57b9dc9-1e9f-4636-bd1d-39f8fb19c7a3', '2026-04-03 16:59:43.682002', '2026-04-15 04:23:50.518649');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (76, 'e1cd11c3-3afd-4b74-bb43-b9eb55cf6335', '[]', '[]', '[]', '[]', 0, NULL, 'none', '[]', 'other', 'none', 0, 58, 50, 70, NULL, '[]', '[]', 0, NULL, 'medium', 0.29, 'easy', 40.6, NULL, NULL, 'No job description provided.', 'Good match (50% skill). Missing: none', 'llama-3.1-8b-instant', 382, 4496, 'cadc6666-88f2-45ff-b484-cdbc9b72656e', '2026-04-03 16:59:46.548822', '2026-04-15 04:23:55.021372');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (77, '363e8798-9d4f-4207-89cc-e8957762c630', '[]', '[]', '[]', '[]', 0, NULL, 'bachelor', '[]', 'software_engineering', 'entry', 0, 58, 50, 70, NULL, '[]', '[]', 0, NULL, 'medium', 0.29, 'easy', 40.6, NULL, NULL, 'No job description provided.', 'Good match (50% skill). Missing: none', 'llama-3.1-8b-instant', 432, 3817, '9c827535-da22-4396-ad5d-cd71c8b1b2b9', '2026-04-03 16:59:49.321307', '2026-04-15 04:23:58.845608');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (78, 'f5d30129-d1f2-4ece-8401-b5a771df1ef4', '[]', '[]', '[]', '[]', NULL, NULL, NULL, '[]', 'other', 'unknown', 0, 58, 50, 70, NULL, '[]', '[]', 0, NULL, 'medium', 0.29, 'medium', 40.6, NULL, NULL, '', 'Good match (50% skill). Missing: none', 'llama-3.1-8b-instant', 419, 3437, '9dc59af0-c7e9-4844-bb06-2e9a6940b004', '2026-04-03 16:59:51.975964', '2026-04-15 04:24:02.290890');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (79, 'bfd8ae82-e475-4f8d-b7bc-3be7d2c1f3d6', '[]', '[]', '[]', '[]', 0, NULL, 'none', '[]', 'other', 'entry', 0, 58, 50, 70, NULL, '[]', '[]', 0, NULL, 'medium', 0.29, 'easy', 40.6, NULL, NULL, '', 'Good match (50% skill). Missing: none', 'llama-3.1-8b-instant', 401, 4397, '102e821b-bc22-49c7-833c-af834277bf77', '2026-04-03 16:59:54.638162', '2026-04-15 04:24:06.695287');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (80, '91ed63ea-f04c-4113-8605-7b6f04152111', '[]', '[]', '[]', '[]', 0, NULL, 'bachelor', '[]', 'other', 'entry', 0, 58, 50, 70, NULL, '[]', '[]', 0, NULL, 'medium', 0.29, 'easy', 40.6, NULL, NULL, '', 'Good match (50% skill). Missing: none', 'llama-3.1-8b-instant', 379, 4496, '509d6404-e155-4a08-a354-0df1628554f6', '2026-04-03 16:59:57.608318', '2026-04-15 04:24:11.199728');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (81, 'fc0da0d2-4213-4c4d-994a-bda436d4ba6c', '[]', '[]', '[]', '[]', 0, NULL, 'bachelor', '[]', 'business_development', 'mid', 0, 58, 50, 70, NULL, '[]', '[]', 0, NULL, 'medium', 0.29, 'medium', 40.6, NULL, NULL, 'No AI summary available.', 'Good match (50% skill). Missing: none', 'llama-3.1-8b-instant', 426, 3375, 'a7d1c41f-0c95-4828-80c9-05e03628cf3c', '2026-04-03 17:00:00.475415', '2026-04-15 04:24:14.581870');
INSERT OR IGNORE INTO 'job_analyses'(_rowid_, 'job_id', 'required_skills', 'preferred_skills', 'tech_stack', 'ats_keywords', 'min_years_experience', 'max_years_experience', 'education_requirement', 'key_responsibilities', 'role_category', 'seniority_detected', 'is_internship', 'match_score', 'skill_match_score', 'experience_match_score', 'semantic_similarity_score', 'matching_skills', 'missing_skills', 'skill_gap_count', 'estimated_applicants', 'competition_level', 'interview_probability', 'job_difficulty', 'priority_score', 'estimated_salary_min', 'estimated_salary_max', 'ai_summary', 'ai_recommendation', 'model_used', 'tokens_used', 'processing_time_ms', 'id', 'created_at', 'updated_at') VALUES (82, '85a26678-120a-4971-92ad-09817888b003', '[]', '[]', '[]', '[]', 0, NULL, 'none', '[]', 'other', 'none', 0, 58, 50, 70, NULL, '[]', '[]', 0, NULL, 'medium', 0.29, 'easy', 40.6, NULL, NULL, 'No job description provided.', 'Good match (50% skill). Missing: none', 'llama-3.1-8b-instant', 390, 4395, '51b47197-c3bc-4d22-aa26-90c18d486a97', '2026-04-03 17:00:03.649023', '2026-04-15 04:24:18.982382');
INSERT OR IGNORE INTO 'applications'(_rowid_, 'user_id', 'job_id', 'resume_id', 'cover_letter_id', 'status', 'method', 'applied_at', 'viewed_at', 'shortlisted_at', 'interview_scheduled_at', 'offer_received_at', 'rejected_at', 'match_score_at_apply', 'job_title_snapshot', 'company_snapshot', 'recruiter_id', 'recruiter_name', 'recruiter_email', 'recruiter_linkedin', 'follow_up_status', 'follow_up_date', 'follow_up_count', 'last_follow_up_at', 'interview_date', 'interview_type', 'interview_notes', 'interview_feedback', 'offer_salary', 'offer_details', 'bot_session_id', 'bot_error', 'bot_screenshot_path', 'retry_count', 'notes', 'is_starred', 'id', 'created_at', 'updated_at') VALUES (109, '364c6ba3-8669-4f9a-bd50-577322459d4d', '3a9fe65c-ac49-400e-8ce3-ff099644df76', NULL, NULL, 'QUEUED', 'AUTO_BOT', NULL, NULL, NULL, NULL, NULL, NULL, 50, 'Artificial Intelligence (AI)', 'Meta Results', NULL, NULL, NULL, NULL, 'NONE', NULL, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, NULL, 0, '408d1f28-a078-4c85-bd9a-66258714b4b7', '2026-04-04 07:53:07.591096', '2026-04-04 08:32:06.162668');
INSERT OR IGNORE INTO 'applications'(_rowid_, 'user_id', 'job_id', 'resume_id', 'cover_letter_id', 'status', 'method', 'applied_at', 'viewed_at', 'shortlisted_at', 'interview_scheduled_at', 'offer_received_at', 'rejected_at', 'match_score_at_apply', 'job_title_snapshot', 'company_snapshot', 'recruiter_id', 'recruiter_name', 'recruiter_email', 'recruiter_linkedin', 'follow_up_status', 'follow_up_date', 'follow_up_count', 'last_follow_up_at', 'interview_date', 'interview_type', 'interview_notes', 'interview_feedback', 'offer_salary', 'offer_details', 'bot_session_id', 'bot_error', 'bot_screenshot_path', 'retry_count', 'notes', 'is_starred', 'id', 'created_at', 'updated_at') VALUES (110, '364c6ba3-8669-4f9a-bd50-577322459d4d', '7722e288-cb9a-426a-aeeb-0d6aefb68500', NULL, NULL, 'QUEUED', 'AUTO_BOT', NULL, NULL, NULL, NULL, NULL, NULL, 50, 'Artificial Intelligence (AI)', 'Mariox Software Private Limited', NULL, NULL, NULL, NULL, 'NONE', NULL, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, NULL, 0, '1e49a8dd-0820-4c9b-a418-ded44b15d45f', '2026-04-04 07:53:07.591102', '2026-04-04 08:32:06.162664');
INSERT OR IGNORE INTO 'applications'(_rowid_, 'user_id', 'job_id', 'resume_id', 'cover_letter_id', 'status', 'method', 'applied_at', 'viewed_at', 'shortlisted_at', 'interview_scheduled_at', 'offer_received_at', 'rejected_at', 'match_score_at_apply', 'job_title_snapshot', 'company_snapshot', 'recruiter_id', 'recruiter_name', 'recruiter_email', 'recruiter_linkedin', 'follow_up_status', 'follow_up_date', 'follow_up_count', 'last_follow_up_at', 'interview_date', 'interview_type', 'interview_notes', 'interview_feedback', 'offer_salary', 'offer_details', 'bot_session_id', 'bot_error', 'bot_screenshot_path', 'retry_count', 'notes', 'is_starred', 'id', 'created_at', 'updated_at') VALUES (111, '364c6ba3-8669-4f9a-bd50-577322459d4d', '04fed8ab-4db5-42a8-b3a8-8d8845a104b6', NULL, NULL, 'QUEUED', 'AUTO_BOT', NULL, NULL, NULL, NULL, NULL, NULL, 50, 'Machine Learning', 'Career Solutions', NULL, NULL, NULL, NULL, 'NONE', NULL, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, NULL, 0, '4d89ac32-4227-427c-887f-e7bc3b53be8c', '2026-04-04 07:53:07.591108', '2026-04-04 08:32:06.162668');
INSERT OR IGNORE INTO 'applications'(_rowid_, 'user_id', 'job_id', 'resume_id', 'cover_letter_id', 'status', 'method', 'applied_at', 'viewed_at', 'shortlisted_at', 'interview_scheduled_at', 'offer_received_at', 'rejected_at', 'match_score_at_apply', 'job_title_snapshot', 'company_snapshot', 'recruiter_id', 'recruiter_name', 'recruiter_email', 'recruiter_linkedin', 'follow_up_status', 'follow_up_date', 'follow_up_count', 'last_follow_up_at', 'interview_date', 'interview_type', 'interview_notes', 'interview_feedback', 'offer_salary', 'offer_details', 'bot_session_id', 'bot_error', 'bot_screenshot_path', 'retry_count', 'notes', 'is_starred', 'id', 'created_at', 'updated_at') VALUES (112, '364c6ba3-8669-4f9a-bd50-577322459d4d', '2a4a41ed-f71a-4113-942b-244e8e88b269', NULL, NULL, 'QUEUED', 'AUTO_BOT', NULL, NULL, NULL, NULL, NULL, NULL, 50, 'Voice Bot/AI Calling', 'Sankar Group', NULL, NULL, NULL, NULL, 'NONE', NULL, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, NULL, 0, '1f6fc79f-fc0d-4306-821c-185281d64307', '2026-04-04 07:53:07.591115', '2026-04-04 08:32:06.162665');
INSERT OR IGNORE INTO 'applications'(_rowid_, 'user_id', 'job_id', 'resume_id', 'cover_letter_id', 'status', 'method', 'applied_at', 'viewed_at', 'shortlisted_at', 'interview_scheduled_at', 'offer_received_at', 'rejected_at', 'match_score_at_apply', 'job_title_snapshot', 'company_snapshot', 'recruiter_id', 'recruiter_name', 'recruiter_email', 'recruiter_linkedin', 'follow_up_status', 'follow_up_date', 'follow_up_count', 'last_follow_up_at', 'interview_date', 'interview_type', 'interview_notes', 'interview_feedback', 'offer_salary', 'offer_details', 'bot_session_id', 'bot_error', 'bot_screenshot_path', 'retry_count', 'notes', 'is_starred', 'id', 'created_at', 'updated_at') VALUES (113, '364c6ba3-8669-4f9a-bd50-577322459d4d', 'd970c190-3463-4b35-8754-781b123740b5', NULL, NULL, 'QUEUED', 'AUTO_BOT', NULL, NULL, NULL, NULL, NULL, NULL, 50, 'Cloud Infrastructure (OCI/AWS)', 'Global Trend', NULL, NULL, NULL, NULL, 'NONE', NULL, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, NULL, 0, '166a0239-74cc-434a-aef5-e89a81c3a188', '2026-04-04 07:53:07.591121', '2026-04-04 08:32:06.162663');
INSERT OR IGNORE INTO 'applications'(_rowid_, 'user_id', 'job_id', 'resume_id', 'cover_letter_id', 'status', 'method', 'applied_at', 'viewed_at', 'shortlisted_at', 'interview_scheduled_at', 'offer_received_at', 'rejected_at', 'match_score_at_apply', 'job_title_snapshot', 'company_snapshot', 'recruiter_id', 'recruiter_name', 'recruiter_email', 'recruiter_linkedin', 'follow_up_status', 'follow_up_date', 'follow_up_count', 'last_follow_up_at', 'interview_date', 'interview_type', 'interview_notes', 'interview_feedback', 'offer_salary', 'offer_details', 'bot_session_id', 'bot_error', 'bot_screenshot_path', 'retry_count', 'notes', 'is_starred', 'id', 'created_at', 'updated_at') VALUES (114, '364c6ba3-8669-4f9a-bd50-577322459d4d', 'eee5907d-e206-402e-8b64-773556b1a50d', NULL, NULL, 'QUEUED', 'AUTO_BOT', NULL, NULL, NULL, NULL, NULL, NULL, 50, 'Teaching Assistant', 'The Skillians', NULL, NULL, NULL, NULL, 'NONE', NULL, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, NULL, 0, '5274f827-e979-4dc0-a85d-10372e1fa25f', '2026-04-04 07:53:07.591128', '2026-04-04 08:32:06.162668');
INSERT OR IGNORE INTO 'applications'(_rowid_, 'user_id', 'job_id', 'resume_id', 'cover_letter_id', 'status', 'method', 'applied_at', 'viewed_at', 'shortlisted_at', 'interview_scheduled_at', 'offer_received_at', 'rejected_at', 'match_score_at_apply', 'job_title_snapshot', 'company_snapshot', 'recruiter_id', 'recruiter_name', 'recruiter_email', 'recruiter_linkedin', 'follow_up_status', 'follow_up_date', 'follow_up_count', 'last_follow_up_at', 'interview_date', 'interview_type', 'interview_notes', 'interview_feedback', 'offer_salary', 'offer_details', 'bot_session_id', 'bot_error', 'bot_screenshot_path', 'retry_count', 'notes', 'is_starred', 'id', 'created_at', 'updated_at') VALUES (115, '364c6ba3-8669-4f9a-bd50-577322459d4d', '6df957bb-4d56-40bf-9db3-318756841817', NULL, NULL, 'QUEUED', 'AUTO_BOT', NULL, NULL, NULL, NULL, NULL, NULL, 50, 'Data Science', 'Shivam Singh', NULL, NULL, NULL, NULL, 'NONE', NULL, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, NULL, 0, 'c541e063-ab1f-40eb-ba26-1caebaa0f23a', '2026-04-04 07:53:07.591133', '2026-04-04 08:32:06.162669');
INSERT OR IGNORE INTO 'applications'(_rowid_, 'user_id', 'job_id', 'resume_id', 'cover_letter_id', 'status', 'method', 'applied_at', 'viewed_at', 'shortlisted_at', 'interview_scheduled_at', 'offer_received_at', 'rejected_at', 'match_score_at_apply', 'job_title_snapshot', 'company_snapshot', 'recruiter_id', 'recruiter_name', 'recruiter_email', 'recruiter_linkedin', 'follow_up_status', 'follow_up_date', 'follow_up_count', 'last_follow_up_at', 'interview_date', 'interview_type', 'interview_notes', 'interview_feedback', 'offer_salary', 'offer_details', 'bot_session_id', 'bot_error', 'bot_screenshot_path', 'retry_count', 'notes', 'is_starred', 'id', 'created_at', 'updated_at') VALUES (116, '364c6ba3-8669-4f9a-bd50-577322459d4d', 'e3bdac33-fb14-4159-9f24-e7a91a3361b3', NULL, NULL, 'QUEUED', 'AUTO_BOT', NULL, NULL, NULL, NULL, NULL, NULL, 50, 'AI Ad Creative', 'Parmar Techmero Solutions Private Limited', NULL, NULL, NULL, NULL, 'NONE', NULL, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, NULL, 0, '01f4cdbe-2dfe-425a-8e97-aa8354b41a18', '2026-04-04 07:53:07.591139', '2026-04-04 08:32:06.162660');
INSERT OR IGNORE INTO 'applications'(_rowid_, 'user_id', 'job_id', 'resume_id', 'cover_letter_id', 'status', 'method', 'applied_at', 'viewed_at', 'shortlisted_at', 'interview_scheduled_at', 'offer_received_at', 'rejected_at', 'match_score_at_apply', 'job_title_snapshot', 'company_snapshot', 'recruiter_id', 'recruiter_name', 'recruiter_email', 'recruiter_linkedin', 'follow_up_status', 'follow_up_date', 'follow_up_count', 'last_follow_up_at', 'interview_date', 'interview_type', 'interview_notes', 'interview_feedback', 'offer_salary', 'offer_details', 'bot_session_id', 'bot_error', 'bot_screenshot_path', 'retry_count', 'notes', 'is_starred', 'id', 'created_at', 'updated_at') VALUES (117, '364c6ba3-8669-4f9a-bd50-577322459d4d', '7ff66f03-62e3-4bf7-a904-6346c6315ef5', NULL, NULL, 'QUEUED', 'AUTO_BOT', NULL, NULL, NULL, NULL, NULL, NULL, 50, 'Mobile App Development', 'CCBUL', NULL, NULL, NULL, NULL, 'NONE', NULL, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, NULL, 0, '9e4f3733-a245-4c25-bb21-3d38a34f2d3b', '2026-04-04 07:53:07.591144', '2026-04-04 08:32:06.162668');
INSERT OR IGNORE INTO 'applications'(_rowid_, 'user_id', 'job_id', 'resume_id', 'cover_letter_id', 'status', 'method', 'applied_at', 'viewed_at', 'shortlisted_at', 'interview_scheduled_at', 'offer_received_at', 'rejected_at', 'match_score_at_apply', 'job_title_snapshot', 'company_snapshot', 'recruiter_id', 'recruiter_name', 'recruiter_email', 'recruiter_linkedin', 'follow_up_status', 'follow_up_date', 'follow_up_count', 'last_follow_up_at', 'interview_date', 'interview_type', 'interview_notes', 'interview_feedback', 'offer_salary', 'offer_details', 'bot_session_id', 'bot_error', 'bot_screenshot_path', 'retry_count', 'notes', 'is_starred', 'id', 'created_at', 'updated_at') VALUES (118, '364c6ba3-8669-4f9a-bd50-577322459d4d', '76a8c6c2-10db-42f9-89a3-945f6f0136f5', NULL, NULL, 'QUEUED', 'AUTO_BOT', NULL, NULL, NULL, NULL, NULL, NULL, 50, 'Backend Development', 'Hillborn Technologies Private Limited', NULL, NULL, NULL, NULL, 'NONE', NULL, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, NULL, 0, '24514d55-52b8-414e-9e1b-3725a8fdbd04', '2026-04-04 07:53:07.591150', '2026-04-04 08:32:06.162666');
INSERT OR IGNORE INTO 'applications'(_rowid_, 'user_id', 'job_id', 'resume_id', 'cover_letter_id', 'status', 'method', 'applied_at', 'viewed_at', 'shortlisted_at', 'interview_scheduled_at', 'offer_received_at', 'rejected_at', 'match_score_at_apply', 'job_title_snapshot', 'company_snapshot', 'recruiter_id', 'recruiter_name', 'recruiter_email', 'recruiter_linkedin', 'follow_up_status', 'follow_up_date', 'follow_up_count', 'last_follow_up_at', 'interview_date', 'interview_type', 'interview_notes', 'interview_feedback', 'offer_salary', 'offer_details', 'bot_session_id', 'bot_error', 'bot_screenshot_path', 'retry_count', 'notes', 'is_starred', 'id', 'created_at', 'updated_at') VALUES (119, '186abe6d-ed82-4ac6-882e-9d0acb5f3192', '46968754-3766-4c75-9968-8b61cf9d5cfe', 'ff2e4b7e-f5af-4e54-9051-48f631937cfa', NULL, 'FAILED', 'AUTO_BOT', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'AI Agent Development', 'Odisoft Technology Private Limited', NULL, NULL, NULL, NULL, 'NONE', NULL, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Session expired. Run save_cookies.py.', NULL, 2, NULL, 0, '0c797985-a221-4502-aa0a-8f4c7bb9f457', '2026-04-15 15:09:20.288798', '2026-04-15 15:09:49.435861');
INSERT OR IGNORE INTO 'applications'(_rowid_, 'user_id', 'job_id', 'resume_id', 'cover_letter_id', 'status', 'method', 'applied_at', 'viewed_at', 'shortlisted_at', 'interview_scheduled_at', 'offer_received_at', 'rejected_at', 'match_score_at_apply', 'job_title_snapshot', 'company_snapshot', 'recruiter_id', 'recruiter_name', 'recruiter_email', 'recruiter_linkedin', 'follow_up_status', 'follow_up_date', 'follow_up_count', 'last_follow_up_at', 'interview_date', 'interview_type', 'interview_notes', 'interview_feedback', 'offer_salary', 'offer_details', 'bot_session_id', 'bot_error', 'bot_screenshot_path', 'retry_count', 'notes', 'is_starred', 'id', 'created_at', 'updated_at') VALUES (1, '364c6ba3-8669-4f9a-bd50-577322459d4d', '0cfe99bd-93a4-4623-be1e-ab404329f848', NULL, NULL, 'SKIPPED', 'AUTO_BOT', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Artificial Intelligence (AI)', 'LawDocs', NULL, NULL, NULL, NULL, 'NONE', NULL, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Not eligible - Internshala profile requirements not met', NULL, 1, NULL, 0, '59c67a14-6c5c-4245-97e3-281fac031a45', '2026-04-04 06:31:13.680724', '2026-04-04 06:31:35.186113');
INSERT OR IGNORE INTO 'applications'(_rowid_, 'user_id', 'job_id', 'resume_id', 'cover_letter_id', 'status', 'method', 'applied_at', 'viewed_at', 'shortlisted_at', 'interview_scheduled_at', 'offer_received_at', 'rejected_at', 'match_score_at_apply', 'job_title_snapshot', 'company_snapshot', 'recruiter_id', 'recruiter_name', 'recruiter_email', 'recruiter_linkedin', 'follow_up_status', 'follow_up_date', 'follow_up_count', 'last_follow_up_at', 'interview_date', 'interview_type', 'interview_notes', 'interview_feedback', 'offer_salary', 'offer_details', 'bot_session_id', 'bot_error', 'bot_screenshot_path', 'retry_count', 'notes', 'is_starred', 'id', 'created_at', 'updated_at') VALUES (2, '364c6ba3-8669-4f9a-bd50-577322459d4d', '058354ec-0eda-4387-9847-7c9ad97ccbfe', NULL, NULL, 'SKIPPED', 'AUTO_BOT', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Artificial Intelligence (AI)', 'Almost Magic Private Limited', NULL, NULL, NULL, NULL, 'NONE', NULL, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Not eligible - Internshala profile requirements not met', NULL, 1, NULL, 0, 'b0639658-fc65-4b45-9f11-68139ea6a05b', '2026-04-04 06:31:13.680731', '2026-04-04 06:31:47.213407');
INSERT OR IGNORE INTO 'applications'(_rowid_, 'user_id', 'job_id', 'resume_id', 'cover_letter_id', 'status', 'method', 'applied_at', 'viewed_at', 'shortlisted_at', 'interview_scheduled_at', 'offer_received_at', 'rejected_at', 'match_score_at_apply', 'job_title_snapshot', 'company_snapshot', 'recruiter_id', 'recruiter_name', 'recruiter_email', 'recruiter_linkedin', 'follow_up_status', 'follow_up_date', 'follow_up_count', 'last_follow_up_at', 'interview_date', 'interview_type', 'interview_notes', 'interview_feedback', 'offer_salary', 'offer_details', 'bot_session_id', 'bot_error', 'bot_screenshot_path', 'retry_count', 'notes', 'is_starred', 'id', 'created_at', 'updated_at') VALUES (3, '364c6ba3-8669-4f9a-bd50-577322459d4d', '769910c5-0560-481f-afec-b05b60ef97d3', NULL, NULL, 'SKIPPED', 'AUTO_BOT', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Data Engineer Intern', 'Cardinal Health', NULL, NULL, NULL, NULL, 'NONE', NULL, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Not eligible - Internshala profile requirements not met', NULL, 1, NULL, 0, '94d25d4e-b2ea-4bfa-b40e-8d1206197f04', '2026-04-04 06:31:13.680735', '2026-04-04 06:31:58.426809');
INSERT OR IGNORE INTO 'applications'(_rowid_, 'user_id', 'job_id', 'resume_id', 'cover_letter_id', 'status', 'method', 'applied_at', 'viewed_at', 'shortlisted_at', 'interview_scheduled_at', 'offer_received_at', 'rejected_at', 'match_score_at_apply', 'job_title_snapshot', 'company_snapshot', 'recruiter_id', 'recruiter_name', 'recruiter_email', 'recruiter_linkedin', 'follow_up_status', 'follow_up_date', 'follow_up_count', 'last_follow_up_at', 'interview_date', 'interview_type', 'interview_notes', 'interview_feedback', 'offer_salary', 'offer_details', 'bot_session_id', 'bot_error', 'bot_screenshot_path', 'retry_count', 'notes', 'is_starred', 'id', 'created_at', 'updated_at') VALUES (4, '364c6ba3-8669-4f9a-bd50-577322459d4d', 'cd9392bb-e927-4f13-b3e9-38b5b1441f20', NULL, NULL, 'SKIPPED', 'AUTO_BOT', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'AI Intern', 'Astra Security', NULL, NULL, NULL, NULL, 'NONE', NULL, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Not eligible - Internshala profile requirements not met', NULL, 1, NULL, 0, 'c80f54d8-47b5-4771-8b43-8b890f331ee5', '2026-04-04 06:31:13.680738', '2026-04-04 06:32:09.545315');
INSERT OR IGNORE INTO 'applications'(_rowid_, 'user_id', 'job_id', 'resume_id', 'cover_letter_id', 'status', 'method', 'applied_at', 'viewed_at', 'shortlisted_at', 'interview_scheduled_at', 'offer_received_at', 'rejected_at', 'match_score_at_apply', 'job_title_snapshot', 'company_snapshot', 'recruiter_id', 'recruiter_name', 'recruiter_email', 'recruiter_linkedin', 'follow_up_status', 'follow_up_date', 'follow_up_count', 'last_follow_up_at', 'interview_date', 'interview_type', 'interview_notes', 'interview_feedback', 'offer_salary', 'offer_details', 'bot_session_id', 'bot_error', 'bot_screenshot_path', 'retry_count', 'notes', 'is_starred', 'id', 'created_at', 'updated_at') VALUES (5, '364c6ba3-8669-4f9a-bd50-577322459d4d', '1ef0f01a-e764-483f-8f56-09f2d69304bf', NULL, NULL, 'SKIPPED', 'AUTO_BOT', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Machine Learning Trainee', 'CodeTikki WorkSpace', NULL, NULL, NULL, NULL, 'NONE', NULL, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Not eligible - Internshala profile requirements not met', NULL, 1, NULL, 0, '99a5bc13-c83e-4e02-abe6-7faff8709464', '2026-04-04 06:31:13.680741', '2026-04-04 06:32:21.114544');
INSERT OR IGNORE INTO 'applications'(_rowid_, 'user_id', 'job_id', 'resume_id', 'cover_letter_id', 'status', 'method', 'applied_at', 'viewed_at', 'shortlisted_at', 'interview_scheduled_at', 'offer_received_at', 'rejected_at', 'match_score_at_apply', 'job_title_snapshot', 'company_snapshot', 'recruiter_id', 'recruiter_name', 'recruiter_email', 'recruiter_linkedin', 'follow_up_status', 'follow_up_date', 'follow_up_count', 'last_follow_up_at', 'interview_date', 'interview_type', 'interview_notes', 'interview_feedback', 'offer_salary', 'offer_details', 'bot_session_id', 'bot_error', 'bot_screenshot_path', 'retry_count', 'notes', 'is_starred', 'id', 'created_at', 'updated_at') VALUES (6, '364c6ba3-8669-4f9a-bd50-577322459d4d', '99138747-d070-4c7f-94a1-4ed6c2ae7b59', NULL, NULL, 'SKIPPED', 'AUTO_BOT', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'AI Magician', 'GNG Developers', NULL, NULL, NULL, NULL, 'NONE', NULL, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Not eligible - Internshala profile requirements not met', NULL, 1, NULL, 0, '827bfa55-007a-424e-bd5b-96b95bf111d3', '2026-04-04 06:31:13.680745', '2026-04-04 06:32:33.326262');
INSERT OR IGNORE INTO 'applications'(_rowid_, 'user_id', 'job_id', 'resume_id', 'cover_letter_id', 'status', 'method', 'applied_at', 'viewed_at', 'shortlisted_at', 'interview_scheduled_at', 'offer_received_at', 'rejected_at', 'match_score_at_apply', 'job_title_snapshot', 'company_snapshot', 'recruiter_id', 'recruiter_name', 'recruiter_email', 'recruiter_linkedin', 'follow_up_status', 'follow_up_date', 'follow_up_count', 'last_follow_up_at', 'interview_date', 'interview_type', 'interview_notes', 'interview_feedback', 'offer_salary', 'offer_details', 'bot_session_id', 'bot_error', 'bot_screenshot_path', 'retry_count', 'notes', 'is_starred', 'id', 'created_at', 'updated_at') VALUES (7, '364c6ba3-8669-4f9a-bd50-577322459d4d', '7f080d3e-16d3-42d4-965f-266c46165c35', NULL, NULL, 'SKIPPED', 'AUTO_BOT', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Artificial Intelligence (AI)', 'Assetcues Solutions Private Limited', NULL, NULL, NULL, NULL, 'NONE', NULL, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Not eligible - Internshala profile requirements not met', NULL, 1, NULL, 0, 'b5e4eea6-141e-4e69-9e08-40c9740401b4', '2026-04-04 06:31:13.680748', '2026-04-04 06:32:44.895527');
INSERT OR IGNORE INTO 'applications'(_rowid_, 'user_id', 'job_id', 'resume_id', 'cover_letter_id', 'status', 'method', 'applied_at', 'viewed_at', 'shortlisted_at', 'interview_scheduled_at', 'offer_received_at', 'rejected_at', 'match_score_at_apply', 'job_title_snapshot', 'company_snapshot', 'recruiter_id', 'recruiter_name', 'recruiter_email', 'recruiter_linkedin', 'follow_up_status', 'follow_up_date', 'follow_up_count', 'last_follow_up_at', 'interview_date', 'interview_type', 'interview_notes', 'interview_feedback', 'offer_salary', 'offer_details', 'bot_session_id', 'bot_error', 'bot_screenshot_path', 'retry_count', 'notes', 'is_starred', 'id', 'created_at', 'updated_at') VALUES (8, '364c6ba3-8669-4f9a-bd50-577322459d4d', 'a6d39891-deb9-443c-af34-2cbfdc3969aa', NULL, NULL, 'SKIPPED', 'AUTO_BOT', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Artificial Intelligence (AI)', 'Arhant Solutions', NULL, NULL, NULL, NULL, 'NONE', NULL, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Not eligible - Internshala profile requirements not met', NULL, 1, NULL, 0, '780b843c-0f0a-44cb-bcdb-ec99909b59b6', '2026-04-04 06:31:13.680751', '2026-04-04 06:32:57.162860');
INSERT OR IGNORE INTO 'applications'(_rowid_, 'user_id', 'job_id', 'resume_id', 'cover_letter_id', 'status', 'method', 'applied_at', 'viewed_at', 'shortlisted_at', 'interview_scheduled_at', 'offer_received_at', 'rejected_at', 'match_score_at_apply', 'job_title_snapshot', 'company_snapshot', 'recruiter_id', 'recruiter_name', 'recruiter_email', 'recruiter_linkedin', 'follow_up_status', 'follow_up_date', 'follow_up_count', 'last_follow_up_at', 'interview_date', 'interview_type', 'interview_notes', 'interview_feedback', 'offer_salary', 'offer_details', 'bot_session_id', 'bot_error', 'bot_screenshot_path', 'retry_count', 'notes', 'is_starred', 'id', 'created_at', 'updated_at') VALUES (9, '364c6ba3-8669-4f9a-bd50-577322459d4d', 'aa90aee3-119b-4707-b8ca-1942df261edc', NULL, NULL, 'SKIPPED', 'AUTO_BOT', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Computer Vision', 'Euphotic Labs Private Limited', NULL, NULL, NULL, NULL, 'NONE', NULL, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Not eligible - Internshala profile requirements not met', NULL, 1, NULL, 0, '57707260-9306-40bb-a61f-f66f67f0d516', '2026-04-04 06:31:13.680754', '2026-04-04 06:33:08.959290');
INSERT OR IGNORE INTO 'applications'(_rowid_, 'user_id', 'job_id', 'resume_id', 'cover_letter_id', 'status', 'method', 'applied_at', 'viewed_at', 'shortlisted_at', 'interview_scheduled_at', 'offer_received_at', 'rejected_at', 'match_score_at_apply', 'job_title_snapshot', 'company_snapshot', 'recruiter_id', 'recruiter_name', 'recruiter_email', 'recruiter_linkedin', 'follow_up_status', 'follow_up_date', 'follow_up_count', 'last_follow_up_at', 'interview_date', 'interview_type', 'interview_notes', 'interview_feedback', 'offer_salary', 'offer_details', 'bot_session_id', 'bot_error', 'bot_screenshot_path', 'retry_count', 'notes', 'is_starred', 'id', 'created_at', 'updated_at') VALUES (10, '364c6ba3-8669-4f9a-bd50-577322459d4d', '42ac7894-d380-46e2-aa9f-73eea07b6297', NULL, NULL, 'SKIPPED', 'AUTO_BOT', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'AI Agent Development', 'TZURONI LTD. (Kefar Sava, Israel)', NULL, NULL, NULL, NULL, 'NONE', NULL, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Not eligible - Internshala profile requirements not met', NULL, 1, NULL, 0, '774c9cec-f701-4b40-b7ca-523f6d57cc9e', '2026-04-04 06:31:13.680758', '2026-04-04 06:33:23.934092');
INSERT OR IGNORE INTO 'applications'(_rowid_, 'user_id', 'job_id', 'resume_id', 'cover_letter_id', 'status', 'method', 'applied_at', 'viewed_at', 'shortlisted_at', 'interview_scheduled_at', 'offer_received_at', 'rejected_at', 'match_score_at_apply', 'job_title_snapshot', 'company_snapshot', 'recruiter_id', 'recruiter_name', 'recruiter_email', 'recruiter_linkedin', 'follow_up_status', 'follow_up_date', 'follow_up_count', 'last_follow_up_at', 'interview_date', 'interview_type', 'interview_notes', 'interview_feedback', 'offer_salary', 'offer_details', 'bot_session_id', 'bot_error', 'bot_screenshot_path', 'retry_count', 'notes', 'is_starred', 'id', 'created_at', 'updated_at') VALUES (11, '364c6ba3-8669-4f9a-bd50-577322459d4d', 'c2aff95f-854e-4ac7-9f3b-0db32913c41e', NULL, NULL, 'SKIPPED', 'AUTO_BOT', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Data Analytics', 'VIZON', NULL, NULL, NULL, NULL, 'NONE', NULL, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Not eligible - Internshala profile requirements not met', NULL, 1, NULL, 0, '69743163-2458-4a18-b2e6-435b283bde77', '2026-04-04 06:31:13.680761', '2026-04-04 06:34:57.435370');
INSERT OR IGNORE INTO 'applications'(_rowid_, 'user_id', 'job_id', 'resume_id', 'cover_letter_id', 'status', 'method', 'applied_at', 'viewed_at', 'shortlisted_at', 'interview_scheduled_at', 'offer_received_at', 'rejected_at', 'match_score_at_apply', 'job_title_snapshot', 'company_snapshot', 'recruiter_id', 'recruiter_name', 'recruiter_email', 'recruiter_linkedin', 'follow_up_status', 'follow_up_date', 'follow_up_count', 'last_follow_up_at', 'interview_date', 'interview_type', 'interview_notes', 'interview_feedback', 'offer_salary', 'offer_details', 'bot_session_id', 'bot_error', 'bot_screenshot_path', 'retry_count', 'notes', 'is_starred', 'id', 'created_at', 'updated_at') VALUES (12, '364c6ba3-8669-4f9a-bd50-577322459d4d', '3487a4cf-2f1a-4ef0-ad9c-ad26c5072a15', NULL, NULL, 'SKIPPED', 'AUTO_BOT', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Artificial Intelligence (AI)', 'Raviraj Sarees Pvt Ltd', NULL, NULL, NULL, NULL, 'NONE', NULL, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Not eligible - Internshala profile requirements not met', NULL, 1, NULL, 0, 'a4557f6e-c294-4adf-a56c-c0672b160ff4', '2026-04-04 06:31:13.680764', '2026-04-04 06:35:09.895960');
INSERT OR IGNORE INTO 'applications'(_rowid_, 'user_id', 'job_id', 'resume_id', 'cover_letter_id', 'status', 'method', 'applied_at', 'viewed_at', 'shortlisted_at', 'interview_scheduled_at', 'offer_received_at', 'rejected_at', 'match_score_at_apply', 'job_title_snapshot', 'company_snapshot', 'recruiter_id', 'recruiter_name', 'recruiter_email', 'recruiter_linkedin', 'follow_up_status', 'follow_up_date', 'follow_up_count', 'last_follow_up_at', 'interview_date', 'interview_type', 'interview_notes', 'interview_feedback', 'offer_salary', 'offer_details', 'bot_session_id', 'bot_error', 'bot_screenshot_path', 'retry_count', 'notes', 'is_starred', 'id', 'created_at', 'updated_at') VALUES (13, '364c6ba3-8669-4f9a-bd50-577322459d4d', 'd2af74a3-439e-4cc4-b259-f1f65691269f', NULL, NULL, 'SKIPPED', 'AUTO_BOT', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'AI Robotics Trainer', 'KlassWAY', NULL, NULL, NULL, NULL, 'NONE', NULL, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Not eligible - Internshala profile requirements not met', NULL, 1, NULL, 0, 'f1e8682b-c2b8-4100-acc8-5722576759df', '2026-04-04 06:31:13.680767', '2026-04-04 06:35:21.916649');
INSERT OR IGNORE INTO 'applications'(_rowid_, 'user_id', 'job_id', 'resume_id', 'cover_letter_id', 'status', 'method', 'applied_at', 'viewed_at', 'shortlisted_at', 'interview_scheduled_at', 'offer_received_at', 'rejected_at', 'match_score_at_apply', 'job_title_snapshot', 'company_snapshot', 'recruiter_id', 'recruiter_name', 'recruiter_email', 'recruiter_linkedin', 'follow_up_status', 'follow_up_date', 'follow_up_count', 'last_follow_up_at', 'interview_date', 'interview_type', 'interview_notes', 'interview_feedback', 'offer_salary', 'offer_details', 'bot_session_id', 'bot_error', 'bot_screenshot_path', 'retry_count', 'notes', 'is_starred', 'id', 'created_at', 'updated_at') VALUES (14, '364c6ba3-8669-4f9a-bd50-577322459d4d', '77be3aa2-ae1e-46b9-a8c7-ffbfee39929d', NULL, NULL, 'SKIPPED', 'AUTO_BOT', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'AI Agent Development', 'Aadi Foundation', NULL, NULL, NULL, NULL, 'NONE', NULL, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Not eligible - Internshala profile requirements not met', NULL, 1, NULL, 0, '0eb4dd51-3715-40be-8d99-60f3acd81f54', '2026-04-04 06:31:13.680771', '2026-04-04 06:35:33.650407');
INSERT OR IGNORE INTO 'applications'(_rowid_, 'user_id', 'job_id', 'resume_id', 'cover_letter_id', 'status', 'method', 'applied_at', 'viewed_at', 'shortlisted_at', 'interview_scheduled_at', 'offer_received_at', 'rejected_at', 'match_score_at_apply', 'job_title_snapshot', 'company_snapshot', 'recruiter_id', 'recruiter_name', 'recruiter_email', 'recruiter_linkedin', 'follow_up_status', 'follow_up_date', 'follow_up_count', 'last_follow_up_at', 'interview_date', 'interview_type', 'interview_notes', 'interview_feedback', 'offer_salary', 'offer_details', 'bot_session_id', 'bot_error', 'bot_screenshot_path', 'retry_count', 'notes', 'is_starred', 'id', 'created_at', 'updated_at') VALUES (15, '364c6ba3-8669-4f9a-bd50-577322459d4d', '92cc66af-11f2-4c2a-b425-71dfc9587d96', NULL, NULL, 'SKIPPED', 'AUTO_BOT', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Artificial Intelligence (AI)', 'CareerNest', NULL, NULL, NULL, NULL, 'NONE', NULL, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Not eligible - Internshala profile requirements not met', NULL, 1, NULL, 0, '73593490-756c-4922-a157-cafb32232f78', '2026-04-04 06:31:13.680774', '2026-04-04 06:35:45.481516');
INSERT OR IGNORE INTO 'applications'(_rowid_, 'user_id', 'job_id', 'resume_id', 'cover_letter_id', 'status', 'method', 'applied_at', 'viewed_at', 'shortlisted_at', 'interview_scheduled_at', 'offer_received_at', 'rejected_at', 'match_score_at_apply', 'job_title_snapshot', 'company_snapshot', 'recruiter_id', 'recruiter_name', 'recruiter_email', 'recruiter_linkedin', 'follow_up_status', 'follow_up_date', 'follow_up_count', 'last_follow_up_at', 'interview_date', 'interview_type', 'interview_notes', 'interview_feedback', 'offer_salary', 'offer_details', 'bot_session_id', 'bot_error', 'bot_screenshot_path', 'retry_count', 'notes', 'is_starred', 'id', 'created_at', 'updated_at') VALUES (16, '364c6ba3-8669-4f9a-bd50-577322459d4d', '20b6ef13-6b70-4b8b-815b-44ef9870fd1a', NULL, NULL, 'SKIPPED', 'AUTO_BOT', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Machine Learning And Web Development', 'Greenleap Robotics Private Limited', NULL, NULL, NULL, NULL, 'NONE', NULL, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Not eligible - Internshala profile requirements not met', NULL, 1, NULL, 0, '9552c93d-0b9e-486d-aafb-12f969106a1d', '2026-04-04 06:31:13.680777', '2026-04-04 06:35:56.652635');
INSERT OR IGNORE INTO 'applications'(_rowid_, 'user_id', 'job_id', 'resume_id', 'cover_letter_id', 'status', 'method', 'applied_at', 'viewed_at', 'shortlisted_at', 'interview_scheduled_at', 'offer_received_at', 'rejected_at', 'match_score_at_apply', 'job_title_snapshot', 'company_snapshot', 'recruiter_id', 'recruiter_name', 'recruiter_email', 'recruiter_linkedin', 'follow_up_status', 'follow_up_date', 'follow_up_count', 'last_follow_up_at', 'interview_date', 'interview_type', 'interview_notes', 'interview_feedback', 'offer_salary', 'offer_details', 'bot_session_id', 'bot_error', 'bot_screenshot_path', 'retry_count', 'notes', 'is_starred', 'id', 'created_at', 'updated_at') VALUES (17, '364c6ba3-8669-4f9a-bd50-577322459d4d', 'f64ba568-5424-4292-b434-5548dc79687e', NULL, NULL, 'SKIPPED', 'AUTO_BOT', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Artificial Intelligence (AI)', 'Emoolar Technology Private Limited', NULL, NULL, NULL, NULL, 'NONE', NULL, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Not eligible - Internshala profile requirements not met', NULL, 1, NULL, 0, 'd41b0744-9bb3-4ab5-a511-99d1b44b893f', '2026-04-04 06:31:13.680780', '2026-04-04 06:36:08.467417');
INSERT OR IGNORE INTO 'applications'(_rowid_, 'user_id', 'job_id', 'resume_id', 'cover_letter_id', 'status', 'method', 'applied_at', 'viewed_at', 'shortlisted_at', 'interview_scheduled_at', 'offer_received_at', 'rejected_at', 'match_score_at_apply', 'job_title_snapshot', 'company_snapshot', 'recruiter_id', 'recruiter_name', 'recruiter_email', 'recruiter_linkedin', 'follow_up_status', 'follow_up_date', 'follow_up_count', 'last_follow_up_at', 'interview_date', 'interview_type', 'interview_notes', 'interview_feedback', 'offer_salary', 'offer_details', 'bot_session_id', 'bot_error', 'bot_screenshot_path', 'retry_count', 'notes', 'is_starred', 'id', 'created_at', 'updated_at') VALUES (18, '364c6ba3-8669-4f9a-bd50-577322459d4d', 'e671f1af-3593-4b62-9060-41a6c8e98818', NULL, NULL, 'SKIPPED', 'AUTO_BOT', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Cloud And Machine Learning (AWS SageMaker)', 'Safecity (Red Dot Foundation)', NULL, NULL, NULL, NULL, 'NONE', NULL, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Not eligible - Internshala profile requirements not met', NULL, 1, NULL, 0, '58ed19d3-9250-4bfa-b118-97cf79f675bc', '2026-04-04 06:31:13.680783', '2026-04-04 06:36:20.186502');
INSERT OR IGNORE INTO 'applications'(_rowid_, 'user_id', 'job_id', 'resume_id', 'cover_letter_id', 'status', 'method', 'applied_at', 'viewed_at', 'shortlisted_at', 'interview_scheduled_at', 'offer_received_at', 'rejected_at', 'match_score_at_apply', 'job_title_snapshot', 'company_snapshot', 'recruiter_id', 'recruiter_name', 'recruiter_email', 'recruiter_linkedin', 'follow_up_status', 'follow_up_date', 'follow_up_count', 'last_follow_up_at', 'interview_date', 'interview_type', 'interview_notes', 'interview_feedback', 'offer_salary', 'offer_details', 'bot_session_id', 'bot_error', 'bot_screenshot_path', 'retry_count', 'notes', 'is_starred', 'id', 'created_at', 'updated_at') VALUES (19, '364c6ba3-8669-4f9a-bd50-577322459d4d', '5f1fb82e-143d-4b35-86ce-4d77a15ac4e3', NULL, NULL, 'SKIPPED', 'AUTO_BOT', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Machine Learning', 'Cloud Back', NULL, NULL, NULL, NULL, 'NONE', NULL, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Not eligible - Internshala profile requirements not met', NULL, 1, NULL, 0, '988ec099-6346-4a9f-83ea-d94ac5fad080', '2026-04-04 06:31:13.680786', '2026-04-04 06:36:31.808298');
INSERT OR IGNORE INTO 'applications'(_rowid_, 'user_id', 'job_id', 'resume_id', 'cover_letter_id', 'status', 'method', 'applied_at', 'viewed_at', 'shortlisted_at', 'interview_scheduled_at', 'offer_received_at', 'rejected_at', 'match_score_at_apply', 'job_title_snapshot', 'company_snapshot', 'recruiter_id', 'recruiter_name', 'recruiter_email', 'recruiter_linkedin', 'follow_up_status', 'follow_up_date', 'follow_up_count', 'last_follow_up_at', 'interview_date', 'interview_type', 'interview_notes', 'interview_feedback', 'offer_salary', 'offer_details', 'bot_session_id', 'bot_error', 'bot_screenshot_path', 'retry_count', 'notes', 'is_starred', 'id', 'created_at', 'updated_at') VALUES (20, '364c6ba3-8669-4f9a-bd50-577322459d4d', 'bcd7218f-2527-4412-ba8d-3460caefd5f0', NULL, NULL, 'SKIPPED', 'AUTO_BOT', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Python Development', 'Cloud Back', NULL, NULL, NULL, NULL, 'NONE', NULL, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Not eligible - Internshala profile requirements not met', NULL, 1, NULL, 0, 'd0a69c64-16ac-4586-97d9-d90768b77877', '2026-04-04 06:31:13.680789', '2026-04-04 06:36:43.034150');
INSERT OR IGNORE INTO 'applications'(_rowid_, 'user_id', 'job_id', 'resume_id', 'cover_letter_id', 'status', 'method', 'applied_at', 'viewed_at', 'shortlisted_at', 'interview_scheduled_at', 'offer_received_at', 'rejected_at', 'match_score_at_apply', 'job_title_snapshot', 'company_snapshot', 'recruiter_id', 'recruiter_name', 'recruiter_email', 'recruiter_linkedin', 'follow_up_status', 'follow_up_date', 'follow_up_count', 'last_follow_up_at', 'interview_date', 'interview_type', 'interview_notes', 'interview_feedback', 'offer_salary', 'offer_details', 'bot_session_id', 'bot_error', 'bot_screenshot_path', 'retry_count', 'notes', 'is_starred', 'id', 'created_at', 'updated_at') VALUES (21, '364c6ba3-8669-4f9a-bd50-577322459d4d', 'b5bf7690-5f76-4955-ac34-9b70e52f1529', NULL, NULL, 'SKIPPED', 'AUTO_BOT', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'AI Team Lead', 'Expose Trendze', NULL, NULL, NULL, NULL, 'NONE', NULL, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Not eligible - Internshala profile requirements not met', NULL, 1, NULL, 0, '63870de7-f3cc-49c7-a7db-576368934cd6', '2026-04-04 06:31:13.680792', '2026-04-04 06:38:58.286447');
INSERT OR IGNORE INTO 'applications'(_rowid_, 'user_id', 'job_id', 'resume_id', 'cover_letter_id', 'status', 'method', 'applied_at', 'viewed_at', 'shortlisted_at', 'interview_scheduled_at', 'offer_received_at', 'rejected_at', 'match_score_at_apply', 'job_title_snapshot', 'company_snapshot', 'recruiter_id', 'recruiter_name', 'recruiter_email', 'recruiter_linkedin', 'follow_up_status', 'follow_up_date', 'follow_up_count', 'last_follow_up_at', 'interview_date', 'interview_type', 'interview_notes', 'interview_feedback', 'offer_salary', 'offer_details', 'bot_session_id', 'bot_error', 'bot_screenshot_path', 'retry_count', 'notes', 'is_starred', 'id', 'created_at', 'updated_at') VALUES (22, '364c6ba3-8669-4f9a-bd50-577322459d4d', '350726b2-86d5-402b-90e4-a0c7613d9fe6', NULL, NULL, 'SKIPPED', 'AUTO_BOT', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Data Science', 'Emoolar Technology Private Limited', NULL, NULL, NULL, NULL, 'NONE', NULL, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Not eligible - Internshala profile requirements not met', NULL, 1, NULL, 0, 'cd1a901b-a9a8-43a8-a1f8-2b86d76487dc', '2026-04-04 06:31:13.680796', '2026-04-04 06:39:09.856742');
INSERT OR IGNORE INTO 'applications'(_rowid_, 'user_id', 'job_id', 'resume_id', 'cover_letter_id', 'status', 'method', 'applied_at', 'viewed_at', 'shortlisted_at', 'interview_scheduled_at', 'offer_received_at', 'rejected_at', 'match_score_at_apply', 'job_title_snapshot', 'company_snapshot', 'recruiter_id', 'recruiter_name', 'recruiter_email', 'recruiter_linkedin', 'follow_up_status', 'follow_up_date', 'follow_up_count', 'last_follow_up_at', 'interview_date', 'interview_type', 'interview_notes', 'interview_feedback', 'offer_salary', 'offer_details', 'bot_session_id', 'bot_error', 'bot_screenshot_path', 'retry_count', 'notes', 'is_starred', 'id', 'created_at', 'updated_at') VALUES (23, '364c6ba3-8669-4f9a-bd50-577322459d4d', 'ef6c98cd-0a22-4243-a39e-8bb3e64ddb0a', NULL, NULL, 'SKIPPED', 'AUTO_BOT', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Artificial Intelligence (AI)', 'Reducate.ai', NULL, NULL, NULL, NULL, 'NONE', NULL, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Not eligible - Internshala profile requirements not met', NULL, 1, NULL, 0, '3f6f12d5-9556-4f7b-acff-9e24ebb54b78', '2026-04-04 06:31:13.680799', '2026-04-04 06:39:21.369261');
INSERT OR IGNORE INTO 'applications'(_rowid_, 'user_id', 'job_id', 'resume_id', 'cover_letter_id', 'status', 'method', 'applied_at', 'viewed_at', 'shortlisted_at', 'interview_scheduled_at', 'offer_received_at', 'rejected_at', 'match_score_at_apply', 'job_title_snapshot', 'company_snapshot', 'recruiter_id', 'recruiter_name', 'recruiter_email', 'recruiter_linkedin', 'follow_up_status', 'follow_up_date', 'follow_up_count', 'last_follow_up_at', 'interview_date', 'interview_type', 'interview_notes', 'interview_feedback', 'offer_salary', 'offer_details', 'bot_session_id', 'bot_error', 'bot_screenshot_path', 'retry_count', 'notes', 'is_starred', 'id', 'created_at', 'updated_at') VALUES (24, '364c6ba3-8669-4f9a-bd50-577322459d4d', '06759dd8-7d7c-4d3f-b125-d7fef40399fb', NULL, NULL, 'SKIPPED', 'AUTO_BOT', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Python Development', 'Mindenious Edutech', NULL, NULL, NULL, NULL, 'NONE', NULL, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Not eligible - Internshala profile requirements not met', NULL, 1, NULL, 0, 'a0b78b83-6ad4-4993-a164-d0e57bd8790a', '2026-04-04 06:31:13.680802', '2026-04-04 06:39:32.827669');
INSERT OR IGNORE INTO 'applications'(_rowid_, 'user_id', 'job_id', 'resume_id', 'cover_letter_id', 'status', 'method', 'applied_at', 'viewed_at', 'shortlisted_at', 'interview_scheduled_at', 'offer_received_at', 'rejected_at', 'match_score_at_apply', 'job_title_snapshot', 'company_snapshot', 'recruiter_id', 'recruiter_name', 'recruiter_email', 'recruiter_linkedin', 'follow_up_status', 'follow_up_date', 'follow_up_count', 'last_follow_up_at', 'interview_date', 'interview_type', 'interview_notes', 'interview_feedback', 'offer_salary', 'offer_details', 'bot_session_id', 'bot_error', 'bot_screenshot_path', 'retry_count', 'notes', 'is_starred', 'id', 'created_at', 'updated_at') VALUES (25, '364c6ba3-8669-4f9a-bd50-577322459d4d', '001f713e-b1d2-4fd5-8f34-5789fb5b710e', NULL, NULL, 'SKIPPED', 'AUTO_BOT', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Data Science', 'Mindenious Edutech', NULL, NULL, NULL, NULL, 'NONE', NULL, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Not eligible - Internshala profile requirements not met', NULL, 1, NULL, 0, '74d13914-70b4-4128-8c3e-940e5388a153', '2026-04-04 06:31:13.680805', '2026-04-04 06:39:44.301273');
INSERT OR IGNORE INTO 'applications'(_rowid_, 'user_id', 'job_id', 'resume_id', 'cover_letter_id', 'status', 'method', 'applied_at', 'viewed_at', 'shortlisted_at', 'interview_scheduled_at', 'offer_received_at', 'rejected_at', 'match_score_at_apply', 'job_title_snapshot', 'company_snapshot', 'recruiter_id', 'recruiter_name', 'recruiter_email', 'recruiter_linkedin', 'follow_up_status', 'follow_up_date', 'follow_up_count', 'last_follow_up_at', 'interview_date', 'interview_type', 'interview_notes', 'interview_feedback', 'offer_salary', 'offer_details', 'bot_session_id', 'bot_error', 'bot_screenshot_path', 'retry_count', 'notes', 'is_starred', 'id', 'created_at', 'updated_at') VALUES (26, '364c6ba3-8669-4f9a-bd50-577322459d4d', 'f983c546-f677-4b6c-8296-23b4111025ce', NULL, NULL, 'SKIPPED', 'AUTO_BOT', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Data Science', 'URHRO', NULL, NULL, NULL, NULL, 'NONE', NULL, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Not eligible - Internshala profile requirements not met', NULL, 1, NULL, 0, 'ac99e8ce-a243-4771-8055-97520c492b6c', '2026-04-04 06:31:13.680808', '2026-04-04 06:39:55.516616');
INSERT OR IGNORE INTO 'applications'(_rowid_, 'user_id', 'job_id', 'resume_id', 'cover_letter_id', 'status', 'method', 'applied_at', 'viewed_at', 'shortlisted_at', 'interview_scheduled_at', 'offer_received_at', 'rejected_at', 'match_score_at_apply', 'job_title_snapshot', 'company_snapshot', 'recruiter_id', 'recruiter_name', 'recruiter_email', 'recruiter_linkedin', 'follow_up_status', 'follow_up_date', 'follow_up_count', 'last_follow_up_at', 'interview_date', 'interview_type', 'interview_notes', 'interview_feedback', 'offer_salary', 'offer_details', 'bot_session_id', 'bot_error', 'bot_screenshot_path', 'retry_count', 'notes', 'is_starred', 'id', 'created_at', 'updated_at') VALUES (27, '364c6ba3-8669-4f9a-bd50-577322459d4d', '87224bf9-90e0-41cf-8377-c1cca6e97d0b', NULL, NULL, 'SKIPPED', 'AUTO_BOT', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Python Development', 'Symonis', NULL, NULL, NULL, NULL, 'NONE', NULL, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Not eligible - Internshala profile requirements not met', NULL, 1, NULL, 0, '19739815-76f9-4581-874c-f627357610e8', '2026-04-04 06:31:13.680811', '2026-04-04 06:40:08.166311');
INSERT OR IGNORE INTO 'applications'(_rowid_, 'user_id', 'job_id', 'resume_id', 'cover_letter_id', 'status', 'method', 'applied_at', 'viewed_at', 'shortlisted_at', 'interview_scheduled_at', 'offer_received_at', 'rejected_at', 'match_score_at_apply', 'job_title_snapshot', 'company_snapshot', 'recruiter_id', 'recruiter_name', 'recruiter_email', 'recruiter_linkedin', 'follow_up_status', 'follow_up_date', 'follow_up_count', 'last_follow_up_at', 'interview_date', 'interview_type', 'interview_notes', 'interview_feedback', 'offer_salary', 'offer_details', 'bot_session_id', 'bot_error', 'bot_screenshot_path', 'retry_count', 'notes', 'is_starred', 'id', 'created_at', 'updated_at') VALUES (28, '364c6ba3-8669-4f9a-bd50-577322459d4d', '51895afe-478b-4bed-b585-a1230cc8cbaa', NULL, NULL, 'SKIPPED', 'AUTO_BOT', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Machine Learning', 'Anubhav Singh', NULL, NULL, NULL, NULL, 'NONE', NULL, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Not eligible - Internshala profile requirements not met', NULL, 1, NULL, 0, 'bdaadc26-3a88-4d3e-80a1-5bcb8ea3e4bf', '2026-04-04 06:31:13.680814', '2026-04-04 06:40:20.183794');
INSERT OR IGNORE INTO 'applications'(_rowid_, 'user_id', 'job_id', 'resume_id', 'cover_letter_id', 'status', 'method', 'applied_at', 'viewed_at', 'shortlisted_at', 'interview_scheduled_at', 'offer_received_at', 'rejected_at', 'match_score_at_apply', 'job_title_snapshot', 'company_snapshot', 'recruiter_id', 'recruiter_name', 'recruiter_email', 'recruiter_linkedin', 'follow_up_status', 'follow_up_date', 'follow_up_count', 'last_follow_up_at', 'interview_date', 'interview_type', 'interview_notes', 'interview_feedback', 'offer_salary', 'offer_details', 'bot_session_id', 'bot_error', 'bot_screenshot_path', 'retry_count', 'notes', 'is_starred', 'id', 'created_at', 'updated_at') VALUES (29, '364c6ba3-8669-4f9a-bd50-577322459d4d', 'e0b54ad2-f432-46bc-a4d9-615b779de21a', NULL, NULL, 'SKIPPED', 'AUTO_BOT', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Machine Learning', 'Symonis', NULL, NULL, NULL, NULL, 'NONE', NULL, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Not eligible - Internshala profile requirements not met', NULL, 1, NULL, 0, '24a5c790-269f-40c5-ab06-8d52e00d6582', '2026-04-04 06:31:13.680817', '2026-04-04 06:40:31.350832');
INSERT OR IGNORE INTO 'applications'(_rowid_, 'user_id', 'job_id', 'resume_id', 'cover_letter_id', 'status', 'method', 'applied_at', 'viewed_at', 'shortlisted_at', 'interview_scheduled_at', 'offer_received_at', 'rejected_at', 'match_score_at_apply', 'job_title_snapshot', 'company_snapshot', 'recruiter_id', 'recruiter_name', 'recruiter_email', 'recruiter_linkedin', 'follow_up_status', 'follow_up_date', 'follow_up_count', 'last_follow_up_at', 'interview_date', 'interview_type', 'interview_notes', 'interview_feedback', 'offer_salary', 'offer_details', 'bot_session_id', 'bot_error', 'bot_screenshot_path', 'retry_count', 'notes', 'is_starred', 'id', 'created_at', 'updated_at') VALUES (30, '364c6ba3-8669-4f9a-bd50-577322459d4d', '1b868b4d-457d-4ea9-bfa3-e5821bfa62a7', NULL, NULL, 'SKIPPED', 'AUTO_BOT', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Data Science', 'Awakn', NULL, NULL, NULL, NULL, 'NONE', NULL, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Not eligible - Internshala profile requirements not met', NULL, 1, NULL, 0, 'e148121b-79f6-445d-90a4-476859f42fad', '2026-04-04 06:31:13.680820', '2026-04-04 06:40:42.698754');
INSERT OR IGNORE INTO 'applications'(_rowid_, 'user_id', 'job_id', 'resume_id', 'cover_letter_id', 'status', 'method', 'applied_at', 'viewed_at', 'shortlisted_at', 'interview_scheduled_at', 'offer_received_at', 'rejected_at', 'match_score_at_apply', 'job_title_snapshot', 'company_snapshot', 'recruiter_id', 'recruiter_name', 'recruiter_email', 'recruiter_linkedin', 'follow_up_status', 'follow_up_date', 'follow_up_count', 'last_follow_up_at', 'interview_date', 'interview_type', 'interview_notes', 'interview_feedback', 'offer_salary', 'offer_details', 'bot_session_id', 'bot_error', 'bot_screenshot_path', 'retry_count', 'notes', 'is_starred', 'id', 'created_at', 'updated_at') VALUES (31, '364c6ba3-8669-4f9a-bd50-577322459d4d', '1893ee73-a045-42bd-868b-f6362b340b66', NULL, NULL, 'SKIPPED', 'AUTO_BOT', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Artificial Intelligence (AI)', 'Andaz Kumar', NULL, NULL, NULL, NULL, 'NONE', NULL, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Not eligible - Internshala profile requirements not met', NULL, 1, NULL, 0, 'ac4cd694-8aec-4e56-8152-0b5043386d81', '2026-04-04 06:31:13.680823', '2026-04-04 07:02:03.886541');
INSERT OR IGNORE INTO 'applications'(_rowid_, 'user_id', 'job_id', 'resume_id', 'cover_letter_id', 'status', 'method', 'applied_at', 'viewed_at', 'shortlisted_at', 'interview_scheduled_at', 'offer_received_at', 'rejected_at', 'match_score_at_apply', 'job_title_snapshot', 'company_snapshot', 'recruiter_id', 'recruiter_name', 'recruiter_email', 'recruiter_linkedin', 'follow_up_status', 'follow_up_date', 'follow_up_count', 'last_follow_up_at', 'interview_date', 'interview_type', 'interview_notes', 'interview_feedback', 'offer_salary', 'offer_details', 'bot_session_id', 'bot_error', 'bot_screenshot_path', 'retry_count', 'notes', 'is_starred', 'id', 'created_at', 'updated_at') VALUES (32, '364c6ba3-8669-4f9a-bd50-577322459d4d', 'be7c027d-abca-4214-b3f8-b3de0adef08c', NULL, NULL, 'SKIPPED', 'AUTO_BOT', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Founders Office', 'Preplaced', NULL, NULL, NULL, NULL, 'NONE', NULL, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Not eligible - Internshala profile requirements not met', NULL, 1, NULL, 0, '0ff4e32e-b5bf-40c7-a533-3ae2bccdaca7', '2026-04-04 06:31:13.680826', '2026-04-04 07:02:15.844762');
INSERT OR IGNORE INTO 'applications'(_rowid_, 'user_id', 'job_id', 'resume_id', 'cover_letter_id', 'status', 'method', 'applied_at', 'viewed_at', 'shortlisted_at', 'interview_scheduled_at', 'offer_received_at', 'rejected_at', 'match_score_at_apply', 'job_title_snapshot', 'company_snapshot', 'recruiter_id', 'recruiter_name', 'recruiter_email', 'recruiter_linkedin', 'follow_up_status', 'follow_up_date', 'follow_up_count', 'last_follow_up_at', 'interview_date', 'interview_type', 'interview_notes', 'interview_feedback', 'offer_salary', 'offer_details', 'bot_session_id', 'bot_error', 'bot_screenshot_path', 'retry_count', 'notes', 'is_starred', 'id', 'created_at', 'updated_at') VALUES (33, '364c6ba3-8669-4f9a-bd50-577322459d4d', '9dff419b-3188-411b-86ac-bde2f9232649', NULL, NULL, 'SKIPPED', 'AUTO_BOT', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Data Annotation Team Management', 'Indiaum Solutions', NULL, NULL, NULL, NULL, 'NONE', NULL, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Not eligible - Internshala profile requirements not met', NULL, 1, NULL, 0, '36f80fc6-43d4-43de-95cd-8fd1d97e3798', '2026-04-04 06:31:13.680829', '2026-04-04 07:02:27.474657');
INSERT OR IGNORE INTO 'applications'(_rowid_, 'user_id', 'job_id', 'resume_id', 'cover_letter_id', 'status', 'method', 'applied_at', 'viewed_at', 'shortlisted_at', 'interview_scheduled_at', 'offer_received_at', 'rejected_at', 'match_score_at_apply', 'job_title_snapshot', 'company_snapshot', 'recruiter_id', 'recruiter_name', 'recruiter_email', 'recruiter_linkedin', 'follow_up_status', 'follow_up_date', 'follow_up_count', 'last_follow_up_at', 'interview_date', 'interview_type', 'interview_notes', 'interview_feedback', 'offer_salary', 'offer_details', 'bot_session_id', 'bot_error', 'bot_screenshot_path', 'retry_count', 'notes', 'is_starred', 'id', 'created_at', 'updated_at') VALUES (34, '364c6ba3-8669-4f9a-bd50-577322459d4d', '7a8f7b54-f044-4ac7-92d1-8aa8462c521c', NULL, NULL, 'SKIPPED', 'AUTO_BOT', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Data Platform Engineering (2026 Graduates Only)', 'Primenumbers Technologies', NULL, NULL, NULL, NULL, 'NONE', NULL, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Not eligible - Internshala profile requirements not met', NULL, 1, NULL, 0, '87a5215e-9400-474e-a59a-597d079c0ca9', '2026-04-04 06:31:13.680832', '2026-04-04 07:02:39.474926');
INSERT OR IGNORE INTO 'applications'(_rowid_, 'user_id', 'job_id', 'resume_id', 'cover_letter_id', 'status', 'method', 'applied_at', 'viewed_at', 'shortlisted_at', 'interview_scheduled_at', 'offer_received_at', 'rejected_at', 'match_score_at_apply', 'job_title_snapshot', 'company_snapshot', 'recruiter_id', 'recruiter_name', 'recruiter_email', 'recruiter_linkedin', 'follow_up_status', 'follow_up_date', 'follow_up_count', 'last_follow_up_at', 'interview_date', 'interview_type', 'interview_notes', 'interview_feedback', 'offer_salary', 'offer_details', 'bot_session_id', 'bot_error', 'bot_screenshot_path', 'retry_count', 'notes', 'is_starred', 'id', 'created_at', 'updated_at') VALUES (91, '364c6ba3-8669-4f9a-bd50-577322459d4d', '85591004-927b-4028-b583-8810f7a74172', NULL, NULL, 'QUEUED', 'AUTO_BOT', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Business Analytics', 'Career-Domain', NULL, NULL, NULL, NULL, 'NONE', NULL, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, NULL, 0, '242d3fbc-44f5-434e-8b35-9472922501e0', '2026-04-04 07:01:42.442869', '2026-04-04 07:01:42.442869');
INSERT OR IGNORE INTO 'applications'(_rowid_, 'user_id', 'job_id', 'resume_id', 'cover_letter_id', 'status', 'method', 'applied_at', 'viewed_at', 'shortlisted_at', 'interview_scheduled_at', 'offer_received_at', 'rejected_at', 'match_score_at_apply', 'job_title_snapshot', 'company_snapshot', 'recruiter_id', 'recruiter_name', 'recruiter_email', 'recruiter_linkedin', 'follow_up_status', 'follow_up_date', 'follow_up_count', 'last_follow_up_at', 'interview_date', 'interview_type', 'interview_notes', 'interview_feedback', 'offer_salary', 'offer_details', 'bot_session_id', 'bot_error', 'bot_screenshot_path', 'retry_count', 'notes', 'is_starred', 'id', 'created_at', 'updated_at') VALUES (92, '364c6ba3-8669-4f9a-bd50-577322459d4d', 'b814049b-cbac-455f-a0ab-5b2b228bd5b6', NULL, NULL, 'QUEUED', 'AUTO_BOT', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Content Marketing', 'Goodera', NULL, NULL, NULL, NULL, 'NONE', NULL, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, NULL, 0, 'e58e077d-92e6-4343-bbce-6274526fa325', '2026-04-04 07:01:42.442872', '2026-04-04 07:01:42.442872');
INSERT OR IGNORE INTO 'applications'(_rowid_, 'user_id', 'job_id', 'resume_id', 'cover_letter_id', 'status', 'method', 'applied_at', 'viewed_at', 'shortlisted_at', 'interview_scheduled_at', 'offer_received_at', 'rejected_at', 'match_score_at_apply', 'job_title_snapshot', 'company_snapshot', 'recruiter_id', 'recruiter_name', 'recruiter_email', 'recruiter_linkedin', 'follow_up_status', 'follow_up_date', 'follow_up_count', 'last_follow_up_at', 'interview_date', 'interview_type', 'interview_notes', 'interview_feedback', 'offer_salary', 'offer_details', 'bot_session_id', 'bot_error', 'bot_screenshot_path', 'retry_count', 'notes', 'is_starred', 'id', 'created_at', 'updated_at') VALUES (93, '364c6ba3-8669-4f9a-bd50-577322459d4d', 'ff0c2f02-c128-4858-943c-e8ad68c1fa3a', NULL, NULL, 'QUEUED', 'AUTO_BOT', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Research And Outreach', 'Marico Innovation Foundation', NULL, NULL, NULL, NULL, 'NONE', NULL, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, NULL, 0, 'c5dc4645-1845-4f71-ab86-8d590552970c', '2026-04-04 07:01:42.442875', '2026-04-04 07:01:42.442875');
INSERT OR IGNORE INTO 'applications'(_rowid_, 'user_id', 'job_id', 'resume_id', 'cover_letter_id', 'status', 'method', 'applied_at', 'viewed_at', 'shortlisted_at', 'interview_scheduled_at', 'offer_received_at', 'rejected_at', 'match_score_at_apply', 'job_title_snapshot', 'company_snapshot', 'recruiter_id', 'recruiter_name', 'recruiter_email', 'recruiter_linkedin', 'follow_up_status', 'follow_up_date', 'follow_up_count', 'last_follow_up_at', 'interview_date', 'interview_type', 'interview_notes', 'interview_feedback', 'offer_salary', 'offer_details', 'bot_session_id', 'bot_error', 'bot_screenshot_path', 'retry_count', 'notes', 'is_starred', 'id', 'created_at', 'updated_at') VALUES (94, '364c6ba3-8669-4f9a-bd50-577322459d4d', '6c77b4c5-17dd-4bf5-914e-1b0fc08cfe86', NULL, NULL, 'QUEUED', 'AUTO_BOT', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Market Research', 'AsiaDirect', NULL, NULL, NULL, NULL, 'NONE', NULL, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, NULL, 0, '52906531-78cd-4a57-909b-ff27ccb5b187', '2026-04-04 07:01:42.442878', '2026-04-04 07:01:42.442879');
INSERT OR IGNORE INTO 'applications'(_rowid_, 'user_id', 'job_id', 'resume_id', 'cover_letter_id', 'status', 'method', 'applied_at', 'viewed_at', 'shortlisted_at', 'interview_scheduled_at', 'offer_received_at', 'rejected_at', 'match_score_at_apply', 'job_title_snapshot', 'company_snapshot', 'recruiter_id', 'recruiter_name', 'recruiter_email', 'recruiter_linkedin', 'follow_up_status', 'follow_up_date', 'follow_up_count', 'last_follow_up_at', 'interview_date', 'interview_type', 'interview_notes', 'interview_feedback', 'offer_salary', 'offer_details', 'bot_session_id', 'bot_error', 'bot_screenshot_path', 'retry_count', 'notes', 'is_starred', 'id', 'created_at', 'updated_at') VALUES (95, '364c6ba3-8669-4f9a-bd50-577322459d4d', '477b224b-bcc1-46ae-890b-e37d7b17f9ae', NULL, NULL, 'QUEUED', 'AUTO_BOT', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'MIS – Lead Management', 'BNM Business Solutions LLP', NULL, NULL, NULL, NULL, 'NONE', NULL, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, NULL, 0, 'ad038c3c-3620-4e34-ad20-c1e7cad86a33', '2026-04-04 07:01:42.442881', '2026-04-04 07:01:42.442882');
INSERT OR IGNORE INTO 'applications'(_rowid_, 'user_id', 'job_id', 'resume_id', 'cover_letter_id', 'status', 'method', 'applied_at', 'viewed_at', 'shortlisted_at', 'interview_scheduled_at', 'offer_received_at', 'rejected_at', 'match_score_at_apply', 'job_title_snapshot', 'company_snapshot', 'recruiter_id', 'recruiter_name', 'recruiter_email', 'recruiter_linkedin', 'follow_up_status', 'follow_up_date', 'follow_up_count', 'last_follow_up_at', 'interview_date', 'interview_type', 'interview_notes', 'interview_feedback', 'offer_salary', 'offer_details', 'bot_session_id', 'bot_error', 'bot_screenshot_path', 'retry_count', 'notes', 'is_starred', 'id', 'created_at', 'updated_at') VALUES (96, '364c6ba3-8669-4f9a-bd50-577322459d4d', '5d1d80e9-6456-486c-af92-ae966db173c1', NULL, NULL, 'QUEUED', 'AUTO_BOT', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'AI Content And Community Associate (WhatsApp Channel)', 'Collective Artists Network', NULL, NULL, NULL, NULL, 'NONE', NULL, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, NULL, 0, '18222384-2290-4fd2-8d05-3b4ed21115cb', '2026-04-04 07:01:42.442884', '2026-04-04 07:01:42.442885');
INSERT OR IGNORE INTO 'applications'(_rowid_, 'user_id', 'job_id', 'resume_id', 'cover_letter_id', 'status', 'method', 'applied_at', 'viewed_at', 'shortlisted_at', 'interview_scheduled_at', 'offer_received_at', 'rejected_at', 'match_score_at_apply', 'job_title_snapshot', 'company_snapshot', 'recruiter_id', 'recruiter_name', 'recruiter_email', 'recruiter_linkedin', 'follow_up_status', 'follow_up_date', 'follow_up_count', 'last_follow_up_at', 'interview_date', 'interview_type', 'interview_notes', 'interview_feedback', 'offer_salary', 'offer_details', 'bot_session_id', 'bot_error', 'bot_screenshot_path', 'retry_count', 'notes', 'is_starred', 'id', 'created_at', 'updated_at') VALUES (97, '364c6ba3-8669-4f9a-bd50-577322459d4d', 'c8e106e5-9008-473d-a692-5677200a7704', NULL, NULL, 'QUEUED', 'AUTO_BOT', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'SEO & AI Optimisation', 'IndiaBizForSale.com', NULL, NULL, NULL, NULL, 'NONE', NULL, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, NULL, 0, '3b2c5ab9-328b-40c8-88d3-38297597b283', '2026-04-04 07:01:42.442887', '2026-04-04 07:01:42.442888');
INSERT OR IGNORE INTO 'applications'(_rowid_, 'user_id', 'job_id', 'resume_id', 'cover_letter_id', 'status', 'method', 'applied_at', 'viewed_at', 'shortlisted_at', 'interview_scheduled_at', 'offer_received_at', 'rejected_at', 'match_score_at_apply', 'job_title_snapshot', 'company_snapshot', 'recruiter_id', 'recruiter_name', 'recruiter_email', 'recruiter_linkedin', 'follow_up_status', 'follow_up_date', 'follow_up_count', 'last_follow_up_at', 'interview_date', 'interview_type', 'interview_notes', 'interview_feedback', 'offer_salary', 'offer_details', 'bot_session_id', 'bot_error', 'bot_screenshot_path', 'retry_count', 'notes', 'is_starred', 'id', 'created_at', 'updated_at') VALUES (98, '364c6ba3-8669-4f9a-bd50-577322459d4d', 'fb5a0eee-2a46-4ed8-a9f3-3806716284b8', NULL, NULL, 'QUEUED', 'AUTO_BOT', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'ERP Functional Consultant', 'Force-Intellect Private Limited', NULL, NULL, NULL, NULL, 'NONE', NULL, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, NULL, 0, 'c666d11a-a908-4d99-9cb2-4456f9f99b39', '2026-04-04 07:01:42.442890', '2026-04-04 07:01:42.442891');
INSERT OR IGNORE INTO 'applications'(_rowid_, 'user_id', 'job_id', 'resume_id', 'cover_letter_id', 'status', 'method', 'applied_at', 'viewed_at', 'shortlisted_at', 'interview_scheduled_at', 'offer_received_at', 'rejected_at', 'match_score_at_apply', 'job_title_snapshot', 'company_snapshot', 'recruiter_id', 'recruiter_name', 'recruiter_email', 'recruiter_linkedin', 'follow_up_status', 'follow_up_date', 'follow_up_count', 'last_follow_up_at', 'interview_date', 'interview_type', 'interview_notes', 'interview_feedback', 'offer_salary', 'offer_details', 'bot_session_id', 'bot_error', 'bot_screenshot_path', 'retry_count', 'notes', 'is_starred', 'id', 'created_at', 'updated_at') VALUES (99, '364c6ba3-8669-4f9a-bd50-577322459d4d', '151bfabe-aafd-42b3-88fa-776aa75d504c', NULL, NULL, 'QUEUED', 'AUTO_BOT', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'HR Operations', 'Jarurat Care', NULL, NULL, NULL, NULL, 'NONE', NULL, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, NULL, 0, 'c0042691-5b5f-48b5-a62d-c0d8191f27d0', '2026-04-04 07:01:42.442894', '2026-04-04 07:01:42.442894');
INSERT OR IGNORE INTO 'applications'(_rowid_, 'user_id', 'job_id', 'resume_id', 'cover_letter_id', 'status', 'method', 'applied_at', 'viewed_at', 'shortlisted_at', 'interview_scheduled_at', 'offer_received_at', 'rejected_at', 'match_score_at_apply', 'job_title_snapshot', 'company_snapshot', 'recruiter_id', 'recruiter_name', 'recruiter_email', 'recruiter_linkedin', 'follow_up_status', 'follow_up_date', 'follow_up_count', 'last_follow_up_at', 'interview_date', 'interview_type', 'interview_notes', 'interview_feedback', 'offer_salary', 'offer_details', 'bot_session_id', 'bot_error', 'bot_screenshot_path', 'retry_count', 'notes', 'is_starred', 'id', 'created_at', 'updated_at') VALUES (100, '364c6ba3-8669-4f9a-bd50-577322459d4d', '3b8beb43-9915-425e-b193-b50fd73df0b5', NULL, NULL, 'QUEUED', 'AUTO_BOT', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Email Marketing & Automation Assistant', 'Giant Leap', NULL, NULL, NULL, NULL, 'NONE', NULL, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, NULL, 0, '47cc1c45-129b-46ee-bac7-61a7489966f1', '2026-04-04 07:01:42.442897', '2026-04-04 07:01:42.442897');
INSERT OR IGNORE INTO 'applications'(_rowid_, 'user_id', 'job_id', 'resume_id', 'cover_letter_id', 'status', 'method', 'applied_at', 'viewed_at', 'shortlisted_at', 'interview_scheduled_at', 'offer_received_at', 'rejected_at', 'match_score_at_apply', 'job_title_snapshot', 'company_snapshot', 'recruiter_id', 'recruiter_name', 'recruiter_email', 'recruiter_linkedin', 'follow_up_status', 'follow_up_date', 'follow_up_count', 'last_follow_up_at', 'interview_date', 'interview_type', 'interview_notes', 'interview_feedback', 'offer_salary', 'offer_details', 'bot_session_id', 'bot_error', 'bot_screenshot_path', 'retry_count', 'notes', 'is_starred', 'id', 'created_at', 'updated_at') VALUES (101, '364c6ba3-8669-4f9a-bd50-577322459d4d', '83595046-eb44-490d-9ca2-c5211a92f967', NULL, NULL, 'QUEUED', 'AUTO_BOT', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Data Analytics', 'RentenPe', NULL, NULL, NULL, NULL, 'NONE', NULL, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, NULL, 0, '6a20be4d-c5b0-45ac-af4a-cf3e444e082e', '2026-04-04 07:01:42.442900', '2026-04-04 07:01:42.442900');
INSERT OR IGNORE INTO 'applications'(_rowid_, 'user_id', 'job_id', 'resume_id', 'cover_letter_id', 'status', 'method', 'applied_at', 'viewed_at', 'shortlisted_at', 'interview_scheduled_at', 'offer_received_at', 'rejected_at', 'match_score_at_apply', 'job_title_snapshot', 'company_snapshot', 'recruiter_id', 'recruiter_name', 'recruiter_email', 'recruiter_linkedin', 'follow_up_status', 'follow_up_date', 'follow_up_count', 'last_follow_up_at', 'interview_date', 'interview_type', 'interview_notes', 'interview_feedback', 'offer_salary', 'offer_details', 'bot_session_id', 'bot_error', 'bot_screenshot_path', 'retry_count', 'notes', 'is_starred', 'id', 'created_at', 'updated_at') VALUES (102, '364c6ba3-8669-4f9a-bd50-577322459d4d', '769910c5-0560-481f-afec-b05b60ef97d3', NULL, NULL, 'FAILED', 'MANUAL', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Data Engineer Intern', 'Cardinal Health', NULL, NULL, NULL, NULL, 'NONE', NULL, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Session expired. Run save_cookies.py.', NULL, 2, NULL, 0, 'f335fb08-2b89-45c5-927f-1efaa0769d0b', '2026-04-04 07:28:48.060652', '2026-04-04 07:41:33.576236');
INSERT OR IGNORE INTO 'applications'(_rowid_, 'user_id', 'job_id', 'resume_id', 'cover_letter_id', 'status', 'method', 'applied_at', 'viewed_at', 'shortlisted_at', 'interview_scheduled_at', 'offer_received_at', 'rejected_at', 'match_score_at_apply', 'job_title_snapshot', 'company_snapshot', 'recruiter_id', 'recruiter_name', 'recruiter_email', 'recruiter_linkedin', 'follow_up_status', 'follow_up_date', 'follow_up_count', 'last_follow_up_at', 'interview_date', 'interview_type', 'interview_notes', 'interview_feedback', 'offer_salary', 'offer_details', 'bot_session_id', 'bot_error', 'bot_screenshot_path', 'retry_count', 'notes', 'is_starred', 'id', 'created_at', 'updated_at') VALUES (103, '364c6ba3-8669-4f9a-bd50-577322459d4d', '1893ee73-a045-42bd-868b-f6362b340b66', NULL, NULL, 'QUEUED', 'AUTO_BOT', NULL, NULL, NULL, NULL, NULL, NULL, 50, 'Artificial Intelligence (AI)', 'Andaz Kumar', NULL, NULL, NULL, NULL, 'NONE', NULL, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, NULL, 0, '9f55d693-34e5-48a1-a8fb-0c0e143ad07f', '2026-04-04 07:53:07.591043', '2026-04-04 08:32:06.162669');
INSERT OR IGNORE INTO 'applications'(_rowid_, 'user_id', 'job_id', 'resume_id', 'cover_letter_id', 'status', 'method', 'applied_at', 'viewed_at', 'shortlisted_at', 'interview_scheduled_at', 'offer_received_at', 'rejected_at', 'match_score_at_apply', 'job_title_snapshot', 'company_snapshot', 'recruiter_id', 'recruiter_name', 'recruiter_email', 'recruiter_linkedin', 'follow_up_status', 'follow_up_date', 'follow_up_count', 'last_follow_up_at', 'interview_date', 'interview_type', 'interview_notes', 'interview_feedback', 'offer_salary', 'offer_details', 'bot_session_id', 'bot_error', 'bot_screenshot_path', 'retry_count', 'notes', 'is_starred', 'id', 'created_at', 'updated_at') VALUES (104, '364c6ba3-8669-4f9a-bd50-577322459d4d', 'be7c027d-abca-4214-b3f8-b3de0adef08c', NULL, NULL, 'QUEUED', 'AUTO_BOT', NULL, NULL, NULL, NULL, NULL, NULL, 50, 'Founders Office', 'Preplaced', NULL, NULL, NULL, NULL, 'NONE', NULL, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, NULL, 0, '8c55da5e-fa2e-47bb-a88f-1e710dc1235c', '2026-04-04 07:53:07.591062', '2026-04-04 08:32:06.162668');
INSERT OR IGNORE INTO 'applications'(_rowid_, 'user_id', 'job_id', 'resume_id', 'cover_letter_id', 'status', 'method', 'applied_at', 'viewed_at', 'shortlisted_at', 'interview_scheduled_at', 'offer_received_at', 'rejected_at', 'match_score_at_apply', 'job_title_snapshot', 'company_snapshot', 'recruiter_id', 'recruiter_name', 'recruiter_email', 'recruiter_linkedin', 'follow_up_status', 'follow_up_date', 'follow_up_count', 'last_follow_up_at', 'interview_date', 'interview_type', 'interview_notes', 'interview_feedback', 'offer_salary', 'offer_details', 'bot_session_id', 'bot_error', 'bot_screenshot_path', 'retry_count', 'notes', 'is_starred', 'id', 'created_at', 'updated_at') VALUES (105, '364c6ba3-8669-4f9a-bd50-577322459d4d', '9dff419b-3188-411b-86ac-bde2f9232649', NULL, NULL, 'QUEUED', 'AUTO_BOT', NULL, NULL, NULL, NULL, NULL, NULL, 50, 'Data Annotation Team Management', 'Indiaum Solutions', NULL, NULL, NULL, NULL, 'NONE', NULL, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, NULL, 0, '3f1db290-50e2-4a3c-9982-eeafcaec317f', '2026-04-04 07:53:07.591070', '2026-04-04 08:32:06.162667');
INSERT OR IGNORE INTO 'applications'(_rowid_, 'user_id', 'job_id', 'resume_id', 'cover_letter_id', 'status', 'method', 'applied_at', 'viewed_at', 'shortlisted_at', 'interview_scheduled_at', 'offer_received_at', 'rejected_at', 'match_score_at_apply', 'job_title_snapshot', 'company_snapshot', 'recruiter_id', 'recruiter_name', 'recruiter_email', 'recruiter_linkedin', 'follow_up_status', 'follow_up_date', 'follow_up_count', 'last_follow_up_at', 'interview_date', 'interview_type', 'interview_notes', 'interview_feedback', 'offer_salary', 'offer_details', 'bot_session_id', 'bot_error', 'bot_screenshot_path', 'retry_count', 'notes', 'is_starred', 'id', 'created_at', 'updated_at') VALUES (106, '364c6ba3-8669-4f9a-bd50-577322459d4d', '7a8f7b54-f044-4ac7-92d1-8aa8462c521c', NULL, NULL, 'QUEUED', 'AUTO_BOT', NULL, NULL, NULL, NULL, NULL, NULL, 50, 'Data Platform Engineering (2026 Graduates Only)', 'Primenumbers Technologies', NULL, NULL, NULL, NULL, 'NONE', NULL, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, NULL, 0, '1ba6e3ca-b731-4ea3-95e3-64ead51f9324', '2026-04-04 07:53:07.591076', '2026-04-04 08:32:06.162664');
INSERT OR IGNORE INTO 'applications'(_rowid_, 'user_id', 'job_id', 'resume_id', 'cover_letter_id', 'status', 'method', 'applied_at', 'viewed_at', 'shortlisted_at', 'interview_scheduled_at', 'offer_received_at', 'rejected_at', 'match_score_at_apply', 'job_title_snapshot', 'company_snapshot', 'recruiter_id', 'recruiter_name', 'recruiter_email', 'recruiter_linkedin', 'follow_up_status', 'follow_up_date', 'follow_up_count', 'last_follow_up_at', 'interview_date', 'interview_type', 'interview_notes', 'interview_feedback', 'offer_salary', 'offer_details', 'bot_session_id', 'bot_error', 'bot_screenshot_path', 'retry_count', 'notes', 'is_starred', 'id', 'created_at', 'updated_at') VALUES (107, '364c6ba3-8669-4f9a-bd50-577322459d4d', '10a143f5-8664-45a0-bccf-79c1565e037c', NULL, NULL, 'QUEUED', 'AUTO_BOT', NULL, NULL, NULL, NULL, NULL, NULL, 50, 'Content Writing (Research Associate In Computer Science)', 'Megaminds IT Services', NULL, NULL, NULL, NULL, 'NONE', NULL, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, NULL, 0, 'f852024f-2237-4a61-946c-c81a7a15f2aa', '2026-04-04 07:53:07.591082', '2026-04-04 08:32:06.162669');
INSERT OR IGNORE INTO 'applications'(_rowid_, 'user_id', 'job_id', 'resume_id', 'cover_letter_id', 'status', 'method', 'applied_at', 'viewed_at', 'shortlisted_at', 'interview_scheduled_at', 'offer_received_at', 'rejected_at', 'match_score_at_apply', 'job_title_snapshot', 'company_snapshot', 'recruiter_id', 'recruiter_name', 'recruiter_email', 'recruiter_linkedin', 'follow_up_status', 'follow_up_date', 'follow_up_count', 'last_follow_up_at', 'interview_date', 'interview_type', 'interview_notes', 'interview_feedback', 'offer_salary', 'offer_details', 'bot_session_id', 'bot_error', 'bot_screenshot_path', 'retry_count', 'notes', 'is_starred', 'id', 'created_at', 'updated_at') VALUES (108, '364c6ba3-8669-4f9a-bd50-577322459d4d', '3620bb0f-25e5-448c-85b0-a630fdc28db4', NULL, NULL, 'QUEUED', 'AUTO_BOT', NULL, NULL, NULL, NULL, NULL, NULL, 50, 'Artificial Intelligence (AI)', 'Eklavya.me', NULL, NULL, NULL, NULL, 'NONE', NULL, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, NULL, 0, '244403aa-f828-4e5d-8460-03030d880fd8', '2026-04-04 07:53:07.591090', '2026-04-04 08:32:06.162666');
INSERT OR IGNORE INTO 'payments'(_rowid_, 'user_id', 'subscription_id', 'amount', 'currency', 'status', 'razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature', 'plan', 'id', 'created_at', 'updated_at') VALUES (1, '186abe6d-ed82-4ac6-882e-9d0acb5f3192', NULL, 400, 'INR', 'CREATED', 'order_SZiMQoRs2DerqK', NULL, NULL, 'pro', '28eb664e-bfe2-40eb-91f2-adcbdb7913cc', '2026-04-05 06:35:51.790220', '2026-04-05 06:35:52.210026');
INSERT OR IGNORE INTO 'payments'(_rowid_, 'user_id', 'subscription_id', 'amount', 'currency', 'status', 'razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature', 'plan', 'id', 'created_at', 'updated_at') VALUES (2, '186abe6d-ed82-4ac6-882e-9d0acb5f3192', NULL, 200, 'INR', 'CREATED', 'order_SZiVNlg7cDW1iV', NULL, NULL, 'starter', '05896a5e-8132-4804-9b40-e3ff48ed2e43', '2026-04-05 06:44:20.273977', '2026-04-05 06:44:20.593935');
INSERT OR IGNORE INTO 'payments'(_rowid_, 'user_id', 'subscription_id', 'amount', 'currency', 'status', 'razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature', 'plan', 'id', 'created_at', 'updated_at') VALUES (3, '186abe6d-ed82-4ac6-882e-9d0acb5f3192', NULL, 400, 'INR', 'CREATED', 'order_SZiZxmcgEQxbID', NULL, NULL, 'pro', 'c14a27aa-ce9b-44be-bcf3-66c196cb0610', '2026-04-05 06:48:40.270499', '2026-04-05 06:48:40.798172');
INSERT OR IGNORE INTO 'payments'(_rowid_, 'user_id', 'subscription_id', 'amount', 'currency', 'status', 'razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature', 'plan', 'id', 'created_at', 'updated_at') VALUES (4, '186abe6d-ed82-4ac6-882e-9d0acb5f3192', NULL, 400, 'INR', 'CREATED', 'order_SZig2ZwuVPGWta', NULL, NULL, 'pro', 'bb368042-32b9-4f96-aa60-34b9c3a6df70', '2026-04-05 06:54:25.542449', '2026-04-05 06:54:26.032723');
INSERT OR IGNORE INTO 'payments'(_rowid_, 'user_id', 'subscription_id', 'amount', 'currency', 'status', 'razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature', 'plan', 'id', 'created_at', 'updated_at') VALUES (5, '186abe6d-ed82-4ac6-882e-9d0acb5f3192', NULL, 200, 'INR', 'CREATED', 'order_SawmsMqG60HEWb', NULL, NULL, 'starter', 'aec82420-0d0b-4c55-81a0-9931de414282', '2026-04-08 09:21:31.985719', '2026-04-08 09:21:36.880388');
INSERT OR IGNORE INTO 'payments'(_rowid_, 'user_id', 'subscription_id', 'amount', 'currency', 'status', 'razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature', 'plan', 'id', 'created_at', 'updated_at') VALUES (6, '186abe6d-ed82-4ac6-882e-9d0acb5f3192', NULL, 200, 'INR', 'CREATED', 'order_Sce1w03O8IiEIr', NULL, NULL, 'starter', '15bded35-075f-4e6d-8cb5-a56395a794b7', '2026-04-12 16:18:41.317202', '2026-04-12 16:18:41.633974');
INSERT OR IGNORE INTO 'payments'(_rowid_, 'user_id', 'subscription_id', 'amount', 'currency', 'status', 'razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature', 'plan', 'id', 'created_at', 'updated_at') VALUES (7, '186abe6d-ed82-4ac6-882e-9d0acb5f3192', NULL, 200, 'INR', 'CREATED', 'order_ScvWEW6SKrlxKx', NULL, NULL, 'starter', 'f408050f-ae1c-49e2-8a53-665a17103dd4', '2026-04-13 09:25:09.818966', '2026-04-13 09:25:10.286973');
INSERT OR IGNORE INTO 'payments'(_rowid_, 'user_id', 'subscription_id', 'amount', 'currency', 'status', 'razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature', 'plan', 'id', 'created_at', 'updated_at') VALUES (8, '186abe6d-ed82-4ac6-882e-9d0acb5f3192', NULL, 400, 'INR', 'CREATED', 'order_ScvWRapQm193Sz', NULL, NULL, 'pro', '5125eb3d-9b00-4167-af8b-8aaaa4d6016a', '2026-04-13 09:25:21.898632', '2026-04-13 09:25:22.254161');
INSERT OR IGNORE INTO 'payments'(_rowid_, 'user_id', 'subscription_id', 'amount', 'currency', 'status', 'razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature', 'plan', 'id', 'created_at', 'updated_at') VALUES (9, 'fecf1cde-739e-4c99-82ea-db6915e226fe', NULL, 200, 'INR', 'CREATED', 'order_Scvede5ym8ULNN', NULL, NULL, 'starter', 'a9bc0935-4e3a-428a-99bc-2fe7d9caf189', '2026-04-13 09:33:06.862641', '2026-04-13 09:33:07.885929');
INSERT OR IGNORE INTO 'payments'(_rowid_, 'user_id', 'subscription_id', 'amount', 'currency', 'status', 'razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature', 'plan', 'id', 'created_at', 'updated_at') VALUES (10, '186abe6d-ed82-4ac6-882e-9d0acb5f3192', NULL, 199, 'INR', 'CREATED', 'order_SdlbfAh0Aj9ft5', NULL, NULL, 'starter', '8b5a4b81-0e60-48a9-9668-44f1dffed03e', '2026-04-15 12:22:21.910705', '2026-04-15 12:22:22.294449');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (901, '96985e0c-b876-4953-940e-8d2d21caf392', 'bot_started', 'queued', 'applying', 'agent', NULL, '611251b4-2d1e-40aa-bfb8-cb81cefb79f4', '2026-04-04 08:03:06.816163', '2026-04-04 08:03:06.816166');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (902, '0c797985-a221-4502-aa0a-8f4c7bb9f457', 'application_created', NULL, 'pending_approval', 'user', '{"method": "auto_bot"}', '12bd4096-c9e9-4f34-8e19-86275218d8e8', '2026-04-15 15:09:20.290593', '2026-04-15 15:09:20.290595');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (903, '0c797985-a221-4502-aa0a-8f4c7bb9f457', 'status_changed', 'pending_approval', 'queued', 'user', '{"action": "approved"}', 'bed4737d-9675-4c7a-ac5a-f2c7109c84b1', '2026-04-15 15:09:27.539432', '2026-04-15 15:09:27.539434');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (904, '0c797985-a221-4502-aa0a-8f4c7bb9f457', 'bot_started', 'queued', 'applying', 'agent', NULL, '52f71411-4f5e-48aa-bdc7-7949b0b16b13', '2026-04-15 15:09:27.567601', '2026-04-15 15:09:27.567602');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (905, '0c797985-a221-4502-aa0a-8f4c7bb9f457', 'bot_started', 'queued', 'applying', 'agent', NULL, '51e1a038-67b5-48de-ad50-af5b6e0124fd', '2026-04-15 15:09:31.835285', '2026-04-15 15:09:31.835289');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (906, '0c797985-a221-4502-aa0a-8f4c7bb9f457', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Session expired. Run save_cookies.py."}', '768f6db9-f09a-43aa-bf34-f74f1089af6f', '2026-04-15 15:09:46.558145', '2026-04-15 15:09:46.558147');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (907, '0c797985-a221-4502-aa0a-8f4c7bb9f457', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Session expired. Run save_cookies.py."}', 'fd986bb3-6320-41d0-a31c-ead82c0121d5', '2026-04-15 15:09:49.436139', '2026-04-15 15:09:49.436141');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (1, '6c2ae341-cc1f-4fc9-9b6e-56dc5b2fddb4', 'application_created', NULL, 'pending_approval', 'user', '{"method": "auto_bot"}', 'fb715480-bb48-4e54-a5f3-623064afc490', '2026-04-03 15:50:28.505833', '2026-04-03 15:50:28.505835');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (2, '954ae486-6dd6-41cd-8611-15c85d132151', 'application_created', NULL, 'pending_approval', 'user', '{"method": "auto_bot"}', 'e1a0a352-8233-44d6-8c06-9dd567a4e297', '2026-04-03 15:50:29.770799', '2026-04-03 15:50:29.770800');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (3, '6c2ae341-cc1f-4fc9-9b6e-56dc5b2fddb4', 'status_changed', 'pending_approval', 'queued', 'user', '{"action": "approved"}', 'ac34ae41-7168-428f-a39c-b25b572d5f30', '2026-04-03 15:51:42.501441', '2026-04-03 15:51:42.501442');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (4, '954ae486-6dd6-41cd-8611-15c85d132151', 'status_changed', 'pending_approval', 'queued', 'user', '{"action": "approved"}', '53017ec8-bd9f-4fae-b483-b3f557dd6249', '2026-04-03 15:51:42.510261', '2026-04-03 15:51:42.510261');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (5, 'c1b714fa-4ad5-4a8f-be96-f099d88aef9a', 'bot_started', 'queued', 'applying', 'agent', NULL, 'de34d602-4753-44d2-ad1a-1c27b7f1b893', '2026-04-03 15:52:59.608907', '2026-04-03 15:52:59.608909');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (6, 'c1b714fa-4ad5-4a8f-be96-f099d88aef9a', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Session expired. Run save_cookies.py."}', '061d9c49-9909-41ac-8752-286e6bc3768d', '2026-04-03 15:53:10.812015', '2026-04-03 15:53:10.812018');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (7, '34fabd5a-d91f-4436-a6b3-18e19e5e497a', 'bot_started', 'queued', 'applying', 'agent', NULL, 'c1ec6d64-cf57-40c5-a307-2200b704511c', '2026-04-03 15:53:10.817720', '2026-04-03 15:53:10.817721');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (8, '34fabd5a-d91f-4436-a6b3-18e19e5e497a', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Session expired. Run save_cookies.py."}', '97a94f93-d6af-442a-b66e-836f4035f750', '2026-04-03 15:53:21.649854', '2026-04-03 15:53:21.649855');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (9, '48ab8737-1911-4cc9-9882-5c0fecf8db1b', 'bot_started', 'queued', 'applying', 'agent', NULL, 'a8cd7449-49ea-462f-9589-605970d75aaf', '2026-04-03 15:53:21.656091', '2026-04-03 15:53:21.656092');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (10, '48ab8737-1911-4cc9-9882-5c0fecf8db1b', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Session expired. Run save_cookies.py."}', '07839fca-1353-4e2f-b3c9-dc4fcb42f1d7', '2026-04-03 15:53:32.710545', '2026-04-03 15:53:32.710547');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (11, 'b898e751-2465-4ca2-9a91-d54397772022', 'bot_started', 'queued', 'applying', 'agent', NULL, '63226085-a9d3-4ad4-8a75-2b9ab817547a', '2026-04-03 15:53:32.716405', '2026-04-03 15:53:32.716406');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (12, 'b898e751-2465-4ca2-9a91-d54397772022', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Session expired. Run save_cookies.py."}', 'b3ab2477-c642-4824-8e91-db60896b9524', '2026-04-03 15:53:43.930692', '2026-04-03 15:53:43.930693');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (13, '7cb84eda-037e-48c4-a8e5-0ce44912c562', 'bot_started', 'queued', 'applying', 'agent', NULL, 'cd1e7e43-484a-4bb5-89d4-2715fc72507d', '2026-04-03 15:53:43.937092', '2026-04-03 15:53:43.937093');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (14, '7cb84eda-037e-48c4-a8e5-0ce44912c562', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Session expired. Run save_cookies.py."}', 'eec07bfa-9d82-49f3-872b-61030549a3c1', '2026-04-03 15:53:54.700989', '2026-04-03 15:53:54.700991');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (15, 'a25ef911-1511-42cc-9875-951178c5d38a', 'bot_started', 'queued', 'applying', 'agent', NULL, 'cdf93d2a-dd43-410c-b3f0-11f3867b5118', '2026-04-03 15:53:54.706484', '2026-04-03 15:53:54.706485');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (16, 'a25ef911-1511-42cc-9875-951178c5d38a', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Session expired. Run save_cookies.py."}', 'ef665f75-08d3-422b-92ae-da475ac22eec', '2026-04-03 15:54:05.732523', '2026-04-03 15:54:05.732525');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (17, '8046a5f1-66a7-4506-a075-0226c8d2036b', 'bot_started', 'queued', 'applying', 'agent', NULL, '66750ee9-dd0a-4e5f-9ad6-db2e3935612c', '2026-04-03 15:54:05.738558', '2026-04-03 15:54:05.738559');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (18, '8046a5f1-66a7-4506-a075-0226c8d2036b', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Session expired. Run save_cookies.py."}', 'e291d5b2-c720-4170-8a5d-39fc0926f05a', '2026-04-03 15:54:16.518566', '2026-04-03 15:54:16.518568');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (19, '4fc3d592-9e7a-4780-9ae9-fe5674212354', 'bot_started', 'queued', 'applying', 'agent', NULL, '8f082420-33d7-49c0-9e09-02703f3a791d', '2026-04-03 15:54:16.523685', '2026-04-03 15:54:16.523686');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (20, '4fc3d592-9e7a-4780-9ae9-fe5674212354', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Session expired. Run save_cookies.py."}', '6314472f-3b66-49b6-9e1f-a503445a82db', '2026-04-03 15:54:27.030318', '2026-04-03 15:54:27.030320');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (21, '929e55e1-f202-4853-b1d3-3603c436fbb6', 'bot_started', 'queued', 'applying', 'agent', NULL, 'ad8b39ad-8ef2-482d-ae59-e288d267c674', '2026-04-03 15:54:27.035909', '2026-04-03 15:54:27.035910');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (22, '929e55e1-f202-4853-b1d3-3603c436fbb6', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Session expired. Run save_cookies.py."}', 'afdca154-343c-4fd1-a362-c94c8fdea4b9', '2026-04-03 15:54:38.413708', '2026-04-03 15:54:38.413709');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (23, '99e0a673-2b64-4206-9a98-a78c534bda1b', 'bot_started', 'queued', 'applying', 'agent', NULL, 'b0aa70b6-abcf-4a4d-9306-89f7c306aee2', '2026-04-03 15:54:38.418754', '2026-04-03 15:54:38.418755');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (24, '99e0a673-2b64-4206-9a98-a78c534bda1b', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Session expired. Run save_cookies.py."}', 'afe9720c-3650-4473-a357-bbe8b103e9ed', '2026-04-03 15:54:51.441569', '2026-04-03 15:54:51.441570');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (25, '9cd7b6e1-a980-41ea-b71c-f157bde477ac', 'bot_started', 'queued', 'applying', 'agent', NULL, 'e61e90ea-80e9-4487-8f9e-9305c40cdbc5', '2026-04-03 15:55:50.781545', '2026-04-03 15:55:50.781547');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (26, '9cd7b6e1-a980-41ea-b71c-f157bde477ac', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible for this internship (location or criteria mismatch)"}', 'b80255f6-38f0-4563-acea-15c537b13ed1', '2026-04-03 15:56:03.417167', '2026-04-03 15:56:03.417169');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (27, '3f80ec06-0f6b-4692-8ebc-3c570bc9bc9a', 'bot_started', 'queued', 'applying', 'agent', NULL, '0355e1cf-690f-4caf-8f53-b3dda074e2ce', '2026-04-03 15:56:03.422462', '2026-04-03 15:56:03.422463');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (28, '3f80ec06-0f6b-4692-8ebc-3c570bc9bc9a', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible for this internship (location or criteria mismatch)"}', 'b21eebf1-3dc8-4337-b1cd-d00e41aae295', '2026-04-03 15:56:16.479373', '2026-04-03 15:56:16.479374');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (29, '54fbc8e7-35b9-4fb3-a424-c6a0987b24f3', 'bot_started', 'queued', 'applying', 'agent', NULL, '39350b2a-5c11-4102-bcc8-a50d3b56781d', '2026-04-03 15:56:16.483841', '2026-04-03 15:56:16.483842');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (30, '54fbc8e7-35b9-4fb3-a424-c6a0987b24f3', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible for this internship (location or criteria mismatch)"}', '74ecce8b-7241-40c7-a60f-885aa58ebcdc', '2026-04-03 15:56:28.832109', '2026-04-03 15:56:28.832109');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (31, '05e022f4-950e-45e4-82c8-03326ee54fef', 'bot_started', 'queued', 'applying', 'agent', NULL, '4c3ccd4a-e932-46b5-9520-82eddeb23ea3', '2026-04-03 15:56:28.837355', '2026-04-03 15:56:28.837356');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (32, '05e022f4-950e-45e4-82c8-03326ee54fef', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible for this internship (location or criteria mismatch)"}', '5c2bcfdf-bac4-4e7c-bc30-08ad2c1bf85f', '2026-04-03 15:56:40.831135', '2026-04-03 15:56:40.831136');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (33, '6815236b-9ad5-4d48-a5e6-1e2559909a34', 'bot_started', 'queued', 'applying', 'agent', NULL, '144ecef8-7361-4fac-826e-43d46f4333a7', '2026-04-03 15:56:40.836510', '2026-04-03 15:56:40.836510');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (34, '6815236b-9ad5-4d48-a5e6-1e2559909a34', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible for this internship (location or criteria mismatch)"}', '0654c0e5-b2e2-4688-a413-02e8c9506e34', '2026-04-03 15:56:52.547064', '2026-04-03 15:56:52.547065');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (35, '43257025-2485-4a63-9128-104119608353', 'bot_started', 'queued', 'applying', 'agent', NULL, 'd76e220b-3cba-4a5b-ad34-1855867daa69', '2026-04-03 15:56:52.552041', '2026-04-03 15:56:52.552042');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (36, '43257025-2485-4a63-9128-104119608353', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible for this internship (location or criteria mismatch)"}', '7390d3a5-a1d4-4f50-9b35-a5dd9a83ab07', '2026-04-03 15:57:04.604692', '2026-04-03 15:57:04.604693');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (37, '04f27143-8564-4a8d-bf22-c66c1176d5c9', 'bot_started', 'queued', 'applying', 'agent', NULL, 'fd716458-e5b7-4b56-be55-73c33483cc41', '2026-04-03 15:57:04.609701', '2026-04-03 15:57:04.609702');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (38, '04f27143-8564-4a8d-bf22-c66c1176d5c9', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible for this internship (location or criteria mismatch)"}', '919368c6-059c-4940-9a2f-56468804d566', '2026-04-03 15:57:16.658451', '2026-04-03 15:57:16.658452');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (39, '6fcae0be-23f7-480a-acc0-d217918fce59', 'bot_started', 'queued', 'applying', 'agent', NULL, '6e2127e9-6619-4471-a9de-ead33fdc5901', '2026-04-03 15:57:16.663143', '2026-04-03 15:57:16.663144');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (40, '6fcae0be-23f7-480a-acc0-d217918fce59', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible for this internship (location or criteria mismatch)"}', '5b714f8d-186c-4564-b018-11852fa5d6dd', '2026-04-03 15:57:29.392554', '2026-04-03 15:57:29.392555');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (41, '4cda2e52-a096-418e-8f04-99fa362483ac', 'bot_started', 'queued', 'applying', 'agent', NULL, '43edc7b3-9bdc-453c-80ec-1056fbc56480', '2026-04-03 15:57:29.396864', '2026-04-03 15:57:29.396865');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (42, '4cda2e52-a096-418e-8f04-99fa362483ac', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible for this internship (location or criteria mismatch)"}', '9eca5c06-87c0-4e04-845b-a00e85a6b66a', '2026-04-03 15:57:41.826029', '2026-04-03 15:57:41.826030');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (43, '3638d392-51f2-429c-a29e-4bcf25dec578', 'bot_started', 'queued', 'applying', 'agent', NULL, '606d22ba-af7a-44fc-9f18-762579feb348', '2026-04-03 15:57:41.830797', '2026-04-03 15:57:41.830798');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (44, '3638d392-51f2-429c-a29e-4bcf25dec578', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible for this internship (location or criteria mismatch)"}', 'aca50599-70c1-45aa-9ff1-fecd4e972078', '2026-04-03 15:57:54.294742', '2026-04-03 15:57:54.294743');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (45, '601485dc-fafd-48bf-b370-4227cf576d18', 'bot_started', 'queued', 'applying', 'agent', NULL, 'f994d41c-dd6e-41b2-91e6-ed04359b64b4', '2026-04-03 16:00:29.001047', '2026-04-03 16:00:29.001050');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (46, '601485dc-fafd-48bf-b370-4227cf576d18', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible for this internship (location or criteria mismatch)"}', '32b2c69b-278e-4730-84ca-dd89b21ef1b3', '2026-04-03 16:00:41.716173', '2026-04-03 16:00:41.716174');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (47, 'a90060fe-d078-402e-96f7-7ee93c945bae', 'bot_started', 'queued', 'applying', 'agent', NULL, 'bbcde4c4-444d-44c6-89f6-6bbe5e28988c', '2026-04-03 16:05:17.976075', '2026-04-03 16:05:17.976078');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (48, 'a90060fe-d078-402e-96f7-7ee93c945bae', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible for this internship (location or criteria mismatch)"}', '7362f559-bef9-43ce-b664-6b2f880f7963', '2026-04-03 16:05:32.578613', '2026-04-03 16:05:32.578616');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (49, '51fbb916-b3a6-4976-881c-1f50426a2008', 'bot_started', 'queued', 'applying', 'agent', NULL, 'b132f7c4-35ab-4321-9ccc-b1f9ac77f0da', '2026-04-03 16:05:32.588036', '2026-04-03 16:05:32.588038');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (50, '51fbb916-b3a6-4976-881c-1f50426a2008', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible for this internship (location or criteria mismatch)"}', '7df02873-2bfc-4d86-ad3f-40a8745d16c0', '2026-04-03 16:05:46.988607', '2026-04-03 16:05:46.988610');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (51, 'd1f36367-8bdd-455b-8cdf-b7eee3613163', 'bot_started', 'queued', 'applying', 'agent', NULL, '40fbd484-c5c0-4d02-9c7e-e32805685e35', '2026-04-03 16:05:47.004010', '2026-04-03 16:05:47.004012');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (52, 'd1f36367-8bdd-455b-8cdf-b7eee3613163', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible for this internship (location or criteria mismatch)"}', 'd612a5c4-9acb-4af5-ae0d-3f958a1faeb8', '2026-04-03 16:06:00.668629', '2026-04-03 16:06:00.668631');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (53, 'ed8e7660-366f-4262-92c7-e1d610f5f20e', 'bot_started', 'queued', 'applying', 'agent', NULL, '8890b410-ac1a-4e78-8ccb-7e17537713d6', '2026-04-03 16:06:00.679226', '2026-04-03 16:06:00.679228');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (54, 'ed8e7660-366f-4262-92c7-e1d610f5f20e', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible for this internship (location or criteria mismatch)"}', '14d49659-fa70-46b3-a41b-26023e868f42', '2026-04-03 16:06:13.373440', '2026-04-03 16:06:13.373441');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (55, '7b3b3f81-aa7a-457d-ab09-54fc0b5cde5b', 'bot_started', 'queued', 'applying', 'agent', NULL, '52eb1e65-0a78-4ce3-9782-e95ff058a7ef', '2026-04-03 16:06:13.378273', '2026-04-03 16:06:13.378274');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (56, '7b3b3f81-aa7a-457d-ab09-54fc0b5cde5b', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible for this internship (location or criteria mismatch)"}', '37edb70c-f5f2-40c2-9089-a06897709070', '2026-04-03 16:06:25.144834', '2026-04-03 16:06:25.144834');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (57, 'f6e69114-15a0-4eae-bd4f-771eefa37ca7', 'bot_started', 'queued', 'applying', 'agent', NULL, '2378b2a0-90f3-4591-a262-8a12a67dc182', '2026-04-03 16:06:25.149423', '2026-04-03 16:06:25.149424');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (58, 'f6e69114-15a0-4eae-bd4f-771eefa37ca7', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible for this internship (location or criteria mismatch)"}', '88490307-224e-4287-ad3b-64fe31b13fa7', '2026-04-03 16:06:38.089850', '2026-04-03 16:06:38.089852');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (59, '17cad60b-bf14-42b8-906f-78ea534c5596', 'bot_started', 'queued', 'applying', 'agent', NULL, '157e5324-0810-423c-80ab-90e47d39ea3c', '2026-04-03 16:06:38.095154', '2026-04-03 16:06:38.095155');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (60, '17cad60b-bf14-42b8-906f-78ea534c5596', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible for this internship (location or criteria mismatch)"}', 'b00e969f-5bb4-4008-8d85-17de0908c506', '2026-04-03 16:06:50.961635', '2026-04-03 16:06:50.961637');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (61, 'd8f18c57-aae9-4d67-92cc-28a319b1d3d0', 'bot_started', 'queued', 'applying', 'agent', NULL, 'f648b3bc-0431-4554-8159-c94fd9fcdd46', '2026-04-03 16:06:50.966595', '2026-04-03 16:06:50.966596');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (62, 'd8f18c57-aae9-4d67-92cc-28a319b1d3d0', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible for this internship (location or criteria mismatch)"}', 'ed4a28c6-9e85-4dc1-9067-8e7c7c510b0e', '2026-04-03 16:07:03.137328', '2026-04-03 16:07:03.137328');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (63, '0d2bb81d-bd94-4656-9f23-a3d349cd6213', 'bot_started', 'queued', 'applying', 'agent', NULL, '906f7683-9758-472d-985e-c5f74b858352', '2026-04-03 16:07:03.142268', '2026-04-03 16:07:03.142269');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (64, '0d2bb81d-bd94-4656-9f23-a3d349cd6213', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible for this internship (location or criteria mismatch)"}', '1b6002e5-05ea-4de9-bf52-add403646d3d', '2026-04-03 16:07:15.481967', '2026-04-03 16:07:15.481967');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (65, '9b8d0801-84e7-4076-842e-039f9d453b71', 'bot_started', 'queued', 'applying', 'agent', NULL, '1c34265b-516b-4f70-897d-210729edc6bf', '2026-04-03 16:07:15.486718', '2026-04-03 16:07:15.486719');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (66, '9b8d0801-84e7-4076-842e-039f9d453b71', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible for this internship (location or criteria mismatch)"}', '434a525d-a48c-4059-ae3f-1433164521be', '2026-04-03 16:07:27.897623', '2026-04-03 16:07:27.897625');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (67, '36392fdf-43b9-40d2-b291-559a55bb8342', 'bot_started', 'queued', 'applying', 'agent', NULL, 'e37b0512-45ec-4996-94fa-bf1001067741', '2026-04-03 16:08:35.735073', '2026-04-03 16:08:35.735075');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (68, '36392fdf-43b9-40d2-b291-559a55bb8342', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible for this internship (location or criteria mismatch)"}', '3d00dda8-f4cb-46d3-bfbe-d1b39b58f0c5', '2026-04-03 16:08:48.393417', '2026-04-03 16:08:48.393419');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (69, 'befe6bd9-3bde-4aab-b23d-bcb0b5a98bea', 'bot_started', 'queued', 'applying', 'agent', NULL, '81b80bde-c901-4786-aec8-0e60677b275f', '2026-04-03 16:08:48.398320', '2026-04-03 16:08:48.398321');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (70, 'befe6bd9-3bde-4aab-b23d-bcb0b5a98bea', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible for this internship (location or criteria mismatch)"}', 'b30b7182-0ddc-4dee-82fa-b7ff3ed6a70f', '2026-04-03 16:09:01.103118', '2026-04-03 16:09:01.103119');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (71, 'ae77fff6-6edf-40b3-b83d-6f3ea59f8811', 'bot_started', 'queued', 'applying', 'agent', NULL, 'be8ad235-6bc1-47e1-843f-0080e71a2694', '2026-04-03 16:09:01.108703', '2026-04-03 16:09:01.108704');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (72, 'ae77fff6-6edf-40b3-b83d-6f3ea59f8811', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible for this internship (location or criteria mismatch)"}', '3b00e60e-e05a-4885-94c0-94d2f90e0ffb', '2026-04-03 16:09:14.144927', '2026-04-03 16:09:14.144929');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (73, 'cbaa9d88-a892-4ea2-bb6f-f7791efac0fe', 'bot_started', 'queued', 'applying', 'agent', NULL, 'cdd93473-042c-4359-be90-a98b06f5bc65', '2026-04-03 16:09:14.149353', '2026-04-03 16:09:14.149354');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (74, 'cbaa9d88-a892-4ea2-bb6f-f7791efac0fe', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible for this internship (location or criteria mismatch)"}', '45cf481e-8eb2-464c-bc82-8c58f6724c32', '2026-04-03 16:09:26.325550', '2026-04-03 16:09:26.325551');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (75, '6e479795-f3cf-45b9-851f-7d44e0fe11d3', 'bot_started', 'queued', 'applying', 'agent', NULL, '39a73a0a-ad52-4197-8471-40699398b083', '2026-04-03 16:09:26.330761', '2026-04-03 16:09:26.330762');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (76, '6e479795-f3cf-45b9-851f-7d44e0fe11d3', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible for this internship (location or criteria mismatch)"}', '0a2987e1-5819-4469-acd8-0f0dc1094f6c', '2026-04-03 16:09:38.689970', '2026-04-03 16:09:38.689972');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (77, 'db98c19f-8c33-4d98-a271-c0b46dd7bf58', 'bot_started', 'queued', 'applying', 'agent', NULL, '138ea533-7b98-4224-801e-88bd1caf8a41', '2026-04-03 16:09:38.694607', '2026-04-03 16:09:38.694608');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (78, 'db98c19f-8c33-4d98-a271-c0b46dd7bf58', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible for this internship (location or criteria mismatch)"}', '5745f323-01fa-475d-aadf-1eb08a35705c', '2026-04-03 16:09:52.520164', '2026-04-03 16:09:52.520165');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (98, '46be4baa-0c9f-4d6c-9f74-961becc8962e', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible for this internship (location or criteria mismatch)"}', '9547c290-1c99-4bad-a0af-c42b034cd98f', '2026-04-03 16:14:32.388429', '2026-04-03 16:14:32.388431');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (99, '3c4e84fd-e91e-4d60-865e-96712b697ab0', 'bot_started', 'queued', 'applying', 'agent', NULL, 'af71b1b6-60f8-4c96-8d0f-feacf7cf7ac2', '2026-04-03 16:14:32.393157', '2026-04-03 16:14:32.393158');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (100, '3c4e84fd-e91e-4d60-865e-96712b697ab0', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible for this internship (location or criteria mismatch)"}', '41efe1ae-0056-4e63-8c93-22e678030eec', '2026-04-03 16:14:44.579754', '2026-04-03 16:14:44.579755');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (101, 'ba6bcc24-d6b1-4e95-bbab-47aad3f58eb5', 'bot_started', 'queued', 'applying', 'agent', NULL, 'cb67f21e-3c77-4491-a566-a5e2f4481c39', '2026-04-03 16:14:44.585587', '2026-04-03 16:14:44.585589');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (102, 'ba6bcc24-d6b1-4e95-bbab-47aad3f58eb5', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible for this internship (location or criteria mismatch)"}', 'e4fce082-14c3-4795-9e1e-032571ab7cf7', '2026-04-03 16:14:56.922477', '2026-04-03 16:14:56.922478');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (103, '598257df-79bc-494a-a18b-a7fa9ae7cd74', 'bot_started', 'queued', 'applying', 'agent', NULL, 'd9bdc06a-207e-4c43-9f15-cc21d005a9ca', '2026-04-03 16:14:56.928116', '2026-04-03 16:14:56.928117');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (104, '598257df-79bc-494a-a18b-a7fa9ae7cd74', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible for this internship (location or criteria mismatch)"}', 'ccc480a0-5502-4bee-908c-ceecb4b9fb16', '2026-04-03 16:15:09.195541', '2026-04-03 16:15:09.195542');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (105, '94dd65d2-c618-4873-9d78-c9ea478a2792', 'bot_started', 'queued', 'applying', 'agent', NULL, 'f6e50ca3-1790-406e-89a7-4d7e90f1cb3d', '2026-04-03 16:15:09.202651', '2026-04-03 16:15:09.202652');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (106, '94dd65d2-c618-4873-9d78-c9ea478a2792', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible for this internship (location or criteria mismatch)"}', '7bca37ce-b3f3-4739-836d-a69929cf5f1d', '2026-04-03 16:15:21.695344', '2026-04-03 16:15:21.695345');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (107, 'dbbea99e-0775-4027-9bb7-c62fa76e72f1', 'bot_started', 'queued', 'applying', 'agent', NULL, '3ef238da-5ea6-40bf-a7e9-57ac16f0dac9', '2026-04-03 16:21:05.181433', '2026-04-03 16:21:05.181433');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (108, 'dbbea99e-0775-4027-9bb7-c62fa76e72f1', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible for this internship (location or criteria mismatch)"}', '01d9732e-2824-4bc5-a003-ff3b3de432fb', '2026-04-03 16:21:18.041714', '2026-04-03 16:21:18.041715');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (109, 'dd43a516-841d-4197-ae3c-f5c91687ecde', 'bot_started', 'queued', 'applying', 'agent', NULL, 'f1da5750-8981-4002-a7ad-fba9662be755', '2026-04-03 16:21:18.048544', '2026-04-03 16:21:18.048544');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (110, 'dd43a516-841d-4197-ae3c-f5c91687ecde', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible for this internship (location or criteria mismatch)"}', 'a53f2a13-837c-4bad-9ff1-e9813f1612eb', '2026-04-03 16:21:31.461489', '2026-04-03 16:21:31.461491');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (111, 'ac128e43-e126-43e3-92bb-1faf19b73e15', 'bot_started', 'queued', 'applying', 'agent', NULL, '4e50a638-ff4e-4660-9f88-c0d1b6d5f60e', '2026-04-03 16:21:31.467106', '2026-04-03 16:21:31.467107');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (112, 'ac128e43-e126-43e3-92bb-1faf19b73e15', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible for this internship (location or criteria mismatch)"}', 'f34ff4fa-3e04-44ae-8cf5-df1bdf120064', '2026-04-03 16:21:45.636091', '2026-04-03 16:21:45.636094');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (113, 'a71df556-49cf-4788-bef2-1e441b1aa32b', 'bot_started', 'queued', 'applying', 'agent', NULL, '6065dc08-c631-4c00-8656-300216debac6', '2026-04-03 16:21:45.643098', '2026-04-03 16:21:45.643099');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (114, 'a71df556-49cf-4788-bef2-1e441b1aa32b', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible for this internship (location or criteria mismatch)"}', 'ae748900-b12e-40ca-8e12-d2421218f6de', '2026-04-03 16:21:57.500362', '2026-04-03 16:21:57.500363');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (115, '677b3af4-4f18-4b08-b0af-dc1bb1dc051c', 'bot_started', 'queued', 'applying', 'agent', NULL, 'b5af16df-399c-41ec-bf07-589b8e0278d8', '2026-04-03 16:21:57.505848', '2026-04-03 16:21:57.505849');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (116, '677b3af4-4f18-4b08-b0af-dc1bb1dc051c', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible for this internship (location or criteria mismatch)"}', 'dcfc95db-b417-4624-bc51-c5ff4b5f4f56', '2026-04-03 16:22:09.481315', '2026-04-03 16:22:09.481316');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (117, 'dc1fbf00-55cc-46ad-a55b-f764a080739d', 'bot_started', 'queued', 'applying', 'agent', NULL, '89efc056-fdeb-4104-93dd-a1b43a403f1e', '2026-04-03 16:22:09.486084', '2026-04-03 16:22:09.486085');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (118, 'dc1fbf00-55cc-46ad-a55b-f764a080739d', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible for this internship (location or criteria mismatch)"}', '58bb5aa7-1b09-4d82-9ae5-cf4fa7e4ffe9', '2026-04-03 16:22:21.405188', '2026-04-03 16:22:21.405189');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (119, '17838050-86b1-4f23-9d93-173b16d2b473', 'bot_started', 'queued', 'applying', 'agent', NULL, '3b6e616c-462d-43de-baa8-00a9a7d7a153', '2026-04-03 16:22:21.410824', '2026-04-03 16:22:21.410825');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (120, '17838050-86b1-4f23-9d93-173b16d2b473', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible for this internship (location or criteria mismatch)"}', 'caf04e59-43eb-41a8-94ee-36b3cd566467', '2026-04-03 16:22:33.809160', '2026-04-03 16:22:33.809160');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (121, '8f6152a8-b6fe-4e30-9ce3-bb15222eaa93', 'bot_started', 'queued', 'applying', 'agent', NULL, 'afc26e0a-ffb4-47c4-a1d2-9463a0de8881', '2026-04-03 16:22:33.814461', '2026-04-03 16:22:33.814461');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (122, '8f6152a8-b6fe-4e30-9ce3-bb15222eaa93', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible for this internship (location or criteria mismatch)"}', '3ea0666c-fc52-4558-88a2-e0ebd0b779e3', '2026-04-03 16:22:47.289924', '2026-04-03 16:22:47.289926');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (123, '828248ad-17b6-4f85-a935-cbd6648e03e3', 'bot_started', 'queued', 'applying', 'agent', NULL, 'c4cfd87c-04bb-49e5-8e88-160e889b4345', '2026-04-03 16:22:47.299856', '2026-04-03 16:22:47.299857');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (124, '828248ad-17b6-4f85-a935-cbd6648e03e3', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible for this internship (location or criteria mismatch)"}', '15685ce1-e190-4b3b-a715-9fc9c9f1baee', '2026-04-03 16:23:00.200378', '2026-04-03 16:23:00.200379');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (125, 'de0e4aed-2863-43ae-a4d4-96fd9f626c19', 'bot_started', 'queued', 'applying', 'agent', NULL, 'c4dc9a59-dbef-4abb-9784-3043a25a7681', '2026-04-03 16:23:00.206124', '2026-04-03 16:23:00.206125');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (126, 'de0e4aed-2863-43ae-a4d4-96fd9f626c19', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible for this internship (location or criteria mismatch)"}', '120b27d1-f95f-4713-9901-14c4bb57dc74', '2026-04-03 16:23:12.583635', '2026-04-03 16:23:12.583635');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (127, 'b39a512c-fc59-431e-ae4a-a3fa907acc17', 'bot_started', 'queued', 'applying', 'agent', NULL, '7ee8fa91-315b-4e62-8d56-210014789f04', '2026-04-03 16:54:22.727353', '2026-04-03 16:54:22.727355');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (128, 'b39a512c-fc59-431e-ae4a-a3fa907acc17', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible for this internship (location or criteria mismatch)"}', '399db431-85fc-453e-9a19-68e7fc360d13', '2026-04-03 16:54:35.207882', '2026-04-03 16:54:35.207883');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (129, '6e0d0c1f-5e5f-469d-ac18-7a7e3f575722', 'bot_started', 'queued', 'applying', 'agent', NULL, 'e05fbf3d-ee90-4131-8606-bbf45509f21a', '2026-04-03 16:54:35.213307', '2026-04-03 16:54:35.213308');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (130, '6e0d0c1f-5e5f-469d-ac18-7a7e3f575722', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible for this internship (location or criteria mismatch)"}', '4eed66bc-aa81-4480-a21c-6ded7e8243a8', '2026-04-03 16:54:47.126075', '2026-04-03 16:54:47.126076');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (131, '6bc55c20-bd75-452c-a0a8-962dda8018d5', 'bot_started', 'queued', 'applying', 'agent', NULL, '02c8716f-d61e-4544-a48e-926b5dfd63a6', '2026-04-03 16:54:47.130999', '2026-04-03 16:54:47.131000');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (132, '6bc55c20-bd75-452c-a0a8-962dda8018d5', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible for this internship (location or criteria mismatch)"}', 'cf5955ec-2c4d-4789-9d25-a3ba2032075d', '2026-04-03 16:54:59.786889', '2026-04-03 16:54:59.786891');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (133, 'b0aae04b-ee3f-4dc2-aa3a-c25284a1c293', 'bot_started', 'queued', 'applying', 'agent', NULL, '0f94cf61-e0d5-4f9d-aad9-d7db9c773433', '2026-04-03 16:54:59.792077', '2026-04-03 16:54:59.792078');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (134, 'b0aae04b-ee3f-4dc2-aa3a-c25284a1c293', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible for this internship (location or criteria mismatch)"}', '3659c21a-8ca3-46c0-8c8f-7d5bb179a8c2', '2026-04-03 16:55:12.382863', '2026-04-03 16:55:12.382864');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (135, '680dc782-9ebe-4497-bbe8-6b8a6e7a62d7', 'bot_started', 'queued', 'applying', 'agent', NULL, '8173660f-b936-4c62-9ad8-e5cab0764fc8', '2026-04-03 16:55:12.388889', '2026-04-03 16:55:12.388890');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (136, '680dc782-9ebe-4497-bbe8-6b8a6e7a62d7', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible for this internship (location or criteria mismatch)"}', 'c38b59a0-0c6c-4202-90bd-1c63b87cdf18', '2026-04-03 16:55:24.932780', '2026-04-03 16:55:24.932782');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (137, 'c561adf1-3245-483c-91f6-8120969af458', 'bot_started', 'queued', 'applying', 'agent', NULL, 'e0efda03-924b-455d-94ad-f9e014709aee', '2026-04-03 16:55:24.938616', '2026-04-03 16:55:24.938618');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (138, 'c561adf1-3245-483c-91f6-8120969af458', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible for this internship (location or criteria mismatch)"}', '44e111db-3938-4524-ad5b-8c625a2a6c06', '2026-04-03 16:55:37.268030', '2026-04-03 16:55:37.268032');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (139, '07cab700-e7b9-4f1a-a50e-d5272f7a6c40', 'bot_started', 'queued', 'applying', 'agent', NULL, '6ce4ab7b-0dd7-49b2-85a7-6ad2ad8994b6', '2026-04-03 16:55:37.273810', '2026-04-03 16:55:37.273811');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (140, '07cab700-e7b9-4f1a-a50e-d5272f7a6c40', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible for this internship (location or criteria mismatch)"}', '142c2fa7-9909-41ff-acd3-04dd806172fc', '2026-04-03 16:55:49.561458', '2026-04-03 16:55:49.561459');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (141, 'd7b01ac3-9f05-48c5-8c16-430a82334656', 'bot_started', 'queued', 'applying', 'agent', NULL, '3bc9adc0-a205-4418-84da-f831257de36c', '2026-04-03 16:55:49.567970', '2026-04-03 16:55:49.567972');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (142, 'd7b01ac3-9f05-48c5-8c16-430a82334656', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible for this internship (location or criteria mismatch)"}', '4248e2d0-972f-4750-a7ef-d11bd1f2a713', '2026-04-03 16:56:01.680269', '2026-04-03 16:56:01.680270');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (143, 'e9ce1afa-951a-4ca9-b2e2-315d314fb41b', 'bot_started', 'queued', 'applying', 'agent', NULL, 'e8b6e51b-25d7-4615-a6db-86d8c052979f', '2026-04-03 16:56:01.685931', '2026-04-03 16:56:01.685933');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (144, 'e9ce1afa-951a-4ca9-b2e2-315d314fb41b', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible for this internship (location or criteria mismatch)"}', '4415b1fc-e132-41ef-988e-676467f54f80', '2026-04-03 16:56:13.989938', '2026-04-03 16:56:13.989939');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (145, '02bdafe4-ea32-4af3-accc-06f013fe3085', 'bot_started', 'queued', 'applying', 'agent', NULL, '908f12ab-501d-4eb7-9cfe-d37f204d133b', '2026-04-03 16:56:13.995210', '2026-04-03 16:56:13.995211');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (146, '02bdafe4-ea32-4af3-accc-06f013fe3085', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible for this internship (location or criteria mismatch)"}', '0a7dd86a-571d-4494-9721-42e6fddccc6c', '2026-04-03 16:56:25.909580', '2026-04-03 16:56:25.909581');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (147, 'dc5b8c7b-11af-4849-adca-70b728506dc1', 'bot_started', 'queued', 'applying', 'agent', NULL, 'fdd857c2-3468-415e-986b-749147d8b4ac', '2026-04-03 17:05:43.215088', '2026-04-03 17:05:43.215089');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (148, 'dc5b8c7b-11af-4849-adca-70b728506dc1', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible for this internship (location or criteria mismatch)"}', '87d7206c-7d1f-4c68-bc9f-bbb73eec61fa', '2026-04-03 17:05:55.648990', '2026-04-03 17:05:55.648991');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (149, '4e3405e2-ecf4-4ded-9d2a-4170fb952173', 'bot_started', 'queued', 'applying', 'agent', NULL, '74517914-e671-4536-ba9c-32e76fe971b5', '2026-04-03 17:05:56.402804', '2026-04-03 17:05:56.402806');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (150, '4e3405e2-ecf4-4ded-9d2a-4170fb952173', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible for this internship (location or criteria mismatch)"}', 'a3a0de1e-dfe9-4930-a621-e5ca7c36aea5', '2026-04-03 17:06:08.533920', '2026-04-03 17:06:08.533921');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (151, '173fbbbc-9551-44da-9dc1-aa879abddd63', 'bot_started', 'queued', 'applying', 'agent', NULL, 'c0286e99-b22d-40b4-bbf2-c06e8621e806', '2026-04-03 17:06:09.224206', '2026-04-03 17:06:09.224209');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (152, '173fbbbc-9551-44da-9dc1-aa879abddd63', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible for this internship (location or criteria mismatch)"}', 'f19ec340-aa6e-4643-8d08-6d5c02e2b8ce', '2026-04-03 17:06:21.661060', '2026-04-03 17:06:21.661061');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (153, '263723ba-61dc-49ee-8f75-c0ea18981d45', 'bot_started', 'queued', 'applying', 'agent', NULL, 'd2697829-dd6e-49f3-8e77-805c7c505965', '2026-04-03 17:06:22.275627', '2026-04-03 17:06:22.275629');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (154, '263723ba-61dc-49ee-8f75-c0ea18981d45', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible for this internship (location or criteria mismatch)"}', 'cf5b3294-2ba4-4e56-b6e5-18c755ab703d', '2026-04-03 17:06:35.266587', '2026-04-03 17:06:35.266588');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (155, 'ec8c543e-5af7-4035-953e-8539a7b26053', 'bot_started', 'queued', 'applying', 'agent', NULL, '91bbc41b-29f4-4239-b270-0ee35e575fa9', '2026-04-03 17:06:35.838423', '2026-04-03 17:06:35.838425');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (156, 'ec8c543e-5af7-4035-953e-8539a7b26053', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible for this internship (location or criteria mismatch)"}', '1dd1af53-200c-40b8-947e-53560358f51a', '2026-04-03 17:06:48.440216', '2026-04-03 17:06:48.440218');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (157, 'e4148302-fb75-415e-8239-bd7f8c1aeeb3', 'bot_started', 'queued', 'applying', 'agent', NULL, 'a17e590e-a560-4867-9dd6-3860ce002410', '2026-04-03 17:06:49.258916', '2026-04-03 17:06:49.258917');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (158, 'e4148302-fb75-415e-8239-bd7f8c1aeeb3', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible for this internship (location or criteria mismatch)"}', '9c2f065b-3d04-4ce8-bcbc-8e1434579cc6', '2026-04-03 17:07:01.457380', '2026-04-03 17:07:01.457382');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (159, '8807bafe-e4b7-4d4f-8247-293489187c8a', 'bot_started', 'queued', 'applying', 'agent', NULL, '1847c320-ae08-427d-83b0-1b87df925905', '2026-04-03 17:07:02.144430', '2026-04-03 17:07:02.144432');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (160, '8807bafe-e4b7-4d4f-8247-293489187c8a', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible for this internship (location or criteria mismatch)"}', 'f203a7c2-a181-4bca-b346-06113e62fec2', '2026-04-03 17:07:14.539041', '2026-04-03 17:07:14.539043');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (161, 'd750c83a-81e5-44d2-9575-ab00441eda38', 'bot_started', 'queued', 'applying', 'agent', NULL, '5424183c-9dc6-42e9-a514-3abf6df8c9c6', '2026-04-03 17:07:15.482019', '2026-04-03 17:07:15.482028');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (162, 'd750c83a-81e5-44d2-9575-ab00441eda38', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible for this internship (location or criteria mismatch)"}', '1c598ff4-5acd-4ad0-95ba-0c98eda62237', '2026-04-03 17:07:28.012196', '2026-04-03 17:07:28.012197');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (163, 'f3df9e8a-27cd-4aa3-b877-91e3e4e79818', 'bot_started', 'queued', 'applying', 'agent', NULL, 'b83916f4-4c62-4187-960a-0d032c80fca0', '2026-04-03 17:07:29.110449', '2026-04-03 17:07:29.110452');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (164, 'f3df9e8a-27cd-4aa3-b877-91e3e4e79818', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible for this internship (location or criteria mismatch)"}', '60877e9f-9657-477f-86e7-9a1c815f6ced', '2026-04-03 17:07:40.998105', '2026-04-03 17:07:40.998106');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (165, '7646ec8a-3e2a-40f4-bb18-6bf0fa4cfb8d', 'bot_started', 'queued', 'applying', 'agent', NULL, '56842d0d-35c0-4b8c-b5d0-dc1263398f32', '2026-04-03 17:07:41.896852', '2026-04-03 17:07:41.896854');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (166, '7646ec8a-3e2a-40f4-bb18-6bf0fa4cfb8d', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible for this internship (location or criteria mismatch)"}', 'd814504c-9ef6-40de-9cb5-4f976f287a53', '2026-04-03 17:07:54.765143', '2026-04-03 17:07:54.765144');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (167, '31014517-3d23-4652-b05b-920a5b16afc2', 'bot_started', 'queued', 'applying', 'agent', NULL, '25f43b64-910a-498f-a16f-94dc3d8b35b2', '2026-04-03 17:09:08.119691', '2026-04-03 17:09:08.119694');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (168, '31014517-3d23-4652-b05b-920a5b16afc2', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible for this internship (location or criteria mismatch)"}', 'f6a5faec-c0ba-429e-9b9a-b2ca2f49fc12', '2026-04-03 17:09:21.003708', '2026-04-03 17:09:21.003709');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (169, '298854cd-bc5f-41f9-ade0-1dd701fdf31d', 'bot_started', 'queued', 'applying', 'agent', NULL, '1d009fc7-de9e-4670-95f9-f4e3884cb8da', '2026-04-03 17:09:21.839994', '2026-04-03 17:09:21.839996');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (170, '298854cd-bc5f-41f9-ade0-1dd701fdf31d', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible for this internship (location or criteria mismatch)"}', '319bf136-f84b-4873-8d45-5a669604bca6', '2026-04-03 17:09:33.592509', '2026-04-03 17:09:33.592509');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (171, 'c15a3511-5a24-443e-aa93-759be15f58c2', 'bot_started', 'queued', 'applying', 'agent', NULL, 'a91b6b1a-119e-4b07-b96f-064b2aedb20a', '2026-04-03 17:09:34.261282', '2026-04-03 17:09:34.261284');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (172, 'c15a3511-5a24-443e-aa93-759be15f58c2', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible for this internship (location or criteria mismatch)"}', '733c164c-7092-4e1f-a59d-765f1702e7f2', '2026-04-03 17:09:46.328827', '2026-04-03 17:09:46.328829');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (173, '1b27a5e9-b5fd-45f9-b22d-04fffd251f0c', 'bot_started', 'queued', 'applying', 'agent', NULL, 'a48dd040-6491-4494-83cf-a4ac964aa0c0', '2026-04-03 17:09:47.032214', '2026-04-03 17:09:47.032217');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (174, '1b27a5e9-b5fd-45f9-b22d-04fffd251f0c', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible for this internship (location or criteria mismatch)"}', '39fe34b0-12cc-492a-80e5-8c2f1dbd4cc6', '2026-04-03 17:09:59.884400', '2026-04-03 17:09:59.884401');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (175, '36c2f2cc-513f-4dbf-a59d-0a3b1de33200', 'bot_started', 'queued', 'applying', 'agent', NULL, 'cf118b64-5fe9-4404-affe-7b02fad242d0', '2026-04-03 17:10:00.652177', '2026-04-03 17:10:00.652180');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (176, '36c2f2cc-513f-4dbf-a59d-0a3b1de33200', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible for this internship (location or criteria mismatch)"}', '8e35d0b7-883d-4396-b263-e7b901c43fa8', '2026-04-03 17:10:14.838594', '2026-04-03 17:10:14.838596');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (177, '6141b087-48d9-446b-a9f3-1de7f8e122ad', 'bot_started', 'queued', 'applying', 'agent', NULL, '7ca94437-cc92-4bce-8ce0-f31a47cabe59', '2026-04-03 17:10:15.708953', '2026-04-03 17:10:15.708956');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (178, '6141b087-48d9-446b-a9f3-1de7f8e122ad', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible for this internship (location or criteria mismatch)"}', '5c040267-d008-4e7a-a0ed-2904b0296594', '2026-04-03 17:10:30.236442', '2026-04-03 17:10:30.236445');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (179, 'd5ef9eb1-7847-4634-a74c-3e6042f3823c', 'bot_started', 'queued', 'applying', 'agent', NULL, '5b489b0f-6a84-4600-a330-33d67732eff3', '2026-04-03 17:10:31.346806', '2026-04-03 17:10:31.346808');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (180, 'd5ef9eb1-7847-4634-a74c-3e6042f3823c', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible for this internship (location or criteria mismatch)"}', '8e0003b8-c91f-4a14-9a08-88a5c0f26b94', '2026-04-03 17:10:44.313099', '2026-04-03 17:10:44.313100');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (181, '074f4bed-b32a-42e5-b0a1-d5bc9963d0dc', 'bot_started', 'queued', 'applying', 'agent', NULL, '5f45a896-ae98-4ac4-b504-46ea529433c4', '2026-04-03 17:10:45.298463', '2026-04-03 17:10:45.298467');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (182, '074f4bed-b32a-42e5-b0a1-d5bc9963d0dc', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible for this internship (location or criteria mismatch)"}', '0fd85bc6-fdc8-4b64-a7ab-c0382bef7c2a', '2026-04-03 17:10:58.157915', '2026-04-03 17:10:58.157916');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (183, '11cb1714-1cec-4e49-a02c-e18698630193', 'bot_started', 'queued', 'applying', 'agent', NULL, '368f27af-f094-4786-b88b-dda6179d8f94', '2026-04-03 17:10:59.224967', '2026-04-03 17:10:59.224969');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (184, '11cb1714-1cec-4e49-a02c-e18698630193', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible for this internship (location or criteria mismatch)"}', '4d799463-9906-41ef-afea-a609be598e30', '2026-04-03 17:11:11.655446', '2026-04-03 17:11:11.655448');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (185, '44fdef65-3433-4bf9-91a2-fb9a5c005ebb', 'bot_started', 'queued', 'applying', 'agent', NULL, 'ac08cc4d-95fd-4777-aeaa-cb7770683142', '2026-04-03 17:11:12.228946', '2026-04-03 17:11:12.228951');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (186, '44fdef65-3433-4bf9-91a2-fb9a5c005ebb', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible for this internship (location or criteria mismatch)"}', '14e2297a-4eee-46cd-a2bd-649d7d11cdb2', '2026-04-03 17:11:25.144102', '2026-04-03 17:11:25.144103');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (187, '4738a64e-5434-4da8-a5d6-7a92c9943be7', 'bot_started', 'queued', 'applying', 'agent', NULL, 'dd35c5e4-5065-45c9-95b4-258487e27597', '2026-04-03 17:18:48.633408', '2026-04-03 17:18:48.633411');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (188, '4738a64e-5434-4da8-a5d6-7a92c9943be7', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible for this internship (location or criteria mismatch)"}', '5bc0dab2-4944-4029-8a28-bc41ac34d959', '2026-04-03 17:19:02.401954', '2026-04-03 17:19:02.401956');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (189, '9fdad399-d0f2-411f-aee8-4f9443b5a8fb', 'bot_started', 'queued', 'applying', 'agent', NULL, 'c4bbdabf-7824-4bc4-a857-a3d5134599ce', '2026-04-03 17:19:06.817159', '2026-04-03 17:19:06.817164');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (190, '9fdad399-d0f2-411f-aee8-4f9443b5a8fb', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible for this internship (location or criteria mismatch)"}', 'fee5eecb-5183-4b86-93ab-db2905340971', '2026-04-03 17:19:20.233317', '2026-04-03 17:19:20.233318');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (191, 'b52ae79e-8725-4fd1-8409-b4eadc020117', 'bot_started', 'queued', 'applying', 'agent', NULL, '9a4bcd0c-5f33-4fd9-883f-b71bb82477e9', '2026-04-03 17:19:20.892350', '2026-04-03 17:19:20.892354');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (192, 'b52ae79e-8725-4fd1-8409-b4eadc020117', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible for this internship (location or criteria mismatch)"}', '55c51ea0-30a8-4fd6-bf11-d3b23af28536', '2026-04-03 17:19:34.209172', '2026-04-03 17:19:34.209174');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (508, 'ef429f9e-2325-43e5-a6aa-40dcc1aecb51', 'bot_started', 'queued', 'applying', 'agent', NULL, '1d12ad5c-acb9-4404-b69f-916beae21b92', '2026-04-04 03:33:23.277774', '2026-04-04 03:33:23.277776');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (509, 'ef429f9e-2325-43e5-a6aa-40dcc1aecb51', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Application modal did not open after clicking Apply"}', 'a0eb87a2-dc42-4980-9146-8cb1983691de', '2026-04-04 03:33:43.453732', '2026-04-04 03:33:43.453733');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (510, '466dc702-0662-4b67-b9f0-c091bce6d205', 'bot_started', 'queued', 'applying', 'agent', NULL, '918eded9-0253-4b1d-8143-551932e8ca63', '2026-04-04 03:33:43.620481', '2026-04-04 03:33:43.620482');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (511, '466dc702-0662-4b67-b9f0-c091bce6d205', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Application modal did not open after clicking Apply"}', '86ee6077-ec03-48b4-95d8-bb6c10f06902', '2026-04-04 03:34:03.380455', '2026-04-04 03:34:03.380456');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (512, 'eca03a9e-5310-4777-b74e-fecfc24d9967', 'bot_started', 'queued', 'applying', 'agent', NULL, '1d09be23-85b9-49d6-8672-604c9cc456b6', '2026-04-04 03:34:03.609987', '2026-04-04 03:34:03.609989');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (513, 'eca03a9e-5310-4777-b74e-fecfc24d9967', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Application modal did not open after clicking Apply"}', '246e8b56-2a94-4a7b-9d9a-a96ec6db6dfa', '2026-04-04 03:34:23.363585', '2026-04-04 03:34:23.363586');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (514, '213964e5-8d7b-4193-9595-446acda0a6bc', 'bot_started', 'queued', 'applying', 'agent', NULL, '9835b78f-059e-4f63-a78d-e89c89424030', '2026-04-04 03:34:23.596682', '2026-04-04 03:34:23.596685');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (515, '213964e5-8d7b-4193-9595-446acda0a6bc', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Application modal did not open after clicking Apply"}', '904ae53f-b8a4-4195-bff9-efda1eb4571f', '2026-04-04 03:34:43.495515', '2026-04-04 03:34:43.495516');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (516, 'a37ac870-ebc1-436d-820f-ccea0fbad5ac', 'bot_started', 'queued', 'applying', 'agent', NULL, '63a678ba-de29-4e1e-b85c-938e42adf22d', '2026-04-04 03:34:43.661429', '2026-04-04 03:34:43.661431');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (517, 'a37ac870-ebc1-436d-820f-ccea0fbad5ac', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Application modal did not open after clicking Apply"}', '9d99a538-99b5-44a5-9a8b-380e4d0c078e', '2026-04-04 03:35:06.577869', '2026-04-04 03:35:06.577870');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (518, '754b0f68-afe3-4f37-8de8-7a5f2ba61c63', 'bot_started', 'queued', 'applying', 'agent', NULL, '38c68129-0062-4349-ad56-5a6293d218c6', '2026-04-04 03:35:06.767504', '2026-04-04 03:35:06.767506');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (519, '754b0f68-afe3-4f37-8de8-7a5f2ba61c63', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Application modal did not open after clicking Apply"}', '3216fb38-1992-4445-85cc-77f869b7b1a5', '2026-04-04 03:35:26.411829', '2026-04-04 03:35:26.411830');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (520, '13dcbc86-f4f4-447d-845d-bf136f34e6f4', 'bot_started', 'queued', 'applying', 'agent', NULL, 'ac092844-2e9e-44c1-a88f-6c8f33ff789d', '2026-04-04 03:35:26.578211', '2026-04-04 03:35:26.578213');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (521, '13dcbc86-f4f4-447d-845d-bf136f34e6f4', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Application modal did not open after clicking Apply"}', 'e571689e-94a5-48ff-9852-e40c349cff60', '2026-04-04 03:35:46.931093', '2026-04-04 03:35:46.931095');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (522, 'b2a79303-0657-4f80-89e3-e4953945e630', 'bot_started', 'queued', 'applying', 'agent', NULL, 'dc34b628-9c98-4897-b30a-b112306680da', '2026-04-04 03:35:47.161161', '2026-04-04 03:35:47.161163');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (523, 'b2a79303-0657-4f80-89e3-e4953945e630', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Application modal did not open after clicking Apply"}', '50fc1f95-ed96-4d88-954f-a2c4d950f3a8', '2026-04-04 03:36:07.197016', '2026-04-04 03:36:07.197017');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (524, '9f800cf6-85f5-43d3-a8a7-96f3b6e11316', 'bot_started', 'queued', 'applying', 'agent', NULL, '88f175f0-eacd-4634-ab07-91eabd34147c', '2026-04-04 03:36:07.366974', '2026-04-04 03:36:07.366975');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (525, '9f800cf6-85f5-43d3-a8a7-96f3b6e11316', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Application modal did not open after clicking Apply"}', '65c25147-9754-424f-84c8-b857a22b6d0b', '2026-04-04 03:36:27.529983', '2026-04-04 03:36:27.529984');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (526, 'a64be615-f37e-4a53-83a2-103ca4619c3c', 'bot_started', 'queued', 'applying', 'agent', NULL, '51a0e3ad-a135-40c0-86d8-ebab3675f7ad', '2026-04-04 03:37:04.568140', '2026-04-04 03:37:04.568142');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (527, 'a64be615-f37e-4a53-83a2-103ca4619c3c', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Application modal did not open after clicking Apply"}', 'ea3680c7-3970-42ec-96c2-39d708b2a816', '2026-04-04 03:37:22.004194', '2026-04-04 03:37:22.004195');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (528, 'ef429f9e-2325-43e5-a6aa-40dcc1aecb51', 'bot_started', 'queued', 'applying', 'agent', NULL, '271320d9-0082-4e23-927a-cae5d2c4d849', '2026-04-04 03:37:22.170667', '2026-04-04 03:37:22.170668');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (529, 'ef429f9e-2325-43e5-a6aa-40dcc1aecb51', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Application modal did not open after clicking Apply"}', 'b3f94209-8067-4702-9de5-7042f2df5cdc', '2026-04-04 03:37:38.811443', '2026-04-04 03:37:38.811444');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (530, '466dc702-0662-4b67-b9f0-c091bce6d205', 'bot_started', 'queued', 'applying', 'agent', NULL, '4e2add91-ce19-42ce-8dfe-797887a20259', '2026-04-04 03:37:39.020006', '2026-04-04 03:37:39.020007');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (531, '466dc702-0662-4b67-b9f0-c091bce6d205', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Application modal did not open after clicking Apply"}', '70926a34-29d3-4063-aab5-c23c59b4de1f', '2026-04-04 03:37:55.679174', '2026-04-04 03:37:55.679174');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (532, 'eca03a9e-5310-4777-b74e-fecfc24d9967', 'bot_started', 'queued', 'applying', 'agent', NULL, 'd27f5d20-40b5-40da-bd17-7132a2ba8034', '2026-04-04 03:37:55.866550', '2026-04-04 03:37:55.866551');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (533, 'eca03a9e-5310-4777-b74e-fecfc24d9967', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Application modal did not open after clicking Apply"}', '3a1c3626-af3d-4358-b076-41dec5f81879', '2026-04-04 03:38:12.843992', '2026-04-04 03:38:12.843993');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (534, '213964e5-8d7b-4193-9595-446acda0a6bc', 'bot_started', 'queued', 'applying', 'agent', NULL, '4a365645-d761-4a66-bcd2-626f2aed415a', '2026-04-04 03:38:13.030885', '2026-04-04 03:38:13.030888');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (535, '213964e5-8d7b-4193-9595-446acda0a6bc', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Application modal did not open after clicking Apply"}', 'a1458a6c-ee75-498f-a7de-5117d5ec5557', '2026-04-04 03:38:30.141692', '2026-04-04 03:38:30.141693');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (536, 'a37ac870-ebc1-436d-820f-ccea0fbad5ac', 'bot_started', 'queued', 'applying', 'agent', NULL, '78c63444-844b-4927-918e-4abda6838c73', '2026-04-04 03:38:30.335723', '2026-04-04 03:38:30.335725');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (537, 'a37ac870-ebc1-436d-820f-ccea0fbad5ac', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Application modal did not open after clicking Apply"}', 'd9d254e5-58bd-4805-b881-a1e32a6e584d', '2026-04-04 03:38:46.568267', '2026-04-04 03:38:46.568268');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (538, '754b0f68-afe3-4f37-8de8-7a5f2ba61c63', 'bot_started', 'queued', 'applying', 'agent', NULL, '2f5e4a65-6d8e-4ba8-a56e-bfc9bfad23c3', '2026-04-04 03:38:46.740895', '2026-04-04 03:38:46.740897');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (539, '754b0f68-afe3-4f37-8de8-7a5f2ba61c63', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Application modal did not open after clicking Apply"}', '6d6a1dff-1ee6-4c70-a470-d43734c661df', '2026-04-04 03:39:03.877614', '2026-04-04 03:39:03.877615');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (540, '13dcbc86-f4f4-447d-845d-bf136f34e6f4', 'bot_started', 'queued', 'applying', 'agent', NULL, '737a1afd-abff-411d-9e28-bfda3b184d20', '2026-04-04 03:39:04.096040', '2026-04-04 03:39:04.096042');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (541, '13dcbc86-f4f4-447d-845d-bf136f34e6f4', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Application modal did not open after clicking Apply"}', 'db3e149b-4fe6-4fd6-b95a-152a9e9443ca', '2026-04-04 03:39:21.086369', '2026-04-04 03:39:21.086370');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (542, 'b2a79303-0657-4f80-89e3-e4953945e630', 'bot_started', 'queued', 'applying', 'agent', NULL, '0b2e6b8b-3e71-400a-8eb7-28eabbb565e2', '2026-04-04 03:39:21.243827', '2026-04-04 03:39:21.243829');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (543, 'b2a79303-0657-4f80-89e3-e4953945e630', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Application modal did not open after clicking Apply"}', '16ffc355-4b67-4af9-b4e6-d8e2f2d86946', '2026-04-04 03:39:37.865075', '2026-04-04 03:39:37.865076');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (544, '9f800cf6-85f5-43d3-a8a7-96f3b6e11316', 'bot_started', 'queued', 'applying', 'agent', NULL, 'ceef680d-fef5-4ea1-bbb9-664647d9114e', '2026-04-04 03:39:38.051254', '2026-04-04 03:39:38.051256');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (545, '9f800cf6-85f5-43d3-a8a7-96f3b6e11316', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Application modal did not open after clicking Apply"}', '7cc24a1f-5835-4e6c-ab0b-ad886725e7d5', '2026-04-04 03:39:54.929552', '2026-04-04 03:39:54.929553');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (546, 'a64be615-f37e-4a53-83a2-103ca4619c3c', 'bot_started', 'queued', 'applying', 'agent', NULL, '64e922e4-1501-4e51-bec1-e9671af65b6b', '2026-04-04 03:40:58.692103', '2026-04-04 03:40:58.692104');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (547, 'a64be615-f37e-4a53-83a2-103ca4619c3c', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Application modal did not open after clicking Apply"}', 'e83acbcc-9865-48c3-b2a5-ec91eb40c270', '2026-04-04 03:41:32.787565', '2026-04-04 03:41:32.787566');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (548, 'ef429f9e-2325-43e5-a6aa-40dcc1aecb51', 'bot_started', 'queued', 'applying', 'agent', NULL, '1eeef6b7-bff9-4ed6-b936-693fe82de529', '2026-04-04 03:41:32.976294', '2026-04-04 03:41:32.976295');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (549, 'ef429f9e-2325-43e5-a6aa-40dcc1aecb51', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Application modal did not open after clicking Apply"}', 'c02f9e10-a71c-461d-a894-e6f9460c84b9', '2026-04-04 03:42:05.963615', '2026-04-04 03:42:05.963616');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (550, '466dc702-0662-4b67-b9f0-c091bce6d205', 'bot_started', 'queued', 'applying', 'agent', NULL, 'cbf5ef93-4fe4-41a9-aeae-5e249ad858cd', '2026-04-04 03:42:06.145282', '2026-04-04 03:42:06.145285');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (551, '466dc702-0662-4b67-b9f0-c091bce6d205', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Application modal did not open after clicking Apply"}', 'b5e36611-acf3-41c8-b361-b504c253d13b', '2026-04-04 03:42:39.486432', '2026-04-04 03:42:39.486433');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (552, 'eca03a9e-5310-4777-b74e-fecfc24d9967', 'bot_started', 'queued', 'applying', 'agent', NULL, '1a04976f-9758-4be3-870d-a4cb38af6b6d', '2026-04-04 03:42:39.831434', '2026-04-04 03:42:39.831435');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (553, 'eca03a9e-5310-4777-b74e-fecfc24d9967', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Application modal did not open after clicking Apply"}', '1b4c84b8-22ea-44f0-873c-fbffff421876', '2026-04-04 03:43:13.422189', '2026-04-04 03:43:13.422190');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (554, '213964e5-8d7b-4193-9595-446acda0a6bc', 'bot_started', 'queued', 'applying', 'agent', NULL, '8ab29963-a1c2-47b5-8ca0-23efe37d08bb', '2026-04-04 03:43:13.584423', '2026-04-04 03:43:13.584425');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (555, '213964e5-8d7b-4193-9595-446acda0a6bc', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Application modal did not open after clicking Apply"}', 'acdcdfcb-c254-48f3-a02a-65b7717a7c07', '2026-04-04 03:43:47.057785', '2026-04-04 03:43:47.057792');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (556, 'a37ac870-ebc1-436d-820f-ccea0fbad5ac', 'bot_started', 'queued', 'applying', 'agent', NULL, '4cae545d-d600-4b82-b16b-0c9c2da73a5e', '2026-04-04 03:43:47.244018', '2026-04-04 03:43:47.244021');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (557, 'a37ac870-ebc1-436d-820f-ccea0fbad5ac', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Application modal did not open after clicking Apply"}', '0227d43a-ecf6-4bca-8672-0393fe8669e9', '2026-04-04 03:44:20.492561', '2026-04-04 03:44:20.492562');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (558, '754b0f68-afe3-4f37-8de8-7a5f2ba61c63', 'bot_started', 'queued', 'applying', 'agent', NULL, 'a5bbadf3-1fac-42ea-aae0-e145b6cf871b', '2026-04-04 03:44:20.694943', '2026-04-04 03:44:20.694944');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (559, '754b0f68-afe3-4f37-8de8-7a5f2ba61c63', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Application modal did not open after clicking Apply"}', '53f5f2d6-d287-4c8c-a3e7-d7b7f279fe14', '2026-04-04 03:44:54.166169', '2026-04-04 03:44:54.166171');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (560, '13dcbc86-f4f4-447d-845d-bf136f34e6f4', 'bot_started', 'queued', 'applying', 'agent', NULL, 'c4817c68-5ee4-4d48-9dd1-7b24e8dda93b', '2026-04-04 03:44:54.322221', '2026-04-04 03:44:54.322222');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (561, '13dcbc86-f4f4-447d-845d-bf136f34e6f4', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Application modal did not open after clicking Apply"}', '08b1a582-501e-49f6-a99e-025daa8fa3f1', '2026-04-04 03:45:27.544501', '2026-04-04 03:45:27.544502');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (562, 'b2a79303-0657-4f80-89e3-e4953945e630', 'bot_started', 'queued', 'applying', 'agent', NULL, 'e03b1716-e26b-47b5-a0d0-f958d20ef6d4', '2026-04-04 03:45:27.870131', '2026-04-04 03:45:27.870133');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (563, 'b2a79303-0657-4f80-89e3-e4953945e630', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Application modal did not open after clicking Apply"}', '120fc3f2-ae20-4c63-bdac-dba9a988e938', '2026-04-04 03:46:01.384854', '2026-04-04 03:46:01.384855');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (564, '9f800cf6-85f5-43d3-a8a7-96f3b6e11316', 'bot_started', 'queued', 'applying', 'agent', NULL, '787af3f9-750c-47e7-83af-f12cd2634f25', '2026-04-04 03:46:01.665037', '2026-04-04 03:46:01.665038');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (565, '9f800cf6-85f5-43d3-a8a7-96f3b6e11316', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Application modal did not open after clicking Apply"}', 'ceac4128-7fd3-4b41-a533-3b6c56b6a6df', '2026-04-04 03:46:34.798725', '2026-04-04 03:46:34.798727');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (566, '3325433d-d518-4306-9b78-37224d2b4d89', 'bot_started', 'queued', 'applying', 'agent', NULL, '8deea22f-1b1c-4104-a50a-16de26de14fd', '2026-04-04 03:47:12.127147', '2026-04-04 03:47:12.127148');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (567, '3325433d-d518-4306-9b78-37224d2b4d89', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Application modal did not open after clicking Apply"}', '1f2c2097-edb1-4220-852d-da01ab97fcd8', '2026-04-04 03:47:45.316567', '2026-04-04 03:47:45.316568');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (568, 'ffea3ee8-bc29-4d72-ae0b-9bc8548eaf28', 'bot_started', 'queued', 'applying', 'agent', NULL, '8b73d426-e1ec-4774-ae18-a26366aee207', '2026-04-04 03:47:45.592493', '2026-04-04 03:47:45.592495');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (569, 'ffea3ee8-bc29-4d72-ae0b-9bc8548eaf28', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Application modal did not open after clicking Apply"}', '9608f8bd-d310-45b1-aea5-f344ef52ab64', '2026-04-04 03:48:19.621657', '2026-04-04 03:48:19.621658');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (570, 'a7c910fb-6062-4b8c-ab55-e9b5f9514178', 'bot_started', 'queued', 'applying', 'agent', NULL, 'b3ba1b69-a459-44b7-9ac3-58de2f75d7cd', '2026-04-04 03:48:19.850797', '2026-04-04 03:48:19.850799');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (571, 'a7c910fb-6062-4b8c-ab55-e9b5f9514178', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Application modal did not open after clicking Apply"}', '1cc8f46a-79c4-4003-904a-02c160fef50e', '2026-04-04 03:48:52.814054', '2026-04-04 03:48:52.814055');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (572, 'ae7b11a9-7e0c-41e3-97f7-769c3c00201a', 'bot_started', 'queued', 'applying', 'agent', NULL, '63219631-f1fb-4096-ae09-7865ec2f357f', '2026-04-04 03:48:52.975407', '2026-04-04 03:48:52.975409');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (573, 'ae7b11a9-7e0c-41e3-97f7-769c3c00201a', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Application modal did not open after clicking Apply"}', '1e228fb4-f160-4171-bae8-a798b1a55e51', '2026-04-04 03:49:26.671108', '2026-04-04 03:49:26.671110');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (574, '35ef04a7-7cef-4cad-be52-5d9799efbacf', 'bot_started', 'queued', 'applying', 'agent', NULL, '393a4519-5e09-4c80-b8bd-bef7e6bb05ca', '2026-04-04 03:49:26.899271', '2026-04-04 03:49:26.899272');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (575, '35ef04a7-7cef-4cad-be52-5d9799efbacf', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Application modal did not open after clicking Apply"}', '9a8a13fc-3e27-414e-a6c2-e1c396fff24e', '2026-04-04 03:50:00.957765', '2026-04-04 03:50:00.957766');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (576, 'a31aadcb-a6d6-4716-96d3-bf747b70d711', 'bot_started', 'queued', 'applying', 'agent', NULL, 'd9107b36-6a77-4d3b-8275-03e89e2e63a4', '2026-04-04 03:50:01.140294', '2026-04-04 03:50:01.140296');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (577, 'a31aadcb-a6d6-4716-96d3-bf747b70d711', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Application modal did not open after clicking Apply"}', 'bfcacd90-1824-463e-a076-3c24ad055205', '2026-04-04 03:50:34.055288', '2026-04-04 03:50:34.055289');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (578, 'f145547a-ea95-40c7-b319-d9f3e709a8d9', 'bot_started', 'queued', 'applying', 'agent', NULL, 'e6d608dc-b646-4d30-8817-acbb5795f4f2', '2026-04-04 03:50:34.233075', '2026-04-04 03:50:34.233077');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (579, 'f145547a-ea95-40c7-b319-d9f3e709a8d9', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Application modal did not open after clicking Apply"}', '5f805487-1fb0-46c2-b7fc-d8f13a25881e', '2026-04-04 03:51:09.357557', '2026-04-04 03:51:09.357559');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (580, '1457bfd5-4e97-460c-bba9-a8ef3e301910', 'bot_started', 'queued', 'applying', 'agent', NULL, '68a5148c-d404-4667-bfa7-98cac8992d1a', '2026-04-04 03:51:09.582157', '2026-04-04 03:51:09.582160');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (581, '4c2963d2-2a51-46e8-99ef-63cb751a6c2f', 'bot_started', 'queued', 'applying', 'agent', NULL, '98ba0ec7-0b2d-4dde-8c7f-75a729e44785', '2026-04-04 03:51:14.761389', '2026-04-04 03:51:14.761390');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (582, '1457bfd5-4e97-460c-bba9-a8ef3e301910', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Application modal did not open after clicking Apply"}', 'f5ecf42d-13a4-4c25-926a-402735585b6d', '2026-04-04 03:51:43.005231', '2026-04-04 03:51:43.005232');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (583, '511c555e-b7b8-4827-90af-b7290ce960dd', 'bot_started', 'queued', 'applying', 'agent', NULL, 'acca2c14-0abd-49c9-9d63-ef50c6ce95a8', '2026-04-04 03:51:43.179245', '2026-04-04 03:51:43.179248');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (584, '4c2963d2-2a51-46e8-99ef-63cb751a6c2f', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Application modal did not open after clicking Apply"}', 'e0deb33c-3102-4d82-9e0d-2d6888675d58', '2026-04-04 03:51:48.595568', '2026-04-04 03:51:48.595569');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (585, '511c555e-b7b8-4827-90af-b7290ce960dd', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Application modal did not open after clicking Apply"}', 'a18815bb-a456-4f27-832e-c608c8b57354', '2026-04-04 03:52:16.174064', '2026-04-04 03:52:16.174066');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (586, 'a9590ba3-8c5b-48c6-b2ff-2168be090eb2', 'bot_started', 'queued', 'applying', 'agent', NULL, '7d3a7d28-6d40-4e8a-8771-a4a4c19d4ef4', '2026-04-04 03:52:16.375351', '2026-04-04 03:52:16.375353');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (587, 'a9590ba3-8c5b-48c6-b2ff-2168be090eb2', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Application modal did not open after clicking Apply"}', '35da837d-53d4-44d3-b59e-760e2b90e72a', '2026-04-04 03:52:49.420171', '2026-04-04 03:52:49.420172');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (588, '88e6f3b8-2960-4be9-b939-8024e10de9a2', 'bot_started', 'queued', 'applying', 'agent', NULL, '3f48ee36-d71e-4675-a0e4-c31b71bc4430', '2026-04-04 03:53:38.342537', '2026-04-04 03:53:38.342539');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (589, '88e6f3b8-2960-4be9-b939-8024e10de9a2', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Application modal did not open after clicking Apply"}', 'ee6b6136-91dc-48d8-b5a3-233abd3a49f3', '2026-04-04 03:54:12.382234', '2026-04-04 03:54:12.382236');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (590, '4c947457-f765-47c1-8a8a-95c05796448e', 'bot_started', 'queued', 'applying', 'agent', NULL, 'ef442b86-4d91-4607-bb8b-79fd2cfd8676', '2026-04-04 03:54:12.771571', '2026-04-04 03:54:12.771573');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (591, '4c947457-f765-47c1-8a8a-95c05796448e', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Application modal did not open after clicking Apply"}', '12b1e292-8719-4861-979d-44708809cdc0', '2026-04-04 03:54:45.533398', '2026-04-04 03:54:45.533399');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (592, '42eb511f-85a3-466f-9753-bdf0249daf13', 'bot_started', 'queued', 'applying', 'agent', NULL, '87c5364a-1ae4-45b6-86cf-82d6e0264f5c', '2026-04-04 03:54:45.707775', '2026-04-04 03:54:45.707777');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (593, '42eb511f-85a3-466f-9753-bdf0249daf13', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Application modal did not open after clicking Apply"}', '7260badb-b3aa-4bdc-be4d-c533f499ee75', '2026-04-04 03:55:19.579438', '2026-04-04 03:55:19.579439');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (594, '316761a8-058f-43d9-8094-53cb7d9feb34', 'bot_started', 'queued', 'applying', 'agent', NULL, '55ed0c28-fa38-49c2-9adc-5f6cd2e3b5aa', '2026-04-04 03:55:19.741005', '2026-04-04 03:55:19.741007');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (595, '316761a8-058f-43d9-8094-53cb7d9feb34', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Application modal did not open after clicking Apply"}', '1c75d91b-328b-4454-ac3b-9fecd2bfe2b9', '2026-04-04 03:55:52.999768', '2026-04-04 03:55:52.999769');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (596, '4de2145d-ef8c-4121-97b1-e9c26b9d2d94', 'bot_started', 'queued', 'applying', 'agent', NULL, 'd3224dfd-54c7-4416-a089-38db2e6dfdea', '2026-04-04 03:55:53.195385', '2026-04-04 03:55:53.195387');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (597, '4de2145d-ef8c-4121-97b1-e9c26b9d2d94', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Application modal did not open after clicking Apply"}', '0f300ad7-272e-4550-bfad-dde68a289c5b', '2026-04-04 03:56:26.553446', '2026-04-04 03:56:26.553447');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (598, '6a48b825-0563-4213-8663-9f3d1a430662', 'bot_started', 'queued', 'applying', 'agent', NULL, 'fa826569-f0d2-4616-a07d-fd0926a92cd3', '2026-04-04 03:56:26.727722', '2026-04-04 03:56:26.727724');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (599, '6a48b825-0563-4213-8663-9f3d1a430662', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Application modal did not open after clicking Apply"}', '8bd64440-6fc8-4bff-8f63-55e45d82b0ad', '2026-04-04 03:57:00.034595', '2026-04-04 03:57:00.034596');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (600, 'b7aff5f7-c579-4dd7-9f13-1592ee726b80', 'bot_started', 'queued', 'applying', 'agent', NULL, 'c291888b-a6f8-4b45-bde8-f91e64179d43', '2026-04-04 03:57:00.189125', '2026-04-04 03:57:00.189127');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (601, 'b7aff5f7-c579-4dd7-9f13-1592ee726b80', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Application modal did not open after clicking Apply"}', '17987051-64c8-4886-90ec-ab55f51ebfe3', '2026-04-04 03:57:33.667628', '2026-04-04 03:57:33.667629');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (602, '44e35fe8-7242-4c08-b9c3-7c42d10f6637', 'bot_started', 'queued', 'applying', 'agent', NULL, 'f6a1304e-bd8c-4078-a508-04f94c431d33', '2026-04-04 03:57:33.879933', '2026-04-04 03:57:33.879934');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (603, '44e35fe8-7242-4c08-b9c3-7c42d10f6637', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Application modal did not open after clicking Apply"}', 'b3749bc5-e1c9-44b3-9c3f-7ba14c62528b', '2026-04-04 03:58:07.438287', '2026-04-04 03:58:07.438289');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (604, 'fd207a62-c5d4-468f-95c2-41628c94fd7e', 'bot_started', 'queued', 'applying', 'agent', NULL, '2135edac-0f49-4ca7-96bf-52aef8bc8b65', '2026-04-04 03:58:07.598739', '2026-04-04 03:58:07.598741');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (605, 'fd207a62-c5d4-468f-95c2-41628c94fd7e', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Application modal did not open after clicking Apply"}', 'fe503214-4f78-4fac-ae08-8af6a5061a3a', '2026-04-04 03:58:40.536960', '2026-04-04 03:58:40.536963');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (606, '47ed1edb-c08f-45cc-994a-dd5a5c750795', 'bot_started', 'queued', 'applying', 'agent', NULL, '8c17a6f2-89e7-43d1-8b74-a9055bd57fb6', '2026-04-04 03:58:40.709843', '2026-04-04 03:58:40.709844');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (607, '47ed1edb-c08f-45cc-994a-dd5a5c750795', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Application modal did not open after clicking Apply"}', '56a3ae68-828d-4c45-b9c0-be0760b9b412', '2026-04-04 03:59:13.748310', '2026-04-04 03:59:13.748311');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (608, '42c6af89-660a-48c8-9d53-14b6fdb3a121', 'bot_started', 'queued', 'applying', 'agent', NULL, '7f78c661-ef13-49a2-a96e-db6a720598c3', '2026-04-04 03:59:57.760063', '2026-04-04 03:59:57.760064');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (609, '42c6af89-660a-48c8-9d53-14b6fdb3a121', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Application modal did not open after clicking Apply"}', '9ba3aca8-a23b-4199-ba70-d6d0f84154be', '2026-04-04 04:00:31.442470', '2026-04-04 04:00:31.442472');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (610, 'e14f0b1e-0b98-4fb1-a568-07c52bf83406', 'bot_started', 'queued', 'applying', 'agent', NULL, '80674088-c290-4bd9-af04-3d2952318984', '2026-04-04 04:00:31.676348', '2026-04-04 04:00:31.676350');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (611, 'e14f0b1e-0b98-4fb1-a568-07c52bf83406', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Application modal did not open after clicking Apply"}', '14b3e345-b443-41ec-a0ef-2ff09561b9f1', '2026-04-04 04:01:04.676076', '2026-04-04 04:01:04.676078');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (612, '80a9c0dd-7fa8-40c9-8d72-cbdb44bfcb4d', 'bot_started', 'queued', 'applying', 'agent', NULL, 'fe138fbc-164a-4f7e-9b98-f44c9fbaacbd', '2026-04-04 04:01:04.875085', '2026-04-04 04:01:04.875087');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (613, '80a9c0dd-7fa8-40c9-8d72-cbdb44bfcb4d', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Application modal did not open after clicking Apply"}', 'a08faa46-70a6-40a6-9072-674cb1d71e67', '2026-04-04 04:01:39.606154', '2026-04-04 04:01:39.606155');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (614, 'c772c153-2298-42ff-b91d-cc5057ad042a', 'bot_started', 'queued', 'applying', 'agent', NULL, '1d2af5db-0ef8-49bc-bca3-0f8af54418f6', '2026-04-04 04:01:39.856965', '2026-04-04 04:01:39.856967');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (615, 'c772c153-2298-42ff-b91d-cc5057ad042a', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Application modal did not open after clicking Apply"}', '769c2dd8-9892-454f-ba19-b4b20881ea99', '2026-04-04 04:18:52.536042', '2026-04-04 04:18:52.536043');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (616, '419099b8-fc90-49b8-928e-48cf48d6648b', 'bot_started', 'queued', 'applying', 'agent', NULL, '9312c178-364b-4b86-8357-58baa20dd53c', '2026-04-04 04:18:55.411690', '2026-04-04 04:18:55.411693');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (617, '419099b8-fc90-49b8-928e-48cf48d6648b', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Page.goto: net::ERR_INTERNET_DISCONNECTED at https://internshala.com/\nCall log:\nnavigating to \"https://internshala.com/\", waiting until \"domcontentloaded\"\n"}', 'e3b4372b-a443-4d6c-b362-1cb68e2b876a', '2026-04-04 04:18:55.818615', '2026-04-04 04:18:55.818616');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (618, 'db25854e-aeee-43cb-94fe-ec990e12412c', 'bot_started', 'queued', 'applying', 'agent', NULL, '69b02d49-99a7-4cb8-b416-7d51e24c113b', '2026-04-04 04:18:58.433119', '2026-04-04 04:18:58.433122');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (619, 'db25854e-aeee-43cb-94fe-ec990e12412c', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Page.goto: net::ERR_INTERNET_DISCONNECTED at https://internshala.com/\nCall log:\nnavigating to \"https://internshala.com/\", waiting until \"domcontentloaded\"\n"}', 'b54f769d-5bcf-4f97-8449-08be66d032f5', '2026-04-04 04:18:58.690776', '2026-04-04 04:18:58.690777');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (620, 'e7f59077-9635-440e-905a-31b81bbafe05', 'bot_started', 'queued', 'applying', 'agent', NULL, '2e85a3c2-171d-499b-aa01-59e0dd5702bc', '2026-04-04 04:19:01.136350', '2026-04-04 04:19:01.136354');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (621, 'e7f59077-9635-440e-905a-31b81bbafe05', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Page.goto: net::ERR_INTERNET_DISCONNECTED at https://internshala.com/\nCall log:\nnavigating to \"https://internshala.com/\", waiting until \"domcontentloaded\"\n"}', '8a1e4e59-cc4b-4b03-b506-ed00346f8a9e', '2026-04-04 04:19:01.388864', '2026-04-04 04:19:01.388865');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (622, 'db52ec31-cb0e-4449-beae-1aaf7ad6e324', 'bot_started', 'queued', 'applying', 'agent', NULL, '2e101209-ff53-4e7a-85db-7c896192e31d', '2026-04-04 04:19:04.103058', '2026-04-04 04:19:04.103061');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (623, 'db52ec31-cb0e-4449-beae-1aaf7ad6e324', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Page.goto: net::ERR_INTERNET_DISCONNECTED at https://internshala.com/\nCall log:\nnavigating to \"https://internshala.com/\", waiting until \"domcontentloaded\"\n"}', '1734a120-5473-4e44-b5f2-131758aa70ce', '2026-04-04 04:19:04.358691', '2026-04-04 04:19:04.358692');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (624, '1e55dc2e-362a-4d08-8362-a5664b7a7aff', 'bot_started', 'queued', 'applying', 'agent', NULL, '6031c384-1063-48c7-96f8-bff27d0bb982', '2026-04-04 04:19:07.012166', '2026-04-04 04:19:07.012169');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (625, '1e55dc2e-362a-4d08-8362-a5664b7a7aff', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Page.goto: net::ERR_INTERNET_DISCONNECTED at https://internshala.com/\nCall log:\nnavigating to \"https://internshala.com/\", waiting until \"domcontentloaded\"\n"}', 'ee49639a-f8b5-4d6f-93b1-33eddb011008', '2026-04-04 04:19:07.263363', '2026-04-04 04:19:07.263364');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (626, 'eead296f-de63-49ff-8a4c-89e8b5af2732', 'bot_started', 'queued', 'applying', 'agent', NULL, '05b22b32-9b79-454e-b546-a8095f06e5bf', '2026-04-04 04:19:09.874409', '2026-04-04 04:19:09.874411');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (627, 'eead296f-de63-49ff-8a4c-89e8b5af2732', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Page.goto: net::ERR_INTERNET_DISCONNECTED at https://internshala.com/\nCall log:\nnavigating to \"https://internshala.com/\", waiting until \"domcontentloaded\"\n"}', '50527e92-956a-44c1-b3f1-108997ef5d23', '2026-04-04 04:19:10.127640', '2026-04-04 04:19:10.127641');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (628, '47547282-360e-4e14-9aa3-917deeb8e979', 'bot_started', 'queued', 'applying', 'agent', NULL, 'a2e7515b-ff2c-4b78-8114-53d8821917e8', '2026-04-04 05:33:38.420889', '2026-04-04 05:33:38.420890');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (629, '47547282-360e-4e14-9aa3-917deeb8e979', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Application modal did not open after clicking Apply"}', 'f16a44ca-6779-4be9-8fff-43309d8efcb8', '2026-04-04 05:34:15.855668', '2026-04-04 05:34:15.855669');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (630, 'b23f68ce-14b8-4c5e-99bc-4f8a0f0c2df2', 'bot_started', 'queued', 'applying', 'agent', NULL, 'b1f251a5-6cd3-4b26-a900-d8eed1d3c088', '2026-04-04 05:34:16.006806', '2026-04-04 05:34:16.006807');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (631, 'b23f68ce-14b8-4c5e-99bc-4f8a0f0c2df2', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Application modal did not open after clicking Apply"}', '16c11249-173f-48e8-828d-a5b999f18932', '2026-04-04 05:34:51.913257', '2026-04-04 05:34:51.913258');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (632, 'ca0c301b-a427-48c5-bdcd-b3e134312e29', 'bot_started', 'queued', 'applying', 'agent', NULL, '96136d12-c935-4449-b6f6-afa791094b98', '2026-04-04 05:35:39.240971', '2026-04-04 05:35:39.240974');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (633, 'ca0c301b-a427-48c5-bdcd-b3e134312e29', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Application modal did not open after clicking Apply"}', '8f7be0df-fb56-4525-a6c6-fd6216fcf3a0', '2026-04-04 05:36:16.249581', '2026-04-04 05:36:16.249582');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (634, 'dddf5a71-72f0-49ce-bc91-eb4afa958b93', 'bot_started', 'queued', 'applying', 'agent', NULL, 'de8cb1dc-e130-47f6-84ef-20d7a0f25419', '2026-04-04 05:36:16.466491', '2026-04-04 05:36:16.466493');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (635, 'dddf5a71-72f0-49ce-bc91-eb4afa958b93', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Application modal did not open after clicking Apply"}', 'c9bd7a47-72ce-4192-86b1-53827f6a6e59', '2026-04-04 05:36:52.534432', '2026-04-04 05:36:52.534434');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (636, 'f17fbd19-5a07-4380-9d36-39693a807d3b', 'bot_started', 'queued', 'applying', 'agent', NULL, 'c02d0809-2e01-4493-9250-801fdade0ffe', '2026-04-04 05:36:52.762395', '2026-04-04 05:36:52.762396');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (637, 'f17fbd19-5a07-4380-9d36-39693a807d3b', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Application modal did not open after clicking Apply"}', '29087f9e-0374-4073-a9c8-bf85cbd09a5d', '2026-04-04 05:37:29.012631', '2026-04-04 05:37:29.012632');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (638, '0c0b11d8-8c86-422b-bd22-c8219d6445f1', 'bot_started', 'queued', 'applying', 'agent', NULL, '5a9372d3-309c-41fe-a116-6b4cb4322e93', '2026-04-04 05:37:29.211768', '2026-04-04 05:37:29.211770');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (639, '0c0b11d8-8c86-422b-bd22-c8219d6445f1', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Application modal did not open after clicking Apply"}', '9be1eb79-7a54-483d-a096-e4fe2411abb5', '2026-04-04 05:38:04.911952', '2026-04-04 05:38:04.911953');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (640, '8da60b03-c79e-4c65-be33-81ccc82be3ad', 'bot_started', 'queued', 'applying', 'agent', NULL, '8086e834-7a47-4ee2-8ecc-bac96338558d', '2026-04-04 05:38:05.271483', '2026-04-04 05:38:05.271484');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (641, '8da60b03-c79e-4c65-be33-81ccc82be3ad', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Application modal did not open after clicking Apply"}', '9b2203c9-e598-439d-8932-4d25f5ba4bab', '2026-04-04 05:38:42.180438', '2026-04-04 05:38:42.180439');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (642, 'c4fbb8a2-6ee9-404d-b9ba-c2336c3ead37', 'bot_started', 'queued', 'applying', 'agent', NULL, '9737ae86-daaf-4e06-af29-db39c76928d1', '2026-04-04 05:38:42.330173', '2026-04-04 05:38:42.330175');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (643, 'c4fbb8a2-6ee9-404d-b9ba-c2336c3ead37', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Application modal did not open after clicking Apply"}', '305c6e5d-1ce1-4f6e-894b-be38cd8210bc', '2026-04-04 05:39:18.896310', '2026-04-04 05:39:18.896311');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (644, '8d40fe04-b7ec-4a1f-8d32-049f6aebc952', 'bot_started', 'queued', 'applying', 'agent', NULL, '524a2717-0890-4936-9d00-d30f69a6225e', '2026-04-04 05:39:19.106160', '2026-04-04 05:39:19.106162');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (645, '8d40fe04-b7ec-4a1f-8d32-049f6aebc952', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Application modal did not open after clicking Apply"}', '32002174-b7d1-4f48-b3c5-8315983e1b92', '2026-04-04 05:39:54.983095', '2026-04-04 05:39:54.983096');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (646, '2972af97-f726-4bf4-91fb-130481add345', 'bot_started', 'queued', 'applying', 'agent', NULL, 'f6ab16eb-925d-48ca-bcd6-15148a27b510', '2026-04-04 05:39:55.205729', '2026-04-04 05:39:55.205731');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (647, '2972af97-f726-4bf4-91fb-130481add345', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Application modal did not open after clicking Apply"}', 'fc97a7f7-4f3c-42b6-a8bf-6ecdc55b62f0', '2026-04-04 05:40:31.579926', '2026-04-04 05:40:31.579927');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (648, '9f6c0a95-3d64-4d48-95de-bf4c6ac51a0d', 'bot_started', 'queued', 'applying', 'agent', NULL, 'a618df89-b462-4f41-8376-1621e5e675a9', '2026-04-04 05:42:22.104014', '2026-04-04 05:42:22.104016');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (649, '9f6c0a95-3d64-4d48-95de-bf4c6ac51a0d', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible - Internshala profile requirements not met"}', '3d1533a6-41a0-48f9-b3bc-702eba18b828', '2026-04-04 05:42:34.511358', '2026-04-04 05:42:34.511359');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (650, '92c9e3f5-8ee2-414f-a0b6-0158ac0ad7c0', 'bot_started', 'queued', 'applying', 'agent', NULL, '430ce592-1a01-4392-a399-565380c8fc9c', '2026-04-04 05:42:34.663552', '2026-04-04 05:42:34.663554');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (651, '92c9e3f5-8ee2-414f-a0b6-0158ac0ad7c0', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible - Internshala profile requirements not met"}', 'c35430fc-8ac3-478b-9ba0-8abc77b51c8b', '2026-04-04 05:42:47.340968', '2026-04-04 05:42:47.340970');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (652, '2f261326-02f4-4e97-a831-98af10cdcf43', 'bot_started', 'queued', 'applying', 'agent', NULL, 'a9b94d07-8a2f-47e4-be6d-fd622d8d08e3', '2026-04-04 05:42:47.513720', '2026-04-04 05:42:47.513722');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (653, '2f261326-02f4-4e97-a831-98af10cdcf43', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible - Internshala profile requirements not met"}', 'cdc3716d-271b-4029-811a-dd14d802a7a5', '2026-04-04 05:42:59.687268', '2026-04-04 05:42:59.687269');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (654, 'dd0ac8de-126d-41ad-9d05-67891f9a3819', 'bot_started', 'queued', 'applying', 'agent', NULL, 'bdfe355e-c65b-43d1-bc66-5dbd96611a81', '2026-04-04 05:42:59.870399', '2026-04-04 05:42:59.870400');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (655, 'dd0ac8de-126d-41ad-9d05-67891f9a3819', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible - Internshala profile requirements not met"}', '2f9dd592-975c-498a-a454-4cd2a55aa028', '2026-04-04 05:43:12.483177', '2026-04-04 05:43:12.483178');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (656, '96961872-f48c-4d0c-96f6-8678ea2d2233', 'bot_started', 'queued', 'applying', 'agent', NULL, '65d79f30-d642-4075-ac0d-00612097488b', '2026-04-04 05:43:12.639778', '2026-04-04 05:43:12.639779');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (657, '96961872-f48c-4d0c-96f6-8678ea2d2233', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible - Internshala profile requirements not met"}', '4b2a9914-d5d0-443d-99eb-cefc1ef9217d', '2026-04-04 05:43:25.416098', '2026-04-04 05:43:25.416099');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (658, '8c3bf165-b6fe-402e-8844-96b9f019a2a8', 'bot_started', 'queued', 'applying', 'agent', NULL, 'c299d204-90b5-415c-8c9a-29015a65411d', '2026-04-04 05:43:25.584414', '2026-04-04 05:43:25.584416');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (659, '8c3bf165-b6fe-402e-8844-96b9f019a2a8', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible - Internshala profile requirements not met"}', '813860e5-2c92-4938-9d16-aeebcee63c03', '2026-04-04 05:43:38.133954', '2026-04-04 05:43:38.133955');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (660, '85a5bf90-c262-488c-a4c8-13f0180e4f96', 'bot_started', 'queued', 'applying', 'agent', NULL, 'b24a7900-758c-4f8d-b833-bdcba0d92d3a', '2026-04-04 05:43:38.276767', '2026-04-04 05:43:38.276769');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (661, '85a5bf90-c262-488c-a4c8-13f0180e4f96', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible - Internshala profile requirements not met"}', 'e37e6483-33bc-4171-ab93-a7c6d39e6203', '2026-04-04 05:43:51.375318', '2026-04-04 05:43:51.375319');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (662, 'c282536b-9662-4714-a0b2-e7d60eb42ce9', 'bot_started', 'queued', 'applying', 'agent', NULL, '856c636d-a7d8-47cd-8f6c-fe7f57c608a1', '2026-04-04 05:43:51.600301', '2026-04-04 05:43:51.600305');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (663, 'c282536b-9662-4714-a0b2-e7d60eb42ce9', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible - Internshala profile requirements not met"}', '3f5d42a1-8911-4234-85c2-760efd9f6d09', '2026-04-04 05:44:04.157727', '2026-04-04 05:44:04.157728');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (664, 'c87a2894-c41b-4e73-a8a2-449b98e60fb7', 'bot_started', 'queued', 'applying', 'agent', NULL, '96a67e80-2b7e-46d0-bb87-b0516a253c38', '2026-04-04 05:44:04.304679', '2026-04-04 05:44:04.304681');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (665, 'c87a2894-c41b-4e73-a8a2-449b98e60fb7', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible - Internshala profile requirements not met"}', '4bcf51c1-195a-4b83-9ac7-0d538e9a9089', '2026-04-04 05:44:16.357221', '2026-04-04 05:44:16.357222');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (666, '6fcb86a7-8807-420f-9e27-6a2414ae486f', 'bot_started', 'queued', 'applying', 'agent', NULL, '748a5e5b-207d-4037-992d-e81e3ba795c0', '2026-04-04 05:44:16.500096', '2026-04-04 05:44:16.500098');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (667, '6fcb86a7-8807-420f-9e27-6a2414ae486f', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible - Internshala profile requirements not met"}', '175312ba-21d2-4ca4-97ff-f7060abab4a0', '2026-04-04 05:44:28.669382', '2026-04-04 05:44:28.669383');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (668, '69b6c600-41dd-41cd-bb39-7e6c08b002e2', 'bot_started', 'queued', 'applying', 'agent', NULL, 'cfe43df8-d3ad-40c4-93fc-8f0c790c4838', '2026-04-04 05:48:10.176547', '2026-04-04 05:48:10.176549');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (669, '69b6c600-41dd-41cd-bb39-7e6c08b002e2', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible - Internshala profile requirements not met"}', '29e3d5ec-4023-421c-af8e-3a2b45fb5a62', '2026-04-04 05:48:22.839931', '2026-04-04 05:48:22.839933');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (670, '6363b178-cd8d-4db1-a6a6-887448191cb5', 'bot_started', 'queued', 'applying', 'agent', NULL, '61c0780c-4782-4a24-bd3a-d754fa83c5e9', '2026-04-04 05:48:23.016255', '2026-04-04 05:48:23.016256');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (671, '6363b178-cd8d-4db1-a6a6-887448191cb5', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible - Internshala profile requirements not met"}', 'f6162f51-92f4-4936-ae8e-f58f7d0745fe', '2026-04-04 05:48:35.625478', '2026-04-04 05:48:35.625479');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (672, '2794ba6f-be96-4efc-a17d-298828a3e55c', 'bot_started', 'queued', 'applying', 'agent', NULL, '3adf542d-f084-438f-9064-78be9746ba87', '2026-04-04 05:48:35.824184', '2026-04-04 05:48:35.824186');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (673, '2794ba6f-be96-4efc-a17d-298828a3e55c', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible - Internshala profile requirements not met"}', 'a306e38b-4fff-4d6f-9928-7d7902474729', '2026-04-04 05:48:49.453110', '2026-04-04 05:48:49.453111');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (674, '20ab1d69-82fa-49fb-b8df-f033bc845b0d', 'bot_started', 'queued', 'applying', 'agent', NULL, '39f79461-ea29-4001-a8f2-8db9d8d61491', '2026-04-04 05:48:49.667142', '2026-04-04 05:48:49.667143');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (675, '20ab1d69-82fa-49fb-b8df-f033bc845b0d', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible - Internshala profile requirements not met"}', '015d17ba-0e43-48a0-b370-78be014dab62', '2026-04-04 05:49:03.292506', '2026-04-04 05:49:03.292507');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (676, '7c3d21ca-cabe-49b4-bccc-742704a82b16', 'bot_started', 'queued', 'applying', 'agent', NULL, '421cc9ea-c86f-4b5a-900d-97a2b2c3b034', '2026-04-04 05:49:03.448473', '2026-04-04 05:49:03.448474');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (677, '7c3d21ca-cabe-49b4-bccc-742704a82b16', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible - Internshala profile requirements not met"}', 'ea8ed782-3edf-41b5-9d46-60fc44fb1d29', '2026-04-04 05:49:16.767464', '2026-04-04 05:49:16.767465');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (678, '74d6368e-87af-4af2-bbf6-daba288ecbfe', 'bot_started', 'queued', 'applying', 'agent', NULL, '9945ffd3-ac94-43bd-957b-d8d3c545a19c', '2026-04-04 05:49:16.987024', '2026-04-04 05:49:16.987026');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (679, '74d6368e-87af-4af2-bbf6-daba288ecbfe', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible - Internshala profile requirements not met"}', 'f23cb446-1574-4ac3-9e69-5a5fd13af119', '2026-04-04 05:49:29.900592', '2026-04-04 05:49:29.900593');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (680, '108cbf3d-c5c2-4d96-aa93-d07ce54a721a', 'bot_started', 'queued', 'applying', 'agent', NULL, 'c5cb15ee-abd7-419e-82df-381b34307513', '2026-04-04 05:49:30.056883', '2026-04-04 05:49:30.056885');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (681, '108cbf3d-c5c2-4d96-aa93-d07ce54a721a', 'bot_failed', 'applying', 'failed', 'agent', '{"error": "Not eligible - Internshala profile requirements not met"}', '5fd494ec-e018-4610-b45a-752b8591fe18', '2026-04-04 05:49:42.342524', '2026-04-04 05:49:42.342524');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (682, '04bfc34a-c079-4f02-919a-7a009f732ef0', 'bot_started', 'queued', 'applying', 'agent', NULL, '1344005f-c183-424b-bbff-b4198d43c04b', '2026-04-04 05:49:42.543239', '2026-04-04 05:49:42.543241');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (882, 'cc198347-066e-45df-8b90-d33346fa15fe', 'status_changed', 'pending_approval', 'queued', 'user', '{"action": "approved"}', '041e6e0c-4487-414a-98f1-ecbb0cf0eec4', '2026-04-04 07:57:59.717977', '2026-04-04 07:57:59.717978');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (883, '1f6fc79f-fc0d-4306-821c-185281d64307', 'status_changed', 'pending_approval', 'queued', 'user', '{"action": "approved"}', '26f9a9e9-f49c-44a9-9351-63845098ce6e', '2026-04-04 07:57:59.722749', '2026-04-04 07:57:59.722749');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (884, '1e49a8dd-0820-4c9b-a418-ded44b15d45f', 'status_changed', 'pending_approval', 'queued', 'user', '{"action": "approved"}', 'dd120d7f-47f1-4b53-a0bf-457b2eeec558', '2026-04-04 07:57:59.728344', '2026-04-04 07:57:59.728345');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (885, '408d1f28-a078-4c85-bd9a-66258714b4b7', 'status_changed', 'pending_approval', 'queued', 'user', '{"action": "approved"}', 'd8780d30-985e-40a6-86b0-b8139bae8254', '2026-04-04 07:57:59.735455', '2026-04-04 07:57:59.735455');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (886, '244403aa-f828-4e5d-8460-03030d880fd8', 'status_changed', 'pending_approval', 'queued', 'user', '{"action": "approved"}', '6164994b-7be8-4fcc-bb6b-e95bae65f3a3', '2026-04-04 07:57:59.740804', '2026-04-04 07:57:59.740805');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (887, '4d89ac32-4227-427c-887f-e7bc3b53be8c', 'status_changed', 'pending_approval', 'queued', 'user', '{"action": "approved"}', '812032e0-cfe6-4ba9-a7e3-762a8b7b4bd3', '2026-04-04 07:57:59.743704', '2026-04-04 07:57:59.743705');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (888, 'f852024f-2237-4a61-946c-c81a7a15f2aa', 'status_changed', 'pending_approval', 'queued', 'user', '{"action": "approved"}', '0976b5f7-c0eb-4f72-8901-7005e86ced41', '2026-04-04 07:57:59.749948', '2026-04-04 07:57:59.749949');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (889, '2f715080-5adf-4273-a170-ac2bca42e393', 'status_changed', 'pending_approval', 'queued', 'user', '{"action": "approved"}', '66b1f708-40d9-4869-a11a-23379fcb2f3e', '2026-04-04 07:57:59.756800', '2026-04-04 07:57:59.756800');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (890, '3f1db290-50e2-4a3c-9982-eeafcaec317f', 'status_changed', 'pending_approval', 'queued', 'user', '{"action": "approved"}', 'f01eefbd-ff70-480f-9bf8-397dc6a8123f', '2026-04-04 07:57:59.758526', '2026-04-04 07:57:59.758526');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (891, '01f4cdbe-2dfe-425a-8e97-aa8354b41a18', 'status_changed', 'pending_approval', 'queued', 'user', '{"action": "approved"}', '0f98c399-3958-4df5-9aee-b4f8932dc81a', '2026-04-04 07:57:59.762472', '2026-04-04 07:57:59.762473');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (892, '8c55da5e-fa2e-47bb-a88f-1e710dc1235c', 'status_changed', 'pending_approval', 'queued', 'user', '{"action": "approved"}', 'e423facc-d995-4f2d-8c61-df7eb05db263', '2026-04-04 07:57:59.767892', '2026-04-04 07:57:59.767892');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (893, '9f55d693-34e5-48a1-a8fb-0c0e143ad07f', 'status_changed', 'pending_approval', 'queued', 'user', '{"action": "approved"}', '42601ee8-d68d-441f-a6bb-93114368cdec', '2026-04-04 07:57:59.788548', '2026-04-04 07:57:59.788549');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (894, 'c541e063-ab1f-40eb-ba26-1caebaa0f23a', 'status_changed', 'pending_approval', 'queued', 'user', '{"action": "approved"}', '2c1f1fa4-cd79-49ae-bd23-2c5562c09c5e', '2026-04-04 07:57:59.794992', '2026-04-04 07:57:59.794993');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (895, '166a0239-74cc-434a-aef5-e89a81c3a188', 'status_changed', 'pending_approval', 'queued', 'user', '{"action": "approved"}', 'bcafa8aa-9fbd-4721-aa67-ef7955a5d2d1', '2026-04-04 07:57:59.798198', '2026-04-04 07:57:59.798199');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (896, '1ba6e3ca-b731-4ea3-95e3-64ead51f9324', 'status_changed', 'pending_approval', 'queued', 'user', '{"action": "approved"}', '747a458a-d5a4-46ee-9db9-90362f005154', '2026-04-04 07:57:59.871289', '2026-04-04 07:57:59.871290');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (897, '3d577146-e29d-426a-bd0a-618cb5e59a05', 'bot_started', 'queued', 'applying', 'agent', NULL, '0d4afa7d-c4f2-4b2e-8c37-63fde5ac78a2', '2026-04-04 08:01:00.394592', '2026-04-04 08:01:00.394593');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (898, '3d577146-e29d-426a-bd0a-618cb5e59a05', 'ineligible', 'applying', 'skipped', 'agent', '{"reason": "Not eligible - profile location does not match job requirements"}', 'ebc6829c-5619-45e1-9154-d580e102089d', '2026-04-04 08:01:13.816895', '2026-04-04 08:01:13.816897');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (899, 'ef08b08c-9fa8-4cb1-8a3f-4169e64010d0', 'bot_started', 'queued', 'applying', 'agent', NULL, '873822c3-a0e0-4a35-8d22-d7b413dd2929', '2026-04-04 08:02:31.994923', '2026-04-04 08:02:31.994926');
INSERT OR IGNORE INTO 'application_events'(_rowid_, 'application_id', 'event_type', 'from_status', 'to_status', 'triggered_by', 'details', 'id', 'created_at', 'updated_at') VALUES (900, 'ef08b08c-9fa8-4cb1-8a3f-4169e64010d0', 'ineligible', 'applying', 'skipped', 'agent', '{"reason": "Not eligible - profile location does not match job requirements"}', '2c157e92-5f9c-471b-b7db-be2d07c54691', '2026-04-04 08:02:45.452654', '2026-04-04 08:02:45.452655');
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3418, 204, 204, 2, NULL, '2026-04-05 03:51:48.513197', 169);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3419, 204, 204, 2, NULL, '2026-04-05 08:53:35.162389', 170);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3420, 204, 204, 2, NULL, '2026-04-05 08:53:35.162393', 171);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3421, 204, 204, 2, NULL, '2026-04-05 08:53:35.162395', 172);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3422, 204, 204, 2, NULL, '2026-04-05 08:53:35.162397', 173);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3423, 204, 204, 2, NULL, '2026-04-05 08:53:35.162400', 174);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3424, 204, 204, 2, NULL, '2026-04-05 08:53:35.162402', 175);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3425, 204, 204, 2, NULL, '2026-04-05 13:13:06.892122', 176);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3426, 204, 204, 2, NULL, '2026-04-05 13:13:06.892149', 177);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3427, 204, 204, 2, NULL, '2026-04-05 13:13:06.892157', 178);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3428, 204, 204, 2, NULL, '2026-04-05 13:13:06.892163', 179);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3429, 204, 204, 2, NULL, '2026-04-05 13:13:06.892168', 180);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3430, 204, 204, 2, NULL, '2026-04-06 07:18:34.310912', 181);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3431, 204, 204, 2, NULL, '2026-04-06 07:18:34.310921', 182);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3432, 204, 204, 2, NULL, '2026-04-06 07:18:34.310925', 183);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3433, 204, 204, 2, NULL, '2026-04-06 07:18:34.310928', 184);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3434, 204, 204, 2, NULL, '2026-04-06 07:18:34.310931', 185);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3435, 204, 204, 2, NULL, '2026-04-06 07:18:34.310934', 186);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3436, 204, 204, 2, NULL, '2026-04-06 07:18:34.310937', 187);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3437, 204, 204, 2, NULL, '2026-04-06 07:18:34.310940', 188);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3438, 204, 204, 2, NULL, '2026-04-06 07:18:34.310943', 189);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3439, 204, 204, 2, NULL, '2026-04-06 07:18:34.310946', 190);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3440, 204, 204, 2, NULL, '2026-04-06 07:18:34.310949', 191);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3441, 204, 204, 2, NULL, '2026-04-06 07:18:34.310952', 192);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3442, 204, 204, 2, NULL, '2026-04-06 07:18:34.310954', 193);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3443, 204, 204, 2, NULL, '2026-04-06 07:18:34.310958', 194);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3444, 204, 204, 2, NULL, '2026-04-06 07:18:34.310960', 195);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3445, 204, 204, 2, NULL, '2026-04-06 07:18:34.310963', 196);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3446, 204, 204, 2, NULL, '2026-04-06 07:18:34.310966', 197);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3447, 204, 204, 2, NULL, '2026-04-06 07:18:34.310968', 198);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3448, 204, 204, 2, NULL, '2026-04-06 07:18:34.310971', 199);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3449, 204, 204, 2, NULL, '2026-04-06 07:18:34.310974', 200);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3450, 204, 204, 2, NULL, '2026-04-12 16:11:13.812442', 201);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3451, 204, 204, 2, NULL, '2026-04-12 16:11:13.812448', 202);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3452, 204, 204, 2, NULL, '2026-04-12 16:11:13.812451', 203);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3453, 204, 204, 2, NULL, '2026-04-12 16:11:13.812453', 204);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3454, 204, 204, 2, NULL, '2026-04-12 16:11:13.812456', 205);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3455, 204, 204, 2, NULL, '2026-04-12 16:11:13.812459', 206);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3456, 204, 204, 2, NULL, '2026-04-12 16:11:13.812461', 207);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3457, 204, 204, 2, NULL, '2026-04-12 16:11:13.812464', 208);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3458, 204, 204, 2, NULL, '2026-04-12 16:11:13.812467', 209);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3459, 204, 204, 2, NULL, '2026-04-12 16:11:13.812469', 210);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3460, 204, 204, 2, NULL, '2026-04-12 16:11:13.812472', 211);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3461, 204, 204, 2, NULL, '2026-04-12 16:11:13.812474', 212);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3462, 204, 204, 2, NULL, '2026-04-12 16:11:13.812477', 213);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3463, 204, 204, 2, NULL, '2026-04-12 16:11:13.812480', 214);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3464, 204, 204, 2, NULL, '2026-04-12 16:11:13.812484', 215);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3465, 204, 204, 2, NULL, '2026-04-12 16:11:13.812486', 216);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1, 14, 14, 2, NULL, '4826d00b-0e5d-4390-b8ac-0ff6c3718369', 255);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2, 14, 14, 2, NULL, '8961dff8-f575-4cf5-a1c9-5bbca71fec6f', 52);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3, 14, 14, 2, NULL, 'e1cd11c3-3afd-4b74-bb43-b9eb55cf6335', 76);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (4, 14, 15, 2, NULL, '001f713e-b1d2-4fd5-8f34-5789fb5b710e', 25);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (5, 14, 15, 2, NULL, '0181751b-362c-4688-9a52-24d2480aa6fb', 142);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (6, 14, 15, 2, NULL, '018db9a0-9cc3-4281-b3d6-a255f76ba47d', 215);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (7, 14, 15, 2, NULL, '01b012e1-a7cd-4d4d-9429-d760a7a36814', 206);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (8, 14, 15, 2, NULL, '024dc32f-45a4-440d-a49e-76174a3350f8', 235);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (9, 14, 15, 2, NULL, '0494439e-6334-4662-adbf-f27c6301a2a6', 272);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (10, 14, 15, 2, NULL, '04fed8ab-4db5-42a8-b3a8-8d8845a104b6', 39);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (11, 14, 15, 2, NULL, '058354ec-0eda-4387-9847-7c9ad97ccbfe', 2);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (12, 14, 15, 2, NULL, '059e47c3-8f18-4ed9-85e8-e2075dcff113', 283);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (13, 14, 15, 2, NULL, '06759dd8-7d7c-4d3f-b125-d7fef40399fb', 24);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (14, 14, 15, 2, NULL, '08c02197-175c-4008-b8fa-559c70200376', 194);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (15, 14, 15, 2, NULL, '0a5a700b-c15c-40d9-b6c1-5fee3938e4af', 253);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (16, 14, 15, 2, NULL, '0b5a5570-39de-4166-a680-d93fb51c0193', 125);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (17, 14, 15, 2, NULL, '0cfe99bd-93a4-4623-be1e-ab404329f848', 1);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (18, 14, 15, 2, NULL, '0f490bd3-81e4-46dc-8dc4-29a1e9396222', 292);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (19, 14, 15, 2, NULL, '103d90c7-16c0-416f-b0a7-4578b495ca8f', 277);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (20, 14, 15, 2, NULL, '10a143f5-8664-45a0-bccf-79c1565e037c', 35);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (21, 14, 15, 2, NULL, '10a5a106-f9a7-4cd1-911a-f700a6385dd2', 171);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (22, 14, 15, 2, NULL, '1229e6e5-8ebf-4ea6-b7c0-61c8c5b322fa', 262);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (23, 14, 15, 2, NULL, '13c186ba-f903-463d-9393-6838c7c829dd', 325);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (24, 14, 15, 2, NULL, '13f66762-9c57-44f5-9404-92cd1d5aadb6', 100);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (25, 14, 15, 2, NULL, '14d4eb79-5860-481c-986e-16e19dca0b4e', 167);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (26, 14, 15, 2, NULL, '151bfabe-aafd-42b3-88fa-776aa75d504c', 69);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (27, 14, 15, 2, NULL, '1616dfee-ae1e-4aad-ae47-775c49334374', 207);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (28, 14, 15, 2, NULL, '16d94f72-ed74-4f23-a12b-cd83b655bf66', 307);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (29, 14, 15, 2, NULL, '1762858e-c461-44d4-9701-8522a0140b7f', 182);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (30, 14, 15, 2, NULL, '187b1bf6-eb19-42b5-add6-7db0af93c633', 169);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (31, 14, 15, 2, NULL, '1893ee73-a045-42bd-868b-f6362b340b66', 31);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (32, 14, 15, 2, NULL, '18ebcbde-13ec-4a94-9feb-ed1c35717858', 179);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (33, 14, 15, 2, NULL, '18fd3d14-d3ee-4321-a802-0da7debaff8d', 181);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (34, 14, 15, 2, NULL, '1b79cfcf-14c3-4504-b0db-16e3cb0d9d69', 290);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (35, 14, 15, 2, NULL, '1b868b4d-457d-4ea9-bfa3-e5821bfa62a7', 30);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (36, 14, 15, 2, NULL, '1c028561-0281-4b31-82f7-73930213d556', 285);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (37, 14, 15, 2, NULL, '1c416b76-a7de-4f88-aeb1-38f61cf2778f', 306);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (38, 14, 15, 2, NULL, '1d3fbee4-7ddb-471c-9806-6ff240cccd4f', 231);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (39, 14, 15, 2, NULL, '1ef0f01a-e764-483f-8f56-09f2d69304bf', 5);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (40, 14, 15, 2, NULL, '1fbccebc-1316-426c-b6ec-a66abc8a77f0', 287);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (41, 14, 15, 2, NULL, '20b6ef13-6b70-4b8b-815b-44ef9870fd1a', 16);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (42, 14, 15, 2, NULL, '2169fa40-49ea-48ad-97df-fb61f0e033f2', 161);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (43, 14, 15, 2, NULL, '21d2af12-10e0-46c6-a1af-2b8234b4adf1', 208);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (44, 14, 15, 2, NULL, '21e06617-f1b8-4cee-a599-7dbf68eb3b6d', 106);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (45, 14, 15, 2, NULL, '232b4ccb-06a8-4fc2-ba68-a36ecf7c29f5', 218);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (46, 14, 15, 2, NULL, '23618cbe-fb29-46b6-85db-7a6ffcd01782', 217);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (47, 14, 15, 2, NULL, '23b0c96c-e5b4-471b-94d6-01077a96a65d', 242);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (48, 14, 15, 2, NULL, '24b1b249-384e-4287-a01e-a1fa73f8865f', 284);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (49, 14, 15, 2, NULL, '25714984-ea0b-4974-add0-abd485ae2a3e', 85);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (50, 14, 15, 2, NULL, '257302ff-ed08-4681-9c26-9580079a9467', 219);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (51, 14, 15, 2, NULL, '25d22dea-b1db-4111-82f6-fa227a7f55e3', 43);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (52, 14, 15, 2, NULL, '25ffe596-d016-4628-96c0-a3af4fe8e9a8', 56);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (53, 14, 15, 2, NULL, '26cd64d3-9d37-4c9a-914e-d19259395301', 216);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (54, 14, 15, 2, NULL, '28833943-db61-466b-a01a-a3de71f271dd', 236);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (55, 14, 15, 2, NULL, '28d0eb25-0751-4834-9375-c51b553df62c', 147);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (56, 14, 15, 2, NULL, '297910be-8b02-4406-9acc-9f4015787554', 127);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (57, 14, 15, 2, NULL, '2a4a41ed-f71a-4113-942b-244e8e88b269', 40);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (58, 14, 15, 2, NULL, '2a5cf452-0331-4447-9ada-913608e7649f', 90);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (59, 14, 15, 2, NULL, '2b4c434e-325c-42cc-8309-2ceed56795e7', 124);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (60, 14, 15, 2, NULL, '2ba298ed-12b6-440f-9bb1-dcf127ac3ac9', 143);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (61, 14, 15, 2, NULL, '2c2ffab9-61b3-44ee-87e3-8f58df7fe024', 259);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (62, 14, 15, 2, NULL, '2c96cb35-966b-4e82-b558-34992c3abd00', 314);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (63, 14, 15, 2, NULL, '2db67bfd-9922-4780-b49f-d69ef6f310a5', 244);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (64, 14, 15, 2, NULL, '302add44-c1d8-4a18-9ea4-78a06d3e52c2', 178);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (65, 14, 15, 2, NULL, '30e1fc90-8a33-4bcf-96da-092423eec800', 128);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (66, 14, 15, 2, NULL, '31ebc0d2-eccb-4ff3-a6c5-03751a5865f2', 94);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (67, 14, 15, 2, NULL, '3280979d-725b-448a-8a81-8866878d697d', 232);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (68, 14, 15, 2, NULL, '3487a4cf-2f1a-4ef0-ad9c-ad26c5072a15', 12);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (69, 14, 15, 2, NULL, '350726b2-86d5-402b-90e4-a0c7613d9fe6', 22);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (70, 14, 15, 2, NULL, '35089a00-236e-4633-8fec-d4da81abaa22', 41);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (71, 14, 15, 2, NULL, '352a10f9-3332-48e8-946e-a04af1d0657a', 190);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (72, 14, 15, 2, NULL, '36151e7e-fe68-45c5-a7f4-8ae1c5993cf6', 185);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (73, 14, 15, 2, NULL, '3620bb0f-25e5-448c-85b0-a630fdc28db4', 36);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (74, 14, 15, 2, NULL, '363e8798-9d4f-4207-89cc-e8957762c630', 77);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (75, 14, 15, 2, NULL, '38329125-3b63-4752-a72c-83f4e8b8c43d', 116);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (76, 14, 15, 2, NULL, '38f9c526-85b3-4c44-9055-afa6475287fc', 196);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (77, 14, 15, 2, NULL, '39fd220f-ebdd-4f7a-9887-e3f17149053e', 220);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (78, 14, 15, 2, NULL, '3a612b95-3a78-4535-ae86-8ebe4e95cc14', 57);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (79, 14, 15, 2, NULL, '3a743c76-6e41-484d-b391-a4b56378a81f', 282);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (80, 14, 15, 2, NULL, '3a9fe65c-ac49-400e-8ce3-ff099644df76', 37);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (81, 14, 15, 2, NULL, '3abc21f3-50f5-4a2b-8c45-9d7c31f64231', 239);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (82, 14, 15, 2, NULL, '3b8beb43-9915-425e-b193-b50fd73df0b5', 70);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (83, 14, 15, 2, NULL, '3bb184ef-0aa0-4d71-b050-d11d705da9e1', 202);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (84, 14, 15, 2, NULL, '3bfc8b90-be4f-4a40-8d8c-8013de11915a', 322);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (85, 14, 15, 2, NULL, '3c7f782e-c5de-452b-8f99-7bf08eeeebb8', 222);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (86, 14, 15, 2, NULL, '3cd0b630-46e4-428f-a510-9c9cce7a19a4', 117);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (87, 14, 15, 2, NULL, '3db0d146-62f5-4a0b-8605-46f28273009a', 313);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (88, 14, 15, 2, NULL, '3e902993-54c5-4926-8bb8-ed7d67eed98e', 245);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (89, 14, 15, 2, NULL, '3f08ae55-35e9-48d2-adbc-d3b8b28da1d3', 129);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (90, 14, 15, 2, NULL, '408bdf2c-ba6e-4b70-9d13-49b87bce89d1', 324);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (91, 14, 15, 2, NULL, '42ac7894-d380-46e2-aa9f-73eea07b6297', 10);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (92, 14, 15, 2, NULL, '43df05dd-2103-47fb-a38c-90e9b01009e6', 104);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (93, 14, 15, 2, NULL, '456bb9f3-bc3c-48a1-a2ec-6177567cfb53', 294);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (94, 14, 15, 2, NULL, '468ed70f-f189-4a0e-ae24-85edbbab398f', 212);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (95, 14, 15, 2, NULL, '46d249e2-efb5-446a-a3d1-63680d4c53b6', 188);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (96, 14, 15, 2, NULL, '477b224b-bcc1-46ae-890b-e37d7b17f9ae', 65);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (97, 14, 16, 2, NULL, '49bdddd2-6d02-4281-9c8a-19941b9f08a3', 130);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (98, 14, 16, 2, NULL, '4a6de53c-908a-4793-84de-c8f910adc425', 105);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (99, 14, 16, 2, NULL, '4c1265ff-241c-4d8d-8788-1df27a5f6a47', 155);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (100, 14, 16, 2, NULL, '4ea8504e-27d3-4245-a1c9-313a92aeb1e0', 136);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (101, 14, 16, 2, NULL, '4fca13db-fb7f-453d-88ce-8e426af0d449', 152);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (102, 14, 16, 2, NULL, '50060427-3c91-418f-ada4-9313c6149736', 99);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (103, 14, 16, 2, NULL, '516f54d3-0299-4429-9dc7-5cc47cb6e5e5', 267);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (104, 14, 16, 2, NULL, '51895afe-478b-4bed-b585-a1230cc8cbaa', 28);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (105, 14, 16, 2, NULL, '51d6996a-a808-4369-ac4e-3c4d8c7c4446', 209);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (106, 14, 16, 2, NULL, '5226d95b-9a84-4ebf-916e-a86e425428cd', 237);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (107, 14, 16, 2, NULL, '522de1bd-e35d-4ba0-9883-83ef53382c17', 213);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (108, 14, 16, 2, NULL, '52420d7b-a0b5-427b-a982-0db52d4e9820', 240);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (109, 14, 16, 2, NULL, '5548d609-c31e-451d-8b65-32a0fab7007c', 224);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (110, 14, 16, 2, NULL, '55d28298-78cf-420a-9163-3b681210b50a', 134);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (111, 14, 16, 2, NULL, '570ce98c-f727-4c20-83ba-e15cf002dfe2', 269);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (112, 14, 16, 2, NULL, '57c48526-d2a0-447f-8a2b-7d2289c9c58f', 42);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (113, 14, 16, 2, NULL, '57d88893-0ffd-4862-9e76-8e495897e717', 270);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (114, 14, 16, 2, NULL, '587d823a-fabe-4df8-9e88-335361561dc8', 288);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (115, 14, 16, 2, NULL, '5891d56e-9cd1-4a18-9d62-bdb72da7bd30', 297);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (116, 14, 16, 2, NULL, '5909a5e7-e4ef-4216-babe-06a3c57bfa0e', 148);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (117, 14, 16, 2, NULL, '59f2da0b-43be-4abd-bf58-1756a46de972', 135);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (118, 14, 16, 2, NULL, '5a7f9047-a0a2-4efa-9c55-2a8d3436cff4', 211);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (119, 14, 16, 2, NULL, '5c3ae2b0-9ed5-4215-9a01-4d0bd0ece487', 225);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (120, 14, 16, 2, NULL, '5cfd1f44-9060-4e42-946b-8ad73b15b6af', 250);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (121, 14, 16, 2, NULL, '5d00dc52-8503-40ad-a0a7-614fcea82e43', 223);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (122, 14, 16, 2, NULL, '5d1d80e9-6456-486c-af92-ae966db173c1', 66);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (123, 14, 16, 2, NULL, '5d66e993-54d5-4a3c-bdf3-727ae12cf3f3', 101);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (124, 14, 16, 2, NULL, '5f1fb82e-143d-4b35-86ce-4d77a15ac4e3', 19);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (125, 14, 16, 2, NULL, '5fb32f08-89a7-4b30-807d-7fb3ba16e1dc', 172);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (126, 14, 16, 2, NULL, '60b22641-393b-4b2b-a569-68e7c1d99e85', 50);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (127, 14, 16, 2, NULL, '60d5fa4b-fd4b-4505-9f96-32ae05855eea', 111);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (128, 14, 16, 2, NULL, '61daff98-cf85-4340-9180-68c696fb16cf', 186);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (129, 14, 16, 2, NULL, '63e7f2ec-4620-44ff-b754-6d179e538271', 227);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (130, 14, 16, 2, NULL, '64ae53a0-e670-4232-a898-61eff6436f71', 113);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (131, 14, 16, 2, NULL, '659734e6-2c5d-4fc9-85d6-eb46455c4cd2', 108);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (132, 14, 16, 2, NULL, '663bcbe2-239e-4666-850a-ca3504a5554a', 89);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (133, 14, 16, 2, NULL, '665247e3-e7f4-4b63-baa4-ec84055fd204', 315);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (134, 14, 16, 2, NULL, '665ad007-86b1-4477-b6df-3bbf90e53f84', 126);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (135, 14, 16, 2, NULL, '67d87bcc-9433-4574-a368-f22c17e11eae', 258);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (136, 14, 16, 2, NULL, '6852f0a5-a9d1-4208-87f0-5da33e23ab8c', 302);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (137, 14, 16, 2, NULL, '68eb5bcc-a67c-4912-af78-5ac3139d535b', 75);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (138, 14, 16, 2, NULL, '690f4089-c294-4490-b6f0-b585048df891', 163);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (139, 14, 16, 2, NULL, '692aba8a-9059-4bee-a7e0-2fcb9ef6f8d5', 46);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (140, 14, 16, 2, NULL, '6a989a58-82f3-415a-8261-f0d6a9e9ccb6', 312);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (141, 14, 16, 2, NULL, '6b56d969-8218-4e03-87ad-324e5e80fb2f', 157);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (142, 14, 16, 2, NULL, '6c77b4c5-17dd-4bf5-914e-1b0fc08cfe86', 64);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (143, 14, 16, 2, NULL, '6d7c697b-a269-4f74-baf9-c0eaada5e643', 44);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (144, 14, 16, 2, NULL, '6d7d659e-c99c-428a-9c06-97eedcd7ebf8', 199);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (145, 14, 16, 2, NULL, '6df957bb-4d56-40bf-9db3-318756841817', 120);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (146, 14, 16, 2, NULL, '7121d259-0e1d-4579-9d5a-c4db47b142ca', 248);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (147, 14, 16, 2, NULL, '714bf797-1fec-4cd7-b2c2-86c0c0d85574', 141);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (148, 14, 16, 2, NULL, '715e483b-1b2b-4adc-a841-2ebf373047b7', 174);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (149, 14, 16, 2, NULL, '7217b95b-4c9d-4433-aed0-2b875aff482b', 251);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (150, 14, 16, 2, NULL, '72373498-22e7-4e44-9533-37636bfcfdc7', 275);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (151, 14, 16, 2, NULL, '725e7fb1-721c-4b92-a281-f8b4c9083afa', 279);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (152, 14, 16, 2, NULL, '726f71c3-3b1b-4689-8671-72df8d3f64c2', 320);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (153, 14, 16, 2, NULL, '72e3411d-2042-47be-8a43-9e117393b81b', 204);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (154, 14, 16, 2, NULL, '738a1e16-6fa2-4879-84da-18d96ff8fd3b', 83);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (155, 14, 16, 2, NULL, '7586480f-a480-42f0-a3e0-817abce8aef8', 221);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (156, 14, 16, 2, NULL, '75baec16-1767-4a2c-845b-11c0eb7b031b', 233);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (157, 14, 16, 2, NULL, '75eb21cb-5f45-433c-b56d-f2a1a1566516', 45);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (158, 14, 16, 2, NULL, '769910c5-0560-481f-afec-b05b60ef97d3', 3);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (159, 14, 16, 2, NULL, '76a8c6c2-10db-42f9-89a3-945f6f0136f5', 123);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (160, 14, 16, 2, NULL, '7722e288-cb9a-426a-aeeb-0d6aefb68500', 38);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (161, 14, 16, 2, NULL, '77be3aa2-ae1e-46b9-a8c7-ffbfee39929d', 14);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (162, 14, 16, 2, NULL, '78755b5a-f1ca-401c-a974-f2fbd6059bbf', 291);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (163, 14, 16, 2, NULL, '7912afcd-e66f-4849-8008-01774b044a37', 309);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (164, 14, 16, 2, NULL, '7980aa20-fbe3-430c-b0d1-3540c95971c3', 102);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (165, 14, 16, 2, NULL, '7a8f7b54-f044-4ac7-92d1-8aa8462c521c', 34);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (166, 14, 16, 2, NULL, '7aa6736d-7bf5-4702-8082-1cbf41255d9a', 316);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (167, 14, 16, 2, NULL, '7ba13d06-50bc-4ea8-a463-0aec2f1b0022', 110);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (168, 14, 16, 2, NULL, '7d79fe9e-5fe0-4dc7-88ad-c619353fe0d8', 274);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (169, 14, 16, 2, NULL, '7f080d3e-16d3-42d4-965f-266c46165c35', 7);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (170, 14, 16, 2, NULL, '7f7d8c6b-d278-45b6-975a-82c6cafad0a7', 115);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (171, 14, 16, 2, NULL, '7fd94fa4-d9ee-450c-96ce-489f25472a17', 214);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (172, 14, 16, 2, NULL, '7fef124a-3f14-4443-88b3-f8ecd1701f85', 295);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (173, 14, 16, 2, NULL, '7ff66f03-62e3-4bf7-a904-6346c6315ef5', 122);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (174, 14, 16, 2, NULL, '81691aa6-c163-46c8-85ad-654d5a1cca7e', 256);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (175, 14, 16, 2, NULL, '8185d2f9-0e5d-4416-8d39-e78efac675c1', 93);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (176, 14, 16, 2, NULL, '8227d398-a6d3-4759-be9a-bde8045b8c4d', 299);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (177, 14, 16, 2, NULL, '828a7509-fdbe-47f3-a56d-56e2768b5781', 175);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (178, 14, 16, 2, NULL, '83595046-eb44-490d-9ca2-c5211a92f967', 71);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (179, 14, 16, 2, NULL, '83b76151-00a9-4f2c-a38c-ef96724ca3b8', 183);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (180, 14, 16, 2, NULL, '83d6e34d-8df2-46c1-98c2-48d5aee5bf61', 200);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (181, 14, 16, 2, NULL, '846d9989-d31c-4d0f-989b-a6fba2ae4a4a', 84);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (182, 14, 16, 2, NULL, '85591004-927b-4028-b583-8810f7a74172', 61);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (183, 14, 16, 2, NULL, '8572abbb-cc61-460d-bc43-80b50a1bff98', 192);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (184, 14, 16, 2, NULL, '85a26678-120a-4971-92ad-09817888b003', 82);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (185, 14, 16, 2, NULL, '8647504a-7caa-44a5-8c20-c4bd2fe606fc', 151);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (186, 14, 16, 2, NULL, '86e104af-408c-455d-a2e8-383645b789ee', 149);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (187, 14, 16, 2, NULL, '87224bf9-90e0-41cf-8377-c1cca6e97d0b', 27);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (188, 14, 16, 2, NULL, '879e2190-ca04-44b0-9364-8446baa678dc', 273);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (189, 14, 16, 2, NULL, '88e8e41a-eaa5-44c6-9017-baff831fde7f', 164);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (190, 14, 19, 2, NULL, '8a8eccc3-086f-42d6-9449-2096738d9010', 92);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (191, 14, 19, 2, NULL, '8ad698ac-3cd4-4058-933f-40ad22631bb3', 226);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (192, 14, 19, 2, NULL, '8c1572e0-54a0-48f3-b6c8-a74bddc1a228', 72);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (193, 14, 19, 2, NULL, '8d5d7564-6ed6-47a9-830d-639a435e1a9b', 86);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (194, 14, 19, 2, NULL, '8d75a4bf-0950-444b-813a-74a33fd0831c', 266);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (195, 14, 19, 2, NULL, '8dac5da7-21d4-46ed-8be9-35542dea07e8', 265);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (196, 14, 19, 2, NULL, '8ffde44b-d022-4946-b86f-6935030b5f70', 189);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (197, 14, 19, 2, NULL, '90b81667-0947-490b-aa2e-24d762748607', 276);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (198, 14, 19, 2, NULL, '90dae3b4-6cf1-44d3-89d2-1ce8ad20a497', 59);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (199, 14, 19, 2, NULL, '91ed63ea-f04c-4113-8605-7b6f04152111', 80);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (200, 14, 19, 2, NULL, '920146e3-8e89-4eb2-a17e-56df1d72f42d', 160);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (201, 14, 19, 2, NULL, '9252e570-1709-42dc-adcb-ec833d89f482', 296);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (202, 14, 19, 2, NULL, '9258f784-17da-4c7b-bb7f-92629b42004f', 73);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (203, 14, 19, 2, NULL, '9278fcc8-f037-49d6-b5ff-6c66b7ec13c0', 159);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (204, 14, 19, 2, NULL, '92cc66af-11f2-4c2a-b425-71dfc9587d96', 15);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (205, 14, 19, 2, NULL, '934042c2-7370-4e6e-98f3-c0710c0ed612', 74);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (206, 14, 19, 2, NULL, '9347fa06-43a6-400f-a845-98bc57d853e1', 210);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (207, 14, 19, 2, NULL, '93cfc0b5-7da8-40ab-a070-af69eaa7c850', 177);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (208, 14, 19, 2, NULL, '9657497a-e096-4c75-bfab-7707d6329854', 48);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (209, 14, 19, 2, NULL, '976c3476-3c4e-4039-9fef-4b338def0377', 195);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (210, 14, 19, 2, NULL, '97e33322-5e5f-4359-aca3-979dec0adee3', 234);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (211, 14, 19, 2, NULL, '98416c36-8d2a-4bb7-aaff-d77e3812fc57', 158);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (212, 14, 19, 2, NULL, '985d14f1-484c-45c2-ba9e-6652433a200b', 261);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (213, 14, 19, 2, NULL, '987a983f-fec1-49de-b274-333109acd6fe', 144);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (214, 14, 19, 2, NULL, '98e3a942-b8c1-4966-8085-2a05cf63319d', 304);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (215, 14, 19, 2, NULL, '99138747-d070-4c7f-94a1-4ed6c2ae7b59', 6);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (216, 14, 19, 2, NULL, '9a8e104a-34ae-447b-a547-7cb7d0f4d2dd', 107);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (217, 14, 19, 2, NULL, '9dff419b-3188-411b-86ac-bde2f9232649', 33);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (218, 14, 19, 2, NULL, '9ec3e1be-7962-49c6-8cc3-c2a09f9af915', 153);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (219, 14, 19, 2, NULL, '9edb7299-3ead-45da-a23b-5f1009577546', 238);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (220, 14, 19, 2, NULL, '9f73c320-66ad-4d1c-a833-12cf3ddd131b', 300);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (221, 14, 19, 2, NULL, '9f802680-2da0-46fe-9179-f22f56e74dbf', 228);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (222, 14, 19, 2, NULL, 'a16f7be6-fa60-43a0-820f-91455d3cad45', 298);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (223, 14, 19, 2, NULL, 'a1d9ceee-cbef-411e-97d4-87650a19cecd', 278);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (224, 14, 19, 2, NULL, 'a347e218-da38-42f7-9269-6281aca69112', 229);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (225, 14, 19, 2, NULL, 'a481344b-940a-4d78-984d-56312e13eaea', 311);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (226, 14, 19, 2, NULL, 'a5ec1ac1-7b45-40e3-be51-1e4e497489a1', 268);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (227, 14, 19, 2, NULL, 'a6d39891-deb9-443c-af34-2cbfdc3969aa', 8);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (228, 14, 19, 2, NULL, 'a79f2934-37ac-4870-b39d-c5607e2114d2', 47);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (229, 14, 19, 2, NULL, 'a831ecbf-c7c4-46b2-9a48-18c95c76e95a', 58);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (230, 14, 19, 2, NULL, 'aa90aee3-119b-4707-b8ca-1942df261edc', 9);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (231, 14, 19, 2, NULL, 'aac3b642-415d-43f6-9d48-88f4eed8da3e', 247);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (232, 14, 19, 2, NULL, 'ac4a2338-d0a5-4acc-94f4-96c63a4ed7ff', 184);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (233, 14, 19, 2, NULL, 'ad504912-182f-4873-9855-47442c2ff4e2', 254);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (234, 14, 19, 2, NULL, 'ad851170-f051-4955-817b-a9cb561e6ccb', 49);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (235, 14, 19, 2, NULL, 'ae866028-d3ab-4d92-afd1-118b6fda7fb4', 230);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (236, 14, 19, 2, NULL, 'aeafc0e9-0016-460d-a243-ff3edd613d30', 318);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (237, 14, 19, 2, NULL, 'b5bf7690-5f76-4955-ac34-9b70e52f1529', 21);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (238, 14, 19, 2, NULL, 'b814049b-cbac-455f-a0ab-5b2b228bd5b6', 62);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (239, 14, 19, 2, NULL, 'b8dd8c41-1fb4-45b1-a21d-112b198831d9', 264);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (240, 14, 19, 2, NULL, 'b94a220d-feac-44e9-b287-60be1dcfe6cd', 146);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (241, 14, 19, 2, NULL, 'b9680914-4977-45f7-ae31-3975014b261d', 280);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (242, 14, 19, 2, NULL, 'b9e0b5c9-a836-42ac-a446-2fcd18d943aa', 162);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (243, 14, 19, 2, NULL, 'ba3929b2-ecf1-436d-801c-4da5ebd00d3f', 156);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (244, 14, 19, 2, NULL, 'bc760301-31bd-4a7e-a88e-fea62f425c4e', 323);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (245, 14, 19, 2, NULL, 'bcd7218f-2527-4412-ba8d-3460caefd5f0', 20);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (246, 14, 19, 2, NULL, 'be7c027d-abca-4214-b3f8-b3de0adef08c', 32);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (247, 14, 19, 2, NULL, 'bfd8ae82-e475-4f8d-b7bc-3be7d2c1f3d6', 79);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (248, 14, 19, 2, NULL, 'c00aa13d-dc77-4d4d-aa1f-7c8f7a40b3f4', 97);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (249, 14, 19, 2, NULL, 'c1723293-c183-4c09-9abf-3867b5d7b40a', 289);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (250, 14, 19, 2, NULL, 'c1b3bbe5-e0d2-45de-96de-62e6adf1d4cc', 55);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (251, 14, 19, 2, NULL, 'c2aff95f-854e-4ac7-9f3b-0db32913c41e', 11);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (252, 14, 19, 2, NULL, 'c4657468-93dd-4175-a74b-7757030d95bf', 201);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (253, 14, 19, 2, NULL, 'c64119bf-7dc1-4b36-9cdc-dc1c3024328c', 263);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (254, 14, 19, 2, NULL, 'c7bdf167-e65a-40db-b3c6-bd39da74a4c0', 140);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (255, 14, 19, 2, NULL, 'c8b216bb-032e-413f-8b46-795b72269a49', 281);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (256, 14, 19, 2, NULL, 'c8e106e5-9008-473d-a692-5677200a7704', 67);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (257, 14, 19, 2, NULL, 'cd4be24c-5e14-4db5-927e-a5c6f120e380', 173);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (258, 14, 19, 2, NULL, 'cd78a8e1-f9b4-4513-b3a6-5b5d4a1c42aa', 317);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (259, 14, 19, 2, NULL, 'cd9392bb-e927-4f13-b3e9-38b5b1441f20', 4);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (260, 14, 19, 2, NULL, 'cdeca280-9489-407b-a254-2a0b9acf77aa', 301);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (261, 14, 19, 2, NULL, 'ce03c457-5ecd-4c53-a612-941bd1f13a51', 205);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (262, 14, 19, 2, NULL, 'd0603a90-c5d6-444b-9866-69cfc7627baf', 252);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (263, 14, 19, 2, NULL, 'd1947f60-e6b8-4b01-8e20-3d9b8d1bf808', 286);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (264, 14, 19, 2, NULL, 'd1c6efca-931b-4a1d-bbdf-3d886bbb93bf', 166);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (265, 14, 19, 2, NULL, 'd2af74a3-439e-4cc4-b259-f1f65691269f', 13);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (266, 14, 19, 2, NULL, 'd30ec1c0-9c7e-4179-9d5e-0ef07750daf7', 114);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (267, 14, 19, 2, NULL, 'd39cf6e2-1a24-4b12-ba00-effeef424d4d', 54);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (268, 14, 19, 2, NULL, 'd6f6b099-b9ea-4d22-be41-fbf46bfdd534', 260);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (269, 14, 19, 2, NULL, 'd7b38b43-86dd-4b74-bc64-6a87ddcbc777', 243);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (270, 14, 19, 2, NULL, 'd80f53fa-829b-42a1-83de-f04e8a6d698f', 88);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (271, 14, 19, 2, NULL, 'd970c190-3463-4b35-8754-781b123740b5', 118);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (272, 14, 19, 2, NULL, 'd9b081d3-71eb-40cf-872a-7893d8906043', 87);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (273, 14, 19, 2, NULL, 'da9924ae-0d5a-4f7d-8c55-fce963552fa6', 103);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (274, 14, 19, 2, NULL, 'dae8a51f-8455-4573-b0b1-0d26f072ebc1', 53);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (275, 14, 19, 2, NULL, 'db25a29f-430a-422c-9109-1a89bcbb85d0', 98);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (276, 14, 19, 2, NULL, 'dd88d17a-ecfa-4d42-a610-6e3b0a3f92ea', 246);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (277, 14, 19, 2, NULL, 'ddef4c6b-4983-4868-a8fa-e5267d32f847', 170);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (278, 14, 19, 2, NULL, 'def8b3ec-264f-41a8-8f05-65df6111acbd', 321);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (279, 14, 19, 2, NULL, 'e0afe51a-f203-4eeb-9c28-0018655555da', 203);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (280, 14, 19, 2, NULL, 'e0b54ad2-f432-46bc-a4d9-615b779de21a', 29);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (281, 14, 19, 2, NULL, 'e13a72e3-f9c6-4ae2-9981-2ab7d4198ae9', 193);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (282, 14, 20, 2, NULL, 'e3bdac33-fb14-4159-9f24-e7a91a3361b3', 121);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (283, 14, 20, 2, NULL, 'e43143c4-f751-4dae-82dc-1b4323e97e3c', 139);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (284, 14, 20, 2, NULL, 'e4bf4c83-a911-4041-81ec-79eb95c22bd4', 131);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (285, 14, 20, 2, NULL, 'e4ededa0-7956-4809-8053-d4e0b2b93a83', 96);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (286, 14, 20, 2, NULL, 'e671f1af-3593-4b62-9060-41a6c8e98818', 18);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (287, 14, 20, 2, NULL, 'e67ae7f3-cd48-4dcf-bebd-c1de380fa390', 308);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (288, 14, 20, 2, NULL, 'e78dbc7b-944c-456c-9c5d-732816edc429', 180);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (289, 14, 20, 2, NULL, 'e796fa36-092e-4098-ac22-50d4aedfb1ce', 51);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (290, 14, 20, 2, NULL, 'e7dde28f-b160-4d5c-8d96-d5cec9f5bdd0', 168);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (291, 14, 20, 2, NULL, 'e8025771-f0df-4c0e-bd20-bb37261184bd', 133);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (292, 14, 20, 2, NULL, 'ea34b178-df3c-4c97-a895-97c4edb6723f', 241);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (293, 14, 20, 2, NULL, 'eaec9286-fa22-4f56-bfbe-49744acee244', 293);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (294, 14, 20, 2, NULL, 'ecbc950c-3a6b-489e-8105-ca28c2afab9c', 197);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (295, 14, 20, 2, NULL, 'edd7926e-61c8-4397-9bd2-cb35bc7a1e0e', 109);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (296, 14, 20, 2, NULL, 'ee398272-f3dd-4634-bc4a-e0ac8234a7c8', 303);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (297, 14, 20, 2, NULL, 'eee5907d-e206-402e-8b64-773556b1a50d', 119);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (298, 14, 20, 2, NULL, 'ef5c4b6e-d48b-412a-b7bc-e4567aef2142', 112);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (299, 14, 20, 2, NULL, 'ef6c98cd-0a22-4243-a39e-8bb3e64ddb0a', 23);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (300, 14, 20, 2, NULL, 'f088bab4-7b5f-4f6c-a594-35373c8fbd63', 305);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (301, 14, 20, 2, NULL, 'f124cf88-a157-4e5c-8110-d88a66d2b367', 257);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (302, 14, 20, 2, NULL, 'f150d52b-39dd-444c-ac95-b2230abed72c', 319);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (303, 14, 20, 2, NULL, 'f1e2b45f-a20f-4bdd-87f9-1f6e99593527', 187);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (304, 14, 20, 2, NULL, 'f28dcd62-9df2-4e62-bea9-5ca39e726403', 191);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (305, 14, 20, 2, NULL, 'f5d30129-d1f2-4ece-8401-b5a771df1ef4', 78);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (306, 14, 20, 2, NULL, 'f5d529e0-f113-44f2-a133-880855349c80', 137);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (307, 14, 20, 2, NULL, 'f5ddd74c-10ed-4224-9f50-3bf16d90efd8', 138);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (308, 14, 20, 2, NULL, 'f6097bad-04cd-4a95-afc8-8fc26f122cf7', 249);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (309, 14, 20, 2, NULL, 'f641cfd8-c4e6-4f84-8402-74b0c7c99bc1', 145);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (310, 14, 20, 2, NULL, 'f64ba568-5424-4292-b434-5548dc79687e', 17);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (311, 14, 20, 2, NULL, 'f983c546-f677-4b6c-8296-23b4111025ce', 26);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (312, 14, 20, 2, NULL, 'f99b79c6-ff16-41a6-8f33-e29dc6baaf32', 198);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (313, 14, 20, 2, NULL, 'f9f6657e-3aa5-4402-9b29-40b7debeed09', 60);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (314, 14, 20, 2, NULL, 'fa44979b-f8ee-4858-983e-9673839277b2', 154);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (315, 14, 20, 2, NULL, 'fa9d2cfa-4eff-40a9-8e78-9bea40124550', 132);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (316, 14, 20, 2, NULL, 'fb5a0eee-2a46-4ed8-a9f3-3806716284b8', 68);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (317, 14, 20, 2, NULL, 'fc0da0d2-4213-4c4d-994a-bda436d4ba6c', 81);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (318, 14, 20, 2, NULL, 'fc44593f-e931-42ce-9f13-3c6a9d8b869b', 271);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (319, 14, 20, 2, NULL, 'fc733f91-b73f-4951-8070-0ef3197e2524', 176);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (320, 14, 20, 2, NULL, 'fd7d6f3b-68e7-4a81-89a9-14793e0f8b13', 91);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (321, 14, 20, 2, NULL, 'fd8e1995-ab5c-42f6-a564-70b938b320ee', 95);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (322, 14, 20, 2, NULL, 'fdebc805-750b-4a7a-98cf-3e06949b7f73', 150);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (323, 14, 20, 2, NULL, 'fe29d7f3-fbaf-47cc-a498-41d3adc149cc', 310);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (324, 14, 20, 2, NULL, 'fe333f49-f297-4851-b29a-db3ccc499272', 165);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (325, 14, 20, 2, NULL, 'ff0c2f02-c128-4858-943c-e8ad68c1fa3a', 63);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (326, 21, 21, 2, NULL, 'INTERNSHALA', 221);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (327, 21, 22, 2, NULL, 'INTERNSHALA', 1);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (328, 21, 22, 2, NULL, 'INTERNSHALA', 2);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (329, 21, 22, 2, NULL, 'INTERNSHALA', 3);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (330, 21, 22, 2, NULL, 'INTERNSHALA', 4);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (331, 21, 22, 2, NULL, 'INTERNSHALA', 5);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (332, 21, 22, 2, NULL, 'INTERNSHALA', 6);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (333, 21, 22, 2, NULL, 'INTERNSHALA', 7);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (334, 21, 22, 2, NULL, 'INTERNSHALA', 8);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (335, 21, 22, 2, NULL, 'INTERNSHALA', 9);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (336, 21, 22, 2, NULL, 'INTERNSHALA', 10);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (337, 21, 22, 2, NULL, 'INTERNSHALA', 11);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (338, 21, 22, 2, NULL, 'INTERNSHALA', 12);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (339, 21, 22, 2, NULL, 'INTERNSHALA', 13);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (340, 21, 22, 2, NULL, 'INTERNSHALA', 14);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (341, 21, 22, 2, NULL, 'INTERNSHALA', 15);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (342, 21, 22, 2, NULL, 'INTERNSHALA', 16);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (343, 21, 22, 2, NULL, 'INTERNSHALA', 17);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (344, 21, 22, 2, NULL, 'INTERNSHALA', 18);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (345, 21, 22, 2, NULL, 'INTERNSHALA', 19);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (346, 21, 22, 2, NULL, 'INTERNSHALA', 20);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (347, 21, 22, 2, NULL, 'INTERNSHALA', 21);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (348, 21, 22, 2, NULL, 'INTERNSHALA', 22);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (349, 21, 22, 2, NULL, 'INTERNSHALA', 23);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (350, 21, 22, 2, NULL, 'INTERNSHALA', 24);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (351, 21, 22, 2, NULL, 'INTERNSHALA', 25);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (352, 21, 22, 2, NULL, 'INTERNSHALA', 26);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (353, 21, 22, 2, NULL, 'INTERNSHALA', 27);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (354, 21, 22, 2, NULL, 'INTERNSHALA', 28);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (355, 21, 22, 2, NULL, 'INTERNSHALA', 29);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (356, 21, 22, 2, NULL, 'INTERNSHALA', 30);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (357, 21, 22, 2, NULL, 'INTERNSHALA', 31);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (358, 21, 22, 2, NULL, 'INTERNSHALA', 32);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (359, 21, 22, 2, NULL, 'INTERNSHALA', 33);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (360, 21, 22, 2, NULL, 'INTERNSHALA', 34);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (361, 21, 22, 2, NULL, 'INTERNSHALA', 35);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (362, 21, 22, 2, NULL, 'INTERNSHALA', 36);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (363, 21, 22, 2, NULL, 'INTERNSHALA', 37);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (364, 21, 22, 2, NULL, 'INTERNSHALA', 38);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (365, 21, 22, 2, NULL, 'INTERNSHALA', 39);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (366, 21, 22, 2, NULL, 'INTERNSHALA', 40);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (367, 21, 22, 2, NULL, 'INTERNSHALA', 41);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (368, 21, 22, 2, NULL, 'INTERNSHALA', 42);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (369, 21, 22, 2, NULL, 'INTERNSHALA', 43);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (370, 21, 22, 2, NULL, 'INTERNSHALA', 44);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (371, 21, 22, 2, NULL, 'INTERNSHALA', 45);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (372, 21, 22, 2, NULL, 'INTERNSHALA', 46);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (373, 21, 22, 2, NULL, 'INTERNSHALA', 47);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (374, 21, 22, 2, NULL, 'INTERNSHALA', 48);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (375, 21, 22, 2, NULL, 'INTERNSHALA', 49);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (376, 21, 22, 2, NULL, 'INTERNSHALA', 50);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (377, 21, 22, 2, NULL, 'INTERNSHALA', 51);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (378, 21, 22, 2, NULL, 'INTERNSHALA', 52);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (379, 21, 22, 2, NULL, 'INTERNSHALA', 53);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (380, 21, 22, 2, NULL, 'INTERNSHALA', 54);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (381, 21, 22, 2, NULL, 'INTERNSHALA', 55);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (382, 21, 22, 2, NULL, 'INTERNSHALA', 56);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (383, 21, 22, 2, NULL, 'INTERNSHALA', 57);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (384, 21, 22, 2, NULL, 'INTERNSHALA', 58);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (385, 21, 22, 2, NULL, 'INTERNSHALA', 59);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (386, 21, 22, 2, NULL, 'INTERNSHALA', 60);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (387, 21, 22, 2, NULL, 'INTERNSHALA', 61);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (388, 21, 22, 2, NULL, 'INTERNSHALA', 62);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (389, 21, 22, 2, NULL, 'INTERNSHALA', 63);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (390, 21, 22, 2, NULL, 'INTERNSHALA', 64);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (391, 21, 22, 2, NULL, 'INTERNSHALA', 65);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (392, 21, 22, 2, NULL, 'INTERNSHALA', 66);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (393, 21, 22, 2, NULL, 'INTERNSHALA', 67);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (394, 21, 22, 2, NULL, 'INTERNSHALA', 68);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (395, 21, 22, 2, NULL, 'INTERNSHALA', 69);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (396, 21, 22, 2, NULL, 'INTERNSHALA', 70);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (397, 21, 22, 2, NULL, 'INTERNSHALA', 71);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (398, 21, 22, 2, NULL, 'INTERNSHALA', 72);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (399, 21, 22, 2, NULL, 'INTERNSHALA', 73);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (400, 21, 22, 2, NULL, 'INTERNSHALA', 74);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (401, 21, 22, 2, NULL, 'INTERNSHALA', 75);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (402, 21, 22, 2, NULL, 'INTERNSHALA', 76);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (403, 21, 22, 2, NULL, 'INTERNSHALA', 77);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (404, 21, 22, 2, NULL, 'INTERNSHALA', 78);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (405, 21, 22, 2, NULL, 'INTERNSHALA', 79);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (406, 21, 22, 2, NULL, 'INTERNSHALA', 80);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (407, 21, 22, 2, NULL, 'INTERNSHALA', 81);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (408, 21, 22, 2, NULL, 'INTERNSHALA', 82);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (409, 21, 22, 2, NULL, 'INTERNSHALA', 83);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (410, 21, 22, 2, NULL, 'INTERNSHALA', 84);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (411, 21, 22, 2, NULL, 'INTERNSHALA', 85);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (412, 21, 22, 2, NULL, 'INTERNSHALA', 86);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (413, 21, 22, 2, NULL, 'INTERNSHALA', 87);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (414, 21, 22, 2, NULL, 'INTERNSHALA', 88);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (415, 21, 22, 2, NULL, 'INTERNSHALA', 89);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (416, 21, 22, 2, NULL, 'INTERNSHALA', 90);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (417, 21, 22, 2, NULL, 'INTERNSHALA', 91);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (418, 21, 22, 2, NULL, 'INTERNSHALA', 92);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (419, 21, 22, 2, NULL, 'INTERNSHALA', 93);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (420, 21, 22, 2, NULL, 'INTERNSHALA', 94);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (421, 21, 22, 2, NULL, 'INTERNSHALA', 95);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (422, 21, 22, 2, NULL, 'INTERNSHALA', 96);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (423, 21, 22, 2, NULL, 'INTERNSHALA', 97);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (424, 21, 22, 2, NULL, 'INTERNSHALA', 98);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (425, 21, 22, 2, NULL, 'INTERNSHALA', 99);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (426, 21, 22, 2, NULL, 'INTERNSHALA', 100);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (427, 21, 22, 2, NULL, 'INTERNSHALA', 101);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (428, 21, 22, 2, NULL, 'INTERNSHALA', 102);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (429, 21, 22, 2, NULL, 'INTERNSHALA', 103);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (430, 21, 22, 2, NULL, 'INTERNSHALA', 104);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (431, 21, 22, 2, NULL, 'INTERNSHALA', 105);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (432, 21, 22, 2, NULL, 'INTERNSHALA', 106);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (433, 21, 22, 2, NULL, 'INTERNSHALA', 107);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (434, 21, 22, 2, NULL, 'INTERNSHALA', 108);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (435, 21, 22, 2, NULL, 'INTERNSHALA', 109);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (436, 21, 22, 2, NULL, 'INTERNSHALA', 110);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (437, 21, 22, 2, NULL, 'INTERNSHALA', 111);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (438, 21, 22, 2, NULL, 'INTERNSHALA', 112);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (439, 21, 22, 2, NULL, 'INTERNSHALA', 113);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (440, 21, 22, 2, NULL, 'INTERNSHALA', 114);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (441, 21, 22, 2, NULL, 'INTERNSHALA', 115);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (442, 21, 22, 2, NULL, 'INTERNSHALA', 116);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (443, 21, 22, 2, NULL, 'INTERNSHALA', 117);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (444, 21, 22, 2, NULL, 'INTERNSHALA', 118);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (445, 21, 22, 2, NULL, 'INTERNSHALA', 119);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (446, 21, 22, 2, NULL, 'INTERNSHALA', 120);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (447, 21, 22, 2, NULL, 'INTERNSHALA', 121);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (448, 21, 22, 2, NULL, 'INTERNSHALA', 122);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (449, 21, 22, 2, NULL, 'INTERNSHALA', 123);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (450, 21, 22, 2, NULL, 'INTERNSHALA', 124);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (451, 21, 22, 2, NULL, 'INTERNSHALA', 125);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (452, 21, 22, 2, NULL, 'INTERNSHALA', 126);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (453, 21, 22, 2, NULL, 'INTERNSHALA', 127);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (454, 21, 22, 2, NULL, 'INTERNSHALA', 128);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (455, 21, 22, 2, NULL, 'INTERNSHALA', 129);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (456, 21, 22, 2, NULL, 'INTERNSHALA', 130);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (457, 21, 22, 2, NULL, 'INTERNSHALA', 131);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (458, 21, 22, 2, NULL, 'INTERNSHALA', 132);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (459, 21, 22, 2, NULL, 'INTERNSHALA', 133);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (460, 21, 22, 2, NULL, 'INTERNSHALA', 134);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (461, 21, 22, 2, NULL, 'INTERNSHALA', 135);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (462, 21, 22, 2, NULL, 'INTERNSHALA', 136);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (463, 21, 22, 2, NULL, 'INTERNSHALA', 137);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (464, 21, 22, 2, NULL, 'INTERNSHALA', 138);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (465, 21, 22, 2, NULL, 'INTERNSHALA', 139);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (466, 21, 22, 2, NULL, 'INTERNSHALA', 140);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (467, 21, 22, 2, NULL, 'INTERNSHALA', 141);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (468, 21, 22, 2, NULL, 'INTERNSHALA', 142);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (469, 21, 22, 2, NULL, 'INTERNSHALA', 143);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (470, 21, 22, 2, NULL, 'INTERNSHALA', 144);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (471, 21, 22, 2, NULL, 'INTERNSHALA', 145);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (472, 21, 22, 2, NULL, 'INTERNSHALA', 146);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (473, 21, 22, 2, NULL, 'INTERNSHALA', 147);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (474, 21, 22, 2, NULL, 'INTERNSHALA', 148);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (475, 21, 22, 2, NULL, 'INTERNSHALA', 149);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (476, 21, 22, 2, NULL, 'INTERNSHALA', 150);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (477, 21, 22, 2, NULL, 'INTERNSHALA', 151);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (478, 21, 22, 2, NULL, 'INTERNSHALA', 152);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (479, 21, 22, 2, NULL, 'INTERNSHALA', 153);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (480, 21, 22, 2, NULL, 'INTERNSHALA', 154);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (481, 21, 22, 2, NULL, 'INTERNSHALA', 155);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (482, 21, 22, 2, NULL, 'INTERNSHALA', 156);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (483, 21, 22, 2, NULL, 'INTERNSHALA', 157);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (484, 21, 22, 2, NULL, 'INTERNSHALA', 158);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (485, 21, 22, 2, NULL, 'INTERNSHALA', 159);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (486, 21, 22, 2, NULL, 'INTERNSHALA', 160);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (487, 21, 22, 2, NULL, 'INTERNSHALA', 161);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (488, 21, 22, 2, NULL, 'INTERNSHALA', 162);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (489, 21, 22, 2, NULL, 'INTERNSHALA', 163);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (490, 21, 22, 2, NULL, 'INTERNSHALA', 164);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (491, 21, 22, 2, NULL, 'INTERNSHALA', 165);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (492, 21, 22, 2, NULL, 'INTERNSHALA', 166);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (493, 21, 22, 2, NULL, 'INTERNSHALA', 167);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (494, 21, 22, 2, NULL, 'INTERNSHALA', 168);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (495, 21, 22, 2, NULL, 'INTERNSHALA', 169);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (496, 21, 22, 2, NULL, 'INTERNSHALA', 170);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (497, 21, 22, 2, NULL, 'INTERNSHALA', 171);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (498, 21, 22, 2, NULL, 'INTERNSHALA', 172);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (499, 21, 22, 2, NULL, 'INTERNSHALA', 173);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (500, 21, 22, 2, NULL, 'INTERNSHALA', 174);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (501, 21, 22, 2, NULL, 'INTERNSHALA', 175);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (502, 21, 22, 2, NULL, 'INTERNSHALA', 176);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (503, 21, 22, 2, NULL, 'INTERNSHALA', 177);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (504, 21, 22, 2, NULL, 'INTERNSHALA', 178);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (505, 21, 22, 2, NULL, 'INTERNSHALA', 179);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (506, 21, 22, 2, NULL, 'INTERNSHALA', 180);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (507, 21, 22, 2, NULL, 'INTERNSHALA', 181);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (508, 21, 22, 2, NULL, 'INTERNSHALA', 182);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (509, 21, 22, 2, NULL, 'INTERNSHALA', 183);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (510, 21, 22, 2, NULL, 'INTERNSHALA', 184);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (511, 21, 22, 2, NULL, 'INTERNSHALA', 185);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (512, 21, 22, 2, NULL, 'INTERNSHALA', 186);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (513, 21, 22, 2, NULL, 'INTERNSHALA', 187);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (514, 21, 22, 2, NULL, 'INTERNSHALA', 188);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (515, 21, 22, 2, NULL, 'INTERNSHALA', 189);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (516, 21, 22, 2, NULL, 'INTERNSHALA', 190);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (517, 21, 22, 2, NULL, 'INTERNSHALA', 191);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (518, 21, 22, 2, NULL, 'INTERNSHALA', 192);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (519, 21, 22, 2, NULL, 'INTERNSHALA', 193);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (520, 21, 22, 2, NULL, 'INTERNSHALA', 194);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (521, 21, 22, 2, NULL, 'INTERNSHALA', 195);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (522, 21, 22, 2, NULL, 'INTERNSHALA', 196);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (523, 21, 22, 2, NULL, 'INTERNSHALA', 197);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (524, 21, 22, 2, NULL, 'INTERNSHALA', 198);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (525, 21, 22, 2, NULL, 'INTERNSHALA', 199);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (526, 21, 22, 2, NULL, 'INTERNSHALA', 200);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (527, 21, 22, 2, NULL, 'INTERNSHALA', 201);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (528, 21, 22, 2, NULL, 'INTERNSHALA', 202);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (529, 21, 22, 2, NULL, 'INTERNSHALA', 203);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (530, 21, 22, 2, NULL, 'INTERNSHALA', 204);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (531, 21, 22, 2, NULL, 'INTERNSHALA', 205);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (532, 21, 22, 2, NULL, 'INTERNSHALA', 206);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (533, 21, 22, 2, NULL, 'INTERNSHALA', 207);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (534, 21, 22, 2, NULL, 'INTERNSHALA', 208);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (535, 21, 22, 2, NULL, 'INTERNSHALA', 209);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (536, 21, 22, 2, NULL, 'INTERNSHALA', 210);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (537, 21, 22, 2, NULL, 'INTERNSHALA', 211);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (538, 21, 22, 2, NULL, 'INTERNSHALA', 212);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (539, 21, 22, 2, NULL, 'INTERNSHALA', 213);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (540, 21, 22, 2, NULL, 'INTERNSHALA', 214);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (541, 21, 22, 2, NULL, 'INTERNSHALA', 215);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (542, 21, 22, 2, NULL, 'INTERNSHALA', 216);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (543, 21, 22, 2, NULL, 'INTERNSHALA', 217);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (544, 21, 22, 2, NULL, 'INTERNSHALA', 218);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (545, 21, 22, 2, NULL, 'INTERNSHALA', 219);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (546, 21, 22, 2, NULL, 'INTERNSHALA', 220);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (547, 21, 23, 2, NULL, 'INTERNSHALA', 222);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (548, 21, 23, 2, NULL, 'INTERNSHALA', 223);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (549, 21, 23, 2, NULL, 'INTERNSHALA', 224);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (550, 21, 23, 2, NULL, 'INTERNSHALA', 225);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (551, 21, 23, 2, NULL, 'INTERNSHALA', 226);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (552, 21, 23, 2, NULL, 'INTERNSHALA', 227);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (553, 21, 23, 2, NULL, 'INTERNSHALA', 228);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (554, 21, 23, 2, NULL, 'INTERNSHALA', 229);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (555, 21, 23, 2, NULL, 'INTERNSHALA', 230);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (556, 21, 23, 2, NULL, 'INTERNSHALA', 231);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (557, 21, 23, 2, NULL, 'INTERNSHALA', 232);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (558, 21, 23, 2, NULL, 'INTERNSHALA', 233);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (559, 21, 23, 2, NULL, 'INTERNSHALA', 234);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (560, 21, 23, 2, NULL, 'INTERNSHALA', 235);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (561, 21, 23, 2, NULL, 'INTERNSHALA', 236);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (562, 21, 23, 2, NULL, 'INTERNSHALA', 237);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (563, 21, 23, 2, NULL, 'INTERNSHALA', 238);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (564, 21, 23, 2, NULL, 'INTERNSHALA', 239);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (565, 21, 23, 2, NULL, 'INTERNSHALA', 240);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (566, 21, 23, 2, NULL, 'INTERNSHALA', 241);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (567, 21, 23, 2, NULL, 'INTERNSHALA', 242);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (568, 21, 23, 2, NULL, 'INTERNSHALA', 243);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (569, 21, 23, 2, NULL, 'INTERNSHALA', 244);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (570, 21, 23, 2, NULL, 'INTERNSHALA', 245);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (571, 21, 23, 2, NULL, 'INTERNSHALA', 246);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (572, 21, 23, 2, NULL, 'INTERNSHALA', 247);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (573, 21, 23, 2, NULL, 'INTERNSHALA', 248);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (574, 21, 23, 2, NULL, 'INTERNSHALA', 249);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (575, 21, 23, 2, NULL, 'INTERNSHALA', 250);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (576, 21, 23, 2, NULL, 'INTERNSHALA', 251);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (577, 21, 23, 2, NULL, 'INTERNSHALA', 252);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (578, 21, 23, 2, NULL, 'INTERNSHALA', 253);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (579, 21, 23, 2, NULL, 'INTERNSHALA', 254);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (580, 21, 23, 2, NULL, 'INTERNSHALA', 255);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (581, 21, 23, 2, NULL, 'INTERNSHALA', 256);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (582, 21, 23, 2, NULL, 'INTERNSHALA', 257);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (583, 21, 23, 2, NULL, 'INTERNSHALA', 258);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (584, 21, 23, 2, NULL, 'INTERNSHALA', 259);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (585, 21, 23, 2, NULL, 'INTERNSHALA', 260);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (586, 21, 23, 2, NULL, 'INTERNSHALA', 261);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (587, 21, 23, 2, NULL, 'INTERNSHALA', 262);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (588, 21, 23, 2, NULL, 'INTERNSHALA', 263);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (589, 21, 23, 2, NULL, 'INTERNSHALA', 264);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (590, 21, 23, 2, NULL, 'INTERNSHALA', 265);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (591, 21, 23, 2, NULL, 'INTERNSHALA', 266);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (592, 21, 23, 2, NULL, 'INTERNSHALA', 267);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (593, 21, 23, 2, NULL, 'INTERNSHALA', 268);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (594, 21, 23, 2, NULL, 'INTERNSHALA', 269);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (595, 21, 23, 2, NULL, 'INTERNSHALA', 270);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (596, 21, 23, 2, NULL, 'INTERNSHALA', 271);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (597, 21, 23, 2, NULL, 'INTERNSHALA', 272);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (598, 21, 23, 2, NULL, 'INTERNSHALA', 273);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (599, 21, 23, 2, NULL, 'INTERNSHALA', 274);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (600, 21, 23, 2, NULL, 'INTERNSHALA', 275);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (601, 21, 23, 2, NULL, 'INTERNSHALA', 276);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (602, 21, 23, 2, NULL, 'INTERNSHALA', 277);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (603, 21, 23, 2, NULL, 'INTERNSHALA', 278);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (604, 21, 23, 2, NULL, 'INTERNSHALA', 279);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (605, 21, 23, 2, NULL, 'INTERNSHALA', 280);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (606, 21, 23, 2, NULL, 'INTERNSHALA', 281);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (607, 21, 23, 2, NULL, 'INTERNSHALA', 282);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (608, 21, 23, 2, NULL, 'INTERNSHALA', 283);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (609, 21, 23, 2, NULL, 'INTERNSHALA', 284);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (610, 21, 23, 2, NULL, 'INTERNSHALA', 285);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (611, 21, 23, 2, NULL, 'INTERNSHALA', 286);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (612, 21, 23, 2, NULL, 'INTERNSHALA', 287);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (613, 21, 23, 2, NULL, 'INTERNSHALA', 288);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (614, 21, 23, 2, NULL, 'INTERNSHALA', 289);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (615, 21, 23, 2, NULL, 'INTERNSHALA', 290);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (616, 21, 23, 2, NULL, 'INTERNSHALA', 291);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (617, 21, 23, 2, NULL, 'INTERNSHALA', 292);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (618, 21, 23, 2, NULL, 'INTERNSHALA', 293);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (619, 21, 23, 2, NULL, 'INTERNSHALA', 294);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (620, 21, 23, 2, NULL, 'INTERNSHALA', 295);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (621, 21, 23, 2, NULL, 'INTERNSHALA', 296);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (622, 21, 23, 2, NULL, 'INTERNSHALA', 297);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (623, 21, 23, 2, NULL, 'INTERNSHALA', 298);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (624, 21, 23, 2, NULL, 'INTERNSHALA', 299);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (625, 21, 23, 2, NULL, 'INTERNSHALA', 300);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (626, 21, 23, 2, NULL, 'INTERNSHALA', 301);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (627, 21, 23, 2, NULL, 'INTERNSHALA', 302);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (628, 21, 23, 2, NULL, 'INTERNSHALA', 303);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (629, 21, 23, 2, NULL, 'INTERNSHALA', 304);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (630, 21, 23, 2, NULL, 'INTERNSHALA', 305);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (631, 21, 23, 2, NULL, 'INTERNSHALA', 306);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (632, 21, 23, 2, NULL, 'INTERNSHALA', 307);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (633, 21, 23, 2, NULL, 'INTERNSHALA', 308);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (634, 21, 23, 2, NULL, 'INTERNSHALA', 309);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (635, 21, 23, 2, NULL, 'INTERNSHALA', 310);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (636, 21, 23, 2, NULL, 'INTERNSHALA', 311);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (637, 21, 23, 2, NULL, 'INTERNSHALA', 312);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (638, 21, 23, 2, NULL, 'INTERNSHALA', 313);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (639, 21, 23, 2, NULL, 'INTERNSHALA', 314);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (640, 21, 23, 2, NULL, 'INTERNSHALA', 315);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (641, 21, 23, 2, NULL, 'INTERNSHALA', 316);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (642, 21, 23, 2, NULL, 'INTERNSHALA', 317);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (643, 21, 23, 2, NULL, 'INTERNSHALA', 318);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (644, 21, 23, 2, NULL, 'INTERNSHALA', 319);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (645, 21, 23, 2, NULL, 'INTERNSHALA', 320);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (646, 21, 23, 2, NULL, 'INTERNSHALA', 321);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (647, 21, 23, 2, NULL, 'INTERNSHALA', 322);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (648, 21, 23, 2, NULL, 'INTERNSHALA', 323);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (649, 21, 23, 2, NULL, 'INTERNSHALA', 324);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (650, 21, 23, 2, NULL, 'INTERNSHALA', 325);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (651, 24, 24, 2, NULL, 'Data Annotation', 181);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (652, 24, 24, 2, NULL, 'QA Engineer (Automation & Manual)', 157);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (653, 24, 25, 2, NULL, '.NET Development', 94);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (654, 24, 25, 2, NULL, 'AI Ad Creative', 121);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (655, 24, 25, 2, NULL, 'AI Agent Development', 10);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (656, 24, 25, 2, NULL, 'AI Agent Development', 14);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (657, 24, 25, 2, NULL, 'AI Agent Development', 60);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (658, 24, 25, 2, NULL, 'AI Agent Development', 170);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (659, 24, 25, 2, NULL, 'AI Agent Development', 216);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (660, 24, 25, 2, NULL, 'AI Agent Development', 220);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (661, 24, 25, 2, NULL, 'AI Agent Development', 225);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (662, 24, 25, 2, NULL, 'AI Agent Development', 238);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (663, 24, 25, 2, NULL, 'AI Agent Development', 241);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (664, 24, 25, 2, NULL, 'AI Agent Development', 249);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (665, 24, 25, 2, NULL, 'AI Agent Development', 266);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (666, 24, 25, 2, NULL, 'AI Agent Development', 284);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (667, 24, 25, 2, NULL, 'AI Agent Development', 292);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (668, 24, 25, 2, NULL, 'AI Agent Development', 308);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (669, 24, 25, 2, NULL, 'AI Agent Development', 314);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (670, 24, 25, 2, NULL, 'AI Agent Development', 317);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (671, 24, 25, 2, NULL, 'AI Agents Expert', 229);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (672, 24, 25, 2, NULL, 'AI Analyst', 156);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (673, 24, 25, 2, NULL, 'AI And Automation Executive', 97);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (674, 24, 25, 2, NULL, 'AI Automation', 256);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (675, 24, 25, 2, NULL, 'AI Automation Intern (Perplexity Computer + OpenClaw + Claude)', 234);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (676, 24, 25, 2, NULL, 'AI Based Developer', 289);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (677, 24, 25, 2, NULL, 'AI Content And Community Associate (WhatsApp Channel)', 66);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (678, 24, 25, 2, NULL, 'AI Creative & E-commerce', 75);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (679, 24, 25, 2, NULL, 'AI Data Annotator (Video Annotation)', 218);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (680, 24, 25, 2, NULL, 'AI Engineer', 184);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (681, 24, 25, 2, NULL, 'AI Engineer', 211);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (682, 24, 25, 2, NULL, 'AI Integration And Automation Project Assistant', 51);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (683, 24, 25, 2, NULL, 'AI Intern', 4);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (684, 24, 25, 2, NULL, 'AI Intern', 206);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (685, 24, 25, 2, NULL, 'AI Intern', 243);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (686, 24, 25, 2, NULL, 'AI Magician', 6);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (687, 24, 25, 2, NULL, 'AI Research And Data Sample Builder', 177);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (688, 24, 25, 2, NULL, 'AI Robotics Trainer', 13);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (689, 24, 25, 2, NULL, 'AI Solutions Intern', 307);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (690, 24, 25, 2, NULL, 'AI Team Lead', 21);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (691, 24, 25, 2, NULL, 'AI Tools Testing', 99);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (692, 24, 25, 2, NULL, 'AI Training Data Labeler', 268);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (693, 24, 25, 2, NULL, 'AI Video Content Creating/Editing', 88);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (694, 24, 25, 2, NULL, 'AI WorkFlow Developer', 228);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (695, 24, 25, 2, NULL, 'AI/ML', 43);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (696, 24, 25, 2, NULL, 'AI/ML', 217);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (697, 24, 25, 2, NULL, 'AI/ML', 272);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (698, 24, 25, 2, NULL, 'AI/ML', 313);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (699, 24, 25, 2, NULL, 'AI/ML Engineer', 199);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (700, 24, 25, 2, NULL, 'AI/ML Engineer', 203);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (701, 24, 25, 2, NULL, 'AI/ML Engineer', 303);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (702, 24, 25, 2, NULL, 'AI/ML Engineering Intern', 311);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (703, 24, 25, 2, NULL, 'AI/ML Python Developer With Full Stack Developer', 320);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (704, 24, 25, 2, NULL, 'Algorithm Development', 169);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (705, 24, 25, 2, NULL, 'Algorithm Development', 274);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (706, 24, 25, 2, NULL, 'Applied AI Developer', 240);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (707, 24, 25, 2, NULL, 'Artificial Intelligence', 306);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (708, 24, 25, 2, NULL, 'Artificial Intelligence (AI)', 1);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (709, 24, 25, 2, NULL, 'Artificial Intelligence (AI)', 2);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (710, 24, 25, 2, NULL, 'Artificial Intelligence (AI)', 7);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (711, 24, 25, 2, NULL, 'Artificial Intelligence (AI)', 8);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (712, 24, 25, 2, NULL, 'Artificial Intelligence (AI)', 12);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (713, 24, 25, 2, NULL, 'Artificial Intelligence (AI)', 15);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (714, 24, 25, 2, NULL, 'Artificial Intelligence (AI)', 17);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (715, 24, 25, 2, NULL, 'Artificial Intelligence (AI)', 23);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (716, 24, 25, 2, NULL, 'Artificial Intelligence (AI)', 31);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (717, 24, 25, 2, NULL, 'Artificial Intelligence (AI)', 36);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (718, 24, 25, 2, NULL, 'Artificial Intelligence (AI)', 37);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (719, 24, 25, 2, NULL, 'Artificial Intelligence (AI)', 38);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (720, 24, 25, 2, NULL, 'Artificial Intelligence (AI)', 41);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (721, 24, 25, 2, NULL, 'Artificial Intelligence (AI)', 128);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (722, 24, 25, 2, NULL, 'Artificial Intelligence (AI)', 147);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (723, 24, 25, 2, NULL, 'Artificial Intelligence (AI)', 149);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (724, 24, 25, 2, NULL, 'Artificial Intelligence (AI)', 154);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (725, 24, 25, 2, NULL, 'Artificial Intelligence (AI)', 155);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (726, 24, 25, 2, NULL, 'Artificial Intelligence (AI)', 168);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (727, 24, 25, 2, NULL, 'Artificial Intelligence (AI)', 175);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (728, 24, 25, 2, NULL, 'Artificial Intelligence (AI)', 186);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (729, 24, 25, 2, NULL, 'Artificial Intelligence (AI)', 202);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (730, 24, 25, 2, NULL, 'Artificial Intelligence (AI)', 207);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (731, 24, 25, 2, NULL, 'Artificial Intelligence (AI)', 208);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (732, 24, 25, 2, NULL, 'Artificial Intelligence (AI)', 212);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (733, 24, 25, 2, NULL, 'Artificial Intelligence (AI)', 214);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (734, 24, 25, 2, NULL, 'Artificial Intelligence (AI)', 219);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (735, 24, 25, 2, NULL, 'Artificial Intelligence (AI)', 227);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (736, 24, 25, 2, NULL, 'Artificial Intelligence (AI)', 233);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (737, 24, 25, 2, NULL, 'Artificial Intelligence (AI)', 235);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (738, 24, 25, 2, NULL, 'Artificial Intelligence (AI)', 236);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (739, 24, 25, 2, NULL, 'Artificial Intelligence (AI)', 254);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (740, 24, 25, 2, NULL, 'Artificial Intelligence (AI)', 257);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (741, 24, 25, 2, NULL, 'Artificial Intelligence (AI)', 262);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (742, 24, 25, 2, NULL, 'Artificial Intelligence (AI)', 273);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (743, 24, 25, 2, NULL, 'Artificial Intelligence (AI)', 275);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (744, 24, 25, 2, NULL, 'Artificial Intelligence (AI)', 276);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (745, 24, 25, 2, NULL, 'Artificial Intelligence (AI)', 286);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (746, 24, 25, 2, NULL, 'Artificial Intelligence (AI)', 287);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (747, 24, 25, 2, NULL, 'Artificial Intelligence (AI)', 290);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (748, 24, 25, 2, NULL, 'Artificial Intelligence (AI)', 310);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (749, 24, 25, 2, NULL, 'Artificial Intelligence (AI)', 319);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (750, 24, 25, 2, NULL, 'Artificial Intelligence (AI)', 324);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (751, 24, 25, 2, NULL, 'Assistant Lead, Campus Technical Learning', 237);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (752, 24, 25, 2, NULL, 'Backend Development', 117);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (753, 24, 25, 2, NULL, 'Backend Development', 123);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (754, 24, 25, 2, NULL, 'Behavioral Data Science', 260);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (755, 24, 25, 2, NULL, 'Big Data', 265);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (756, 24, 25, 2, NULL, 'BioML Research Associate', 271);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (757, 24, 25, 2, NULL, 'Blockchain Development', 160);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (758, 24, 25, 2, NULL, 'Business Analytics', 57);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (759, 24, 25, 2, NULL, 'Business Analytics', 61);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (760, 24, 25, 2, NULL, 'Business Analytics', 173);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (761, 24, 25, 2, NULL, 'Business Analytics', 280);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (762, 24, 25, 2, NULL, 'Business Intelligence', 58);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (763, 24, 25, 2, NULL, 'CUA Trajectory Specialist - 65129', 179);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (764, 24, 25, 2, NULL, 'Cloud And Machine Learning (AWS SageMaker)', 18);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (765, 24, 25, 2, NULL, 'Cloud Infrastructure (OCI/AWS)', 118);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (766, 24, 25, 2, NULL, 'Computer Vision', 9);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (767, 24, 25, 2, NULL, 'Computer Vision', 221);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (768, 24, 25, 2, NULL, 'Computer Vision', 263);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (769, 24, 25, 2, NULL, 'Computer Vision', 264);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (770, 24, 25, 2, NULL, 'Content Creator', 54);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (771, 24, 25, 2, NULL, 'Content Creator', 89);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (772, 24, 25, 2, NULL, 'Content Marketing', 62);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (773, 24, 25, 2, NULL, 'Content Writing', 126);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (774, 24, 25, 2, NULL, 'Content Writing (Research Associate In Computer Science)', 35);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (775, 24, 25, 2, NULL, 'Cyber Security', 101);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (776, 24, 25, 2, NULL, 'Cyber Security', 102);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (777, 24, 25, 2, NULL, 'Cyber Security', 103);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (778, 24, 25, 2, NULL, 'Data & AI Engineering', 293);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (779, 24, 25, 2, NULL, 'Data Analyst And Lead Management', 174);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (780, 24, 25, 2, NULL, 'Data Analytics', 11);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (781, 24, 25, 2, NULL, 'Data Analytics', 71);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (782, 24, 25, 2, NULL, 'Data Analytics', 78);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (783, 24, 25, 2, NULL, 'Data Analytics', 141);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (784, 24, 25, 2, NULL, 'Data Analytics', 172);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (785, 24, 25, 2, NULL, 'Data Analytics', 190);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (786, 24, 25, 2, NULL, 'Data Analytics', 281);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (787, 24, 26, 2, NULL, 'Data Annotation - ML', 201);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (788, 24, 26, 2, NULL, 'Data Annotation Team Management', 33);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (789, 24, 26, 2, NULL, 'Data Engineer Intern', 3);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (790, 24, 26, 2, NULL, 'Data Labeling Associate', 270);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (791, 24, 26, 2, NULL, 'Data Management', 53);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (792, 24, 26, 2, NULL, 'Data Platform Engineering (2026 Graduates Only)', 34);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (793, 24, 26, 2, NULL, 'Data Science', 22);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (794, 24, 26, 2, NULL, 'Data Science', 25);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (795, 24, 26, 2, NULL, 'Data Science', 26);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (796, 24, 26, 2, NULL, 'Data Science', 30);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (797, 24, 26, 2, NULL, 'Data Science', 46);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (798, 24, 26, 2, NULL, 'Data Science', 120);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (799, 24, 26, 2, NULL, 'Data Science', 143);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (800, 24, 26, 2, NULL, 'Data Science', 182);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (801, 24, 26, 2, NULL, 'Data Science', 210);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (802, 24, 26, 2, NULL, 'Data Science', 213);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (803, 24, 26, 2, NULL, 'Data Science', 222);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (804, 24, 26, 2, NULL, 'Data Science', 231);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (805, 24, 26, 2, NULL, 'Data Science', 244);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (806, 24, 26, 2, NULL, 'Data Science', 246);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (807, 24, 26, 2, NULL, 'Data Science', 285);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (808, 24, 26, 2, NULL, 'Data Science', 297);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (809, 24, 26, 2, NULL, 'Data Science', 299);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (810, 24, 26, 2, NULL, 'Data Science', 301);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (811, 24, 26, 2, NULL, 'Data Science', 323);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (812, 24, 26, 2, NULL, 'Data Science', 325);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (813, 24, 26, 2, NULL, 'Data Structuring And Data Cleaning For AI Models', 312);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (814, 24, 26, 2, NULL, 'Data Tagging Associate', 267);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (815, 24, 26, 2, NULL, 'Data Visualization', 52);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (816, 24, 26, 2, NULL, 'Digital Marketing', 56);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (817, 24, 26, 2, NULL, 'Digital Marketing', 80);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (818, 24, 26, 2, NULL, 'Digital Marketing', 87);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (819, 24, 26, 2, NULL, 'Digital Marketing', 90);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (820, 24, 26, 2, NULL, 'Digital Marketing', 129);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (821, 24, 26, 2, NULL, 'Digital Marketing & User Retention', 187);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (822, 24, 26, 2, NULL, 'Dropshipping E-commerce', 74);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (823, 24, 26, 2, NULL, 'E Commerce Business Manager', 72);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (824, 24, 26, 2, NULL, 'ERP Functional Consultant', 68);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (825, 24, 26, 2, NULL, 'Email Marketing & Automation Assistant', 70);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (826, 24, 26, 2, NULL, 'Embedded Systems', 50);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (827, 24, 26, 2, NULL, 'Environment Artist (Intern)', 95);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (828, 24, 26, 2, NULL, 'Equity Advisor/Business Development', 81);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (829, 24, 26, 2, NULL, 'Experiential Learning Mentor', 153);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (830, 24, 26, 2, NULL, 'Field Research Associate - Biodiversity Monitoring', 83);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (831, 24, 26, 2, NULL, 'Financial Technical Analysis (Intraday Trading)', 55);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (832, 24, 26, 2, NULL, 'Flutter Developer', 198);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (833, 24, 26, 2, NULL, 'Flutter Development', 136);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (834, 24, 26, 2, NULL, 'Flutter Development', 195);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (835, 24, 26, 2, NULL, 'Flutter Development', 197);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (836, 24, 26, 2, NULL, 'Founders Office', 32);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (837, 24, 26, 2, NULL, 'Founders Office', 73);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (838, 24, 26, 2, NULL, 'Founding AI Engineer', 209);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (839, 24, 26, 2, NULL, 'Front End Development', 100);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (840, 24, 26, 2, NULL, 'Frontend Engineer Intern', 161);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (841, 24, 26, 2, NULL, 'Full Stack Development', 49);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (842, 24, 26, 2, NULL, 'Full Stack Development', 108);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (843, 24, 26, 2, NULL, 'Full Stack Development', 158);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (844, 24, 26, 2, NULL, 'Full Stack Development', 200);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (845, 24, 26, 2, NULL, 'Full Stack Development', 204);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (846, 24, 26, 2, NULL, 'Full Stack Development- 2027 Batch (Founding Team)', 252);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (847, 24, 26, 2, NULL, 'Full Stack Web Development & AI', 232);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (848, 24, 26, 2, NULL, 'Game Development', 133);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (849, 24, 26, 2, NULL, 'Game Development', 138);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (850, 24, 26, 2, NULL, 'Game Development', 196);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (851, 24, 26, 2, NULL, 'Generative Engine Optimization (GEO)', 283);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (852, 24, 26, 2, NULL, 'Genrative AI Engineer', 230);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (853, 24, 26, 2, NULL, 'Global Talent Intern', 132);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (854, 24, 26, 2, NULL, 'HR Operations', 69);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (855, 24, 26, 2, NULL, 'Image Labeling', 269);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (856, 24, 26, 2, NULL, 'Image Tagging Executive', 242);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (857, 24, 26, 2, NULL, 'Internet Of Things (IoT)', 159);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (858, 24, 26, 2, NULL, 'Java Development', 112);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (859, 24, 26, 2, NULL, 'Java Development', 114);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (860, 24, 26, 2, NULL, 'Junior Full Stack Developer', 191);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (861, 24, 26, 2, NULL, 'Lead Management', 180);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (862, 24, 26, 2, NULL, 'MIS – Lead Management', 65);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (863, 24, 26, 2, NULL, 'MLOps and AI Infra', 226);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (864, 24, 26, 2, NULL, 'MLOps and AI Infra', 258);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (865, 24, 26, 2, NULL, 'Machine Learning', 19);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (866, 24, 26, 2, NULL, 'Machine Learning', 28);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (867, 24, 26, 2, NULL, 'Machine Learning', 29);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (868, 24, 26, 2, NULL, 'Machine Learning', 39);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (869, 24, 26, 2, NULL, 'Machine Learning', 44);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (870, 24, 26, 2, NULL, 'Machine Learning', 47);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (871, 24, 26, 2, NULL, 'Machine Learning', 110);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (872, 24, 26, 2, NULL, 'Machine Learning', 140);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (873, 24, 26, 2, NULL, 'Machine Learning', 166);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (874, 24, 26, 2, NULL, 'Machine Learning', 183);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (875, 24, 26, 2, NULL, 'Machine Learning', 185);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (876, 24, 26, 2, NULL, 'Machine Learning', 247);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (877, 24, 26, 2, NULL, 'Machine Learning', 250);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (878, 24, 26, 2, NULL, 'Machine Learning', 259);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (879, 24, 26, 2, NULL, 'Machine Learning', 261);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (880, 24, 26, 2, NULL, 'Machine Learning', 278);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (881, 24, 26, 2, NULL, 'Machine Learning', 291);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (882, 24, 26, 2, NULL, 'Machine Learning', 295);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (883, 24, 26, 2, NULL, 'Machine Learning', 302);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (884, 24, 26, 2, NULL, 'Machine Learning', 305);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (885, 24, 26, 2, NULL, 'Machine Learning', 309);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (886, 24, 26, 2, NULL, 'Machine Learning', 316);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (887, 24, 26, 2, NULL, 'Machine Learning And Web Development', 16);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (888, 24, 26, 2, NULL, 'Machine Learning Data Annotation', 322);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (889, 24, 26, 2, NULL, 'Machine Learning Intern  RAG For Hardware Design Generation', 178);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (890, 24, 26, 2, NULL, 'Machine Learning Trainee', 5);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (891, 24, 26, 2, NULL, 'Market Research', 64);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (892, 24, 26, 2, NULL, 'Market Research', 85);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (893, 24, 26, 2, NULL, 'Marketing', 79);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (894, 24, 26, 2, NULL, 'Mobile App Development', 92);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (895, 24, 26, 2, NULL, 'Mobile App Development', 96);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (896, 24, 26, 2, NULL, 'Mobile App Development', 122);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (897, 24, 26, 2, NULL, 'No-Code AI Automation', 224);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (898, 24, 26, 2, NULL, 'Office Manager', 125);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (899, 24, 26, 2, NULL, 'Open Knowledge Project', 59);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (900, 24, 26, 2, NULL, 'OpenClaw Trajectory Specialist - 65130', 127);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (901, 24, 26, 2, NULL, 'OpenClaw Trajectory Specialist - 65130', 142);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (902, 24, 26, 2, NULL, 'OpenClaw Trajectory Specialist - 65130', 146);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (903, 24, 26, 2, NULL, 'OpenClaw Trajectory Specialist - 65130', 288);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (904, 24, 26, 2, NULL, 'Point Cloud Object Detection And LiDAR Annotation Expert', 253);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (905, 24, 26, 2, NULL, 'Product', 318);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (906, 24, 26, 2, NULL, 'Product Management', 162);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (907, 24, 26, 2, NULL, 'Product Management', 321);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (908, 24, 26, 2, NULL, 'Product Research (E-commerce)', 77);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (909, 24, 26, 2, NULL, 'Prompt Engineering', 255);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (910, 24, 26, 2, NULL, 'Python AI Developer', 304);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (911, 24, 26, 2, NULL, 'Python Developer', 300);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (912, 24, 26, 2, NULL, 'Python Development', 20);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (913, 24, 26, 2, NULL, 'Python Development', 24);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (914, 24, 26, 2, NULL, 'Python Development', 27);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (915, 24, 26, 2, NULL, 'Python Development', 42);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (916, 24, 26, 2, NULL, 'Python Development', 45);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (917, 24, 26, 2, NULL, 'Python Development', 48);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (918, 24, 26, 2, NULL, 'Python Development', 124);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (919, 24, 26, 2, NULL, 'Python Development', 139);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (920, 24, 26, 2, NULL, 'Python Development', 165);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (921, 24, 26, 2, NULL, 'Python Development', 171);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (922, 24, 26, 2, NULL, 'Python Development', 245);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (923, 24, 26, 2, NULL, 'Python Development', 248);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (924, 24, 26, 2, NULL, 'Python Development', 251);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (925, 24, 26, 2, NULL, 'Python Development', 279);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (926, 24, 26, 2, NULL, 'Python Development', 282);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (927, 24, 26, 2, NULL, 'Python Development', 294);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (928, 24, 26, 2, NULL, 'Python Development', 296);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (929, 24, 26, 2, NULL, 'Python Development', 298);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (930, 24, 180, 2, NULL, 'React Native Development', 151);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (931, 24, 180, 2, NULL, 'Research And Outreach', 63);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (932, 24, 180, 2, NULL, 'Robotics Engineer', 167);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (933, 24, 180, 2, NULL, 'SEO & AI Optimisation', 67);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (934, 24, 180, 2, NULL, 'SQL/Data Engineer Intern', 131);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (935, 24, 180, 2, NULL, 'STEM Associate', 193);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (936, 24, 180, 2, NULL, 'STEM/Robotics and AI Facilitator/Trainer', 188);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (937, 24, 180, 2, NULL, 'Search Engine Optimization (SEO)', 189);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (938, 24, 180, 2, NULL, 'Selenium Web Scraper Developer', 164);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (939, 24, 180, 2, NULL, 'Shopify Developer', 194);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (940, 24, 180, 2, NULL, 'Social Media (YT)', 82);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (941, 24, 180, 2, NULL, 'Social Media Marketing', 84);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (942, 24, 180, 2, NULL, 'Social Media Outreach', 86);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (943, 24, 180, 2, NULL, 'Software Developer', 91);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (944, 24, 180, 2, NULL, 'Software Developer', 116);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (945, 24, 180, 2, NULL, 'Software Developer', 215);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (946, 24, 180, 2, NULL, 'Software Development', 93);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (947, 24, 180, 2, NULL, 'Software Development', 106);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (948, 24, 180, 2, NULL, 'Software Development', 152);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (949, 24, 180, 2, NULL, 'Software Development', 223);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (950, 24, 180, 2, NULL, 'Software Development', 315);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (951, 24, 180, 2, NULL, 'Software Engineer Volunteer -  Revenue Share', 176);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (952, 24, 180, 2, NULL, 'Software Testing', 134);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (953, 24, 180, 2, NULL, 'Startup Research & Policy', 144);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (954, 24, 180, 2, NULL, 'Systems Analyst Internship', 130);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (955, 24, 180, 2, NULL, 'Teaching Assistant', 119);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (956, 24, 180, 2, NULL, 'Tech Lead - Cloud Engineer/AI Engineer/Full Stack Developer', 135);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (957, 24, 180, 2, NULL, 'Technical Artist (Intern)', 109);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (958, 24, 180, 2, NULL, 'Technical Intern', 145);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (959, 24, 180, 2, NULL, 'Technical Operations', 239);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (960, 24, 180, 2, NULL, 'Urdu Data Annotation', 205);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (961, 24, 180, 2, NULL, 'Vibe Coding Intern', 137);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (962, 24, 180, 2, NULL, 'Video Annotation (DataForce) Experts', 277);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (963, 24, 180, 2, NULL, 'Voice Bot/AI Calling', 40);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (964, 24, 180, 2, NULL, 'Web Development', 104);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (965, 24, 180, 2, NULL, 'Web Development', 105);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (966, 24, 180, 2, NULL, 'Web Development', 107);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (967, 24, 180, 2, NULL, 'Web Development', 113);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (968, 24, 180, 2, NULL, 'Web Development', 115);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (969, 24, 180, 2, NULL, 'Web Development', 150);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (970, 24, 180, 2, NULL, 'Web Development', 163);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (971, 24, 180, 2, NULL, 'Website & Product Listing Executive', 148);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (972, 24, 180, 2, NULL, 'WordPress Content & Web Design', 98);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (973, 24, 180, 2, NULL, 'WordPress Development', 111);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (974, 24, 180, 2, NULL, 'X Growth', 192);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (975, 24, 180, 2, NULL, 'Youtube SEO & Social Media Executive', 76);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (976, 181, 181, 2, NULL, 'Marico Innovation Foundation', 63);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (977, 181, 181, 2, NULL, 'Vega Visionary Training FZE', 46);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (978, 181, 182, 2, NULL, 'AIESEC India (Mumbai, India)', 132);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (979, 181, 182, 2, NULL, 'AKHARI KOSHISH FOUNDATION', 224);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (980, 181, 182, 2, NULL, 'Aadi Foundation', 14);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (981, 181, 182, 2, NULL, 'Accredian', 182);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (982, 181, 182, 2, NULL, 'Acoustika India Private Limited', 74);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (983, 181, 182, 2, NULL, 'Across The Globe (ATG)', 155);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (984, 181, 182, 2, NULL, 'Across The Globe (ATG)', 262);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (985, 181, 182, 2, NULL, 'Almost Magic Private Limited', 2);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (986, 181, 182, 2, NULL, 'Alster IT Solutions', 124);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (987, 181, 182, 2, NULL, 'Analyttica Datalab', 131);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (988, 181, 182, 2, NULL, 'Anavai Technologies', 252);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (989, 181, 182, 2, NULL, 'Andaz Kumar', 31);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (990, 181, 182, 2, NULL, 'Angel Broking Limited', 81);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (991, 181, 182, 2, NULL, 'Anubhav Singh', 28);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (992, 181, 182, 2, NULL, 'AppQuarterz Technologies', 157);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (993, 181, 182, 2, NULL, 'Arhant Solutions', 8);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (994, 181, 182, 2, NULL, 'Artha Energy Projects Private Limited', 213);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (995, 181, 182, 2, NULL, 'AsiaDirect', 64);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (996, 181, 182, 2, NULL, 'Assetcues Solutions Private Limited', 7);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (997, 181, 182, 2, NULL, 'Astra Security', 4);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (998, 181, 182, 2, NULL, 'Awakn', 30);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (999, 181, 182, 2, NULL, 'Awarno', 249);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1000, 181, 182, 2, NULL, 'BNM Business Solutions LLP', 65);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1001, 181, 182, 2, NULL, 'BNM Business Solutions LLP', 174);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1002, 181, 182, 2, NULL, 'BNM Business Solutions LLP', 180);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1003, 181, 182, 2, NULL, 'Bal Sansar Sanstha', 99);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1004, 181, 182, 2, NULL, 'Balaji Telefilms Limited', 82);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1005, 181, 182, 2, NULL, 'Be4Breach', 204);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1006, 181, 182, 2, NULL, 'BiriyaniBoys Productions House LLP', 80);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1007, 181, 182, 2, NULL, 'Black March Studios', 95);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1008, 181, 182, 2, NULL, 'Black March Studios', 109);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1009, 181, 182, 2, NULL, 'Bold Monk Labs', 232);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1010, 181, 182, 2, NULL, 'Bright Media Solution Private Limited', 308);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1011, 181, 182, 2, NULL, 'CCBUL', 122);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1012, 181, 182, 2, NULL, 'CREATE', 243);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1013, 181, 182, 2, NULL, 'CapitalXB', 73);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1014, 181, 182, 2, NULL, 'CarVach', 289);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1015, 181, 182, 2, NULL, 'Cardinal Health', 3);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1016, 181, 182, 2, NULL, 'Career Solutions', 39);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1017, 181, 182, 2, NULL, 'Career-Domain', 61);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1018, 181, 182, 2, NULL, 'CareerNest', 15);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1019, 181, 182, 2, NULL, 'CareerNest', 302);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1020, 181, 182, 2, NULL, 'CattleGuru Private Limited', 227);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1021, 181, 182, 2, NULL, 'CiteSert', 316);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1022, 181, 182, 2, NULL, 'Cloud Back', 19);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1023, 181, 182, 2, NULL, 'Cloud Back', 20);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1024, 181, 182, 2, NULL, 'Cloud Back', 47);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1025, 181, 182, 2, NULL, 'Cloud Back', 48);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1026, 181, 182, 2, NULL, 'Cloud Back', 103);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1027, 181, 182, 2, NULL, 'Cloud Back', 112);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1028, 181, 182, 2, NULL, 'Cloud Back', 113);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1029, 181, 182, 2, NULL, 'Cloud Back', 171);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1030, 181, 182, 2, NULL, 'Cloud Back', 172);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1031, 181, 182, 2, NULL, 'Cloud Back', 185);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1032, 181, 182, 2, NULL, 'Cloud Back', 251);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1033, 181, 182, 2, NULL, 'Cloud Back', 261);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1034, 181, 182, 2, NULL, 'CodeTikki WorkSpace', 5);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1035, 181, 182, 2, NULL, 'Codemesh Systems LLP', 85);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1036, 181, 182, 2, NULL, 'Collective Artists Network', 66);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1037, 181, 182, 2, NULL, 'Configtap', 217);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1038, 181, 182, 2, NULL, 'Creator Cove', 72);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1039, 181, 182, 2, NULL, 'Daice Labs', 311);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1040, 181, 182, 2, NULL, 'Daten & Wissen Private Limited', 181);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1041, 181, 182, 2, NULL, 'Deep Life Savers', 52);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1042, 181, 182, 2, NULL, 'DeepThought CultureTech Ventures Private Limited', 260);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1043, 181, 182, 2, NULL, 'Design Plunge', 220);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1044, 181, 182, 2, NULL, 'Dilogs AI', 88);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1045, 181, 182, 2, NULL, 'DivyaNetra AI', 214);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1046, 181, 182, 2, NULL, 'Driphunter By Avhad Enterprises', 200);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1047, 181, 182, 2, NULL, 'Eastencher Software Private Limited', 215);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1048, 181, 182, 2, NULL, 'Eduminatti', 104);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1049, 181, 182, 2, NULL, 'Eklavya.me', 36);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1050, 181, 182, 2, NULL, 'Ekokintsugi', 125);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1051, 181, 182, 2, NULL, 'Emoolar Technology Private Limited', 17);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1052, 181, 182, 2, NULL, 'Emoolar Technology Private Limited', 22);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1053, 181, 182, 2, NULL, 'Emoolar Technology Private Limited', 101);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1054, 181, 182, 2, NULL, 'Emoolar Technology Private Limited', 246);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1055, 181, 182, 2, NULL, 'Emoolar Technology Private Limited', 299);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1056, 181, 182, 2, NULL, 'Emoolar Technology Private Limited', 325);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1057, 181, 182, 2, NULL, 'Enlight Lab', 238);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1058, 181, 182, 2, NULL, 'Euphotic Labs Private Limited', 9);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1059, 181, 182, 2, NULL, 'Euphotic Labs Private Limited', 254);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1060, 181, 182, 2, NULL, 'Expose Trendze', 21);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1061, 181, 182, 2, NULL, 'Fermions', 178);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1062, 181, 182, 2, NULL, 'Fine Data Analytics Private Limited', 320);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1063, 181, 182, 2, NULL, 'FiveS Digital Private Limited', 318);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1064, 181, 182, 2, NULL, 'Force-Intellect Private Limited', 68);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1065, 181, 182, 2, NULL, 'FormsADDA', 126);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1066, 181, 182, 2, NULL, 'Founding Years Learning Solutions Private Limited', 58);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1067, 181, 182, 2, NULL, 'GNG Developers', 6);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1068, 181, 182, 2, NULL, 'Gaadimech Technology Private Limited', 89);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1069, 181, 182, 2, NULL, 'Game Of Guru', 151);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1070, 181, 182, 2, NULL, 'GetMax Solutions', 216);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1071, 181, 182, 2, NULL, 'Giant Leap', 70);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1072, 181, 182, 2, NULL, 'Global Ace Technology', 218);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1073, 181, 182, 2, NULL, 'Global Trend', 118);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1074, 181, 182, 2, NULL, 'Goalisb', 76);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1075, 181, 182, 2, NULL, 'Goodera', 62);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1076, 181, 182, 2, NULL, 'Graindigits', 256);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1077, 181, 182, 2, NULL, 'Grameen Shramik Pratishthan', 51);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1078, 181, 182, 2, NULL, 'Graps Marketing Pvt Ltd', 90);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1079, 181, 182, 2, NULL, 'Graydot Technologies Private Limited', 317);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1080, 181, 182, 2, NULL, 'Greenleap Robotics Private Limited', 16);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1081, 181, 182, 2, NULL, 'Grinning Co. (Fremont, United States)', 186);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1082, 181, 182, 2, NULL, 'Headway Consulting', 233);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1083, 181, 182, 2, NULL, 'Hillborn Technologies Private Limited', 123);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1084, 181, 182, 2, NULL, 'Hiration', 100);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1085, 181, 182, 2, NULL, 'Hubnine India Private Limited', 221);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1086, 181, 182, 2, NULL, 'IIIT Hyderabad', 59);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1087, 181, 182, 2, NULL, 'IIT Guwahati', 263);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1088, 181, 182, 2, NULL, 'ITechServ', 93);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1089, 181, 182, 2, NULL, 'IWerk InfoSolutions LLP', 208);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1090, 181, 182, 2, NULL, 'IdealVillage', 96);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1091, 181, 182, 2, NULL, 'InLabels', 161);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1092, 181, 182, 2, NULL, 'IndiaBizForSale.com', 67);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1093, 181, 182, 2, NULL, 'Indiaum Solutions', 33);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1094, 181, 182, 2, NULL, 'Indiaum Solutions', 242);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1095, 181, 182, 2, NULL, 'Indiaum Solutions', 267);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1096, 181, 182, 2, NULL, 'Indiaum Solutions', 268);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1097, 181, 182, 2, NULL, 'Indiaum Solutions', 269);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1098, 181, 182, 2, NULL, 'Indiaum Solutions', 270);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1099, 181, 182, 2, NULL, 'Indiaum Solutions', 322);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1100, 181, 182, 2, NULL, 'Indika AI Private Limited', 205);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1101, 181, 182, 2, NULL, 'Indika AI Private Limited', 291);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1102, 181, 182, 2, NULL, 'Inflexion Analytics', 293);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1103, 181, 182, 2, NULL, 'Infoware', 319);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1104, 181, 182, 2, NULL, 'Innomax IT Solutions', 137);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1105, 181, 182, 2, NULL, 'Inorbvict Healthcare India Private Limited', 149);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1106, 181, 182, 2, NULL, 'Inorbvict Healthcare India Private Limited', 304);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1107, 181, 182, 2, NULL, 'InstaCAD Solutions India Private Limited', 272);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1108, 181, 182, 2, NULL, 'Insurance Buddha', 282);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1109, 181, 182, 2, NULL, 'Intugine Technologies Private Limited', 159);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1110, 181, 182, 2, NULL, 'Itech Serv', 91);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1111, 181, 182, 2, NULL, 'Jarurat Care', 69);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1112, 181, 182, 2, NULL, 'Jarvis Technology & Strategy Consulting', 198);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1113, 181, 182, 2, NULL, 'Joveo', 206);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1114, 181, 182, 2, NULL, 'KIDLOLAND KIDS & TODDLER GAMES PRIVATE LIMITED', 168);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1115, 181, 182, 2, NULL, 'Kayno World Education Private Limited', 170);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1116, 181, 182, 2, NULL, 'Khurana Technology Solutions', 191);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1117, 181, 182, 2, NULL, 'KlassWAY', 13);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1118, 181, 182, 2, NULL, 'L2BC', 136);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1119, 181, 182, 2, NULL, 'LI Blocks Private Limited', 188);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1120, 181, 182, 2, NULL, 'LawDocs', 1);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1121, 181, 182, 2, NULL, 'LegPro', 202);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1122, 181, 182, 2, NULL, 'Liberdat B.V.', 309);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1123, 181, 182, 2, NULL, 'Lila Poonawalla Foundation', 228);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1124, 181, 182, 2, NULL, 'Login2Xplore', 49);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1125, 181, 182, 2, NULL, 'MYKNOT Services (OPC) Private Limited', 108);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1126, 181, 182, 2, NULL, 'Madhura Power Technologies Private Limited', 219);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1127, 181, 186, 2, NULL, 'Mariox Software Private Limited', 38);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1128, 181, 186, 2, NULL, 'Maxgen Technologies Private Limited', 297);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1129, 181, 186, 2, NULL, 'Maxgen Technologies Private Limited', 298);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1130, 181, 186, 2, NULL, 'Maxgen Technologies Private Limited', 300);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1131, 181, 186, 2, NULL, 'Maxgen Technologies Private Limited', 301);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1132, 181, 186, 2, NULL, 'MechQuick', 173);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1133, 181, 186, 2, NULL, 'Medius Technologies Private Limited', 164);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1134, 181, 186, 2, NULL, 'Megaminds IT Services', 35);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1135, 181, 186, 2, NULL, 'Mem0 AI', 258);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1136, 181, 186, 2, NULL, 'Mentdesk Technologies Private Limited', 226);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1137, 181, 186, 2, NULL, 'Meta Results', 37);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1138, 181, 186, 2, NULL, 'Microsoft', 231);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1139, 181, 186, 2, NULL, 'Mindenious Edutech', 24);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1140, 181, 186, 2, NULL, 'Mindenious Edutech', 25);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1141, 181, 186, 2, NULL, 'Mommywize Private Limited', 207);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1142, 181, 186, 2, NULL, 'Monkhub', 134);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1143, 181, 186, 2, NULL, 'Monkhub', 138);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1144, 181, 186, 2, NULL, 'Motovolt', 284);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1145, 181, 186, 2, NULL, 'Mple AI', 321);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1146, 181, 186, 2, NULL, 'Muncho Technologies Private Limited', 315);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1147, 181, 186, 2, NULL, 'MyCloud Technology', 247);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1148, 181, 186, 2, NULL, 'MyCloud Technology', 248);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1149, 181, 186, 2, NULL, 'MyCloud Technology', 294);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1150, 181, 186, 2, NULL, 'MyCloud Technology', 295);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1151, 181, 186, 2, NULL, 'NFJ Labs Private Limited', 163);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1152, 181, 186, 2, NULL, 'Neurasys', 165);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1153, 181, 186, 2, NULL, 'Neurasys', 166);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1154, 181, 186, 2, NULL, 'New Business Strategies Corporation', 175);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1155, 181, 186, 2, NULL, 'OMNIDYA TECH LLP', 323);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1156, 181, 186, 2, NULL, 'OMR Shipping India Private Limited', 97);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1157, 181, 186, 2, NULL, 'OMitra Journey Solution Private Limited', 162);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1158, 181, 186, 2, NULL, 'Odisoft Technology Private Limited', 225);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1159, 181, 186, 2, NULL, 'Om Tekriwal', 313);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1160, 181, 186, 2, NULL, 'Opvia.in', 77);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1161, 181, 186, 2, NULL, 'OxiqAI', 292);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1162, 181, 186, 2, NULL, 'Parmar Techmero Solutions Private Limited', 121);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1163, 181, 186, 2, NULL, 'Pickyfits Official', 194);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1164, 181, 186, 2, NULL, 'Pilgrim', 283);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1165, 181, 186, 2, NULL, 'Pivotal Teleradiology', 287);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1166, 181, 186, 2, NULL, 'PlanetMeta.Live', 273);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1167, 181, 186, 2, NULL, 'Pollinate Impact', 307);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1168, 181, 186, 2, NULL, 'Pradip Nichite', 192);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1169, 181, 186, 2, NULL, 'Praxis Home Retail Limited', 57);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1170, 181, 186, 2, NULL, 'Preplaced', 32);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1171, 181, 186, 2, NULL, 'Primenumbers Technologies', 34);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1172, 181, 186, 2, NULL, 'Primetrade.ai', 290);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1173, 181, 186, 2, NULL, 'Protecht (Wyoming, United States)', 184);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1174, 181, 186, 2, NULL, 'Qodeit', 87);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1175, 181, 186, 2, NULL, 'Quantiphi', 237);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1176, 181, 186, 2, NULL, 'Quantum Root', 230);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1177, 181, 186, 2, NULL, 'Qubixo', 245);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1178, 181, 186, 2, NULL, 'Qubixo', 250);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1179, 181, 186, 2, NULL, 'Qubixo', 296);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1180, 181, 186, 2, NULL, 'Qubixo', 305);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1181, 181, 186, 2, NULL, 'Qwings', 193);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1182, 181, 186, 2, NULL, 'R J Gala & Associates', 129);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1183, 181, 186, 2, NULL, 'RIZE', 285);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1184, 181, 186, 2, NULL, 'ROBO-G', 153);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1185, 181, 186, 2, NULL, 'Ramesh S', 199);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1186, 181, 186, 2, NULL, 'Random Groups Of Companies', 78);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1187, 181, 186, 2, NULL, 'Raviraj Sarees Pvt Ltd', 12);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1188, 181, 186, 2, NULL, 'Reach Technologies', 169);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1189, 181, 186, 2, NULL, 'Reach Technologies', 274);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1190, 181, 186, 2, NULL, 'Reach Technologies', 275);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1191, 181, 186, 2, NULL, 'Read-Ink Technologies Private Limited', 84);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1192, 181, 186, 2, NULL, 'Reducate.ai', 23);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1193, 181, 186, 2, NULL, 'RentenPe', 71);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1194, 181, 186, 2, NULL, 'Restyle', 314);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1195, 181, 186, 2, NULL, 'Robin Bosky', 75);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1196, 181, 186, 2, NULL, 'Robocapital', 257);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1197, 181, 186, 2, NULL, 'Rupadi', 211);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1198, 181, 186, 2, NULL, 'SKIDEV EDUTECH PRIVATE LIMITED', 41);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1199, 181, 186, 2, NULL, 'STARTUP GROWW CONSULTING SERVICES PRIVATE LIMITED', 144);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1200, 181, 186, 2, NULL, 'Safecity (Red Dot Foundation)', 18);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1201, 181, 186, 2, NULL, 'Saltocorp', 133);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1202, 181, 186, 2, NULL, 'Sameer Khatri', 135);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1203, 181, 186, 2, NULL, 'Sanatan Organic', 324);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1204, 181, 186, 2, NULL, 'Saniya SanjayGaikwad', 210);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1205, 181, 186, 2, NULL, 'Sankar Group', 40);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1206, 181, 186, 2, NULL, 'Satyukt Analytics Private Limited', 197);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1207, 181, 186, 2, NULL, 'SaveIN', 117);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1208, 181, 186, 2, NULL, 'Score Merit', 105);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1209, 181, 186, 2, NULL, 'ServiceHive', 259);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1210, 181, 186, 2, NULL, 'Shivam Singh', 120);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1211, 181, 186, 2, NULL, 'Shivam Singh', 143);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1212, 181, 186, 2, NULL, 'Shunya Digital', 60);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1213, 181, 186, 2, NULL, 'Siemens Healthcare Private Limited', 145);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1214, 181, 186, 2, NULL, 'Sigma Health (Wolverhampton, United Kingdom)', 98);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1215, 181, 186, 2, NULL, 'Simpler Growth', 189);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1216, 181, 186, 2, NULL, 'Skill Bharat Association', 241);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1217, 181, 186, 2, NULL, 'SkillLevel', 110);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1218, 181, 186, 2, NULL, 'SmartLabprojects', 286);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1219, 181, 186, 2, NULL, 'Softel Technologies Incorporation', 94);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1220, 181, 186, 2, NULL, 'Solera Life Science Private Limited', 234);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1221, 181, 186, 2, NULL, 'Solvitude', 253);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1222, 181, 186, 2, NULL, 'Solvitude', 277);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1223, 181, 186, 2, NULL, 'Sparks To Ideas', 222);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1224, 181, 186, 2, NULL, 'SportVot', 264);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1225, 181, 186, 2, NULL, 'Stackwise', 244);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1226, 181, 186, 2, NULL, 'Statcon Energiaa', 156);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1227, 181, 186, 2, NULL, 'Steadwing', 209);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1228, 181, 186, 2, NULL, 'Stories Arabia FZ', 158);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1229, 181, 186, 2, NULL, 'Suresh Dani''s Classes', 160);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1230, 181, 186, 2, NULL, 'Suresh Dani''s Classes', 195);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1231, 181, 186, 2, NULL, 'Suresh Dani''s Classes', 196);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1232, 181, 186, 2, NULL, 'Sybrant Technologies Private Limited', 306);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1233, 181, 186, 2, NULL, 'Symonis', 27);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1234, 181, 186, 2, NULL, 'Symonis', 29);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1235, 181, 186, 2, NULL, 'Symonis', 44);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1236, 181, 186, 2, NULL, 'Symonis', 45);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1237, 181, 186, 2, NULL, 'Symonis', 102);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1238, 181, 186, 2, NULL, 'Symonis', 114);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1239, 181, 186, 2, NULL, 'Symonis', 115);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1240, 181, 186, 2, NULL, 'Symonis', 139);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1241, 181, 186, 2, NULL, 'Symonis', 140);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1242, 181, 186, 2, NULL, 'Symonis', 141);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1243, 181, 186, 2, NULL, 'Symonis', 183);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1244, 181, 186, 2, NULL, 'Symonis', 190);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1245, 181, 186, 2, NULL, 'TAS Consultants FZ-LLC', 212);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1246, 181, 186, 2, NULL, 'TESK Labs', 255);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1247, 181, 186, 2, NULL, 'TRIKSHA', 303);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1248, 181, 186, 2, NULL, 'TRISARAN GRAMEEN MICRO APPEX FEDERATION', 150);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1249, 181, 186, 2, NULL, 'TRISKN', 54);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1250, 181, 186, 2, NULL, 'TSTEPS PRIVATE LIMITED', 265);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1251, 181, 186, 2, NULL, 'TSTEPS PRIVATE LIMITED', 266);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1252, 181, 186, 2, NULL, 'TSTEPS PRIVATE LIMITED', 276);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1253, 181, 186, 2, NULL, 'TSTEPS PRIVATE LIMITED', 278);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1254, 181, 186, 2, NULL, 'TSTEPS PRIVATE LIMITED', 279);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1255, 181, 186, 2, NULL, 'TSTEPS PRIVATE LIMITED', 280);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1256, 181, 186, 2, NULL, 'TSTEPS PRIVATE LIMITED', 281);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1257, 181, 186, 2, NULL, 'TZURONI LTD. (Kefar Sava, Israel)', 10);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1258, 181, 186, 2, NULL, 'Talview', 116);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1259, 181, 186, 2, NULL, 'Tanj ITech Private Limited', 106);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1260, 181, 186, 2, NULL, 'Tax-O-Smart LLP', 154);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1261, 181, 186, 2, NULL, 'Tech Analogy', 239);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1262, 181, 186, 2, NULL, 'TechTrapture', 147);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1263, 181, 186, 2, NULL, 'Techasoft Private Limited', 42);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1264, 181, 186, 2, NULL, 'Technoculture Research', 167);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1265, 181, 186, 2, NULL, 'Technoculture Research', 271);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1266, 181, 186, 2, NULL, 'Tensai Ventures LLC', 92);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1267, 181, 186, 2, NULL, 'The Clay Company', 148);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1268, 181, 186, 2, NULL, 'The Expert Web Agency', 111);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1269, 181, 186, 2, NULL, 'The Skillians', 119);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1270, 181, 186, 2, NULL, 'Thriveit Media', 86);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1271, 181, 186, 2, NULL, 'Tidal7 Asia - A J7 Agency', 56);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1272, 181, 186, 2, NULL, 'Toytales', 235);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1273, 181, 186, 2, NULL, 'Trader For Tomorrow', 55);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1274, 181, 186, 2, NULL, 'Triluxo Technologies Private Limited', 43);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1275, 181, 186, 2, NULL, 'TrustSignal Ventures Private Limited', 152);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1276, 181, 186, 2, NULL, 'Turing', 127);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1277, 181, 186, 2, NULL, 'Turing', 142);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1278, 181, 186, 2, NULL, 'Turing', 146);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1279, 181, 186, 2, NULL, 'Turing', 179);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1280, 181, 186, 2, NULL, 'Turing', 288);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1281, 181, 186, 2, NULL, 'UNITED CARBON TECHNOLOGIES PRIVATE LIMITED', 177);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1282, 181, 186, 2, NULL, 'URHRO', 26);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1283, 181, 186, 2, NULL, 'Unnati Enterprises', 53);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1284, 181, 186, 2, NULL, 'VIZON', 11);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1285, 181, 186, 2, NULL, 'VIZON', 236);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1286, 181, 186, 2, NULL, 'VVP Healthcare Evolution Pvt Ltd', 203);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1287, 181, 186, 2, NULL, 'Vaibhav Wakade', 50);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1288, 181, 187, 2, NULL, 'Venera Technologies Private Limited', 201);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1289, 181, 187, 2, NULL, 'Veritem Health Private Limited', 187);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1290, 181, 187, 2, NULL, 'Vishwa Jagran Manav Sewa Sangh Charitable Trust', 229);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1291, 181, 187, 2, NULL, 'Wagons Learning Private Limited', 310);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1292, 181, 187, 2, NULL, 'Webgenesis', 107);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1293, 181, 187, 2, NULL, 'Wildly Tech Private Limited', 83);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1294, 181, 187, 2, NULL, 'Wingman Pro', 128);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1295, 181, 187, 2, NULL, 'Wobot Intelligence Private Limited', 240);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1296, 181, 187, 2, NULL, 'Workfall', 130);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1297, 181, 187, 2, NULL, 'Wudmin Energy', 79);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1298, 181, 187, 2, NULL, 'ZKAP EDTECH SERVICES PRIVATE LIMITED', 312);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1299, 181, 187, 2, NULL, 'ZenAppStudio', 176);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1300, 181, 187, 2, NULL, 'Zyaro', 223);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1301, 188, 188, 2, NULL, 'NEW', 317);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1302, 188, 189, 2, NULL, 'ANALYZED', 1);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1303, 188, 189, 2, NULL, 'ANALYZED', 2);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1304, 188, 189, 2, NULL, 'ANALYZED', 3);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1305, 188, 189, 2, NULL, 'ANALYZED', 4);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1306, 188, 189, 2, NULL, 'ANALYZED', 5);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1307, 188, 189, 2, NULL, 'ANALYZED', 6);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1308, 188, 189, 2, NULL, 'ANALYZED', 7);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1309, 188, 189, 2, NULL, 'ANALYZED', 8);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1310, 188, 189, 2, NULL, 'ANALYZED', 9);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1311, 188, 189, 2, NULL, 'ANALYZED', 10);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1312, 188, 189, 2, NULL, 'ANALYZED', 11);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1313, 188, 189, 2, NULL, 'ANALYZED', 12);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1314, 188, 189, 2, NULL, 'ANALYZED', 13);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1315, 188, 189, 2, NULL, 'ANALYZED', 14);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1316, 188, 189, 2, NULL, 'ANALYZED', 15);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1317, 188, 189, 2, NULL, 'ANALYZED', 16);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1318, 188, 189, 2, NULL, 'ANALYZED', 17);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1319, 188, 189, 2, NULL, 'ANALYZED', 18);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1320, 188, 189, 2, NULL, 'ANALYZED', 19);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1321, 188, 189, 2, NULL, 'ANALYZED', 20);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1322, 188, 189, 2, NULL, 'ANALYZED', 21);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1323, 188, 189, 2, NULL, 'ANALYZED', 22);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1324, 188, 189, 2, NULL, 'ANALYZED', 23);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1325, 188, 189, 2, NULL, 'ANALYZED', 24);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1326, 188, 189, 2, NULL, 'ANALYZED', 25);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1327, 188, 189, 2, NULL, 'ANALYZED', 26);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1328, 188, 189, 2, NULL, 'ANALYZED', 27);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1329, 188, 189, 2, NULL, 'ANALYZED', 28);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1330, 188, 189, 2, NULL, 'ANALYZED', 29);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1331, 188, 189, 2, NULL, 'ANALYZED', 30);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1332, 188, 189, 2, NULL, 'ANALYZED', 31);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1333, 188, 189, 2, NULL, 'ANALYZED', 32);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1334, 188, 189, 2, NULL, 'ANALYZED', 33);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1335, 188, 189, 2, NULL, 'ANALYZED', 34);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1336, 188, 189, 2, NULL, 'ANALYZED', 35);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1337, 188, 189, 2, NULL, 'ANALYZED', 36);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1338, 188, 189, 2, NULL, 'ANALYZED', 37);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1339, 188, 189, 2, NULL, 'ANALYZED', 38);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1340, 188, 189, 2, NULL, 'ANALYZED', 39);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1341, 188, 189, 2, NULL, 'ANALYZED', 40);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1342, 188, 189, 2, NULL, 'ANALYZED', 41);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1343, 188, 189, 2, NULL, 'ANALYZED', 42);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1344, 188, 189, 2, NULL, 'ANALYZED', 43);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1345, 188, 189, 2, NULL, 'ANALYZED', 44);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1346, 188, 189, 2, NULL, 'ANALYZED', 45);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1347, 188, 189, 2, NULL, 'ANALYZED', 46);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1348, 188, 189, 2, NULL, 'ANALYZED', 47);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1349, 188, 189, 2, NULL, 'ANALYZED', 48);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1350, 188, 189, 2, NULL, 'ANALYZED', 49);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1351, 188, 189, 2, NULL, 'ANALYZED', 50);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1352, 188, 189, 2, NULL, 'ANALYZED', 51);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1353, 188, 189, 2, NULL, 'ANALYZED', 52);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1354, 188, 189, 2, NULL, 'ANALYZED', 53);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1355, 188, 189, 2, NULL, 'ANALYZED', 54);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1356, 188, 189, 2, NULL, 'ANALYZED', 55);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1357, 188, 189, 2, NULL, 'ANALYZED', 56);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1358, 188, 189, 2, NULL, 'ANALYZED', 57);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1359, 188, 189, 2, NULL, 'ANALYZED', 58);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1360, 188, 189, 2, NULL, 'ANALYZED', 59);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1361, 188, 189, 2, NULL, 'ANALYZED', 60);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1362, 188, 189, 2, NULL, 'ANALYZED', 61);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1363, 188, 189, 2, NULL, 'ANALYZED', 62);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1364, 188, 189, 2, NULL, 'ANALYZED', 63);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1365, 188, 189, 2, NULL, 'ANALYZED', 64);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1366, 188, 189, 2, NULL, 'ANALYZED', 65);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1367, 188, 189, 2, NULL, 'ANALYZED', 66);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1368, 188, 189, 2, NULL, 'ANALYZED', 67);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1369, 188, 189, 2, NULL, 'ANALYZED', 68);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1370, 188, 189, 2, NULL, 'ANALYZED', 69);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1371, 188, 189, 2, NULL, 'ANALYZED', 70);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1372, 188, 189, 2, NULL, 'ANALYZED', 71);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1373, 188, 189, 2, NULL, 'ANALYZED', 72);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1374, 188, 189, 2, NULL, 'ANALYZED', 73);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1375, 188, 189, 2, NULL, 'ANALYZED', 74);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1376, 188, 189, 2, NULL, 'ANALYZED', 75);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1377, 188, 189, 2, NULL, 'ANALYZED', 76);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1378, 188, 189, 2, NULL, 'ANALYZED', 77);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1379, 188, 189, 2, NULL, 'ANALYZED', 78);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1380, 188, 189, 2, NULL, 'ANALYZED', 79);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1381, 188, 189, 2, NULL, 'ANALYZED', 80);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1382, 188, 189, 2, NULL, 'ANALYZED', 81);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1383, 188, 189, 2, NULL, 'ANALYZED', 82);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1384, 188, 189, 2, NULL, 'ANALYZED', 83);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1385, 188, 189, 2, NULL, 'ANALYZED', 84);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1386, 188, 189, 2, NULL, 'ANALYZED', 85);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1387, 188, 189, 2, NULL, 'ANALYZED', 86);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1388, 188, 189, 2, NULL, 'ANALYZED', 87);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1389, 188, 189, 2, NULL, 'ANALYZED', 88);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1390, 188, 189, 2, NULL, 'ANALYZED', 89);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1391, 188, 189, 2, NULL, 'ANALYZED', 90);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1392, 188, 189, 2, NULL, 'ANALYZED', 91);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1393, 188, 189, 2, NULL, 'ANALYZED', 92);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1394, 188, 189, 2, NULL, 'ANALYZED', 93);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1395, 188, 189, 2, NULL, 'ANALYZED', 94);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1396, 188, 189, 2, NULL, 'ANALYZED', 95);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1397, 188, 189, 2, NULL, 'ANALYZED', 96);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1398, 188, 189, 2, NULL, 'ANALYZED', 97);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1399, 188, 189, 2, NULL, 'ANALYZED', 98);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1400, 188, 189, 2, NULL, 'ANALYZED', 99);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1401, 188, 189, 2, NULL, 'ANALYZED', 100);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1402, 188, 189, 2, NULL, 'ANALYZED', 101);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1403, 188, 189, 2, NULL, 'ANALYZED', 102);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1404, 188, 189, 2, NULL, 'ANALYZED', 103);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1405, 188, 189, 2, NULL, 'ANALYZED', 104);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1406, 188, 189, 2, NULL, 'ANALYZED', 105);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1407, 188, 189, 2, NULL, 'ANALYZED', 106);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1408, 188, 189, 2, NULL, 'ANALYZED', 107);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1409, 188, 189, 2, NULL, 'ANALYZED', 108);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1410, 188, 189, 2, NULL, 'ANALYZED', 109);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1411, 188, 189, 2, NULL, 'ANALYZED', 110);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1412, 188, 189, 2, NULL, 'ANALYZED', 111);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1413, 188, 189, 2, NULL, 'ANALYZED', 112);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1414, 188, 189, 2, NULL, 'ANALYZED', 113);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1415, 188, 189, 2, NULL, 'ANALYZED', 114);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1416, 188, 189, 2, NULL, 'ANALYZED', 115);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1417, 188, 189, 2, NULL, 'ANALYZED', 116);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1418, 188, 189, 2, NULL, 'ANALYZED', 117);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1419, 188, 189, 2, NULL, 'ANALYZED', 119);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1420, 188, 189, 2, NULL, 'ANALYZED', 120);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1421, 188, 189, 2, NULL, 'ANALYZED', 121);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1422, 188, 189, 2, NULL, 'ANALYZED', 122);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1423, 188, 189, 2, NULL, 'ANALYZED', 123);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1424, 188, 189, 2, NULL, 'ANALYZED', 124);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1425, 188, 189, 2, NULL, 'ANALYZED', 125);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1426, 188, 189, 2, NULL, 'ANALYZED', 126);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1427, 188, 189, 2, NULL, 'ANALYZED', 127);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1428, 188, 189, 2, NULL, 'ANALYZED', 128);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1429, 188, 189, 2, NULL, 'ANALYZED', 129);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1430, 188, 189, 2, NULL, 'ANALYZED', 130);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1431, 188, 189, 2, NULL, 'ANALYZED', 131);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1432, 188, 189, 2, NULL, 'ANALYZED', 132);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1433, 188, 189, 2, NULL, 'ANALYZED', 133);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1434, 188, 189, 2, NULL, 'ANALYZED', 134);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1435, 188, 189, 2, NULL, 'ANALYZED', 135);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1436, 188, 189, 2, NULL, 'ANALYZED', 136);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1437, 188, 189, 2, NULL, 'ANALYZED', 137);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1438, 188, 189, 2, NULL, 'ANALYZED', 138);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1439, 188, 189, 2, NULL, 'ANALYZED', 139);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1440, 188, 189, 2, NULL, 'ANALYZED', 140);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1441, 188, 189, 2, NULL, 'ANALYZED', 141);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1442, 188, 189, 2, NULL, 'ANALYZED', 142);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1443, 188, 189, 2, NULL, 'ANALYZED', 143);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1444, 188, 189, 2, NULL, 'ANALYZED', 144);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1445, 188, 189, 2, NULL, 'ANALYZED', 145);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1446, 188, 189, 2, NULL, 'ANALYZED', 146);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1447, 188, 189, 2, NULL, 'ANALYZED', 147);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1448, 188, 189, 2, NULL, 'ANALYZED', 148);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1449, 188, 189, 2, NULL, 'NEW', 149);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1450, 188, 189, 2, NULL, 'NEW', 150);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1451, 188, 189, 2, NULL, 'NEW', 151);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1452, 188, 189, 2, NULL, 'NEW', 152);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1453, 188, 189, 2, NULL, 'NEW', 153);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1454, 188, 189, 2, NULL, 'NEW', 154);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1455, 188, 189, 2, NULL, 'NEW', 155);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1456, 188, 189, 2, NULL, 'NEW', 156);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1457, 188, 189, 2, NULL, 'NEW', 157);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1458, 188, 189, 2, NULL, 'NEW', 158);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1459, 188, 189, 2, NULL, 'NEW', 159);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1460, 188, 189, 2, NULL, 'NEW', 160);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1461, 188, 189, 2, NULL, 'NEW', 161);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1462, 188, 189, 2, NULL, 'NEW', 162);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1463, 188, 189, 2, NULL, 'NEW', 163);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1464, 188, 189, 2, NULL, 'NEW', 164);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1465, 188, 189, 2, NULL, 'NEW', 165);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1466, 188, 189, 2, NULL, 'NEW', 166);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1467, 188, 189, 2, NULL, 'NEW', 167);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1468, 188, 189, 2, NULL, 'NEW', 168);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1469, 188, 189, 2, NULL, 'NEW', 169);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1470, 188, 189, 2, NULL, 'NEW', 170);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1471, 188, 189, 2, NULL, 'NEW', 171);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1472, 188, 189, 2, NULL, 'NEW', 172);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1473, 188, 189, 2, NULL, 'NEW', 173);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1474, 188, 189, 2, NULL, 'NEW', 174);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1475, 188, 189, 2, NULL, 'NEW', 175);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1476, 188, 189, 2, NULL, 'NEW', 176);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1477, 188, 189, 2, NULL, 'NEW', 177);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1478, 188, 189, 2, NULL, 'NEW', 178);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1479, 188, 189, 2, NULL, 'NEW', 179);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1480, 188, 189, 2, NULL, 'NEW', 180);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1481, 188, 189, 2, NULL, 'NEW', 181);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1482, 188, 189, 2, NULL, 'NEW', 182);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1483, 188, 189, 2, NULL, 'NEW', 183);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1484, 188, 189, 2, NULL, 'NEW', 184);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1485, 188, 189, 2, NULL, 'NEW', 185);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1486, 188, 189, 2, NULL, 'NEW', 186);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1487, 188, 189, 2, NULL, 'NEW', 187);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1488, 188, 189, 2, NULL, 'NEW', 188);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1489, 188, 189, 2, NULL, 'NEW', 189);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1490, 188, 189, 2, NULL, 'NEW', 190);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1491, 188, 189, 2, NULL, 'NEW', 191);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1492, 188, 189, 2, NULL, 'NEW', 192);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1493, 188, 189, 2, NULL, 'NEW', 193);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1494, 188, 189, 2, NULL, 'NEW', 194);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1495, 188, 189, 2, NULL, 'NEW', 195);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1496, 188, 189, 2, NULL, 'NEW', 196);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1497, 188, 189, 2, NULL, 'NEW', 197);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1498, 188, 189, 2, NULL, 'NEW', 198);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1499, 188, 189, 2, NULL, 'NEW', 199);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1500, 188, 189, 2, NULL, 'NEW', 200);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1501, 188, 189, 2, NULL, 'NEW', 201);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1502, 188, 189, 2, NULL, 'NEW', 202);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1503, 188, 189, 2, NULL, 'NEW', 203);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1504, 188, 189, 2, NULL, 'NEW', 204);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1505, 188, 189, 2, NULL, 'NEW', 205);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1506, 188, 189, 2, NULL, 'NEW', 206);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1507, 188, 189, 2, NULL, 'NEW', 207);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1508, 188, 189, 2, NULL, 'NEW', 208);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1509, 188, 189, 2, NULL, 'NEW', 209);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1510, 188, 189, 2, NULL, 'NEW', 210);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1511, 188, 189, 2, NULL, 'NEW', 211);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1512, 188, 189, 2, NULL, 'NEW', 212);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1513, 188, 189, 2, NULL, 'NEW', 213);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1514, 188, 189, 2, NULL, 'NEW', 214);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1515, 188, 189, 2, NULL, 'NEW', 215);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1516, 188, 189, 2, NULL, 'NEW', 216);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1517, 188, 189, 2, NULL, 'NEW', 217);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1518, 188, 189, 2, NULL, 'NEW', 218);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1519, 188, 189, 2, NULL, 'NEW', 219);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1520, 188, 189, 2, NULL, 'NEW', 220);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1521, 188, 189, 2, NULL, 'NEW', 221);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1522, 188, 189, 2, NULL, 'NEW', 222);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1523, 188, 189, 2, NULL, 'NEW', 223);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1524, 188, 189, 2, NULL, 'NEW', 224);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1525, 188, 189, 2, NULL, 'NEW', 225);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1526, 188, 189, 2, NULL, 'NEW', 226);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1527, 188, 189, 2, NULL, 'NEW', 227);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1528, 188, 189, 2, NULL, 'NEW', 228);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1529, 188, 189, 2, NULL, 'NEW', 229);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1530, 188, 189, 2, NULL, 'NEW', 230);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1531, 188, 189, 2, NULL, 'NEW', 231);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1532, 188, 189, 2, NULL, 'NEW', 232);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1533, 188, 189, 2, NULL, 'NEW', 233);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1534, 188, 189, 2, NULL, 'NEW', 234);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1535, 188, 189, 2, NULL, 'NEW', 235);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1536, 188, 189, 2, NULL, 'NEW', 236);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1537, 188, 189, 2, NULL, 'NEW', 237);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1538, 188, 189, 2, NULL, 'NEW', 238);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1539, 188, 189, 2, NULL, 'NEW', 239);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1540, 188, 189, 2, NULL, 'NEW', 240);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1541, 188, 189, 2, NULL, 'NEW', 241);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1542, 188, 189, 2, NULL, 'NEW', 242);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1543, 188, 189, 2, NULL, 'NEW', 243);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1544, 188, 189, 2, NULL, 'NEW', 244);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1545, 188, 189, 2, NULL, 'NEW', 245);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1546, 188, 189, 2, NULL, 'NEW', 246);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1547, 188, 189, 2, NULL, 'NEW', 247);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1548, 188, 189, 2, NULL, 'NEW', 248);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1549, 188, 189, 2, NULL, 'NEW', 249);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1550, 188, 189, 2, NULL, 'NEW', 250);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1551, 188, 189, 2, NULL, 'NEW', 251);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1552, 188, 189, 2, NULL, 'NEW', 252);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1553, 188, 189, 2, NULL, 'NEW', 253);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1554, 188, 189, 2, NULL, 'NEW', 254);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1555, 188, 189, 2, NULL, 'NEW', 255);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1556, 188, 189, 2, NULL, 'NEW', 256);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1557, 188, 189, 2, NULL, 'NEW', 257);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1558, 188, 189, 2, NULL, 'NEW', 258);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1559, 188, 189, 2, NULL, 'NEW', 259);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1560, 188, 189, 2, NULL, 'NEW', 260);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1561, 188, 189, 2, NULL, 'NEW', 261);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1562, 188, 189, 2, NULL, 'NEW', 262);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1563, 188, 189, 2, NULL, 'NEW', 263);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1564, 188, 189, 2, NULL, 'NEW', 264);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1565, 188, 189, 2, NULL, 'NEW', 265);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1566, 188, 189, 2, NULL, 'NEW', 266);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1567, 188, 189, 2, NULL, 'NEW', 267);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1568, 188, 189, 2, NULL, 'NEW', 268);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1569, 188, 189, 2, NULL, 'NEW', 269);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1570, 188, 189, 2, NULL, 'NEW', 270);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1571, 188, 189, 2, NULL, 'NEW', 271);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1572, 188, 189, 2, NULL, 'NEW', 272);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1573, 188, 189, 2, NULL, 'NEW', 273);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1574, 188, 189, 2, NULL, 'NEW', 274);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1575, 188, 189, 2, NULL, 'NEW', 275);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1576, 188, 189, 2, NULL, 'NEW', 276);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1577, 188, 189, 2, NULL, 'NEW', 277);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1578, 188, 189, 2, NULL, 'NEW', 278);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1579, 188, 189, 2, NULL, 'NEW', 279);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1580, 188, 189, 2, NULL, 'NEW', 280);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1581, 188, 189, 2, NULL, 'NEW', 281);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1582, 188, 189, 2, NULL, 'NEW', 282);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1583, 188, 189, 2, NULL, 'NEW', 283);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1584, 188, 189, 2, NULL, 'NEW', 284);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1585, 188, 189, 2, NULL, 'NEW', 285);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1586, 188, 189, 2, NULL, 'NEW', 286);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1587, 188, 189, 2, NULL, 'NEW', 287);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1588, 188, 189, 2, NULL, 'NEW', 288);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1589, 188, 189, 2, NULL, 'NEW', 289);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1590, 188, 189, 2, NULL, 'NEW', 290);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1591, 188, 189, 2, NULL, 'NEW', 291);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1592, 188, 189, 2, NULL, 'NEW', 292);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1593, 188, 189, 2, NULL, 'NEW', 293);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1594, 188, 189, 2, NULL, 'NEW', 294);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1595, 188, 189, 2, NULL, 'NEW', 295);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1596, 188, 189, 2, NULL, 'NEW', 296);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1597, 188, 189, 2, NULL, 'NEW', 297);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1598, 188, 189, 2, NULL, 'NEW', 298);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1599, 188, 189, 2, NULL, 'NEW', 299);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1600, 188, 189, 2, NULL, 'NEW', 300);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1601, 188, 189, 2, NULL, 'NEW', 301);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1602, 188, 189, 2, NULL, 'NEW', 302);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1603, 188, 189, 2, NULL, 'NEW', 303);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1604, 188, 189, 2, NULL, 'NEW', 304);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1605, 188, 189, 2, NULL, 'NEW', 305);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1606, 188, 189, 2, NULL, 'NEW', 306);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1607, 188, 189, 2, NULL, 'NEW', 307);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1608, 188, 189, 2, NULL, 'NEW', 308);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1609, 188, 189, 2, NULL, 'NEW', 309);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1610, 188, 189, 2, NULL, 'NEW', 310);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1611, 188, 189, 2, NULL, 'NEW', 311);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1612, 188, 189, 2, NULL, 'NEW', 312);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1613, 188, 189, 2, NULL, 'NEW', 313);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1614, 188, 189, 2, NULL, 'NEW', 314);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1615, 188, 189, 2, NULL, 'NEW', 315);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1616, 188, 189, 2, NULL, 'NEW', 316);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1617, 188, 190, 2, NULL, 'NEW', 318);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1618, 188, 190, 2, NULL, 'NEW', 319);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1619, 188, 190, 2, NULL, 'NEW', 320);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1620, 188, 190, 2, NULL, 'NEW', 321);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1621, 188, 190, 2, NULL, 'NEW', 322);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1622, 188, 190, 2, NULL, 'NEW', 323);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1623, 188, 190, 2, NULL, 'NEW', 324);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1624, 188, 190, 2, NULL, 'NEW', 325);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1625, 188, 190, 2, NULL, 'SKIPPED', 118);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1626, 191, 191, 2, NULL, 1, 1);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1627, 191, 191, 2, NULL, 1, 2);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1628, 191, 191, 2, NULL, 1, 3);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1629, 191, 191, 2, NULL, 1, 4);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1630, 191, 191, 2, NULL, 1, 5);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1631, 191, 191, 2, NULL, 1, 6);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1632, 191, 191, 2, NULL, 1, 7);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1633, 191, 191, 2, NULL, 1, 8);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1634, 191, 191, 2, NULL, 1, 9);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1635, 191, 191, 2, NULL, 1, 10);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1636, 191, 191, 2, NULL, 1, 11);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1637, 191, 191, 2, NULL, 1, 12);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1638, 191, 191, 2, NULL, 1, 13);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1639, 191, 191, 2, NULL, 1, 14);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1640, 191, 191, 2, NULL, 1, 15);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1641, 191, 191, 2, NULL, 1, 16);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1642, 191, 191, 2, NULL, 1, 17);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1643, 191, 191, 2, NULL, 1, 18);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1644, 191, 191, 2, NULL, 1, 19);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1645, 191, 191, 2, NULL, 1, 20);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1646, 191, 191, 2, NULL, 1, 21);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1647, 191, 191, 2, NULL, 1, 22);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1648, 191, 191, 2, NULL, 1, 23);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1649, 191, 191, 2, NULL, 1, 24);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1650, 191, 191, 2, NULL, 1, 25);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1651, 191, 191, 2, NULL, 1, 26);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1652, 191, 191, 2, NULL, 1, 27);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1653, 191, 191, 2, NULL, 1, 28);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1654, 191, 191, 2, NULL, 1, 29);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1655, 191, 191, 2, NULL, 1, 30);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1656, 191, 191, 2, NULL, 1, 31);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1657, 191, 191, 2, NULL, 1, 32);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1658, 191, 191, 2, NULL, 1, 33);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1659, 191, 191, 2, NULL, 1, 34);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1660, 191, 191, 2, NULL, 1, 35);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1661, 191, 191, 2, NULL, 1, 36);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1662, 191, 191, 2, NULL, 1, 37);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1663, 191, 191, 2, NULL, 1, 38);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1664, 191, 191, 2, NULL, 1, 39);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1665, 191, 191, 2, NULL, 1, 40);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1666, 191, 191, 2, NULL, 1, 41);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1667, 191, 191, 2, NULL, 1, 42);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1668, 191, 191, 2, NULL, 1, 43);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1669, 191, 191, 2, NULL, 1, 44);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1670, 191, 191, 2, NULL, 1, 45);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1671, 191, 191, 2, NULL, 1, 46);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1672, 191, 191, 2, NULL, 1, 47);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1673, 191, 191, 2, NULL, 1, 48);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1674, 191, 191, 2, NULL, 1, 49);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1675, 191, 191, 2, NULL, 1, 50);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1676, 191, 191, 2, NULL, 1, 51);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1677, 191, 191, 2, NULL, 1, 52);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1678, 191, 191, 2, NULL, 1, 53);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1679, 191, 191, 2, NULL, 1, 54);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1680, 191, 191, 2, NULL, 1, 55);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1681, 191, 191, 2, NULL, 1, 56);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1682, 191, 191, 2, NULL, 1, 57);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1683, 191, 191, 2, NULL, 1, 58);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1684, 191, 191, 2, NULL, 1, 59);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1685, 191, 191, 2, NULL, 1, 60);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1686, 191, 191, 2, NULL, 1, 61);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1687, 191, 191, 2, NULL, 1, 62);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1688, 191, 191, 2, NULL, 1, 63);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1689, 191, 191, 2, NULL, 1, 64);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1690, 191, 191, 2, NULL, 1, 65);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1691, 191, 191, 2, NULL, 1, 66);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1692, 191, 191, 2, NULL, 1, 67);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1693, 191, 191, 2, NULL, 1, 68);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1694, 191, 191, 2, NULL, 1, 69);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1695, 191, 191, 2, NULL, 1, 70);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1696, 191, 191, 2, NULL, 1, 71);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1697, 191, 191, 2, NULL, 1, 72);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1698, 191, 191, 2, NULL, 1, 73);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1699, 191, 191, 2, NULL, 1, 74);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1700, 191, 191, 2, NULL, 1, 75);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1701, 191, 191, 2, NULL, 1, 76);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1702, 191, 191, 2, NULL, 1, 77);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1703, 191, 191, 2, NULL, 1, 78);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1704, 191, 191, 2, NULL, 1, 79);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1705, 191, 191, 2, NULL, 1, 80);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1706, 191, 191, 2, NULL, 1, 81);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1707, 191, 191, 2, NULL, 1, 82);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1708, 191, 191, 2, NULL, 1, 83);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1709, 191, 191, 2, NULL, 1, 84);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1710, 191, 191, 2, NULL, 1, 85);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1711, 191, 191, 2, NULL, 1, 86);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1712, 191, 191, 2, NULL, 1, 87);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1713, 191, 191, 2, NULL, 1, 88);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1714, 191, 191, 2, NULL, 1, 89);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1715, 191, 191, 2, NULL, 1, 90);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1716, 191, 191, 2, NULL, 1, 91);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1717, 191, 191, 2, NULL, 1, 92);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1718, 191, 191, 2, NULL, 1, 93);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1719, 191, 191, 2, NULL, 1, 94);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1720, 191, 191, 2, NULL, 1, 95);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1721, 191, 191, 2, NULL, 1, 96);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1722, 191, 191, 2, NULL, 1, 97);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1723, 191, 191, 2, NULL, 1, 98);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1724, 191, 191, 2, NULL, 1, 99);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1725, 191, 191, 2, NULL, 1, 100);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1726, 191, 191, 2, NULL, 1, 101);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1727, 191, 191, 2, NULL, 1, 102);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1728, 191, 191, 2, NULL, 1, 103);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1729, 191, 191, 2, NULL, 1, 104);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1730, 191, 191, 2, NULL, 1, 105);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1731, 191, 191, 2, NULL, 1, 106);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1732, 191, 191, 2, NULL, 1, 107);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1733, 191, 191, 2, NULL, 1, 108);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1734, 191, 191, 2, NULL, 1, 109);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1735, 191, 191, 2, NULL, 1, 110);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1736, 191, 191, 2, NULL, 1, 111);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1737, 191, 191, 2, NULL, 1, 112);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1738, 191, 191, 2, NULL, 1, 113);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1739, 191, 191, 2, NULL, 1, 114);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1740, 191, 191, 2, NULL, 1, 115);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1741, 191, 191, 2, NULL, 1, 116);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1742, 191, 191, 2, NULL, 1, 117);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1743, 191, 191, 2, NULL, 1, 118);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1744, 191, 191, 2, NULL, 1, 119);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1745, 191, 191, 2, NULL, 1, 120);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1746, 191, 191, 2, NULL, 1, 121);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1747, 191, 191, 2, NULL, 1, 122);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1748, 191, 191, 2, NULL, 1, 123);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1749, 191, 191, 2, NULL, 1, 124);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1750, 191, 191, 2, NULL, 1, 125);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1751, 191, 191, 2, NULL, 1, 126);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1752, 191, 191, 2, NULL, 1, 127);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1753, 191, 191, 2, NULL, 1, 128);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1754, 191, 191, 2, NULL, 1, 129);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1755, 191, 191, 2, NULL, 1, 130);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1756, 191, 191, 2, NULL, 1, 131);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1757, 191, 191, 2, NULL, 1, 132);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1758, 191, 191, 2, NULL, 1, 133);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1759, 191, 191, 2, NULL, 1, 134);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1760, 191, 191, 2, NULL, 1, 135);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1761, 191, 191, 2, NULL, 1, 136);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1762, 191, 191, 2, NULL, 1, 137);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1763, 191, 191, 2, NULL, 1, 138);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1764, 191, 191, 2, NULL, 1, 139);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1765, 191, 191, 2, NULL, 1, 140);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1766, 191, 191, 2, NULL, 1, 141);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1767, 191, 191, 2, NULL, 1, 142);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1768, 191, 191, 2, NULL, 1, 143);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1769, 191, 191, 2, NULL, 1, 144);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1770, 191, 191, 2, NULL, 1, 145);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1771, 191, 191, 2, NULL, 1, 146);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1772, 191, 191, 2, NULL, 1, 147);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1773, 191, 191, 2, NULL, 1, 148);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1774, 191, 191, 2, NULL, 1, 149);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1775, 191, 191, 2, NULL, 1, 150);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1776, 191, 191, 2, NULL, 1, 151);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1777, 191, 191, 2, NULL, 1, 152);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1778, 191, 191, 2, NULL, 1, 153);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1779, 191, 191, 2, NULL, 1, 154);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1780, 191, 191, 2, NULL, 1, 155);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1781, 191, 191, 2, NULL, 1, 156);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1782, 191, 191, 2, NULL, 1, 157);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1783, 191, 191, 2, NULL, 1, 158);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1784, 191, 191, 2, NULL, 1, 159);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1785, 191, 191, 2, NULL, 1, 160);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1786, 191, 191, 2, NULL, 1, 161);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1787, 191, 191, 2, NULL, 1, 162);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1788, 191, 191, 2, NULL, 1, 163);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1789, 191, 191, 2, NULL, 1, 164);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1790, 191, 191, 2, NULL, 1, 165);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1791, 191, 191, 2, NULL, 1, 166);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1792, 191, 191, 2, NULL, 1, 167);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1793, 191, 191, 2, NULL, 1, 168);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1794, 191, 191, 2, NULL, 1, 169);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1795, 191, 191, 2, NULL, 1, 170);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1796, 191, 191, 2, NULL, 1, 171);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1797, 191, 191, 2, NULL, 1, 172);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1798, 191, 191, 2, NULL, 1, 173);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1799, 191, 191, 2, NULL, 1, 174);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1800, 191, 191, 2, NULL, 1, 175);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1801, 191, 191, 2, NULL, 1, 176);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1802, 191, 191, 2, NULL, 1, 177);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1803, 191, 191, 2, NULL, 1, 178);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1804, 191, 191, 2, NULL, 1, 179);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1805, 191, 191, 2, NULL, 1, 180);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1806, 191, 191, 2, NULL, 1, 181);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1807, 191, 191, 2, NULL, 1, 182);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1808, 191, 191, 2, NULL, 1, 183);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1809, 191, 191, 2, NULL, 1, 184);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1810, 191, 191, 2, NULL, 1, 185);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1811, 191, 191, 2, NULL, 1, 186);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1812, 191, 191, 2, NULL, 1, 187);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1813, 191, 191, 2, NULL, 1, 188);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1814, 191, 191, 2, NULL, 1, 189);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1815, 191, 191, 2, NULL, 1, 190);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1816, 191, 191, 2, NULL, 1, 191);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1817, 191, 191, 2, NULL, 1, 192);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1818, 191, 191, 2, NULL, 1, 193);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1819, 191, 191, 2, NULL, 1, 194);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1820, 191, 191, 2, NULL, 1, 195);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1821, 191, 191, 2, NULL, 1, 196);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1822, 191, 191, 2, NULL, 1, 197);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1823, 191, 191, 2, NULL, 1, 198);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1824, 191, 191, 2, NULL, 1, 199);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1825, 191, 191, 2, NULL, 1, 200);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1826, 191, 191, 2, NULL, 1, 201);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1827, 191, 191, 2, NULL, 1, 202);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1828, 191, 191, 2, NULL, 1, 203);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1829, 191, 191, 2, NULL, 1, 204);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1830, 191, 191, 2, NULL, 1, 205);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1831, 191, 191, 2, NULL, 1, 206);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1832, 191, 191, 2, NULL, 1, 207);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1833, 191, 191, 2, NULL, 1, 208);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1834, 191, 191, 2, NULL, 1, 209);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1835, 191, 191, 2, NULL, 1, 210);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1836, 191, 191, 2, NULL, 1, 211);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1837, 191, 191, 2, NULL, 1, 212);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1838, 191, 191, 2, NULL, 1, 213);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1839, 191, 191, 2, NULL, 1, 214);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1840, 191, 191, 2, NULL, 1, 215);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1841, 191, 191, 2, NULL, 1, 216);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1842, 191, 191, 2, NULL, 1, 217);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1843, 191, 191, 2, NULL, 1, 218);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1844, 191, 191, 2, NULL, 1, 219);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1845, 191, 191, 2, NULL, 1, 220);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1846, 191, 191, 2, NULL, 1, 221);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1847, 191, 191, 2, NULL, 1, 222);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1848, 191, 191, 2, NULL, 1, 223);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1849, 191, 191, 2, NULL, 1, 224);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1850, 191, 191, 2, NULL, 1, 225);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1851, 191, 191, 2, NULL, 1, 226);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1852, 191, 191, 2, NULL, 1, 227);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1853, 191, 191, 2, NULL, 1, 228);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1854, 191, 191, 2, NULL, 1, 229);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1855, 191, 191, 2, NULL, 1, 230);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1856, 191, 191, 2, NULL, 1, 231);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1857, 191, 191, 2, NULL, 1, 232);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1858, 191, 191, 2, NULL, 1, 233);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1859, 191, 191, 2, NULL, 1, 234);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1860, 191, 191, 2, NULL, 1, 235);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1861, 191, 191, 2, NULL, 1, 236);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1862, 191, 191, 2, NULL, 1, 237);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1863, 191, 191, 2, NULL, 1, 238);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1864, 191, 191, 2, NULL, 1, 239);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1865, 191, 191, 2, NULL, 1, 240);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1866, 191, 191, 2, NULL, 1, 241);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1867, 191, 191, 2, NULL, 1, 242);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1868, 191, 191, 2, NULL, 1, 243);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1869, 191, 191, 2, NULL, 1, 244);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1870, 191, 191, 2, NULL, 1, 245);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1871, 191, 191, 2, NULL, 1, 246);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1872, 191, 191, 2, NULL, 1, 247);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1873, 191, 191, 2, NULL, 1, 248);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1874, 191, 191, 2, NULL, 1, 249);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1875, 191, 191, 2, NULL, 1, 250);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1876, 191, 191, 2, NULL, 1, 251);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1877, 191, 191, 2, NULL, 1, 252);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1878, 191, 191, 2, NULL, 1, 253);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1879, 191, 191, 2, NULL, 1, 254);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1880, 191, 191, 2, NULL, 1, 255);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1881, 191, 191, 2, NULL, 1, 256);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1882, 191, 191, 2, NULL, 1, 257);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1883, 191, 191, 2, NULL, 1, 258);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1884, 191, 191, 2, NULL, 1, 259);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1885, 191, 191, 2, NULL, 1, 260);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1886, 191, 191, 2, NULL, 1, 261);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1887, 191, 191, 2, NULL, 1, 262);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1888, 191, 191, 2, NULL, 1, 263);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1889, 191, 191, 2, NULL, 1, 264);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1890, 191, 191, 2, NULL, 1, 265);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1891, 191, 191, 2, NULL, 1, 266);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1892, 191, 191, 2, NULL, 1, 267);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1893, 191, 191, 2, NULL, 1, 268);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1894, 191, 191, 2, NULL, 1, 269);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1895, 191, 191, 2, NULL, 1, 270);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1896, 191, 191, 2, NULL, 1, 271);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1897, 191, 191, 2, NULL, 1, 272);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1898, 191, 191, 2, NULL, 1, 273);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1899, 191, 191, 2, NULL, 1, 274);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1900, 191, 191, 2, NULL, 1, 275);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1901, 191, 191, 2, NULL, 1, 276);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1902, 191, 191, 2, NULL, 1, 277);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1903, 191, 191, 2, NULL, 1, 278);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1904, 191, 191, 2, NULL, 1, 279);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1905, 191, 191, 2, NULL, 1, 280);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1906, 191, 191, 2, NULL, 1, 281);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1907, 191, 191, 2, NULL, 1, 282);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1908, 191, 191, 2, NULL, 1, 283);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1909, 191, 191, 2, NULL, 1, 284);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1910, 191, 191, 2, NULL, 1, 285);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1911, 191, 191, 2, NULL, 1, 286);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1912, 191, 191, 2, NULL, 1, 287);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1913, 191, 191, 2, NULL, 1, 288);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1914, 191, 191, 2, NULL, 1, 289);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1915, 191, 191, 2, NULL, 1, 290);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1916, 191, 191, 2, NULL, 1, 291);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1917, 191, 191, 2, NULL, 1, 292);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1918, 191, 191, 2, NULL, 1, 293);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1919, 191, 191, 2, NULL, 1, 294);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1920, 191, 191, 2, NULL, 1, 295);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1921, 191, 191, 2, NULL, 1, 296);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1922, 191, 191, 2, NULL, 1, 297);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1923, 191, 191, 2, NULL, 1, 298);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1924, 191, 191, 2, NULL, 1, 299);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1925, 191, 191, 2, NULL, 1, 300);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1926, 191, 191, 2, NULL, 1, 301);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1927, 191, 191, 2, NULL, 1, 302);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1928, 191, 191, 2, NULL, 1, 303);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1929, 191, 191, 2, NULL, 1, 304);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1930, 191, 191, 2, NULL, 1, 305);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1931, 191, 191, 2, NULL, 1, 306);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1932, 191, 191, 2, NULL, 1, 307);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1933, 191, 191, 2, NULL, 1, 308);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1934, 191, 191, 2, NULL, 1, 309);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1935, 191, 191, 2, NULL, 1, 310);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1936, 191, 191, 2, NULL, 1, 311);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1937, 191, 191, 2, NULL, 1, 312);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1938, 191, 191, 2, NULL, 1, 313);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1939, 191, 191, 2, NULL, 1, 314);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1940, 191, 191, 2, NULL, 1, 315);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1941, 191, 191, 2, NULL, 1, 316);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1942, 191, 191, 2, NULL, 1, 317);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1943, 191, 191, 2, NULL, 1, 318);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1944, 191, 191, 2, NULL, 1, 319);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1945, 191, 191, 2, NULL, 1, 320);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1946, 191, 191, 2, NULL, 1, 321);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1947, 191, 191, 2, NULL, 1, 322);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1948, 191, 191, 2, NULL, 1, 323);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1949, 191, 191, 2, NULL, 1, 324);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1950, 191, 191, 2, NULL, 1, 325);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1951, 192, 192, 2, NULL, 'INTERNSHIP', 234);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1952, 192, 193, 2, NULL, 'INTERNSHIP', 1);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1953, 192, 193, 2, NULL, 'INTERNSHIP', 2);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1954, 192, 193, 2, NULL, 'INTERNSHIP', 3);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1955, 192, 193, 2, NULL, 'INTERNSHIP', 4);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1956, 192, 193, 2, NULL, 'INTERNSHIP', 5);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1957, 192, 193, 2, NULL, 'INTERNSHIP', 6);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1958, 192, 193, 2, NULL, 'INTERNSHIP', 7);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1959, 192, 193, 2, NULL, 'INTERNSHIP', 8);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1960, 192, 193, 2, NULL, 'INTERNSHIP', 9);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1961, 192, 193, 2, NULL, 'INTERNSHIP', 10);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1962, 192, 193, 2, NULL, 'INTERNSHIP', 11);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1963, 192, 193, 2, NULL, 'INTERNSHIP', 12);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1964, 192, 193, 2, NULL, 'INTERNSHIP', 13);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1965, 192, 193, 2, NULL, 'INTERNSHIP', 14);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1966, 192, 193, 2, NULL, 'INTERNSHIP', 15);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1967, 192, 193, 2, NULL, 'INTERNSHIP', 16);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1968, 192, 193, 2, NULL, 'INTERNSHIP', 17);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1969, 192, 193, 2, NULL, 'INTERNSHIP', 18);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1970, 192, 193, 2, NULL, 'INTERNSHIP', 19);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1971, 192, 193, 2, NULL, 'INTERNSHIP', 20);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1972, 192, 193, 2, NULL, 'INTERNSHIP', 21);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1973, 192, 193, 2, NULL, 'INTERNSHIP', 22);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1974, 192, 193, 2, NULL, 'INTERNSHIP', 23);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1975, 192, 193, 2, NULL, 'INTERNSHIP', 24);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1976, 192, 193, 2, NULL, 'INTERNSHIP', 25);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1977, 192, 193, 2, NULL, 'INTERNSHIP', 26);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1978, 192, 193, 2, NULL, 'INTERNSHIP', 27);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1979, 192, 193, 2, NULL, 'INTERNSHIP', 28);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1980, 192, 193, 2, NULL, 'INTERNSHIP', 29);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1981, 192, 193, 2, NULL, 'INTERNSHIP', 30);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1982, 192, 193, 2, NULL, 'INTERNSHIP', 31);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1983, 192, 193, 2, NULL, 'INTERNSHIP', 32);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1984, 192, 193, 2, NULL, 'INTERNSHIP', 33);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1985, 192, 193, 2, NULL, 'INTERNSHIP', 34);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1986, 192, 193, 2, NULL, 'INTERNSHIP', 35);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1987, 192, 193, 2, NULL, 'INTERNSHIP', 36);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1988, 192, 193, 2, NULL, 'INTERNSHIP', 37);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1989, 192, 193, 2, NULL, 'INTERNSHIP', 38);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1990, 192, 193, 2, NULL, 'INTERNSHIP', 39);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1991, 192, 193, 2, NULL, 'INTERNSHIP', 40);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1992, 192, 193, 2, NULL, 'INTERNSHIP', 41);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1993, 192, 193, 2, NULL, 'INTERNSHIP', 42);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1994, 192, 193, 2, NULL, 'INTERNSHIP', 43);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1995, 192, 193, 2, NULL, 'INTERNSHIP', 44);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1996, 192, 193, 2, NULL, 'INTERNSHIP', 45);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1997, 192, 193, 2, NULL, 'INTERNSHIP', 46);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1998, 192, 193, 2, NULL, 'INTERNSHIP', 47);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (1999, 192, 193, 2, NULL, 'INTERNSHIP', 48);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2000, 192, 193, 2, NULL, 'INTERNSHIP', 49);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2001, 192, 193, 2, NULL, 'INTERNSHIP', 50);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2002, 192, 193, 2, NULL, 'INTERNSHIP', 51);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2003, 192, 193, 2, NULL, 'INTERNSHIP', 52);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2004, 192, 193, 2, NULL, 'INTERNSHIP', 53);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2005, 192, 193, 2, NULL, 'INTERNSHIP', 54);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2006, 192, 193, 2, NULL, 'INTERNSHIP', 55);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2007, 192, 193, 2, NULL, 'INTERNSHIP', 56);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2008, 192, 193, 2, NULL, 'INTERNSHIP', 57);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2009, 192, 193, 2, NULL, 'INTERNSHIP', 58);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2010, 192, 193, 2, NULL, 'INTERNSHIP', 59);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2011, 192, 193, 2, NULL, 'INTERNSHIP', 60);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2012, 192, 193, 2, NULL, 'INTERNSHIP', 61);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2013, 192, 193, 2, NULL, 'INTERNSHIP', 62);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2014, 192, 193, 2, NULL, 'INTERNSHIP', 63);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2015, 192, 193, 2, NULL, 'INTERNSHIP', 64);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2016, 192, 193, 2, NULL, 'INTERNSHIP', 65);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2017, 192, 193, 2, NULL, 'INTERNSHIP', 66);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2018, 192, 193, 2, NULL, 'INTERNSHIP', 67);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2019, 192, 193, 2, NULL, 'INTERNSHIP', 68);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2020, 192, 193, 2, NULL, 'INTERNSHIP', 69);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2021, 192, 193, 2, NULL, 'INTERNSHIP', 70);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2022, 192, 193, 2, NULL, 'INTERNSHIP', 71);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2023, 192, 193, 2, NULL, 'INTERNSHIP', 72);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2024, 192, 193, 2, NULL, 'INTERNSHIP', 73);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2025, 192, 193, 2, NULL, 'INTERNSHIP', 74);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2026, 192, 193, 2, NULL, 'INTERNSHIP', 75);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2027, 192, 193, 2, NULL, 'INTERNSHIP', 76);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2028, 192, 193, 2, NULL, 'INTERNSHIP', 77);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2029, 192, 193, 2, NULL, 'INTERNSHIP', 78);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2030, 192, 193, 2, NULL, 'INTERNSHIP', 79);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2031, 192, 193, 2, NULL, 'INTERNSHIP', 80);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2032, 192, 193, 2, NULL, 'INTERNSHIP', 81);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2033, 192, 193, 2, NULL, 'INTERNSHIP', 82);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2034, 192, 193, 2, NULL, 'INTERNSHIP', 83);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2035, 192, 193, 2, NULL, 'INTERNSHIP', 84);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2036, 192, 193, 2, NULL, 'INTERNSHIP', 85);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2037, 192, 193, 2, NULL, 'INTERNSHIP', 86);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2038, 192, 193, 2, NULL, 'INTERNSHIP', 87);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2039, 192, 193, 2, NULL, 'INTERNSHIP', 88);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2040, 192, 193, 2, NULL, 'INTERNSHIP', 89);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2041, 192, 193, 2, NULL, 'INTERNSHIP', 90);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2042, 192, 193, 2, NULL, 'INTERNSHIP', 91);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2043, 192, 193, 2, NULL, 'INTERNSHIP', 92);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2044, 192, 193, 2, NULL, 'INTERNSHIP', 93);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2045, 192, 193, 2, NULL, 'INTERNSHIP', 94);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2046, 192, 193, 2, NULL, 'INTERNSHIP', 95);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2047, 192, 193, 2, NULL, 'INTERNSHIP', 96);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2048, 192, 193, 2, NULL, 'INTERNSHIP', 97);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2049, 192, 193, 2, NULL, 'INTERNSHIP', 98);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2050, 192, 193, 2, NULL, 'INTERNSHIP', 99);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2051, 192, 193, 2, NULL, 'INTERNSHIP', 100);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2052, 192, 193, 2, NULL, 'INTERNSHIP', 101);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2053, 192, 193, 2, NULL, 'INTERNSHIP', 102);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2054, 192, 193, 2, NULL, 'INTERNSHIP', 103);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2055, 192, 193, 2, NULL, 'INTERNSHIP', 104);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2056, 192, 193, 2, NULL, 'INTERNSHIP', 105);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2057, 192, 193, 2, NULL, 'INTERNSHIP', 106);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2058, 192, 193, 2, NULL, 'INTERNSHIP', 107);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2059, 192, 193, 2, NULL, 'INTERNSHIP', 108);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2060, 192, 193, 2, NULL, 'INTERNSHIP', 109);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2061, 192, 193, 2, NULL, 'INTERNSHIP', 110);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2062, 192, 193, 2, NULL, 'INTERNSHIP', 111);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2063, 192, 193, 2, NULL, 'INTERNSHIP', 112);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2064, 192, 193, 2, NULL, 'INTERNSHIP', 113);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2065, 192, 193, 2, NULL, 'INTERNSHIP', 114);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2066, 192, 193, 2, NULL, 'INTERNSHIP', 115);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2067, 192, 193, 2, NULL, 'INTERNSHIP', 116);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2068, 192, 193, 2, NULL, 'INTERNSHIP', 117);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2069, 192, 193, 2, NULL, 'INTERNSHIP', 118);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2070, 192, 193, 2, NULL, 'INTERNSHIP', 119);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2071, 192, 193, 2, NULL, 'INTERNSHIP', 120);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2072, 192, 193, 2, NULL, 'INTERNSHIP', 121);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2073, 192, 193, 2, NULL, 'INTERNSHIP', 122);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2074, 192, 193, 2, NULL, 'INTERNSHIP', 123);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2075, 192, 193, 2, NULL, 'INTERNSHIP', 124);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2076, 192, 193, 2, NULL, 'INTERNSHIP', 125);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2077, 192, 193, 2, NULL, 'INTERNSHIP', 126);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2078, 192, 193, 2, NULL, 'INTERNSHIP', 127);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2079, 192, 193, 2, NULL, 'INTERNSHIP', 128);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2080, 192, 193, 2, NULL, 'INTERNSHIP', 129);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2081, 192, 193, 2, NULL, 'INTERNSHIP', 130);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2082, 192, 193, 2, NULL, 'INTERNSHIP', 131);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2083, 192, 193, 2, NULL, 'INTERNSHIP', 132);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2084, 192, 193, 2, NULL, 'INTERNSHIP', 133);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2085, 192, 193, 2, NULL, 'INTERNSHIP', 134);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2086, 192, 193, 2, NULL, 'INTERNSHIP', 135);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2087, 192, 193, 2, NULL, 'INTERNSHIP', 136);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2088, 192, 193, 2, NULL, 'INTERNSHIP', 137);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2089, 192, 193, 2, NULL, 'INTERNSHIP', 138);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2090, 192, 193, 2, NULL, 'INTERNSHIP', 139);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2091, 192, 193, 2, NULL, 'INTERNSHIP', 140);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2092, 192, 193, 2, NULL, 'INTERNSHIP', 141);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2093, 192, 193, 2, NULL, 'INTERNSHIP', 142);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2094, 192, 193, 2, NULL, 'INTERNSHIP', 143);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2095, 192, 193, 2, NULL, 'INTERNSHIP', 144);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2096, 192, 193, 2, NULL, 'INTERNSHIP', 145);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2097, 192, 193, 2, NULL, 'INTERNSHIP', 146);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2098, 192, 193, 2, NULL, 'INTERNSHIP', 147);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2099, 192, 193, 2, NULL, 'INTERNSHIP', 148);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2100, 192, 193, 2, NULL, 'INTERNSHIP', 149);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2101, 192, 193, 2, NULL, 'INTERNSHIP', 150);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2102, 192, 193, 2, NULL, 'INTERNSHIP', 151);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2103, 192, 193, 2, NULL, 'INTERNSHIP', 152);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2104, 192, 193, 2, NULL, 'INTERNSHIP', 153);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2105, 192, 193, 2, NULL, 'INTERNSHIP', 154);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2106, 192, 193, 2, NULL, 'INTERNSHIP', 155);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2107, 192, 193, 2, NULL, 'INTERNSHIP', 156);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2108, 192, 193, 2, NULL, 'INTERNSHIP', 157);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2109, 192, 193, 2, NULL, 'INTERNSHIP', 158);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2110, 192, 193, 2, NULL, 'INTERNSHIP', 159);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2111, 192, 193, 2, NULL, 'INTERNSHIP', 160);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2112, 192, 193, 2, NULL, 'INTERNSHIP', 161);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2113, 192, 193, 2, NULL, 'INTERNSHIP', 162);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2114, 192, 193, 2, NULL, 'INTERNSHIP', 163);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2115, 192, 193, 2, NULL, 'INTERNSHIP', 164);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2116, 192, 193, 2, NULL, 'INTERNSHIP', 165);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2117, 192, 193, 2, NULL, 'INTERNSHIP', 166);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2118, 192, 193, 2, NULL, 'INTERNSHIP', 167);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2119, 192, 193, 2, NULL, 'INTERNSHIP', 168);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2120, 192, 193, 2, NULL, 'INTERNSHIP', 169);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2121, 192, 193, 2, NULL, 'INTERNSHIP', 170);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2122, 192, 193, 2, NULL, 'INTERNSHIP', 171);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2123, 192, 193, 2, NULL, 'INTERNSHIP', 172);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2124, 192, 193, 2, NULL, 'INTERNSHIP', 173);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2125, 192, 193, 2, NULL, 'INTERNSHIP', 174);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2126, 192, 193, 2, NULL, 'INTERNSHIP', 175);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2127, 192, 193, 2, NULL, 'INTERNSHIP', 176);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2128, 192, 193, 2, NULL, 'INTERNSHIP', 177);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2129, 192, 193, 2, NULL, 'INTERNSHIP', 178);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2130, 192, 193, 2, NULL, 'INTERNSHIP', 179);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2131, 192, 193, 2, NULL, 'INTERNSHIP', 180);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2132, 192, 193, 2, NULL, 'INTERNSHIP', 181);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2133, 192, 193, 2, NULL, 'INTERNSHIP', 182);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2134, 192, 193, 2, NULL, 'INTERNSHIP', 183);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2135, 192, 193, 2, NULL, 'INTERNSHIP', 184);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2136, 192, 193, 2, NULL, 'INTERNSHIP', 185);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2137, 192, 193, 2, NULL, 'INTERNSHIP', 186);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2138, 192, 193, 2, NULL, 'INTERNSHIP', 187);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2139, 192, 193, 2, NULL, 'INTERNSHIP', 188);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2140, 192, 193, 2, NULL, 'INTERNSHIP', 189);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2141, 192, 193, 2, NULL, 'INTERNSHIP', 190);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2142, 192, 193, 2, NULL, 'INTERNSHIP', 191);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2143, 192, 193, 2, NULL, 'INTERNSHIP', 192);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2144, 192, 193, 2, NULL, 'INTERNSHIP', 193);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2145, 192, 193, 2, NULL, 'INTERNSHIP', 194);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2146, 192, 193, 2, NULL, 'INTERNSHIP', 195);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2147, 192, 193, 2, NULL, 'INTERNSHIP', 196);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2148, 192, 193, 2, NULL, 'INTERNSHIP', 197);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2149, 192, 193, 2, NULL, 'INTERNSHIP', 198);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2150, 192, 193, 2, NULL, 'INTERNSHIP', 199);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2151, 192, 193, 2, NULL, 'INTERNSHIP', 200);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2152, 192, 193, 2, NULL, 'INTERNSHIP', 201);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2153, 192, 193, 2, NULL, 'INTERNSHIP', 202);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2154, 192, 193, 2, NULL, 'INTERNSHIP', 203);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2155, 192, 193, 2, NULL, 'INTERNSHIP', 204);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2156, 192, 193, 2, NULL, 'INTERNSHIP', 205);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2157, 192, 193, 2, NULL, 'INTERNSHIP', 206);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2158, 192, 193, 2, NULL, 'INTERNSHIP', 207);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2159, 192, 193, 2, NULL, 'INTERNSHIP', 208);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2160, 192, 193, 2, NULL, 'INTERNSHIP', 209);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2161, 192, 193, 2, NULL, 'INTERNSHIP', 210);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2162, 192, 193, 2, NULL, 'INTERNSHIP', 211);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2163, 192, 193, 2, NULL, 'INTERNSHIP', 212);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2164, 192, 193, 2, NULL, 'INTERNSHIP', 213);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2165, 192, 193, 2, NULL, 'INTERNSHIP', 214);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2166, 192, 193, 2, NULL, 'INTERNSHIP', 215);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2167, 192, 193, 2, NULL, 'INTERNSHIP', 216);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2168, 192, 193, 2, NULL, 'INTERNSHIP', 217);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2169, 192, 193, 2, NULL, 'INTERNSHIP', 218);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2170, 192, 193, 2, NULL, 'INTERNSHIP', 219);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2171, 192, 193, 2, NULL, 'INTERNSHIP', 220);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2172, 192, 193, 2, NULL, 'INTERNSHIP', 221);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2173, 192, 193, 2, NULL, 'INTERNSHIP', 222);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2174, 192, 193, 2, NULL, 'INTERNSHIP', 223);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2175, 192, 193, 2, NULL, 'INTERNSHIP', 224);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2176, 192, 193, 2, NULL, 'INTERNSHIP', 225);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2177, 192, 193, 2, NULL, 'INTERNSHIP', 226);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2178, 192, 193, 2, NULL, 'INTERNSHIP', 227);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2179, 192, 193, 2, NULL, 'INTERNSHIP', 228);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2180, 192, 193, 2, NULL, 'INTERNSHIP', 229);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2181, 192, 193, 2, NULL, 'INTERNSHIP', 230);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2182, 192, 193, 2, NULL, 'INTERNSHIP', 231);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2183, 192, 193, 2, NULL, 'INTERNSHIP', 232);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2184, 192, 193, 2, NULL, 'INTERNSHIP', 233);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2185, 192, 194, 2, NULL, 'INTERNSHIP', 235);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2186, 192, 194, 2, NULL, 'INTERNSHIP', 236);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2187, 192, 194, 2, NULL, 'INTERNSHIP', 237);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2188, 192, 194, 2, NULL, 'INTERNSHIP', 238);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2189, 192, 194, 2, NULL, 'INTERNSHIP', 239);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2190, 192, 194, 2, NULL, 'INTERNSHIP', 240);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2191, 192, 194, 2, NULL, 'INTERNSHIP', 241);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2192, 192, 194, 2, NULL, 'INTERNSHIP', 242);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2193, 192, 194, 2, NULL, 'INTERNSHIP', 243);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2194, 192, 194, 2, NULL, 'INTERNSHIP', 244);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2195, 192, 194, 2, NULL, 'INTERNSHIP', 245);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2196, 192, 194, 2, NULL, 'INTERNSHIP', 246);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2197, 192, 194, 2, NULL, 'INTERNSHIP', 247);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2198, 192, 194, 2, NULL, 'INTERNSHIP', 248);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2199, 192, 194, 2, NULL, 'INTERNSHIP', 249);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2200, 192, 194, 2, NULL, 'INTERNSHIP', 250);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2201, 192, 194, 2, NULL, 'INTERNSHIP', 251);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2202, 192, 194, 2, NULL, 'INTERNSHIP', 252);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2203, 192, 194, 2, NULL, 'INTERNSHIP', 253);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2204, 192, 194, 2, NULL, 'INTERNSHIP', 254);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2205, 192, 194, 2, NULL, 'INTERNSHIP', 255);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2206, 192, 194, 2, NULL, 'INTERNSHIP', 256);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2207, 192, 194, 2, NULL, 'INTERNSHIP', 257);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2208, 192, 194, 2, NULL, 'INTERNSHIP', 258);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2209, 192, 194, 2, NULL, 'INTERNSHIP', 259);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2210, 192, 194, 2, NULL, 'INTERNSHIP', 260);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2211, 192, 194, 2, NULL, 'INTERNSHIP', 261);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2212, 192, 194, 2, NULL, 'INTERNSHIP', 262);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2213, 192, 194, 2, NULL, 'INTERNSHIP', 263);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2214, 192, 194, 2, NULL, 'INTERNSHIP', 264);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2215, 192, 194, 2, NULL, 'INTERNSHIP', 265);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2216, 192, 194, 2, NULL, 'INTERNSHIP', 266);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2217, 192, 194, 2, NULL, 'INTERNSHIP', 267);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2218, 192, 194, 2, NULL, 'INTERNSHIP', 268);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2219, 192, 194, 2, NULL, 'INTERNSHIP', 269);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2220, 192, 194, 2, NULL, 'INTERNSHIP', 270);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2221, 192, 194, 2, NULL, 'INTERNSHIP', 271);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2222, 192, 194, 2, NULL, 'INTERNSHIP', 272);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2223, 192, 194, 2, NULL, 'INTERNSHIP', 273);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2224, 192, 194, 2, NULL, 'INTERNSHIP', 274);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2225, 192, 194, 2, NULL, 'INTERNSHIP', 275);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2226, 192, 194, 2, NULL, 'INTERNSHIP', 276);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2227, 192, 194, 2, NULL, 'INTERNSHIP', 277);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2228, 192, 194, 2, NULL, 'INTERNSHIP', 278);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2229, 192, 194, 2, NULL, 'INTERNSHIP', 279);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2230, 192, 194, 2, NULL, 'INTERNSHIP', 280);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2231, 192, 194, 2, NULL, 'INTERNSHIP', 281);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2232, 192, 194, 2, NULL, 'INTERNSHIP', 282);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2233, 192, 194, 2, NULL, 'INTERNSHIP', 283);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2234, 192, 194, 2, NULL, 'INTERNSHIP', 284);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2235, 192, 194, 2, NULL, 'INTERNSHIP', 285);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2236, 192, 194, 2, NULL, 'INTERNSHIP', 286);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2237, 192, 194, 2, NULL, 'INTERNSHIP', 287);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2238, 192, 194, 2, NULL, 'INTERNSHIP', 288);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2239, 192, 194, 2, NULL, 'INTERNSHIP', 289);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2240, 192, 194, 2, NULL, 'INTERNSHIP', 290);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2241, 192, 194, 2, NULL, 'INTERNSHIP', 291);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2242, 192, 194, 2, NULL, 'INTERNSHIP', 292);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2243, 192, 194, 2, NULL, 'INTERNSHIP', 293);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2244, 192, 194, 2, NULL, 'INTERNSHIP', 294);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2245, 192, 194, 2, NULL, 'INTERNSHIP', 295);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2246, 192, 194, 2, NULL, 'INTERNSHIP', 296);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2247, 192, 194, 2, NULL, 'INTERNSHIP', 297);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2248, 192, 194, 2, NULL, 'INTERNSHIP', 298);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2249, 192, 194, 2, NULL, 'INTERNSHIP', 299);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2250, 192, 194, 2, NULL, 'INTERNSHIP', 300);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2251, 192, 194, 2, NULL, 'INTERNSHIP', 301);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2252, 192, 194, 2, NULL, 'INTERNSHIP', 302);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2253, 192, 194, 2, NULL, 'INTERNSHIP', 303);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2254, 192, 194, 2, NULL, 'INTERNSHIP', 304);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2255, 192, 194, 2, NULL, 'INTERNSHIP', 305);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2256, 192, 194, 2, NULL, 'INTERNSHIP', 306);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2257, 192, 194, 2, NULL, 'INTERNSHIP', 307);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2258, 192, 194, 2, NULL, 'INTERNSHIP', 308);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2259, 192, 194, 2, NULL, 'INTERNSHIP', 309);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2260, 192, 194, 2, NULL, 'INTERNSHIP', 310);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2261, 192, 194, 2, NULL, 'INTERNSHIP', 311);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2262, 192, 194, 2, NULL, 'INTERNSHIP', 312);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2263, 192, 194, 2, NULL, 'INTERNSHIP', 313);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2264, 192, 194, 2, NULL, 'INTERNSHIP', 314);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2265, 192, 194, 2, NULL, 'INTERNSHIP', 315);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2266, 192, 194, 2, NULL, 'INTERNSHIP', 316);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2267, 192, 194, 2, NULL, 'INTERNSHIP', 317);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2268, 192, 194, 2, NULL, 'INTERNSHIP', 318);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2269, 192, 194, 2, NULL, 'INTERNSHIP', 319);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2270, 192, 194, 2, NULL, 'INTERNSHIP', 320);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2271, 192, 194, 2, NULL, 'INTERNSHIP', 321);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2272, 192, 194, 2, NULL, 'INTERNSHIP', 322);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2273, 192, 194, 2, NULL, 'INTERNSHIP', 323);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2274, 192, 194, 2, NULL, 'INTERNSHIP', 324);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2275, 192, 194, 2, NULL, 'INTERNSHIP', 325);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2276, 195, 195, 2, NULL, 'REMOTE', 277);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2277, 195, 196, 2, NULL, 'ONSITE', 1);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2278, 195, 196, 2, NULL, 'ONSITE', 2);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2279, 195, 196, 2, NULL, 'ONSITE', 6);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2280, 195, 196, 2, NULL, 'ONSITE', 7);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2281, 195, 196, 2, NULL, 'ONSITE', 8);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2282, 195, 196, 2, NULL, 'ONSITE', 9);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2283, 195, 196, 2, NULL, 'ONSITE', 12);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2284, 195, 196, 2, NULL, 'ONSITE', 13);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2285, 195, 196, 2, NULL, 'ONSITE', 16);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2286, 195, 196, 2, NULL, 'ONSITE', 24);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2287, 195, 196, 2, NULL, 'ONSITE', 25);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2288, 195, 196, 2, NULL, 'ONSITE', 26);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2289, 195, 196, 2, NULL, 'ONSITE', 28);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2290, 195, 196, 2, NULL, 'ONSITE', 34);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2291, 195, 196, 2, NULL, 'ONSITE', 39);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2292, 195, 196, 2, NULL, 'ONSITE', 42);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2293, 195, 196, 2, NULL, 'ONSITE', 50);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2294, 195, 196, 2, NULL, 'ONSITE', 51);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2295, 195, 196, 2, NULL, 'ONSITE', 52);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2296, 195, 196, 2, NULL, 'ONSITE', 53);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2297, 195, 196, 2, NULL, 'ONSITE', 54);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2298, 195, 196, 2, NULL, 'ONSITE', 56);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2299, 195, 196, 2, NULL, 'ONSITE', 57);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2300, 195, 196, 2, NULL, 'ONSITE', 58);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2301, 195, 196, 2, NULL, 'ONSITE', 60);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2302, 195, 196, 2, NULL, 'ONSITE', 61);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2303, 195, 196, 2, NULL, 'ONSITE', 62);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2304, 195, 196, 2, NULL, 'ONSITE', 63);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2305, 195, 196, 2, NULL, 'ONSITE', 64);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2306, 195, 196, 2, NULL, 'ONSITE', 65);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2307, 195, 196, 2, NULL, 'ONSITE', 66);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2308, 195, 196, 2, NULL, 'ONSITE', 67);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2309, 195, 196, 2, NULL, 'ONSITE', 68);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2310, 195, 196, 2, NULL, 'ONSITE', 71);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2311, 195, 196, 2, NULL, 'ONSITE', 72);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2312, 195, 196, 2, NULL, 'ONSITE', 73);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2313, 195, 196, 2, NULL, 'ONSITE', 74);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2314, 195, 196, 2, NULL, 'ONSITE', 75);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2315, 195, 196, 2, NULL, 'ONSITE', 77);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2316, 195, 196, 2, NULL, 'ONSITE', 78);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2317, 195, 196, 2, NULL, 'ONSITE', 79);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2318, 195, 196, 2, NULL, 'ONSITE', 80);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2319, 195, 196, 2, NULL, 'ONSITE', 81);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2320, 195, 196, 2, NULL, 'ONSITE', 82);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2321, 195, 196, 2, NULL, 'ONSITE', 83);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2322, 195, 196, 2, NULL, 'ONSITE', 84);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2323, 195, 196, 2, NULL, 'ONSITE', 85);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2324, 195, 196, 2, NULL, 'ONSITE', 86);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2325, 195, 196, 2, NULL, 'ONSITE', 87);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2326, 195, 196, 2, NULL, 'ONSITE', 88);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2327, 195, 196, 2, NULL, 'ONSITE', 89);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2328, 195, 196, 2, NULL, 'ONSITE', 90);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2329, 195, 196, 2, NULL, 'ONSITE', 91);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2330, 195, 196, 2, NULL, 'ONSITE', 93);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2331, 195, 196, 2, NULL, 'ONSITE', 94);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2332, 195, 196, 2, NULL, 'ONSITE', 105);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2333, 195, 196, 2, NULL, 'ONSITE', 106);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2334, 195, 196, 2, NULL, 'ONSITE', 107);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2335, 195, 196, 2, NULL, 'ONSITE', 116);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2336, 195, 196, 2, NULL, 'ONSITE', 117);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2337, 195, 196, 2, NULL, 'ONSITE', 121);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2338, 195, 196, 2, NULL, 'ONSITE', 125);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2339, 195, 196, 2, NULL, 'ONSITE', 126);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2340, 195, 196, 2, NULL, 'ONSITE', 127);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2341, 195, 196, 2, NULL, 'ONSITE', 129);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2342, 195, 196, 2, NULL, 'ONSITE', 132);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2343, 195, 196, 2, NULL, 'ONSITE', 134);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2344, 195, 196, 2, NULL, 'ONSITE', 135);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2345, 195, 196, 2, NULL, 'ONSITE', 136);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2346, 195, 196, 2, NULL, 'ONSITE', 137);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2347, 195, 196, 2, NULL, 'ONSITE', 138);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2348, 195, 196, 2, NULL, 'ONSITE', 142);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2349, 195, 196, 2, NULL, 'ONSITE', 144);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2350, 195, 196, 2, NULL, 'ONSITE', 145);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2351, 195, 196, 2, NULL, 'ONSITE', 146);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2352, 195, 196, 2, NULL, 'ONSITE', 148);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2353, 195, 196, 2, NULL, 'ONSITE', 149);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2354, 195, 196, 2, NULL, 'ONSITE', 152);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2355, 195, 196, 2, NULL, 'ONSITE', 153);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2356, 195, 196, 2, NULL, 'ONSITE', 154);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2357, 195, 196, 2, NULL, 'ONSITE', 156);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2358, 195, 196, 2, NULL, 'ONSITE', 157);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2359, 195, 196, 2, NULL, 'ONSITE', 159);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2360, 195, 196, 2, NULL, 'ONSITE', 160);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2361, 195, 196, 2, NULL, 'ONSITE', 167);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2362, 195, 196, 2, NULL, 'ONSITE', 168);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2363, 195, 196, 2, NULL, 'ONSITE', 174);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2364, 195, 196, 2, NULL, 'ONSITE', 176);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2365, 195, 196, 2, NULL, 'ONSITE', 177);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2366, 195, 196, 2, NULL, 'ONSITE', 179);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2367, 195, 196, 2, NULL, 'ONSITE', 180);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2368, 195, 196, 2, NULL, 'ONSITE', 181);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2369, 195, 196, 2, NULL, 'ONSITE', 187);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2370, 195, 196, 2, NULL, 'ONSITE', 188);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2371, 195, 196, 2, NULL, 'ONSITE', 189);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2372, 195, 196, 2, NULL, 'ONSITE', 193);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2373, 195, 196, 2, NULL, 'ONSITE', 195);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2374, 195, 196, 2, NULL, 'ONSITE', 196);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2375, 195, 196, 2, NULL, 'ONSITE', 197);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2376, 195, 196, 2, NULL, 'ONSITE', 198);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2377, 195, 196, 2, NULL, 'ONSITE', 200);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2378, 195, 196, 2, NULL, 'ONSITE', 201);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2379, 195, 196, 2, NULL, 'ONSITE', 202);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2380, 195, 196, 2, NULL, 'ONSITE', 203);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2381, 195, 196, 2, NULL, 'ONSITE', 213);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2382, 195, 196, 2, NULL, 'ONSITE', 214);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2383, 195, 196, 2, NULL, 'ONSITE', 215);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2384, 195, 196, 2, NULL, 'ONSITE', 216);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2385, 195, 196, 2, NULL, 'ONSITE', 217);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2386, 195, 196, 2, NULL, 'ONSITE', 218);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2387, 195, 196, 2, NULL, 'ONSITE', 219);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2388, 195, 196, 2, NULL, 'ONSITE', 220);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2389, 195, 196, 2, NULL, 'ONSITE', 222);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2390, 195, 196, 2, NULL, 'ONSITE', 223);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2391, 195, 196, 2, NULL, 'ONSITE', 231);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2392, 195, 196, 2, NULL, 'ONSITE', 237);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2393, 195, 196, 2, NULL, 'ONSITE', 239);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2394, 195, 196, 2, NULL, 'ONSITE', 241);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2395, 195, 196, 2, NULL, 'ONSITE', 243);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2396, 195, 196, 2, NULL, 'ONSITE', 252);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2397, 195, 196, 2, NULL, 'ONSITE', 254);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2398, 195, 196, 2, NULL, 'ONSITE', 256);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2399, 195, 196, 2, NULL, 'ONSITE', 257);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2400, 195, 196, 2, NULL, 'ONSITE', 263);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2401, 195, 196, 2, NULL, 'ONSITE', 264);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2402, 195, 196, 2, NULL, 'ONSITE', 265);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2403, 195, 196, 2, NULL, 'ONSITE', 266);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2404, 195, 196, 2, NULL, 'ONSITE', 271);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2405, 195, 196, 2, NULL, 'ONSITE', 272);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2406, 195, 196, 2, NULL, 'ONSITE', 276);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2407, 195, 196, 2, NULL, 'ONSITE', 278);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2408, 195, 196, 2, NULL, 'ONSITE', 279);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2409, 195, 196, 2, NULL, 'ONSITE', 280);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2410, 195, 196, 2, NULL, 'ONSITE', 281);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2411, 195, 196, 2, NULL, 'ONSITE', 283);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2412, 195, 196, 2, NULL, 'ONSITE', 284);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2413, 195, 196, 2, NULL, 'ONSITE', 288);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2414, 195, 196, 2, NULL, 'ONSITE', 289);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2415, 195, 196, 2, NULL, 'ONSITE', 291);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2416, 195, 196, 2, NULL, 'ONSITE', 293);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2417, 195, 196, 2, NULL, 'ONSITE', 297);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2418, 195, 196, 2, NULL, 'ONSITE', 298);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2419, 195, 196, 2, NULL, 'ONSITE', 300);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2420, 195, 196, 2, NULL, 'ONSITE', 301);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2421, 195, 196, 2, NULL, 'ONSITE', 303);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2422, 195, 196, 2, NULL, 'ONSITE', 304);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2423, 195, 196, 2, NULL, 'ONSITE', 306);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2424, 195, 196, 2, NULL, 'ONSITE', 312);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2425, 195, 196, 2, NULL, 'ONSITE', 313);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2426, 195, 196, 2, NULL, 'ONSITE', 318);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2427, 195, 196, 2, NULL, 'ONSITE', 319);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2428, 195, 196, 2, NULL, 'ONSITE', 320);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2429, 195, 196, 2, NULL, 'ONSITE', 321);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2430, 195, 196, 2, NULL, 'ONSITE', 323);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2431, 195, 196, 2, NULL, 'REMOTE', 3);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2432, 195, 196, 2, NULL, 'REMOTE', 4);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2433, 195, 196, 2, NULL, 'REMOTE', 5);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2434, 195, 196, 2, NULL, 'REMOTE', 10);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2435, 195, 196, 2, NULL, 'REMOTE', 11);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2436, 195, 196, 2, NULL, 'REMOTE', 14);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2437, 195, 196, 2, NULL, 'REMOTE', 15);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2438, 195, 196, 2, NULL, 'REMOTE', 17);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2439, 195, 196, 2, NULL, 'REMOTE', 18);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2440, 195, 196, 2, NULL, 'REMOTE', 19);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2441, 195, 196, 2, NULL, 'REMOTE', 20);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2442, 195, 196, 2, NULL, 'REMOTE', 21);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2443, 195, 196, 2, NULL, 'REMOTE', 22);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2444, 195, 196, 2, NULL, 'REMOTE', 23);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2445, 195, 196, 2, NULL, 'REMOTE', 27);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2446, 195, 196, 2, NULL, 'REMOTE', 29);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2447, 195, 196, 2, NULL, 'REMOTE', 30);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2448, 195, 196, 2, NULL, 'REMOTE', 31);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2449, 195, 196, 2, NULL, 'REMOTE', 32);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2450, 195, 196, 2, NULL, 'REMOTE', 33);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2451, 195, 196, 2, NULL, 'REMOTE', 35);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2452, 195, 196, 2, NULL, 'REMOTE', 36);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2453, 195, 196, 2, NULL, 'REMOTE', 37);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2454, 195, 196, 2, NULL, 'REMOTE', 38);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2455, 195, 196, 2, NULL, 'REMOTE', 40);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2456, 195, 196, 2, NULL, 'REMOTE', 41);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2457, 195, 196, 2, NULL, 'REMOTE', 43);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2458, 195, 196, 2, NULL, 'REMOTE', 44);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2459, 195, 196, 2, NULL, 'REMOTE', 45);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2460, 195, 196, 2, NULL, 'REMOTE', 46);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2461, 195, 196, 2, NULL, 'REMOTE', 47);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2462, 195, 196, 2, NULL, 'REMOTE', 48);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2463, 195, 196, 2, NULL, 'REMOTE', 49);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2464, 195, 196, 2, NULL, 'REMOTE', 55);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2465, 195, 196, 2, NULL, 'REMOTE', 59);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2466, 195, 196, 2, NULL, 'REMOTE', 69);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2467, 195, 196, 2, NULL, 'REMOTE', 70);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2468, 195, 196, 2, NULL, 'REMOTE', 76);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2469, 195, 196, 2, NULL, 'REMOTE', 92);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2470, 195, 196, 2, NULL, 'REMOTE', 95);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2471, 195, 196, 2, NULL, 'REMOTE', 96);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2472, 195, 196, 2, NULL, 'REMOTE', 97);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2473, 195, 196, 2, NULL, 'REMOTE', 98);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2474, 195, 196, 2, NULL, 'REMOTE', 99);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2475, 195, 196, 2, NULL, 'REMOTE', 100);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2476, 195, 196, 2, NULL, 'REMOTE', 101);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2477, 195, 196, 2, NULL, 'REMOTE', 102);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2478, 195, 196, 2, NULL, 'REMOTE', 103);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2479, 195, 196, 2, NULL, 'REMOTE', 104);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2480, 195, 196, 2, NULL, 'REMOTE', 108);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2481, 195, 196, 2, NULL, 'REMOTE', 109);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2482, 195, 196, 2, NULL, 'REMOTE', 110);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2483, 195, 196, 2, NULL, 'REMOTE', 111);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2484, 195, 196, 2, NULL, 'REMOTE', 112);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2485, 195, 196, 2, NULL, 'REMOTE', 113);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2486, 195, 196, 2, NULL, 'REMOTE', 114);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2487, 195, 196, 2, NULL, 'REMOTE', 115);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2488, 195, 196, 2, NULL, 'REMOTE', 118);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2489, 195, 196, 2, NULL, 'REMOTE', 119);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2490, 195, 196, 2, NULL, 'REMOTE', 120);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2491, 195, 196, 2, NULL, 'REMOTE', 122);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2492, 195, 196, 2, NULL, 'REMOTE', 123);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2493, 195, 196, 2, NULL, 'REMOTE', 124);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2494, 195, 196, 2, NULL, 'REMOTE', 128);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2495, 195, 196, 2, NULL, 'REMOTE', 130);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2496, 195, 196, 2, NULL, 'REMOTE', 131);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2497, 195, 196, 2, NULL, 'REMOTE', 133);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2498, 195, 196, 2, NULL, 'REMOTE', 139);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2499, 195, 196, 2, NULL, 'REMOTE', 140);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2500, 195, 196, 2, NULL, 'REMOTE', 141);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2501, 195, 196, 2, NULL, 'REMOTE', 143);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2502, 195, 196, 2, NULL, 'REMOTE', 147);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2503, 195, 196, 2, NULL, 'REMOTE', 150);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2504, 195, 196, 2, NULL, 'REMOTE', 151);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2505, 195, 196, 2, NULL, 'REMOTE', 155);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2506, 195, 196, 2, NULL, 'REMOTE', 158);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2507, 195, 196, 2, NULL, 'REMOTE', 161);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2508, 195, 196, 2, NULL, 'REMOTE', 162);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2509, 195, 196, 2, NULL, 'REMOTE', 163);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2510, 195, 196, 2, NULL, 'REMOTE', 164);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2511, 195, 196, 2, NULL, 'REMOTE', 165);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2512, 195, 196, 2, NULL, 'REMOTE', 166);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2513, 195, 196, 2, NULL, 'REMOTE', 169);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2514, 195, 196, 2, NULL, 'REMOTE', 170);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2515, 195, 196, 2, NULL, 'REMOTE', 171);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2516, 195, 196, 2, NULL, 'REMOTE', 172);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2517, 195, 196, 2, NULL, 'REMOTE', 173);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2518, 195, 196, 2, NULL, 'REMOTE', 175);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2519, 195, 196, 2, NULL, 'REMOTE', 178);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2520, 195, 196, 2, NULL, 'REMOTE', 182);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2521, 195, 196, 2, NULL, 'REMOTE', 183);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2522, 195, 196, 2, NULL, 'REMOTE', 184);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2523, 195, 196, 2, NULL, 'REMOTE', 185);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2524, 195, 196, 2, NULL, 'REMOTE', 186);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2525, 195, 196, 2, NULL, 'REMOTE', 190);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2526, 195, 196, 2, NULL, 'REMOTE', 191);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2527, 195, 196, 2, NULL, 'REMOTE', 192);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2528, 195, 196, 2, NULL, 'REMOTE', 194);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2529, 195, 196, 2, NULL, 'REMOTE', 199);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2530, 195, 196, 2, NULL, 'REMOTE', 204);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2531, 195, 196, 2, NULL, 'REMOTE', 205);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2532, 195, 196, 2, NULL, 'REMOTE', 206);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2533, 195, 196, 2, NULL, 'REMOTE', 207);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2534, 195, 196, 2, NULL, 'REMOTE', 208);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2535, 195, 196, 2, NULL, 'REMOTE', 209);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2536, 195, 196, 2, NULL, 'REMOTE', 210);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2537, 195, 196, 2, NULL, 'REMOTE', 211);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2538, 195, 196, 2, NULL, 'REMOTE', 212);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2539, 195, 196, 2, NULL, 'REMOTE', 221);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2540, 195, 196, 2, NULL, 'REMOTE', 224);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2541, 195, 196, 2, NULL, 'REMOTE', 225);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2542, 195, 196, 2, NULL, 'REMOTE', 226);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2543, 195, 196, 2, NULL, 'REMOTE', 227);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2544, 195, 196, 2, NULL, 'REMOTE', 228);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2545, 195, 196, 2, NULL, 'REMOTE', 229);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2546, 195, 196, 2, NULL, 'REMOTE', 230);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2547, 195, 196, 2, NULL, 'REMOTE', 232);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2548, 195, 196, 2, NULL, 'REMOTE', 233);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2549, 195, 196, 2, NULL, 'REMOTE', 234);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2550, 195, 196, 2, NULL, 'REMOTE', 235);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2551, 195, 196, 2, NULL, 'REMOTE', 236);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2552, 195, 196, 2, NULL, 'REMOTE', 238);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2553, 195, 196, 2, NULL, 'REMOTE', 240);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2554, 195, 196, 2, NULL, 'REMOTE', 242);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2555, 195, 196, 2, NULL, 'REMOTE', 244);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2556, 195, 196, 2, NULL, 'REMOTE', 245);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2557, 195, 196, 2, NULL, 'REMOTE', 246);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2558, 195, 196, 2, NULL, 'REMOTE', 247);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2559, 195, 196, 2, NULL, 'REMOTE', 248);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2560, 195, 196, 2, NULL, 'REMOTE', 249);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2561, 195, 196, 2, NULL, 'REMOTE', 250);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2562, 195, 196, 2, NULL, 'REMOTE', 251);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2563, 195, 196, 2, NULL, 'REMOTE', 253);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2564, 195, 196, 2, NULL, 'REMOTE', 255);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2565, 195, 196, 2, NULL, 'REMOTE', 258);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2566, 195, 196, 2, NULL, 'REMOTE', 259);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2567, 195, 196, 2, NULL, 'REMOTE', 260);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2568, 195, 196, 2, NULL, 'REMOTE', 261);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2569, 195, 196, 2, NULL, 'REMOTE', 262);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2570, 195, 196, 2, NULL, 'REMOTE', 267);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2571, 195, 196, 2, NULL, 'REMOTE', 268);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2572, 195, 196, 2, NULL, 'REMOTE', 269);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2573, 195, 196, 2, NULL, 'REMOTE', 270);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2574, 195, 196, 2, NULL, 'REMOTE', 273);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2575, 195, 196, 2, NULL, 'REMOTE', 274);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2576, 195, 196, 2, NULL, 'REMOTE', 275);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2577, 195, 197, 2, NULL, 'REMOTE', 282);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2578, 195, 197, 2, NULL, 'REMOTE', 285);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2579, 195, 197, 2, NULL, 'REMOTE', 286);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2580, 195, 197, 2, NULL, 'REMOTE', 287);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2581, 195, 197, 2, NULL, 'REMOTE', 290);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2582, 195, 197, 2, NULL, 'REMOTE', 292);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2583, 195, 197, 2, NULL, 'REMOTE', 294);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2584, 195, 197, 2, NULL, 'REMOTE', 295);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2585, 195, 197, 2, NULL, 'REMOTE', 296);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2586, 195, 197, 2, NULL, 'REMOTE', 299);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2587, 195, 197, 2, NULL, 'REMOTE', 302);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2588, 195, 197, 2, NULL, 'REMOTE', 305);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2589, 195, 197, 2, NULL, 'REMOTE', 307);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2590, 195, 197, 2, NULL, 'REMOTE', 308);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2591, 195, 197, 2, NULL, 'REMOTE', 309);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2592, 195, 197, 2, NULL, 'REMOTE', 310);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2593, 195, 197, 2, NULL, 'REMOTE', 311);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2594, 195, 197, 2, NULL, 'REMOTE', 314);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2595, 195, 197, 2, NULL, 'REMOTE', 315);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2596, 195, 197, 2, NULL, 'REMOTE', 316);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2597, 195, 197, 2, NULL, 'REMOTE', 317);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2598, 195, 197, 2, NULL, 'REMOTE', 322);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2599, 195, 197, 2, NULL, 'REMOTE', 324);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2600, 195, 197, 2, NULL, 'REMOTE', 325);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2601, 198, 198, 2, NULL, '2026-04-03 15:48:16.147708', 124);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2602, 198, 198, 2, NULL, '2026-04-12 16:11:13.812560', 244);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2603, 198, 199, 2, NULL, '2026-04-03 15:48:16.147195', 1);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2604, 198, 199, 2, NULL, '2026-04-03 15:48:16.147210', 2);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2605, 198, 199, 2, NULL, '2026-04-03 15:48:16.147221', 3);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2606, 198, 199, 2, NULL, '2026-04-03 15:48:16.147226', 4);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2607, 198, 199, 2, NULL, '2026-04-03 15:48:16.147231', 5);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2608, 198, 199, 2, NULL, '2026-04-03 15:48:16.147235', 6);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2609, 198, 199, 2, NULL, '2026-04-03 15:48:16.147241', 7);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2610, 198, 199, 2, NULL, '2026-04-03 15:48:16.147246', 8);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2611, 198, 199, 2, NULL, '2026-04-03 15:48:16.147251', 9);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2612, 198, 199, 2, NULL, '2026-04-03 15:48:16.147255', 10);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2613, 198, 199, 2, NULL, '2026-04-03 15:48:16.147259', 11);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2614, 198, 199, 2, NULL, '2026-04-03 15:48:16.147263', 12);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2615, 198, 199, 2, NULL, '2026-04-03 15:48:16.147267', 13);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2616, 198, 199, 2, NULL, '2026-04-03 15:48:16.147272', 14);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2617, 198, 199, 2, NULL, '2026-04-03 15:48:16.147276', 15);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2618, 198, 199, 2, NULL, '2026-04-03 15:48:16.147280', 16);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2619, 198, 199, 2, NULL, '2026-04-03 15:48:16.147284', 17);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2620, 198, 199, 2, NULL, '2026-04-03 15:48:16.147288', 18);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2621, 198, 199, 2, NULL, '2026-04-03 15:48:16.147292', 19);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2622, 198, 199, 2, NULL, '2026-04-03 15:48:16.147296', 20);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2623, 198, 199, 2, NULL, '2026-04-03 15:48:16.147300', 21);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2624, 198, 199, 2, NULL, '2026-04-03 15:48:16.147304', 22);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2625, 198, 199, 2, NULL, '2026-04-03 15:48:16.147308', 23);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2626, 198, 199, 2, NULL, '2026-04-03 15:48:16.147312', 24);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2627, 198, 199, 2, NULL, '2026-04-03 15:48:16.147317', 25);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2628, 198, 199, 2, NULL, '2026-04-03 15:48:16.147321', 26);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2629, 198, 199, 2, NULL, '2026-04-03 15:48:16.147325', 27);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2630, 198, 199, 2, NULL, '2026-04-03 15:48:16.147329', 28);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2631, 198, 199, 2, NULL, '2026-04-03 15:48:16.147333', 29);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2632, 198, 199, 2, NULL, '2026-04-03 15:48:16.147337', 30);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2633, 198, 199, 2, NULL, '2026-04-03 15:48:16.147341', 31);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2634, 198, 199, 2, NULL, '2026-04-03 15:48:16.147345', 32);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2635, 198, 199, 2, NULL, '2026-04-03 15:48:16.147349', 33);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2636, 198, 199, 2, NULL, '2026-04-03 15:48:16.147352', 34);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2637, 198, 199, 2, NULL, '2026-04-03 15:48:16.147356', 35);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2638, 198, 199, 2, NULL, '2026-04-03 15:48:16.147360', 36);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2639, 198, 199, 2, NULL, '2026-04-03 15:48:16.147364', 37);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2640, 198, 199, 2, NULL, '2026-04-03 15:48:16.147368', 38);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2641, 198, 199, 2, NULL, '2026-04-03 15:48:16.147372', 39);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2642, 198, 199, 2, NULL, '2026-04-03 15:48:16.147376', 40);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2643, 198, 199, 2, NULL, '2026-04-03 15:48:16.147379', 41);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2644, 198, 199, 2, NULL, '2026-04-03 15:48:16.147383', 42);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2645, 198, 199, 2, NULL, '2026-04-03 15:48:16.147387', 43);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2646, 198, 199, 2, NULL, '2026-04-03 15:48:16.147391', 44);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2647, 198, 199, 2, NULL, '2026-04-03 15:48:16.147395', 45);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2648, 198, 199, 2, NULL, '2026-04-03 15:48:16.147399', 46);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2649, 198, 199, 2, NULL, '2026-04-03 15:48:16.147402', 47);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2650, 198, 199, 2, NULL, '2026-04-03 15:48:16.147406', 48);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2651, 198, 199, 2, NULL, '2026-04-03 15:48:16.147410', 49);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2652, 198, 199, 2, NULL, '2026-04-03 15:48:16.147414', 50);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2653, 198, 199, 2, NULL, '2026-04-03 15:48:16.147418', 51);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2654, 198, 199, 2, NULL, '2026-04-03 15:48:16.147423', 52);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2655, 198, 199, 2, NULL, '2026-04-03 15:48:16.147427', 53);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2656, 198, 199, 2, NULL, '2026-04-03 15:48:16.147431', 54);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2657, 198, 199, 2, NULL, '2026-04-03 15:48:16.147435', 55);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2658, 198, 199, 2, NULL, '2026-04-03 15:48:16.147439', 56);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2659, 198, 199, 2, NULL, '2026-04-03 15:48:16.147443', 57);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2660, 198, 199, 2, NULL, '2026-04-03 15:48:16.147447', 58);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2661, 198, 199, 2, NULL, '2026-04-03 15:48:16.147451', 59);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2662, 198, 199, 2, NULL, '2026-04-03 15:48:16.147455', 60);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2663, 198, 199, 2, NULL, '2026-04-03 15:48:16.147459', 61);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2664, 198, 199, 2, NULL, '2026-04-03 15:48:16.147463', 62);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2665, 198, 199, 2, NULL, '2026-04-03 15:48:16.147467', 63);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2666, 198, 199, 2, NULL, '2026-04-03 15:48:16.147471', 64);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2667, 198, 199, 2, NULL, '2026-04-03 15:48:16.147475', 65);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2668, 198, 199, 2, NULL, '2026-04-03 15:48:16.147479', 66);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2669, 198, 199, 2, NULL, '2026-04-03 15:48:16.147482', 67);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2670, 198, 199, 2, NULL, '2026-04-03 15:48:16.147486', 68);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2671, 198, 199, 2, NULL, '2026-04-03 15:48:16.147490', 69);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2672, 198, 199, 2, NULL, '2026-04-03 15:48:16.147494', 70);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2673, 198, 199, 2, NULL, '2026-04-03 15:48:16.147498', 71);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2674, 198, 199, 2, NULL, '2026-04-03 15:48:16.147502', 72);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2675, 198, 199, 2, NULL, '2026-04-03 15:48:16.147506', 73);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2676, 198, 199, 2, NULL, '2026-04-03 15:48:16.147509', 74);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2677, 198, 199, 2, NULL, '2026-04-03 15:48:16.147513', 75);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2678, 198, 199, 2, NULL, '2026-04-03 15:48:16.147517', 76);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2679, 198, 199, 2, NULL, '2026-04-03 15:48:16.147521', 77);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2680, 198, 199, 2, NULL, '2026-04-03 15:48:16.147525', 78);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2681, 198, 199, 2, NULL, '2026-04-03 15:48:16.147529', 79);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2682, 198, 199, 2, NULL, '2026-04-03 15:48:16.147533', 80);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2683, 198, 199, 2, NULL, '2026-04-03 15:48:16.147536', 81);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2684, 198, 199, 2, NULL, '2026-04-03 15:48:16.147540', 82);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2685, 198, 199, 2, NULL, '2026-04-03 15:48:16.147544', 83);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2686, 198, 199, 2, NULL, '2026-04-03 15:48:16.147550', 84);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2687, 198, 199, 2, NULL, '2026-04-03 15:48:16.147554', 85);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2688, 198, 199, 2, NULL, '2026-04-03 15:48:16.147558', 86);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2689, 198, 199, 2, NULL, '2026-04-03 15:48:16.147562', 87);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2690, 198, 199, 2, NULL, '2026-04-03 15:48:16.147566', 88);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2691, 198, 199, 2, NULL, '2026-04-03 15:48:16.147570', 89);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2692, 198, 199, 2, NULL, '2026-04-03 15:48:16.147574', 90);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2693, 198, 199, 2, NULL, '2026-04-03 15:48:16.147578', 91);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2694, 198, 199, 2, NULL, '2026-04-03 15:48:16.147582', 92);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2695, 198, 199, 2, NULL, '2026-04-03 15:48:16.147586', 93);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2696, 198, 199, 2, NULL, '2026-04-03 15:48:16.147589', 94);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2697, 198, 199, 2, NULL, '2026-04-03 15:48:16.147593', 95);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2698, 198, 199, 2, NULL, '2026-04-03 15:48:16.147597', 96);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2699, 198, 199, 2, NULL, '2026-04-03 15:48:16.147601', 97);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2700, 198, 199, 2, NULL, '2026-04-03 15:48:16.147605', 98);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2701, 198, 199, 2, NULL, '2026-04-03 15:48:16.147609', 99);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2702, 198, 199, 2, NULL, '2026-04-03 15:48:16.147612', 100);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2703, 198, 199, 2, NULL, '2026-04-03 15:48:16.147616', 101);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2704, 198, 199, 2, NULL, '2026-04-03 15:48:16.147620', 102);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2705, 198, 199, 2, NULL, '2026-04-03 15:48:16.147624', 103);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2706, 198, 199, 2, NULL, '2026-04-03 15:48:16.147628', 104);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2707, 198, 199, 2, NULL, '2026-04-03 15:48:16.147632', 105);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2708, 198, 199, 2, NULL, '2026-04-03 15:48:16.147636', 106);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2709, 198, 199, 2, NULL, '2026-04-03 15:48:16.147639', 107);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2710, 198, 199, 2, NULL, '2026-04-03 15:48:16.147643', 108);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2711, 198, 199, 2, NULL, '2026-04-03 15:48:16.147647', 109);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2712, 198, 199, 2, NULL, '2026-04-03 15:48:16.147651', 110);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2713, 198, 199, 2, NULL, '2026-04-03 15:48:16.147655', 111);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2714, 198, 199, 2, NULL, '2026-04-03 15:48:16.147659', 112);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2715, 198, 199, 2, NULL, '2026-04-03 15:48:16.147663', 113);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2716, 198, 199, 2, NULL, '2026-04-03 15:48:16.147667', 114);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2717, 198, 199, 2, NULL, '2026-04-03 15:48:16.147671', 115);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2718, 198, 199, 2, NULL, '2026-04-03 15:48:16.147675', 116);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2719, 198, 199, 2, NULL, '2026-04-03 15:48:16.147680', 117);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2720, 198, 199, 2, NULL, '2026-04-03 15:48:16.147683', 118);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2721, 198, 199, 2, NULL, '2026-04-03 15:48:16.147688', 119);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2722, 198, 199, 2, NULL, '2026-04-03 15:48:16.147692', 120);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2723, 198, 199, 2, NULL, '2026-04-03 15:48:16.147696', 121);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2724, 198, 199, 2, NULL, '2026-04-03 15:48:16.147700', 122);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2725, 198, 199, 2, NULL, '2026-04-03 15:48:16.147704', 123);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2726, 198, 200, 2, NULL, '2026-04-03 15:51:29.210596', 125);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2727, 198, 200, 2, NULL, '2026-04-03 15:51:29.210604', 126);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2728, 198, 200, 2, NULL, '2026-04-04 02:34:55.838193', 127);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2729, 198, 200, 2, NULL, '2026-04-04 02:34:55.838205', 128);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2730, 198, 200, 2, NULL, '2026-04-04 02:34:55.838211', 129);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2731, 198, 200, 2, NULL, '2026-04-04 02:34:55.838220', 130);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2732, 198, 200, 2, NULL, '2026-04-04 02:34:55.838225', 131);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2733, 198, 200, 2, NULL, '2026-04-04 02:34:55.838229', 132);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2734, 198, 200, 2, NULL, '2026-04-04 02:34:55.838233', 133);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2735, 198, 200, 2, NULL, '2026-04-04 02:34:55.838242', 134);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2736, 198, 200, 2, NULL, '2026-04-04 05:42:04.363537', 135);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2737, 198, 200, 2, NULL, '2026-04-04 05:42:04.363546', 136);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2738, 198, 200, 2, NULL, '2026-04-04 05:42:04.363550', 137);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2739, 198, 200, 2, NULL, '2026-04-04 05:42:04.363559', 138);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2740, 198, 200, 2, NULL, '2026-04-04 05:51:27.826735', 139);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2741, 198, 200, 2, NULL, '2026-04-04 05:51:27.826746', 140);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2742, 198, 200, 2, NULL, '2026-04-04 05:51:27.826750', 141);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2743, 198, 200, 2, NULL, '2026-04-04 09:08:08.593229', 142);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2744, 198, 200, 2, NULL, '2026-04-04 09:08:08.593241', 143);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2745, 198, 200, 2, NULL, '2026-04-04 09:08:08.593246', 144);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2746, 198, 200, 2, NULL, '2026-04-04 09:08:08.593250', 145);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2747, 198, 200, 2, NULL, '2026-04-04 09:27:05.155140', 146);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2748, 198, 200, 2, NULL, '2026-04-04 09:53:27.313339', 147);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2749, 198, 200, 2, NULL, '2026-04-04 09:53:27.313351', 148);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2750, 198, 200, 2, NULL, '2026-04-04 12:02:11.318884', 149);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2751, 198, 200, 2, NULL, '2026-04-04 12:02:11.318895', 150);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2752, 198, 200, 2, NULL, '2026-04-04 12:02:11.318902', 151);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2753, 198, 200, 2, NULL, '2026-04-04 12:02:11.318914', 152);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2754, 198, 200, 2, NULL, '2026-04-04 12:02:11.318921', 153);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2755, 198, 200, 2, NULL, '2026-04-04 13:48:53.326992', 154);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2756, 198, 200, 2, NULL, '2026-04-04 16:38:39.798586', 155);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2757, 198, 200, 2, NULL, '2026-04-04 16:38:39.798601', 156);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2758, 198, 200, 2, NULL, '2026-04-05 03:51:48.513136', 157);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2759, 198, 200, 2, NULL, '2026-04-05 03:51:48.513147', 158);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2760, 198, 200, 2, NULL, '2026-04-05 03:51:48.513152', 159);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2761, 198, 200, 2, NULL, '2026-04-05 03:51:48.513157', 160);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2762, 198, 200, 2, NULL, '2026-04-05 03:51:48.513162', 161);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2763, 198, 200, 2, NULL, '2026-04-05 03:51:48.513166', 162);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2764, 198, 200, 2, NULL, '2026-04-05 03:51:48.513170', 163);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2765, 198, 200, 2, NULL, '2026-04-05 03:51:48.513175', 164);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2766, 198, 200, 2, NULL, '2026-04-05 03:51:48.513179', 165);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2767, 198, 200, 2, NULL, '2026-04-05 03:51:48.513184', 166);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2768, 198, 200, 2, NULL, '2026-04-05 03:51:48.513188', 167);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2769, 198, 200, 2, NULL, '2026-04-05 03:51:48.513192', 168);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2770, 198, 200, 2, NULL, '2026-04-05 03:51:48.513197', 169);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2771, 198, 200, 2, NULL, '2026-04-05 08:53:35.162389', 170);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2772, 198, 200, 2, NULL, '2026-04-05 08:53:35.162393', 171);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2773, 198, 200, 2, NULL, '2026-04-05 08:53:35.162395', 172);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2774, 198, 200, 2, NULL, '2026-04-05 08:53:35.162397', 173);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2775, 198, 200, 2, NULL, '2026-04-05 08:53:35.162400', 174);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2776, 198, 200, 2, NULL, '2026-04-05 08:53:35.162402', 175);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2777, 198, 200, 2, NULL, '2026-04-05 13:13:06.892122', 176);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2778, 198, 200, 2, NULL, '2026-04-05 13:13:06.892149', 177);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2779, 198, 200, 2, NULL, '2026-04-05 13:13:06.892157', 178);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2780, 198, 200, 2, NULL, '2026-04-05 13:13:06.892163', 179);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2781, 198, 200, 2, NULL, '2026-04-05 13:13:06.892168', 180);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2782, 198, 200, 2, NULL, '2026-04-06 07:18:34.310912', 181);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2783, 198, 200, 2, NULL, '2026-04-06 07:18:34.310921', 182);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2784, 198, 200, 2, NULL, '2026-04-06 07:18:34.310925', 183);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2785, 198, 200, 2, NULL, '2026-04-06 07:18:34.310928', 184);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2786, 198, 200, 2, NULL, '2026-04-06 07:18:34.310931', 185);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2787, 198, 200, 2, NULL, '2026-04-06 07:18:34.310934', 186);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2788, 198, 200, 2, NULL, '2026-04-06 07:18:34.310937', 187);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2789, 198, 200, 2, NULL, '2026-04-06 07:18:34.310940', 188);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2790, 198, 200, 2, NULL, '2026-04-06 07:18:34.310943', 189);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2791, 198, 200, 2, NULL, '2026-04-06 07:18:34.310946', 190);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2792, 198, 200, 2, NULL, '2026-04-06 07:18:34.310949', 191);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2793, 198, 200, 2, NULL, '2026-04-06 07:18:34.310952', 192);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2794, 198, 200, 2, NULL, '2026-04-06 07:18:34.310954', 193);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2795, 198, 200, 2, NULL, '2026-04-06 07:18:34.310958', 194);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2796, 198, 200, 2, NULL, '2026-04-06 07:18:34.310960', 195);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2797, 198, 200, 2, NULL, '2026-04-06 07:18:34.310963', 196);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2798, 198, 200, 2, NULL, '2026-04-06 07:18:34.310966', 197);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2799, 198, 200, 2, NULL, '2026-04-06 07:18:34.310968', 198);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2800, 198, 200, 2, NULL, '2026-04-06 07:18:34.310971', 199);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2801, 198, 200, 2, NULL, '2026-04-06 07:18:34.310974', 200);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2802, 198, 200, 2, NULL, '2026-04-12 16:11:13.812442', 201);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2803, 198, 200, 2, NULL, '2026-04-12 16:11:13.812448', 202);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2804, 198, 200, 2, NULL, '2026-04-12 16:11:13.812451', 203);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2805, 198, 200, 2, NULL, '2026-04-12 16:11:13.812453', 204);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2806, 198, 200, 2, NULL, '2026-04-12 16:11:13.812456', 205);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2807, 198, 200, 2, NULL, '2026-04-12 16:11:13.812459', 206);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2808, 198, 200, 2, NULL, '2026-04-12 16:11:13.812461', 207);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2809, 198, 200, 2, NULL, '2026-04-12 16:11:13.812464', 208);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2810, 198, 200, 2, NULL, '2026-04-12 16:11:13.812467', 209);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2811, 198, 200, 2, NULL, '2026-04-12 16:11:13.812469', 210);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2812, 198, 200, 2, NULL, '2026-04-12 16:11:13.812472', 211);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2813, 198, 200, 2, NULL, '2026-04-12 16:11:13.812474', 212);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2814, 198, 200, 2, NULL, '2026-04-12 16:11:13.812477', 213);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2815, 198, 200, 2, NULL, '2026-04-12 16:11:13.812480', 214);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2816, 198, 200, 2, NULL, '2026-04-12 16:11:13.812484', 215);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2817, 198, 200, 2, NULL, '2026-04-12 16:11:13.812486', 216);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2818, 198, 200, 2, NULL, '2026-04-12 16:11:13.812489', 217);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2819, 198, 200, 2, NULL, '2026-04-12 16:11:13.812492', 218);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2820, 198, 200, 2, NULL, '2026-04-12 16:11:13.812495', 219);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2821, 198, 200, 2, NULL, '2026-04-12 16:11:13.812498', 220);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2822, 198, 200, 2, NULL, '2026-04-12 16:11:13.812500', 221);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2823, 198, 200, 2, NULL, '2026-04-12 16:11:13.812504', 222);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2824, 198, 200, 2, NULL, '2026-04-12 16:11:13.812506', 223);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2825, 198, 200, 2, NULL, '2026-04-12 16:11:13.812509', 224);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2826, 198, 200, 2, NULL, '2026-04-12 16:11:13.812512', 225);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2827, 198, 200, 2, NULL, '2026-04-12 16:11:13.812514', 226);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2828, 198, 200, 2, NULL, '2026-04-12 16:11:13.812517', 227);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2829, 198, 200, 2, NULL, '2026-04-12 16:11:13.812519', 228);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2830, 198, 200, 2, NULL, '2026-04-12 16:11:13.812521', 229);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2831, 198, 200, 2, NULL, '2026-04-12 16:11:13.812524', 230);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2832, 198, 200, 2, NULL, '2026-04-12 16:11:13.812526', 231);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2833, 198, 200, 2, NULL, '2026-04-12 16:11:13.812529', 232);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2834, 198, 200, 2, NULL, '2026-04-12 16:11:13.812531', 233);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2835, 198, 200, 2, NULL, '2026-04-12 16:11:13.812534', 234);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2836, 198, 200, 2, NULL, '2026-04-12 16:11:13.812536', 235);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2837, 198, 200, 2, NULL, '2026-04-12 16:11:13.812539', 236);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2838, 198, 200, 2, NULL, '2026-04-12 16:11:13.812541', 237);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2839, 198, 200, 2, NULL, '2026-04-12 16:11:13.812544', 238);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2840, 198, 200, 2, NULL, '2026-04-12 16:11:13.812546', 239);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2841, 198, 200, 2, NULL, '2026-04-12 16:11:13.812549', 240);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2842, 198, 200, 2, NULL, '2026-04-12 16:11:13.812551', 241);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2843, 198, 200, 2, NULL, '2026-04-12 16:11:13.812554', 242);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2844, 198, 200, 2, NULL, '2026-04-12 16:11:13.812557', 243);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2845, 198, 201, 2, NULL, '2026-04-12 16:11:13.812563', 245);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2846, 198, 201, 2, NULL, '2026-04-12 16:11:13.812575', 246);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2847, 198, 201, 2, NULL, '2026-04-12 16:11:13.812578', 247);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2848, 198, 201, 2, NULL, '2026-04-12 16:11:13.812581', 248);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2849, 198, 201, 2, NULL, '2026-04-12 16:11:13.812584', 249);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2850, 198, 201, 2, NULL, '2026-04-12 16:11:13.812586', 250);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2851, 198, 201, 2, NULL, '2026-04-12 16:11:13.812588', 251);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2852, 198, 201, 2, NULL, '2026-04-12 16:11:13.812591', 252);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2853, 198, 201, 2, NULL, '2026-04-12 16:11:13.812593', 253);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2854, 198, 201, 2, NULL, '2026-04-12 16:11:13.812596', 254);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2855, 198, 201, 2, NULL, '2026-04-12 16:11:13.812598', 255);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2856, 198, 201, 2, NULL, '2026-04-12 16:11:13.812601', 256);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2857, 198, 201, 2, NULL, '2026-04-12 16:11:13.812603', 257);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2858, 198, 201, 2, NULL, '2026-04-12 16:11:13.812605', 258);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2859, 198, 201, 2, NULL, '2026-04-12 16:11:13.812608', 259);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2860, 198, 201, 2, NULL, '2026-04-12 16:11:13.812610', 260);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2861, 198, 201, 2, NULL, '2026-04-12 16:11:13.812613', 261);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2862, 198, 201, 2, NULL, '2026-04-12 16:11:13.812615', 262);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2863, 198, 201, 2, NULL, '2026-04-12 16:11:13.812618', 263);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2864, 198, 201, 2, NULL, '2026-04-12 16:11:13.812620', 264);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2865, 198, 201, 2, NULL, '2026-04-12 16:11:13.812623', 265);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2866, 198, 201, 2, NULL, '2026-04-12 16:11:13.812625', 266);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2867, 198, 201, 2, NULL, '2026-04-12 16:11:13.812628', 267);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2868, 198, 201, 2, NULL, '2026-04-12 16:11:13.812630', 268);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2869, 198, 201, 2, NULL, '2026-04-12 16:11:13.812632', 269);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2870, 198, 201, 2, NULL, '2026-04-12 16:11:13.812635', 270);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2871, 198, 201, 2, NULL, '2026-04-12 16:11:13.812637', 271);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2872, 198, 201, 2, NULL, '2026-04-12 16:11:13.812640', 272);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2873, 198, 201, 2, NULL, '2026-04-12 16:11:13.812642', 273);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2874, 198, 201, 2, NULL, '2026-04-12 16:11:13.812645', 274);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2875, 198, 201, 2, NULL, '2026-04-12 16:11:13.812647', 275);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2876, 198, 201, 2, NULL, '2026-04-12 16:11:13.812650', 276);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2877, 198, 201, 2, NULL, '2026-04-12 16:11:13.812652', 277);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2878, 198, 201, 2, NULL, '2026-04-12 16:11:13.812654', 278);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2879, 198, 201, 2, NULL, '2026-04-12 16:11:13.812657', 279);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2880, 198, 201, 2, NULL, '2026-04-12 16:11:13.812659', 280);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2881, 198, 201, 2, NULL, '2026-04-12 16:11:13.812662', 281);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2882, 198, 201, 2, NULL, '2026-04-14 15:50:14.975803', 282);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2883, 198, 201, 2, NULL, '2026-04-14 15:50:14.975815', 283);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2884, 198, 201, 2, NULL, '2026-04-14 15:50:14.975821', 284);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2885, 198, 201, 2, NULL, '2026-04-14 15:50:14.975832', 285);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2886, 198, 201, 2, NULL, '2026-04-14 15:50:14.975838', 286);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2887, 198, 201, 2, NULL, '2026-04-14 15:50:14.975843', 287);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2888, 198, 201, 2, NULL, '2026-04-14 15:50:14.975848', 288);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2889, 198, 201, 2, NULL, '2026-04-14 15:50:14.975856', 289);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2890, 198, 201, 2, NULL, '2026-04-14 15:50:14.975861', 290);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2891, 198, 201, 2, NULL, '2026-04-14 15:50:14.975866', 291);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2892, 198, 201, 2, NULL, '2026-04-14 15:50:14.975871', 292);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2893, 198, 201, 2, NULL, '2026-04-14 15:50:14.975876', 293);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2894, 198, 201, 2, NULL, '2026-04-14 15:50:14.975881', 294);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2895, 198, 201, 2, NULL, '2026-04-14 15:50:14.975886', 295);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2896, 198, 201, 2, NULL, '2026-04-14 15:50:14.975891', 296);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2897, 198, 201, 2, NULL, '2026-04-14 15:50:14.975896', 297);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2898, 198, 201, 2, NULL, '2026-04-14 15:50:14.975901', 298);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2899, 198, 201, 2, NULL, '2026-04-14 15:50:14.975906', 299);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2900, 198, 201, 2, NULL, '2026-04-14 15:50:14.975911', 300);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2901, 198, 201, 2, NULL, '2026-04-14 15:50:14.975916', 301);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2902, 198, 201, 2, NULL, '2026-04-14 15:50:14.975920', 302);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2903, 198, 201, 2, NULL, '2026-04-14 15:50:14.975925', 303);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2904, 198, 201, 2, NULL, '2026-04-14 15:50:14.975930', 304);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2905, 198, 201, 2, NULL, '2026-04-14 15:50:14.975935', 305);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2906, 198, 201, 2, NULL, '2026-04-14 15:50:14.975940', 306);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2907, 198, 201, 2, NULL, '2026-04-14 17:12:36.880105', 307);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2908, 198, 201, 2, NULL, '2026-04-14 17:12:36.880115', 308);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2909, 198, 201, 2, NULL, '2026-04-14 17:12:36.880131', 309);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2910, 198, 201, 2, NULL, '2026-04-14 17:12:36.880138', 310);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2911, 198, 201, 2, NULL, '2026-04-14 17:12:36.880145', 311);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2912, 198, 201, 2, NULL, '2026-04-14 17:12:36.880151', 312);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2913, 198, 201, 2, NULL, '2026-04-14 17:12:36.880159', 313);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2914, 198, 201, 2, NULL, '2026-04-14 17:12:36.880165', 314);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2915, 198, 201, 2, NULL, '2026-04-14 17:12:36.880171', 315);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2916, 198, 201, 2, NULL, '2026-04-14 17:12:36.880176', 316);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2917, 198, 201, 2, NULL, '2026-04-14 17:12:36.880182', 317);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2918, 198, 201, 2, NULL, '2026-04-15 04:18:45.936275', 318);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2919, 198, 201, 2, NULL, '2026-04-15 04:18:45.936287', 319);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2920, 198, 201, 2, NULL, '2026-04-15 04:18:45.936294', 320);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2921, 198, 201, 2, NULL, '2026-04-15 04:18:45.936300', 321);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2922, 198, 201, 2, NULL, '2026-04-15 04:18:45.936306', 322);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2923, 198, 201, 2, NULL, '2026-04-15 04:18:45.936311', 323);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2924, 198, 201, 2, NULL, '2026-04-15 04:18:45.936317', 324);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2925, 198, 201, 2, NULL, '2026-04-15 04:18:45.936323', 325);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2926, 202, 202, 2, NULL, NULL, 1);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2927, 202, 202, 2, NULL, NULL, 2);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2928, 202, 202, 2, NULL, NULL, 3);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2929, 202, 202, 2, NULL, NULL, 4);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2930, 202, 202, 2, NULL, NULL, 5);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2931, 202, 202, 2, NULL, NULL, 6);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2932, 202, 202, 2, NULL, NULL, 7);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2933, 202, 202, 2, NULL, NULL, 8);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2934, 202, 202, 2, NULL, NULL, 9);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2935, 202, 202, 2, NULL, NULL, 10);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2936, 202, 202, 2, NULL, NULL, 11);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2937, 202, 202, 2, NULL, NULL, 12);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2938, 202, 202, 2, NULL, NULL, 13);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2939, 202, 202, 2, NULL, NULL, 14);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2940, 202, 202, 2, NULL, NULL, 15);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2941, 202, 202, 2, NULL, NULL, 16);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2942, 202, 202, 2, NULL, NULL, 17);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2943, 202, 202, 2, NULL, NULL, 18);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2944, 202, 202, 2, NULL, NULL, 19);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2945, 202, 202, 2, NULL, NULL, 20);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2946, 202, 202, 2, NULL, NULL, 21);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2947, 202, 202, 2, NULL, NULL, 22);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2948, 202, 202, 2, NULL, NULL, 23);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2949, 202, 202, 2, NULL, NULL, 24);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2950, 202, 202, 2, NULL, NULL, 25);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2951, 202, 202, 2, NULL, NULL, 26);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2952, 202, 202, 2, NULL, NULL, 27);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2953, 202, 202, 2, NULL, NULL, 28);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2954, 202, 202, 2, NULL, NULL, 29);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2955, 202, 202, 2, NULL, NULL, 30);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2956, 202, 202, 2, NULL, NULL, 31);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2957, 202, 202, 2, NULL, NULL, 32);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2958, 202, 202, 2, NULL, NULL, 33);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2959, 202, 202, 2, NULL, NULL, 34);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2960, 202, 202, 2, NULL, NULL, 35);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2961, 202, 202, 2, NULL, NULL, 36);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2962, 202, 202, 2, NULL, NULL, 37);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2963, 202, 202, 2, NULL, NULL, 38);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2964, 202, 202, 2, NULL, NULL, 39);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2965, 202, 202, 2, NULL, NULL, 40);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2966, 202, 202, 2, NULL, NULL, 41);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2967, 202, 202, 2, NULL, NULL, 42);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2968, 202, 202, 2, NULL, NULL, 43);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2969, 202, 202, 2, NULL, NULL, 44);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2970, 202, 202, 2, NULL, NULL, 45);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2971, 202, 202, 2, NULL, NULL, 46);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2972, 202, 202, 2, NULL, NULL, 47);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2973, 202, 202, 2, NULL, NULL, 48);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2974, 202, 202, 2, NULL, NULL, 49);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2975, 202, 202, 2, NULL, NULL, 50);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2976, 202, 202, 2, NULL, NULL, 51);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2977, 202, 202, 2, NULL, NULL, 52);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2978, 202, 202, 2, NULL, NULL, 53);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2979, 202, 202, 2, NULL, NULL, 54);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2980, 202, 202, 2, NULL, NULL, 55);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2981, 202, 202, 2, NULL, NULL, 56);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2982, 202, 202, 2, NULL, NULL, 57);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2983, 202, 202, 2, NULL, NULL, 58);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2984, 202, 202, 2, NULL, NULL, 59);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2985, 202, 202, 2, NULL, NULL, 60);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2986, 202, 202, 2, NULL, NULL, 61);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2987, 202, 202, 2, NULL, NULL, 62);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2988, 202, 202, 2, NULL, NULL, 63);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2989, 202, 202, 2, NULL, NULL, 64);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2990, 202, 202, 2, NULL, NULL, 65);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2991, 202, 202, 2, NULL, NULL, 66);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2992, 202, 202, 2, NULL, NULL, 67);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2993, 202, 202, 2, NULL, NULL, 68);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2994, 202, 202, 2, NULL, NULL, 69);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2995, 202, 202, 2, NULL, NULL, 70);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2996, 202, 202, 2, NULL, NULL, 71);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2997, 202, 202, 2, NULL, NULL, 72);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2998, 202, 202, 2, NULL, NULL, 73);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (2999, 202, 202, 2, NULL, NULL, 74);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3000, 202, 202, 2, NULL, NULL, 75);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3001, 202, 202, 2, NULL, NULL, 76);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3002, 202, 202, 2, NULL, NULL, 77);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3003, 202, 202, 2, NULL, NULL, 78);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3004, 202, 202, 2, NULL, NULL, 79);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3005, 202, 202, 2, NULL, NULL, 80);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3006, 202, 202, 2, NULL, NULL, 81);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3007, 202, 202, 2, NULL, NULL, 82);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3008, 202, 202, 2, NULL, NULL, 83);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3009, 202, 202, 2, NULL, NULL, 84);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3010, 202, 202, 2, NULL, NULL, 85);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3011, 202, 202, 2, NULL, NULL, 86);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3012, 202, 202, 2, NULL, NULL, 87);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3013, 202, 202, 2, NULL, NULL, 88);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3014, 202, 202, 2, NULL, NULL, 89);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3015, 202, 202, 2, NULL, NULL, 90);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3016, 202, 202, 2, NULL, NULL, 91);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3017, 202, 202, 2, NULL, NULL, 92);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3018, 202, 202, 2, NULL, NULL, 93);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3019, 202, 202, 2, NULL, NULL, 94);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3020, 202, 202, 2, NULL, NULL, 95);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3021, 202, 202, 2, NULL, NULL, 96);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3022, 202, 202, 2, NULL, NULL, 97);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3023, 202, 202, 2, NULL, NULL, 98);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3024, 202, 202, 2, NULL, NULL, 99);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3025, 202, 202, 2, NULL, NULL, 100);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3026, 202, 202, 2, NULL, NULL, 101);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3027, 202, 202, 2, NULL, NULL, 102);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3028, 202, 202, 2, NULL, NULL, 103);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3029, 202, 202, 2, NULL, NULL, 104);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3030, 202, 202, 2, NULL, NULL, 105);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3031, 202, 202, 2, NULL, NULL, 106);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3032, 202, 202, 2, NULL, NULL, 107);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3033, 202, 202, 2, NULL, NULL, 108);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3034, 202, 202, 2, NULL, NULL, 109);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3035, 202, 202, 2, NULL, NULL, 110);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3036, 202, 202, 2, NULL, NULL, 111);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3037, 202, 202, 2, NULL, NULL, 112);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3038, 202, 202, 2, NULL, NULL, 113);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3039, 202, 202, 2, NULL, NULL, 114);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3040, 202, 202, 2, NULL, NULL, 115);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3041, 202, 202, 2, NULL, NULL, 116);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3042, 202, 202, 2, NULL, NULL, 117);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3043, 202, 202, 2, NULL, NULL, 118);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3044, 202, 202, 2, NULL, NULL, 119);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3045, 202, 202, 2, NULL, NULL, 120);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3046, 202, 202, 2, NULL, NULL, 121);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3047, 202, 202, 2, NULL, NULL, 122);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3048, 202, 202, 2, NULL, NULL, 123);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3049, 202, 202, 2, NULL, NULL, 124);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3050, 202, 202, 2, NULL, NULL, 125);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3051, 202, 202, 2, NULL, NULL, 126);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3052, 202, 202, 2, NULL, NULL, 127);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3053, 202, 202, 2, NULL, NULL, 128);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3054, 202, 202, 2, NULL, NULL, 129);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3055, 202, 202, 2, NULL, NULL, 130);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3056, 202, 202, 2, NULL, NULL, 131);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3057, 202, 202, 2, NULL, NULL, 132);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3058, 202, 202, 2, NULL, NULL, 133);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3059, 202, 202, 2, NULL, NULL, 134);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3060, 202, 202, 2, NULL, NULL, 135);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3061, 202, 202, 2, NULL, NULL, 136);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3062, 202, 202, 2, NULL, NULL, 137);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3063, 202, 202, 2, NULL, NULL, 138);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3064, 202, 202, 2, NULL, NULL, 139);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3065, 202, 202, 2, NULL, NULL, 140);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3066, 202, 202, 2, NULL, NULL, 141);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3067, 202, 202, 2, NULL, NULL, 142);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3068, 202, 202, 2, NULL, NULL, 143);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3069, 202, 202, 2, NULL, NULL, 144);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3070, 202, 202, 2, NULL, NULL, 145);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3071, 202, 202, 2, NULL, NULL, 146);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3072, 202, 202, 2, NULL, NULL, 147);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3073, 202, 202, 2, NULL, NULL, 148);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3074, 202, 202, 2, NULL, NULL, 149);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3075, 202, 202, 2, NULL, NULL, 150);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3076, 202, 202, 2, NULL, NULL, 151);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3077, 202, 202, 2, NULL, NULL, 152);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3078, 202, 202, 2, NULL, NULL, 153);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3079, 202, 202, 2, NULL, NULL, 154);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3080, 202, 202, 2, NULL, NULL, 155);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3081, 202, 202, 2, NULL, NULL, 156);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3082, 202, 202, 2, NULL, NULL, 157);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3083, 202, 202, 2, NULL, NULL, 158);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3084, 202, 202, 2, NULL, NULL, 159);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3085, 202, 202, 2, NULL, NULL, 160);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3086, 202, 202, 2, NULL, NULL, 161);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3087, 202, 202, 2, NULL, NULL, 162);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3088, 202, 202, 2, NULL, NULL, 163);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3089, 202, 202, 2, NULL, NULL, 164);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3090, 202, 202, 2, NULL, NULL, 165);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3091, 202, 202, 2, NULL, NULL, 166);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3092, 202, 202, 2, NULL, NULL, 167);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3093, 202, 202, 2, NULL, NULL, 168);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3094, 202, 202, 2, NULL, NULL, 169);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3095, 202, 202, 2, NULL, NULL, 170);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3096, 202, 202, 2, NULL, NULL, 171);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3097, 202, 202, 2, NULL, NULL, 172);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3098, 202, 202, 2, NULL, NULL, 173);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3099, 202, 202, 2, NULL, NULL, 174);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3100, 202, 202, 2, NULL, NULL, 175);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3101, 202, 202, 2, NULL, NULL, 176);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3102, 202, 202, 2, NULL, NULL, 177);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3103, 202, 202, 2, NULL, NULL, 178);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3104, 202, 202, 2, NULL, NULL, 179);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3105, 202, 202, 2, NULL, NULL, 180);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3106, 202, 202, 2, NULL, NULL, 181);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3107, 202, 202, 2, NULL, NULL, 182);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3108, 202, 202, 2, NULL, NULL, 183);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3109, 202, 202, 2, NULL, NULL, 184);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3110, 202, 202, 2, NULL, NULL, 185);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3111, 202, 202, 2, NULL, NULL, 186);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3112, 202, 202, 2, NULL, NULL, 187);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3113, 202, 202, 2, NULL, NULL, 188);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3114, 202, 202, 2, NULL, NULL, 189);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3115, 202, 202, 2, NULL, NULL, 190);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3116, 202, 202, 2, NULL, NULL, 191);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3117, 202, 202, 2, NULL, NULL, 192);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3118, 202, 202, 2, NULL, NULL, 193);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3119, 202, 202, 2, NULL, NULL, 194);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3120, 202, 202, 2, NULL, NULL, 195);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3121, 202, 202, 2, NULL, NULL, 196);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3122, 202, 202, 2, NULL, NULL, 197);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3123, 202, 202, 2, NULL, NULL, 198);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3124, 202, 202, 2, NULL, NULL, 199);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3125, 202, 202, 2, NULL, NULL, 200);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3126, 202, 202, 2, NULL, NULL, 201);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3127, 202, 202, 2, NULL, NULL, 202);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3128, 202, 202, 2, NULL, NULL, 203);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3129, 202, 202, 2, NULL, NULL, 204);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3130, 202, 202, 2, NULL, NULL, 205);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3131, 202, 202, 2, NULL, NULL, 206);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3132, 202, 202, 2, NULL, NULL, 207);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3133, 202, 202, 2, NULL, NULL, 208);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3134, 202, 202, 2, NULL, NULL, 209);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3135, 202, 202, 2, NULL, NULL, 210);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3136, 202, 202, 2, NULL, NULL, 211);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3137, 202, 202, 2, NULL, NULL, 212);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3138, 202, 202, 2, NULL, NULL, 213);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3139, 202, 202, 2, NULL, NULL, 214);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3140, 202, 202, 2, NULL, NULL, 215);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3141, 202, 202, 2, NULL, NULL, 216);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3142, 202, 202, 2, NULL, NULL, 217);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3143, 202, 202, 2, NULL, NULL, 218);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3144, 202, 202, 2, NULL, NULL, 219);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3145, 202, 202, 2, NULL, NULL, 220);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3146, 202, 202, 2, NULL, NULL, 221);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3147, 202, 202, 2, NULL, NULL, 222);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3148, 202, 202, 2, NULL, NULL, 223);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3149, 202, 202, 2, NULL, NULL, 224);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3150, 202, 202, 2, NULL, NULL, 225);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3151, 202, 202, 2, NULL, NULL, 226);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3152, 202, 202, 2, NULL, NULL, 227);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3153, 202, 202, 2, NULL, NULL, 228);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3154, 202, 202, 2, NULL, NULL, 229);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3155, 202, 202, 2, NULL, NULL, 230);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3156, 202, 202, 2, NULL, NULL, 231);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3157, 202, 202, 2, NULL, NULL, 232);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3158, 202, 202, 2, NULL, NULL, 233);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3159, 202, 202, 2, NULL, NULL, 234);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3160, 202, 202, 2, NULL, NULL, 235);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3161, 202, 202, 2, NULL, NULL, 236);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3162, 202, 202, 2, NULL, NULL, 237);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3163, 202, 202, 2, NULL, NULL, 238);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3164, 202, 202, 2, NULL, NULL, 239);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3165, 202, 202, 2, NULL, NULL, 240);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3166, 202, 202, 2, NULL, NULL, 241);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3167, 202, 202, 2, NULL, NULL, 242);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3168, 202, 202, 2, NULL, NULL, 243);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3169, 202, 202, 2, NULL, NULL, 244);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3170, 202, 202, 2, NULL, NULL, 245);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3171, 202, 202, 2, NULL, NULL, 246);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3172, 202, 202, 2, NULL, NULL, 247);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3173, 202, 202, 2, NULL, NULL, 248);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3174, 202, 202, 2, NULL, NULL, 249);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3175, 202, 202, 2, NULL, NULL, 250);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3176, 202, 202, 2, NULL, NULL, 251);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3177, 202, 202, 2, NULL, NULL, 252);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3178, 202, 202, 2, NULL, NULL, 253);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3179, 202, 202, 2, NULL, NULL, 254);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3180, 202, 202, 2, NULL, NULL, 255);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3181, 202, 202, 2, NULL, NULL, 256);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3182, 202, 202, 2, NULL, NULL, 257);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3183, 202, 202, 2, NULL, NULL, 258);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3184, 202, 202, 2, NULL, NULL, 259);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3185, 202, 202, 2, NULL, NULL, 260);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3186, 202, 202, 2, NULL, NULL, 261);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3187, 202, 202, 2, NULL, NULL, 262);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3188, 202, 202, 2, NULL, NULL, 263);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3189, 202, 202, 2, NULL, NULL, 264);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3190, 202, 202, 2, NULL, NULL, 265);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3191, 202, 202, 2, NULL, NULL, 266);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3192, 202, 202, 2, NULL, NULL, 267);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3193, 202, 202, 2, NULL, NULL, 268);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3194, 202, 202, 2, NULL, NULL, 269);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3195, 202, 202, 2, NULL, NULL, 270);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3196, 202, 202, 2, NULL, NULL, 271);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3197, 202, 202, 2, NULL, NULL, 272);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3198, 202, 202, 2, NULL, NULL, 273);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3199, 202, 202, 2, NULL, NULL, 274);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3200, 202, 202, 2, NULL, NULL, 275);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3201, 202, 202, 2, NULL, NULL, 276);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3202, 202, 202, 2, NULL, NULL, 277);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3203, 202, 202, 2, NULL, NULL, 278);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3204, 202, 202, 2, NULL, NULL, 279);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3205, 202, 202, 2, NULL, NULL, 280);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3206, 202, 202, 2, NULL, NULL, 281);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3207, 202, 202, 2, NULL, NULL, 282);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3208, 202, 202, 2, NULL, NULL, 283);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3209, 202, 202, 2, NULL, NULL, 284);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3210, 202, 202, 2, NULL, NULL, 285);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3211, 202, 202, 2, NULL, NULL, 286);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3212, 202, 202, 2, NULL, NULL, 287);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3213, 202, 202, 2, NULL, NULL, 288);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3214, 202, 202, 2, NULL, NULL, 289);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3215, 202, 202, 2, NULL, NULL, 290);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3216, 202, 202, 2, NULL, NULL, 291);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3217, 202, 202, 2, NULL, NULL, 292);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3218, 202, 202, 2, NULL, NULL, 293);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3219, 202, 202, 2, NULL, NULL, 294);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3220, 202, 202, 2, NULL, NULL, 295);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3221, 202, 202, 2, NULL, NULL, 296);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3222, 202, 202, 2, NULL, NULL, 297);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3223, 202, 202, 2, NULL, NULL, 298);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3224, 202, 202, 2, NULL, NULL, 299);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3225, 202, 202, 2, NULL, NULL, 300);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3226, 202, 202, 2, NULL, NULL, 301);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3227, 202, 202, 2, NULL, NULL, 302);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3228, 202, 202, 2, NULL, NULL, 303);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3229, 202, 202, 2, NULL, NULL, 304);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3230, 202, 202, 2, NULL, NULL, 305);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3231, 202, 202, 2, NULL, NULL, 306);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3232, 202, 202, 2, NULL, NULL, 307);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3233, 202, 202, 2, NULL, NULL, 308);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3234, 202, 202, 2, NULL, NULL, 309);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3235, 202, 202, 2, NULL, NULL, 310);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3236, 202, 202, 2, NULL, NULL, 311);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3237, 202, 202, 2, NULL, NULL, 312);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3238, 202, 202, 2, NULL, NULL, 313);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3239, 202, 202, 2, NULL, NULL, 314);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3240, 202, 202, 2, NULL, NULL, 315);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3241, 202, 202, 2, NULL, NULL, 316);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3242, 202, 202, 2, NULL, NULL, 317);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3243, 202, 202, 2, NULL, NULL, 318);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3244, 202, 202, 2, NULL, NULL, 319);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3245, 202, 202, 2, NULL, NULL, 320);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3246, 202, 202, 2, NULL, NULL, 321);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3247, 202, 202, 2, NULL, NULL, 322);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3248, 202, 202, 2, NULL, NULL, 323);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3249, 202, 202, 2, NULL, NULL, 324);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3250, 202, 202, 2, NULL, NULL, 325);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3251, 203, 203, 2, NULL, '2026-04-03 15:48:16.147195', 1);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3252, 203, 203, 2, NULL, '2026-04-03 15:48:16.147210', 2);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3253, 203, 203, 2, NULL, '2026-04-03 15:48:16.147221', 3);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3254, 203, 203, 2, NULL, '2026-04-03 15:48:16.147226', 4);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3255, 203, 203, 2, NULL, '2026-04-03 15:48:16.147231', 5);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3256, 203, 203, 2, NULL, '2026-04-03 15:48:16.147235', 6);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3257, 203, 203, 2, NULL, '2026-04-03 15:48:16.147241', 7);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3258, 203, 203, 2, NULL, '2026-04-03 15:48:16.147246', 8);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3259, 203, 203, 2, NULL, '2026-04-03 15:48:16.147251', 9);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3260, 203, 203, 2, NULL, '2026-04-03 15:48:16.147255', 10);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3261, 203, 203, 2, NULL, '2026-04-03 15:48:16.147259', 11);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3262, 203, 203, 2, NULL, '2026-04-03 15:48:16.147263', 12);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3263, 203, 203, 2, NULL, '2026-04-03 15:48:16.147267', 13);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3264, 203, 203, 2, NULL, '2026-04-03 15:48:16.147272', 14);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3265, 203, 203, 2, NULL, '2026-04-03 15:48:16.147276', 15);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3266, 203, 203, 2, NULL, '2026-04-03 15:48:16.147280', 16);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3267, 203, 203, 2, NULL, '2026-04-03 15:48:16.147284', 17);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3268, 203, 203, 2, NULL, '2026-04-03 15:48:16.147288', 18);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3269, 203, 203, 2, NULL, '2026-04-03 15:48:16.147292', 19);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3270, 203, 203, 2, NULL, '2026-04-03 15:48:16.147296', 20);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3271, 203, 203, 2, NULL, '2026-04-03 15:48:16.147300', 21);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3272, 203, 203, 2, NULL, '2026-04-03 15:48:16.147304', 22);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3273, 203, 203, 2, NULL, '2026-04-03 15:48:16.147308', 23);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3274, 203, 203, 2, NULL, '2026-04-03 15:48:16.147312', 24);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3275, 203, 203, 2, NULL, '2026-04-03 15:48:16.147317', 25);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3276, 203, 203, 2, NULL, '2026-04-03 15:48:16.147321', 26);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3277, 203, 203, 2, NULL, '2026-04-03 15:48:16.147325', 27);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3278, 203, 203, 2, NULL, '2026-04-03 15:48:16.147329', 28);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3279, 203, 203, 2, NULL, '2026-04-03 15:48:16.147333', 29);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3280, 203, 203, 2, NULL, '2026-04-03 15:48:16.147337', 30);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3281, 203, 203, 2, NULL, '2026-04-03 15:48:16.147341', 31);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3282, 203, 203, 2, NULL, '2026-04-03 15:48:16.147345', 32);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3283, 203, 203, 2, NULL, '2026-04-03 15:48:16.147349', 33);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3284, 203, 203, 2, NULL, '2026-04-03 15:48:16.147352', 34);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3285, 203, 203, 2, NULL, '2026-04-03 15:48:16.147356', 35);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3286, 203, 203, 2, NULL, '2026-04-03 15:48:16.147360', 36);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3287, 203, 203, 2, NULL, '2026-04-03 15:48:16.147364', 37);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3288, 203, 203, 2, NULL, '2026-04-03 15:48:16.147368', 38);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3289, 203, 203, 2, NULL, '2026-04-03 15:48:16.147372', 39);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3290, 203, 203, 2, NULL, '2026-04-03 15:48:16.147376', 40);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3291, 203, 203, 2, NULL, '2026-04-03 15:48:16.147379', 41);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3292, 203, 203, 2, NULL, '2026-04-03 15:48:16.147383', 42);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3293, 203, 203, 2, NULL, '2026-04-03 15:48:16.147387', 43);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3294, 203, 203, 2, NULL, '2026-04-03 15:48:16.147391', 44);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3295, 203, 203, 2, NULL, '2026-04-03 15:48:16.147395', 45);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3296, 203, 203, 2, NULL, '2026-04-03 15:48:16.147399', 46);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3297, 203, 203, 2, NULL, '2026-04-03 15:48:16.147402', 47);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3298, 203, 203, 2, NULL, '2026-04-03 15:48:16.147406', 48);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3299, 203, 203, 2, NULL, '2026-04-03 15:48:16.147410', 49);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3300, 203, 203, 2, NULL, '2026-04-03 15:48:16.147414', 50);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3301, 203, 203, 2, NULL, '2026-04-03 15:48:16.147418', 51);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3302, 203, 203, 2, NULL, '2026-04-03 15:48:16.147423', 52);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3303, 203, 203, 2, NULL, '2026-04-03 15:48:16.147427', 53);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3304, 203, 203, 2, NULL, '2026-04-03 15:48:16.147431', 54);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3305, 203, 203, 2, NULL, '2026-04-03 15:48:16.147435', 55);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3306, 203, 203, 2, NULL, '2026-04-03 15:48:16.147439', 56);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3307, 203, 203, 2, NULL, '2026-04-03 15:48:16.147443', 57);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3308, 203, 203, 2, NULL, '2026-04-03 15:48:16.147447', 58);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3309, 203, 203, 2, NULL, '2026-04-03 15:48:16.147451', 59);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3310, 203, 203, 2, NULL, '2026-04-03 15:48:16.147455', 60);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3311, 203, 203, 2, NULL, '2026-04-03 15:48:16.147459', 61);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3312, 203, 203, 2, NULL, '2026-04-03 15:48:16.147463', 62);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3313, 203, 203, 2, NULL, '2026-04-03 15:48:16.147467', 63);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3314, 203, 203, 2, NULL, '2026-04-03 15:48:16.147471', 64);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3315, 203, 203, 2, NULL, '2026-04-03 15:48:16.147475', 65);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3316, 203, 203, 2, NULL, '2026-04-03 15:48:16.147479', 66);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3317, 203, 203, 2, NULL, '2026-04-03 15:48:16.147482', 67);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3318, 203, 203, 2, NULL, '2026-04-03 15:48:16.147486', 68);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3319, 203, 203, 2, NULL, '2026-04-03 15:48:16.147490', 69);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3320, 203, 203, 2, NULL, '2026-04-03 15:48:16.147494', 70);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3321, 203, 203, 2, NULL, '2026-04-03 15:48:16.147498', 71);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3322, 203, 203, 2, NULL, '2026-04-03 15:48:16.147502', 72);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3323, 203, 203, 2, NULL, '2026-04-03 15:48:16.147506', 73);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3324, 203, 203, 2, NULL, '2026-04-03 15:48:16.147509', 74);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3325, 203, 203, 2, NULL, '2026-04-03 15:48:16.147513', 75);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3326, 203, 203, 2, NULL, '2026-04-03 15:48:16.147517', 76);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3327, 203, 203, 2, NULL, '2026-04-03 15:48:16.147521', 77);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3328, 203, 203, 2, NULL, '2026-04-03 15:48:16.147525', 78);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3329, 203, 203, 2, NULL, '2026-04-03 15:48:16.147529', 79);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3330, 203, 203, 2, NULL, '2026-04-03 15:48:16.147533', 80);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3331, 203, 203, 2, NULL, '2026-04-03 15:48:16.147536', 81);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3332, 203, 203, 2, NULL, '2026-04-03 15:48:16.147540', 82);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3333, 203, 203, 2, NULL, '2026-04-03 15:48:16.147544', 83);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3334, 203, 203, 2, NULL, '2026-04-03 15:48:16.147550', 84);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3335, 203, 203, 2, NULL, '2026-04-03 15:48:16.147554', 85);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3336, 203, 203, 2, NULL, '2026-04-03 15:48:16.147558', 86);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3337, 203, 203, 2, NULL, '2026-04-03 15:48:16.147562', 87);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3338, 203, 203, 2, NULL, '2026-04-03 15:48:16.147566', 88);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3339, 203, 203, 2, NULL, '2026-04-03 15:48:16.147570', 89);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3340, 203, 203, 2, NULL, '2026-04-03 15:48:16.147574', 90);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3341, 203, 203, 2, NULL, '2026-04-03 15:48:16.147578', 91);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3342, 203, 203, 2, NULL, '2026-04-03 15:48:16.147582', 92);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3343, 203, 203, 2, NULL, '2026-04-03 15:48:16.147586', 93);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3344, 203, 203, 2, NULL, '2026-04-03 15:48:16.147589', 94);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3345, 203, 203, 2, NULL, '2026-04-03 15:48:16.147593', 95);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3346, 203, 203, 2, NULL, '2026-04-03 15:48:16.147597', 96);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3347, 203, 203, 2, NULL, '2026-04-03 15:48:16.147601', 97);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3348, 203, 203, 2, NULL, '2026-04-03 15:48:16.147605', 98);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3349, 203, 203, 2, NULL, '2026-04-03 15:48:16.147609', 99);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3350, 203, 203, 2, NULL, '2026-04-03 15:48:16.147612', 100);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3351, 203, 203, 2, NULL, '2026-04-03 15:48:16.147616', 101);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3352, 203, 203, 2, NULL, '2026-04-03 15:48:16.147620', 102);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3353, 203, 203, 2, NULL, '2026-04-03 15:48:16.147624', 103);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3354, 203, 203, 2, NULL, '2026-04-03 15:48:16.147628', 104);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3355, 203, 203, 2, NULL, '2026-04-03 15:48:16.147632', 105);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3356, 203, 203, 2, NULL, '2026-04-03 15:48:16.147636', 106);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3357, 203, 203, 2, NULL, '2026-04-03 15:48:16.147639', 107);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3358, 203, 203, 2, NULL, '2026-04-03 15:48:16.147643', 108);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3359, 203, 203, 2, NULL, '2026-04-03 15:48:16.147647', 109);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3360, 204, 204, 2, NULL, '2026-04-03 15:48:16.147655', 111);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3361, 204, 204, 2, NULL, '2026-04-03 15:48:16.147659', 112);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3362, 204, 204, 2, NULL, '2026-04-03 15:48:16.147663', 113);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3363, 204, 204, 2, NULL, '2026-04-03 15:48:16.147667', 114);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3364, 204, 204, 2, NULL, '2026-04-03 15:48:16.147671', 115);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3365, 204, 204, 2, NULL, '2026-04-03 15:48:16.147675', 116);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3366, 204, 204, 2, NULL, '2026-04-03 15:48:16.147680', 117);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3367, 204, 204, 2, NULL, '2026-04-03 15:48:16.147683', 118);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3368, 204, 204, 2, NULL, '2026-04-03 15:48:16.147688', 119);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3369, 204, 204, 2, NULL, '2026-04-03 15:48:16.147692', 120);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3370, 204, 204, 2, NULL, '2026-04-03 15:48:16.147696', 121);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3371, 204, 204, 2, NULL, '2026-04-03 15:48:16.147700', 122);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3372, 204, 204, 2, NULL, '2026-04-03 15:48:16.147704', 123);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3373, 204, 204, 2, NULL, '2026-04-03 15:48:16.147708', 124);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3374, 204, 204, 2, NULL, '2026-04-03 15:51:29.210596', 125);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3375, 204, 204, 2, NULL, '2026-04-03 15:51:29.210604', 126);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3376, 204, 204, 2, NULL, '2026-04-04 02:34:55.838193', 127);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3377, 204, 204, 2, NULL, '2026-04-04 02:34:55.838205', 128);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3378, 204, 204, 2, NULL, '2026-04-04 02:34:55.838211', 129);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3379, 204, 204, 2, NULL, '2026-04-04 02:34:55.838220', 130);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3380, 204, 204, 2, NULL, '2026-04-04 02:34:55.838225', 131);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3381, 204, 204, 2, NULL, '2026-04-04 02:34:55.838229', 132);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3382, 204, 204, 2, NULL, '2026-04-04 02:34:55.838233', 133);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3383, 204, 204, 2, NULL, '2026-04-04 02:34:55.838242', 134);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3384, 204, 204, 2, NULL, '2026-04-04 05:42:04.363537', 135);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3385, 204, 204, 2, NULL, '2026-04-04 05:42:04.363546', 136);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3386, 204, 204, 2, NULL, '2026-04-04 05:42:04.363550', 137);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3387, 204, 204, 2, NULL, '2026-04-04 05:42:04.363559', 138);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3388, 204, 204, 2, NULL, '2026-04-04 05:51:27.826735', 139);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3389, 204, 204, 2, NULL, '2026-04-04 05:51:27.826746', 140);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3390, 204, 204, 2, NULL, '2026-04-04 05:51:27.826750', 141);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3391, 204, 204, 2, NULL, '2026-04-04 09:08:08.593229', 142);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3392, 204, 204, 2, NULL, '2026-04-04 09:08:08.593241', 143);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3393, 204, 204, 2, NULL, '2026-04-04 09:08:08.593246', 144);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3394, 204, 204, 2, NULL, '2026-04-04 09:08:08.593250', 145);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3395, 204, 204, 2, NULL, '2026-04-04 09:27:05.155140', 146);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3396, 204, 204, 2, NULL, '2026-04-04 09:53:27.313339', 147);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3397, 204, 204, 2, NULL, '2026-04-04 09:53:27.313351', 148);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3398, 204, 204, 2, NULL, '2026-04-04 12:02:11.318884', 149);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3399, 204, 204, 2, NULL, '2026-04-04 12:02:11.318895', 150);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3400, 204, 204, 2, NULL, '2026-04-04 12:02:11.318902', 151);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3401, 204, 204, 2, NULL, '2026-04-04 12:02:11.318914', 152);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3402, 204, 204, 2, NULL, '2026-04-04 12:02:11.318921', 153);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3403, 204, 204, 2, NULL, '2026-04-04 13:48:53.326992', 154);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3404, 204, 204, 2, NULL, '2026-04-04 16:38:39.798586', 155);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3405, 204, 204, 2, NULL, '2026-04-04 16:38:39.798601', 156);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3406, 204, 204, 2, NULL, '2026-04-05 03:51:48.513136', 157);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3407, 204, 204, 2, NULL, '2026-04-05 03:51:48.513147', 158);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3408, 204, 204, 2, NULL, '2026-04-05 03:51:48.513152', 159);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3409, 204, 204, 2, NULL, '2026-04-05 03:51:48.513157', 160);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3410, 204, 204, 2, NULL, '2026-04-05 03:51:48.513162', 161);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3411, 204, 204, 2, NULL, '2026-04-05 03:51:48.513166', 162);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3412, 204, 204, 2, NULL, '2026-04-05 03:51:48.513170', 163);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3413, 204, 204, 2, NULL, '2026-04-05 03:51:48.513175', 164);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3414, 204, 204, 2, NULL, '2026-04-05 03:51:48.513179', 165);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3415, 204, 204, 2, NULL, '2026-04-05 03:51:48.513184', 166);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3416, 204, 204, 2, NULL, '2026-04-05 03:51:48.513188', 167);
INSERT OR IGNORE INTO 'lost_and_found'(_rowid_, 'rootpgno', 'pgno', 'nfield', 'id', 'c0', 'c1') VALUES (3417, 204, 204, 2, NULL, '2026-04-05 03:51:48.513192', 168);
INSERT OR IGNORE INTO 'user_sessions'(_rowid_, 'user_id', 'device_id', 'device_name', 'device_type', 'browser', 'os', 'ip_address', 'location', 'user_agent', 'refresh_token_hash', 'refresh_token_expires_at', 'access_token_jti', 'last_used_at', 'is_current', 'is_active', 'id', 'created_at', 'updated_at') VALUES (1, 'fecf1cde-739e-4c99-82ea-db6915e226fe', 'default', 'Login', NULL, NULL, NULL, NULL, NULL, NULL, '$2b$12$qXyeemSYVS6WW7yZ7CwkXu6ZVxCEOUr0qg4W8MYHFaw/5FCOXoyRe', '2026-05-15 14:04:16.584641', '6da56fc9-9f3a-4df1-b067-a32ae1eb701b', '2026-04-15 14:04:16.415847', 1, 1, 'e15c368a-dafe-4776-abf3-9ae76446359b', '2026-04-15 14:04:16.416244', '2026-04-15 14:04:16.585085');
INSERT OR IGNORE INTO 'user_sessions'(_rowid_, 'user_id', 'device_id', 'device_name', 'device_type', 'browser', 'os', 'ip_address', 'location', 'user_agent', 'refresh_token_hash', 'refresh_token_expires_at', 'access_token_jti', 'last_used_at', 'is_current', 'is_active', 'id', 'created_at', 'updated_at') VALUES (2, '186abe6d-ed82-4ac6-882e-9d0acb5f3192', 'default', 'Login', NULL, NULL, NULL, NULL, NULL, NULL, '$2b$12$t2PfuAFDEwA9ErLPOf0IreH/ZhCpJEZpNw/c4dD6v7fRsq1qkoeJ6', '2026-05-15 16:34:22.554746', '796dc2a2-63cb-46bf-a5a7-5c634474ef19', '2026-04-15 16:34:22.386044', 1, 1, 'd62582eb-5c2c-4a0e-b058-790324931ee5', '2026-04-15 14:53:22.538763', '2026-04-15 16:34:22.555169');
CREATE TABLE lost_and_found_0(rootpgno INTEGER, pgno INTEGER, nfield INTEGER, id INTEGER, c0, c1, c2, c3);
INSERT INTO lost_and_found_0 VALUES(247, 247, 2, NULL, '186abe6d-ed82-4ac6-882e-9d0acb5f3192', 2, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(247, 247, 2, NULL, 'fecf1cde-739e-4c99-82ea-db6915e226fe', 1, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(248, 248, 2, NULL, 'd62582eb-5c2c-4a0e-b058-790324931ee5', 2, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(248, 248, 2, NULL, 'e15c368a-dafe-4776-abf3-9ae76446359b', 1, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(249, 249, 2, NULL, '6da56fc9-9f3a-4df1-b067-a32ae1eb701b', 1, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(249, 249, 2, NULL, '796dc2a2-63cb-46bf-a5a7-5c634474ef19', 2, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, '009c6847-d6a2-441e-9666-389c7763565a', 53, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, '0212fd7a-661d-463c-90ef-2d74f47c235d', 63, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, '03395b89-5bfa-435f-859e-c1ff10097e6e', 62, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, '0343abc0-2029-4f4f-b409-0d2b9c96fe47', 66, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, '0445cda7-acd1-4475-8854-ad0749dbab54', 17, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, '04e725cf-0026-4ee1-b529-904a9a887394', 43, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, '05780a3b-ea63-476d-9ed0-9054d27184c4', 86, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, '09e8b2f8-b9ae-4733-8c97-384bf44f6732', 4, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, '10b585c5-0f44-4462-b702-1e75d1c8253f', 81, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, '10cf96c2-5a8b-44fa-9db4-dd6cf9d13cbc', 41, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, '13050657-2d55-4ff9-b15e-b6505524bd2c', 38, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, '168a5664-eff0-456f-86cf-9ea5fdc83383', 30, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, '1d598ba1-20de-4637-8cf0-f25d1b10492b', 36, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, '230e0ed6-93cb-46e9-a527-54c43731b113', 2, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, '251d5e6a-1d45-4309-8785-50ce8e43c37e', 84, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, '253a7890-5124-4ce5-8546-30b79b02cc81', 45, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, '25a6a06c-dc6e-4b55-985d-586074b5d5d2', 25, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, '2cd5178c-96e2-4078-aa5f-b9de01ff287d', 35, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, '34f80d05-c5bd-4826-90e5-2da118c75576', 58, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, '3856d73e-d3c9-4bc3-b614-4d5389ff550a', 29, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, '385a8509-3270-4ec3-8c4c-67baf3e69423', 78, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, '3b970e4c-a085-4ca7-bfe9-782c28d6943c', 77, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, '3fc9ac41-0de9-4d96-8da1-92de0d8dcc7a', 89, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, '4143b142-b8b3-45ed-a3e3-b8938bb7581c', 46, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, '41ab7652-a836-4a04-9b1f-187905858dd7', 85, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, '45408b1b-dbbd-477f-94b8-24351fdd126d', 33, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, '4604cf16-f9b1-4667-bd73-b056588a104a', 80, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, '46968754-3766-4c75-9968-8b61cf9d5cfe', 1, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, '4718de2e-f3b0-478c-9165-6e24bfd90e38', 12, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, '4baf743e-c1c8-4e10-a243-e481c38fd715', 11, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, '4f046f5e-5ac1-42fe-9ee9-75681331f233', 18, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, '510af956-c231-458d-a34b-ca0bc5103b8a', 70, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, '53aa2d6d-4f4e-4558-b6d0-ac1dae6f2946', 32, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, '549197bd-f2f6-468c-af26-3d27bb6fdff5', 75, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, '55057df4-4b24-4fe4-803a-62e967611caf', 21, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, '5651da83-cb0f-4c83-ac5f-9431e508f50a', 14, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, '5a0cc1d5-a7f4-4119-a218-54a0c002f7d5', 56, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, '6818aebc-bc8a-4a44-835a-4623ec96ce64', 8, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, '742db9e1-606a-4a23-a006-a312debbc0d0', 90, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, '7b55f8c9-ea0d-48d3-939e-6fa87a49868d', 88, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, '7ea8f334-afcc-497e-9fc1-c90878558b9f', 60, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, '8002de8a-5b2c-4f68-a043-38ed228dad59', 37, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, '876f6d23-da78-402c-9ae6-e32ba17e0a79', 83, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, '8f57eb0a-3065-40bd-8851-7588d0951bc2', 27, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, '9307fbca-d711-4f48-ab70-d4f791d3998e', 31, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, '94867af5-6240-48bf-b1f8-ac5c74224c85', 13, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, '95f305e5-4ee6-4723-a92e-9f3030924072', 57, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, '990e7dc5-4e5d-4c4e-aa09-85ed9a3695a7', 50, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, '99e5c806-b2cf-422c-8e13-aa1e4116622a', 76, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, '9a209d79-5646-4d69-b6ee-908430499298', 22, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, '9a6663ca-6e4b-4d38-8803-a8394d58a2fc', 61, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, '9d1b7295-2c44-4654-ad0e-da3d0f98c30c', 59, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, '9ea8a597-044f-4493-9bca-70e90892e773', 51, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, 'a23bc2e6-5c06-438d-a1e2-8a16887cb27f', 74, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, 'a3516441-1f89-41e7-a62c-6559d870054a', 34, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, 'a6265a74-b44c-4039-8c45-d7470082e51a', 54, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, 'a7108d59-f1ec-4a46-a464-ad2354d1b76b', 9, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, 'a7853614-dd4c-4bb8-9b3b-b2817cb9a942', 28, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, 'b0b17496-5f08-4e97-b110-f6650f5c9dc1', 3, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, 'b4243507-6e8d-4621-a6c5-9733985a00a1', 52, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, 'b593f7fa-3d22-4555-9280-f3e4dd125ac5', 26, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, 'bb189e5f-afbb-4de6-8175-b460b9d5ba47', 10, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, 'bb2b0f89-7d19-45ac-9312-7ef17017d3b7', 71, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, 'bb7ea0f1-ea41-41dc-827d-c9f271a8d7f3', 49, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, 'bbec8ab9-d74c-4345-86de-f605d08ce6fc', 23, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, 'bbed8803-ee64-4a4a-850f-57a93e429c9d', 20, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, 'bd175d5f-cf0e-465c-8341-a7fd75e441d9', 16, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, 'c202f72b-fa87-49e0-a71b-a7d28efbdd50', 79, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, 'c2377b71-050c-4e2d-9a60-c8ea430544b2', 6, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, 'c3e1d3cb-62c5-48a4-9dc1-16349a08c3a0', 67, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, 'cd0b3435-fd62-4d46-9a83-f67b603dc2fc', 48, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, 'cee0820f-4371-4693-9b8b-7ab7a5ee5563', 87, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, 'd41b0fdb-6a3b-475c-b03c-0e77594e4e7c', 44, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, 'd5170bc2-6066-4c98-995c-22bc95e3cb26', 68, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, 'd7bd74b4-6087-4f44-8c72-b9f883f3b0e2', 69, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, 'e050eefd-d117-4605-a4bd-7272698e65c6', 19, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, 'e3d052d8-5b87-4a94-95ea-101aa9d6c2a6', 65, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, 'e956f992-d67c-4ae7-a680-7d7d3924eab6', 72, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, 'ec5e13a5-2ed9-45c2-95d2-d221a3c1cddd', 7, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, 'ee023b7e-48fc-4551-90a4-c3c68cf4487e', 47, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, 'ef64408d-89f9-4fb6-b409-825fe895e61d', 55, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, 'f01e8141-32d8-41f1-bde8-42679082dec2', 40, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, 'f0251e4b-4de4-4673-b483-77270d3509fe', 64, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, 'f0299244-c613-4790-8592-e1f7d8ad3049', 24, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, 'f13c5507-0a59-477f-a4b4-684f4b539047', 82, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, 'f3eea210-df9c-4e2c-bd25-9a21c99ae9fa', 15, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, 'f4201a79-985d-4eeb-9ba0-8e4296e8d68a', 5, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, 'f56438cd-06d1-4ffb-9417-38ddcd4e1a96', 42, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, 'fa59bfb9-0721-428b-b910-bdd63fce8681', 39, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(251, 251, 2, NULL, 'fcfc5246-4672-4039-bb8f-711d2c94f5e6', 73, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(252, 252, 4, NULL, 'INTERNSHALA', 'internshala_3109425', '186abe6d-ed82-4ac6-882e-9d0acb5f3192', 34);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'AI Agent Development', 1, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'AI Agent Development', 15, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'AI Agent Development', 18, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'AI Agent Development', 30, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'AI Agent Development', 45, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'AI Agent Development', 50, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'AI Agent Development', 71, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'AI Agent Development', 82, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'AI Agent Development', 88, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'AI Agent Expert', 39, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'AI Automation', 77, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'AI Automation Intern (Perplexity Computer + OpenClaw + Claude)', 29, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'AI Data Annotator (Video Annotation)', 24, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'AI Engineer', 10, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'AI Intern', 25, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'AI Solutions Intern', 11, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'AI/ML', 8, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'AI/ML', 37, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'AI/ML', 44, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'AI/ML Engineer', 16, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'Artificial Intelligence', 73, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'Artificial Intelligence (AI)', 7, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'Artificial Intelligence (AI)', 12, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'Artificial Intelligence (AI)', 19, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'Artificial Intelligence (AI)', 23, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'Artificial Intelligence (AI)', 26, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'Artificial Intelligence (AI)', 28, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'Artificial Intelligence (AI)', 31, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'Artificial Intelligence (AI)', 32, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'Artificial Intelligence (AI)', 38, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'Artificial Intelligence (AI)', 42, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'Artificial Intelligence (AI)', 43, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'Artificial Intelligence (AI)', 51, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'Artificial Intelligence (AI)', 53, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'Artificial Intelligence (AI)', 59, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'Artificial Intelligence (AI)', 75, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'Artificial Intelligence (AI)', 78, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'Artificial Intelligence (AI)', 84, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'Assistant Lead, Campus Technical Learning', 55, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'Behavioral Data Science', 81, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'Big Data', 87, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'Cloud And Machine Learning (AWS SageMaker)', 33, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'Computer Vision', 21, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'Computer Vision', 85, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'Computer Vision', 86, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'Data Analytics', 52, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'Data Annotation - ML', 2, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'Data Science', 9, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'Data Science', 14, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'Data Science', 17, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'Data Science', 22, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'Data Science', 58, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'Data Science', 64, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'Data Science', 67, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'Data Science', 70, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'Data Structuring And Data Cleaning For AI Models', 35, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'Data Tagging Associate', 90, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'Founding AI Engineer', 36, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'Full Stack Development', 4, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'Full Stack Web Development & AI', 27, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'Generative Engine Optimization (GEO)', 3, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'Genrative AI Engineer', 20, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'Hybrid Bioinformatics & AI (Integrated Cohort, Ultraceuticals)', 46, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'Image Labeling', 34, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'Image Tagging Executive', 89, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'MLOps and AI Infra', 5, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'MLOps and AI Infra', 79, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'Machine Learning', 48, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'Machine Learning', 56, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'Machine Learning', 60, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'Machine Learning', 62, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'Machine Learning', 68, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'Machine Learning', 80, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'Machine Learning', 83, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'Machine Learning (Modeling and Evaluation)', 57, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'Machine Learning AI', 49, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'OpenClaw Trajectory Specialist - 65130', 54, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'Point Cloud Object Detection And LiDAR Annotation Expert', 74, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'Prompt Engineering', 76, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'Python AI Developer', 69, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'Python Developer', 66, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'Python Development', 13, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'Python Development', 61, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'Python Development', 63, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'Python Development', 65, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'Python Development', 72, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'Software Developer', 6, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'Software Development', 40, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'Software Engineer Intern (AI/ML) - AI Powered Global Tech Startup', 41, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(253, 253, 2, NULL, 'Technical Operations', 47, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, '009c6847-d6a2-441e-9666-389c7763565a', 53, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, '0212fd7a-661d-463c-90ef-2d74f47c235d', 63, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, '03395b89-5bfa-435f-859e-c1ff10097e6e', 62, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, '0343abc0-2029-4f4f-b409-0d2b9c96fe47', 66, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, '0445cda7-acd1-4475-8854-ad0749dbab54', 17, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, '04e725cf-0026-4ee1-b529-904a9a887394', 43, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, '05780a3b-ea63-476d-9ed0-9054d27184c4', 86, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, '09e8b2f8-b9ae-4733-8c97-384bf44f6732', 4, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, '10b585c5-0f44-4462-b702-1e75d1c8253f', 81, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, '10cf96c2-5a8b-44fa-9db4-dd6cf9d13cbc', 41, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, '13050657-2d55-4ff9-b15e-b6505524bd2c', 38, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, '168a5664-eff0-456f-86cf-9ea5fdc83383', 30, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, '1d598ba1-20de-4637-8cf0-f25d1b10492b', 36, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, '230e0ed6-93cb-46e9-a527-54c43731b113', 2, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, '251d5e6a-1d45-4309-8785-50ce8e43c37e', 84, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, '253a7890-5124-4ce5-8546-30b79b02cc81', 45, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, '25a6a06c-dc6e-4b55-985d-586074b5d5d2', 25, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, '2cd5178c-96e2-4078-aa5f-b9de01ff287d', 35, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, '34f80d05-c5bd-4826-90e5-2da118c75576', 58, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, '3856d73e-d3c9-4bc3-b614-4d5389ff550a', 29, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, '385a8509-3270-4ec3-8c4c-67baf3e69423', 78, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, '3b970e4c-a085-4ca7-bfe9-782c28d6943c', 77, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, '3fc9ac41-0de9-4d96-8da1-92de0d8dcc7a', 89, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, '4143b142-b8b3-45ed-a3e3-b8938bb7581c', 46, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, '41ab7652-a836-4a04-9b1f-187905858dd7', 85, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, '45408b1b-dbbd-477f-94b8-24351fdd126d', 33, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, '4604cf16-f9b1-4667-bd73-b056588a104a', 80, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, '46968754-3766-4c75-9968-8b61cf9d5cfe', 1, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, '4718de2e-f3b0-478c-9165-6e24bfd90e38', 12, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, '4baf743e-c1c8-4e10-a243-e481c38fd715', 11, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, '4f046f5e-5ac1-42fe-9ee9-75681331f233', 18, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, '510af956-c231-458d-a34b-ca0bc5103b8a', 70, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, '53aa2d6d-4f4e-4558-b6d0-ac1dae6f2946', 32, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, '549197bd-f2f6-468c-af26-3d27bb6fdff5', 75, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, '55057df4-4b24-4fe4-803a-62e967611caf', 21, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, '5651da83-cb0f-4c83-ac5f-9431e508f50a', 14, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, '5a0cc1d5-a7f4-4119-a218-54a0c002f7d5', 56, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, '6818aebc-bc8a-4a44-835a-4623ec96ce64', 8, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, '742db9e1-606a-4a23-a006-a312debbc0d0', 90, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, '7b55f8c9-ea0d-48d3-939e-6fa87a49868d', 88, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, '7ea8f334-afcc-497e-9fc1-c90878558b9f', 60, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, '8002de8a-5b2c-4f68-a043-38ed228dad59', 37, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, '876f6d23-da78-402c-9ae6-e32ba17e0a79', 83, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, '8f57eb0a-3065-40bd-8851-7588d0951bc2', 27, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, '9307fbca-d711-4f48-ab70-d4f791d3998e', 31, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, '94867af5-6240-48bf-b1f8-ac5c74224c85', 13, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, '95f305e5-4ee6-4723-a92e-9f3030924072', 57, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, '990e7dc5-4e5d-4c4e-aa09-85ed9a3695a7', 50, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, '99e5c806-b2cf-422c-8e13-aa1e4116622a', 76, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, '9a209d79-5646-4d69-b6ee-908430499298', 22, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, '9a6663ca-6e4b-4d38-8803-a8394d58a2fc', 61, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, '9d1b7295-2c44-4654-ad0e-da3d0f98c30c', 59, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, '9ea8a597-044f-4493-9bca-70e90892e773', 51, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, 'a23bc2e6-5c06-438d-a1e2-8a16887cb27f', 74, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, 'a3516441-1f89-41e7-a62c-6559d870054a', 34, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, 'a6265a74-b44c-4039-8c45-d7470082e51a', 54, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, 'a7108d59-f1ec-4a46-a464-ad2354d1b76b', 9, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, 'a7853614-dd4c-4bb8-9b3b-b2817cb9a942', 28, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, 'b0b17496-5f08-4e97-b110-f6650f5c9dc1', 3, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, 'b4243507-6e8d-4621-a6c5-9733985a00a1', 52, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, 'b593f7fa-3d22-4555-9280-f3e4dd125ac5', 26, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, 'bb189e5f-afbb-4de6-8175-b460b9d5ba47', 10, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, 'bb2b0f89-7d19-45ac-9312-7ef17017d3b7', 71, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, 'bb7ea0f1-ea41-41dc-827d-c9f271a8d7f3', 49, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, 'bbec8ab9-d74c-4345-86de-f605d08ce6fc', 23, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, 'bbed8803-ee64-4a4a-850f-57a93e429c9d', 20, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, 'bd175d5f-cf0e-465c-8341-a7fd75e441d9', 16, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, 'c202f72b-fa87-49e0-a71b-a7d28efbdd50', 79, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, 'c2377b71-050c-4e2d-9a60-c8ea430544b2', 6, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, 'c3e1d3cb-62c5-48a4-9dc1-16349a08c3a0', 67, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, 'cd0b3435-fd62-4d46-9a83-f67b603dc2fc', 48, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, 'cee0820f-4371-4693-9b8b-7ab7a5ee5563', 87, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, 'd41b0fdb-6a3b-475c-b03c-0e77594e4e7c', 44, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, 'd5170bc2-6066-4c98-995c-22bc95e3cb26', 68, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, 'd7bd74b4-6087-4f44-8c72-b9f883f3b0e2', 69, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, 'e050eefd-d117-4605-a4bd-7272698e65c6', 19, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, 'e3d052d8-5b87-4a94-95ea-101aa9d6c2a6', 65, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, 'e956f992-d67c-4ae7-a680-7d7d3924eab6', 72, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, 'ec5e13a5-2ed9-45c2-95d2-d221a3c1cddd', 7, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, 'ee023b7e-48fc-4551-90a4-c3c68cf4487e', 47, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, 'ef64408d-89f9-4fb6-b409-825fe895e61d', 55, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, 'f01e8141-32d8-41f1-bde8-42679082dec2', 40, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, 'f0251e4b-4de4-4673-b483-77270d3509fe', 64, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, 'f0299244-c613-4790-8592-e1f7d8ad3049', 24, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, 'f13c5507-0a59-477f-a4b4-684f4b539047', 82, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, 'f3eea210-df9c-4e2c-bd25-9a21c99ae9fa', 15, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, 'f4201a79-985d-4eeb-9ba0-8e4296e8d68a', 5, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, 'f56438cd-06d1-4ffb-9417-38ddcd4e1a96', 42, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, 'fa59bfb9-0721-428b-b910-bdd63fce8681', 39, NULL, NULL);
INSERT INTO lost_and_found_0 VALUES(254, 254, 2, NULL, 'fcfc5246-4672-4039-bb8f-711d2c94f5e6', 73, NULL, NULL);
CREATE INDEX ix_user_skills_user_id ON user_skills (user_id);
CREATE INDEX ix_user_skills_id ON user_skills (id);
CREATE INDEX ix_user_skills_created_at ON user_skills (created_at);
CREATE INDEX ix_resumes_target_job_id ON resumes (target_job_id);
CREATE INDEX ix_resumes_created_at ON resumes (created_at);
CREATE INDEX ix_resumes_user_id ON resumes (user_id);
CREATE INDEX ix_resumes_id ON resumes (id);
CREATE INDEX ix_resumes_is_active ON resumes (is_active);
CREATE INDEX ix_resumes_resume_type ON resumes (resume_type);
CREATE INDEX ix_recruiters_created_at ON recruiters (created_at);
CREATE INDEX ix_recruiters_user_id ON recruiters (user_id);
CREATE INDEX ix_recruiters_id ON recruiters (id);
CREATE INDEX ix_recruiters_company ON recruiters (company);
CREATE INDEX ix_notifications_status ON notifications (status);
CREATE INDEX ix_notifications_id ON notifications (id);
CREATE INDEX ix_notifications_user_id ON notifications (user_id);
CREATE INDEX ix_notifications_created_at ON notifications (created_at);
CREATE INDEX ix_agent_tasks_created_at ON agent_tasks (created_at);
CREATE INDEX ix_agent_tasks_related_job_id ON agent_tasks (related_job_id);
CREATE INDEX ix_agent_tasks_id ON agent_tasks (id);
CREATE INDEX ix_agent_tasks_task_type ON agent_tasks (task_type);
CREATE INDEX ix_agent_tasks_status ON agent_tasks (status);
CREATE INDEX ix_skill_gaps_created_at ON skill_gaps (created_at);
CREATE INDEX ix_skill_gaps_id ON skill_gaps (id);
CREATE INDEX ix_skill_gaps_user_id ON skill_gaps (user_id);
CREATE INDEX ix_market_snapshots_id ON market_snapshots (id);
CREATE INDEX ix_market_snapshots_created_at ON market_snapshots (created_at);
CREATE INDEX ix_market_snapshots_snapshot_date ON market_snapshots (snapshot_date);
CREATE INDEX ix_learning_plans_id ON learning_plans (id);
CREATE INDEX ix_learning_plans_user_id ON learning_plans (user_id);
CREATE INDEX ix_learning_plans_created_at ON learning_plans (created_at);
CREATE INDEX ix_generated_projects_user_id ON generated_projects (user_id);
CREATE INDEX ix_generated_projects_created_at ON generated_projects (created_at);
CREATE INDEX ix_generated_projects_id ON generated_projects (id);
CREATE INDEX ix_credential_vaults_created_at ON credential_vaults (created_at);
CREATE INDEX ix_credential_vaults_credential_type ON credential_vaults (credential_type);
CREATE INDEX ix_credential_vaults_id ON credential_vaults (id);
CREATE INDEX ix_credential_vaults_user_id ON credential_vaults (user_id);
CREATE INDEX ix_user_consents_user_id ON user_consents (user_id);
CREATE INDEX ix_user_consents_id ON user_consents (id);
CREATE INDEX ix_user_consents_consent_type ON user_consents (consent_type);
CREATE INDEX ix_user_consents_created_at ON user_consents (created_at);
CREATE INDEX ix_consent_versions_id ON consent_versions (id);
CREATE INDEX ix_consent_versions_created_at ON consent_versions (created_at);
CREATE INDEX ix_audit_logs_timestamp ON audit_logs (timestamp);
CREATE INDEX ix_audit_user_action ON audit_logs (user_id, action);
CREATE INDEX ix_audit_timestamp_action ON audit_logs (timestamp, action);
CREATE INDEX ix_audit_resource ON audit_logs (resource_type, resource_id);
CREATE INDEX ix_audit_logs_user_id ON audit_logs (user_id);
CREATE INDEX ix_audit_ip_timestamp ON audit_logs (ip_address, timestamp);
CREATE INDEX ix_audit_logs_action ON audit_logs (action);
CREATE INDEX ix_audit_logs_id ON audit_logs (id);
CREATE INDEX ix_audit_user_timestamp ON audit_logs (user_id, timestamp);
CREATE INDEX ix_subscriptions_created_at ON subscriptions (created_at);
CREATE INDEX ix_subscriptions_status ON subscriptions (status);
CREATE INDEX ix_subscriptions_id ON subscriptions (id);
CREATE INDEX ix_subscriptions_user_id ON subscriptions (user_id);
CREATE INDEX ix_platform_cookies_created_at ON platform_cookies (created_at);
CREATE INDEX ix_platform_cookies_user_id ON platform_cookies (user_id);
CREATE INDEX ix_platform_cookies_platform ON platform_cookies (platform);
CREATE INDEX ix_platform_cookies_id ON platform_cookies (id);
CREATE INDEX ix_job_analyses_match_score ON job_analyses (match_score);
CREATE INDEX ix_job_analyses_created_at ON job_analyses (created_at);
CREATE INDEX ix_job_analyses_id ON job_analyses (id);
CREATE INDEX ix_applications_resume_id ON applications (resume_id);
CREATE INDEX ix_applications_recruiter_id ON applications (recruiter_id);
CREATE INDEX ix_applications_status ON applications (status);
CREATE INDEX ix_applications_job_id ON applications (job_id);
CREATE INDEX ix_applications_user_id ON applications (user_id);
CREATE INDEX ix_applications_id ON applications (id);
CREATE INDEX ix_applications_created_at ON applications (created_at);
CREATE INDEX ix_recruiter_messages_recruiter_id ON recruiter_messages (recruiter_id);
CREATE INDEX ix_recruiter_messages_id ON recruiter_messages (id);
CREATE INDEX ix_recruiter_messages_created_at ON recruiter_messages (created_at);
CREATE INDEX ix_credential_use_logs_id ON credential_use_logs (id);
CREATE INDEX ix_credential_use_logs_user_id ON credential_use_logs (user_id);
CREATE INDEX ix_credential_use_logs_credential_id ON credential_use_logs (credential_id);
CREATE INDEX ix_credential_use_logs_created_at ON credential_use_logs (created_at);
CREATE INDEX ix_payments_user_id ON payments (user_id);
CREATE INDEX ix_payments_created_at ON payments (created_at);
CREATE INDEX ix_payments_id ON payments (id);
CREATE INDEX ix_payments_razorpay_payment_id ON payments (razorpay_payment_id);
CREATE INDEX ix_payments_subscription_id ON payments (subscription_id);
CREATE INDEX ix_cover_letters_application_id ON cover_letters (application_id);
CREATE INDEX ix_cover_letters_user_id ON cover_letters (user_id);
CREATE INDEX ix_cover_letters_created_at ON cover_letters (created_at);
CREATE INDEX ix_cover_letters_id ON cover_letters (id);
CREATE INDEX ix_cover_letters_job_id ON cover_letters (job_id);
CREATE INDEX ix_application_events_id ON application_events (id);
CREATE INDEX ix_application_events_application_id ON application_events (application_id);
CREATE INDEX ix_application_events_created_at ON application_events (created_at);
CREATE INDEX ix_interviews_application_id ON interviews (application_id);
CREATE INDEX ix_interviews_created_at ON interviews (created_at);
CREATE INDEX ix_interviews_user_id ON interviews (user_id);
CREATE INDEX ix_interviews_id ON interviews (id);
CREATE INDEX ix_mock_interview_sessions_interview_id ON mock_interview_sessions (interview_id);
CREATE INDEX ix_user_sessions_created_at ON user_sessions (created_at);
PRAGMA writable_schema = off;
COMMIT;
