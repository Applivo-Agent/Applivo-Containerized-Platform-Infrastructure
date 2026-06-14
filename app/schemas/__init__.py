"""
app/schemas/__init__.py
All Pydantic schemas for every route and service.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional, Literal
from pydantic import BaseModel, EmailStr, Field


# ── Auth ──────────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    full_name: str = Field(min_length=1, max_length=255)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=72)


class GoogleLoginRequest(BaseModel):
    id_token: str


class MessageResponse(BaseModel):
    message: str


class OTPVerifyRequest(BaseModel):
    email: EmailStr
    otp: str = Field(min_length=6, max_length=6)
    purpose: Literal["login", "register", "password_reset"]


class RegisterVerifyRequest(BaseModel):
    email: EmailStr
    otp: str = Field(min_length=6, max_length=6)
    purpose: Literal["register"] = "register"
    # User data for account creation
    password: str = Field(min_length=8, max_length=72)
    full_name: str = Field(min_length=1, max_length=255)


class AuthResponse(BaseModel):
    message: str
    session_id: Optional[str] = None
    email: Optional[EmailStr] = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    user_id: str
    email: str


class UserOut(BaseModel):
    id: str
    email: str
    full_name: str
    is_active: bool
    is_superuser: bool
    last_login_at: Optional[datetime] = None
    created_at: datetime
    model_config = {"from_attributes": True}


# ── Profile ───────────────────────────────────────────────────────────────────

class UserSkillCreate(BaseModel):
    name: str = Field(max_length=100)
    category: Optional[str] = None
    proficiency: Optional[str] = None
    years_experience: Optional[float] = None
    is_primary: bool = False


class UserSkillOut(UserSkillCreate):
    id: str
    user_id: str
    created_at: datetime
    model_config = {"from_attributes": True}


class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = Field(default=None, max_length=255)  # saved to User model
    email: Optional[str] = None                                       # saved to User model
    phone: Optional[str] = Field(default=None, max_length=20)
    location: Optional[str] = Field(default=None, max_length=255)
    linkedin_url: Optional[str] = Field(default=None, max_length=500)
    github_url: Optional[str] = Field(default=None, max_length=500)
    portfolio_url: Optional[str] = Field(default=None, max_length=500)
    experience_level: Optional[str] = None
    desired_roles: Optional[List[str]] = None
    desired_locations: Optional[List[str]] = None
    open_to_remote: Optional[bool] = None
    open_to_hybrid: Optional[bool] = None
    min_salary: Optional[int] = None
    preferred_company_size: Optional[List[str]] = None
    preferred_industries: Optional[List[str]] = None
    avoid_companies: Optional[List[str]] = None
    professional_summary: Optional[str] = None
    career_goals: Optional[str] = None
    unique_value_proposition: Optional[str] = None
    education: Optional[List[dict]] = None
    work_experience: Optional[List[dict]] = None
    projects: Optional[List[dict]] = None
    certifications: Optional[List[dict]] = None
    awards: Optional[List[dict]] = None
    publications: Optional[List[dict]] = None
    auto_apply_enabled: Optional[bool] = None
    auto_apply_threshold: Optional[int] = Field(default=None, ge=0, le=100)
    auto_apply_daily_limit: Optional[int] = Field(default=None, ge=1, le=50)
    require_apply_approval: Optional[bool] = None
    notify_new_jobs: Optional[bool] = None
    notify_applications: Optional[bool] = None
    notify_interviews: Optional[bool] = None
    notify_via_telegram: Optional[bool] = None
    notify_via_email: Optional[bool] = None
    telegram_chat_id: Optional[str] = None
    notification_email: Optional[str] = None
    linkedin_session_cookie: Optional[str] = None
    indeed_session_cookie: Optional[str] = None


class UserProfileOut(BaseModel):
    id: str
    user_id: str
    full_name: Optional[str] = None   # from User model
    email: Optional[str] = None       # from User model
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    experience_level: Optional[str] = None
    desired_roles: List[str]
    desired_locations: List[str]
    open_to_remote: bool
    open_to_hybrid: bool
    min_salary: int
    preferred_company_size: List[str]
    preferred_industries: List[str]
    avoid_companies: List[str]
    professional_summary: Optional[str] = None
    career_goals: Optional[str] = None
    unique_value_proposition: Optional[str] = None
    education: List[dict]
    work_experience: List[dict]
    projects: List[dict]
    certifications: List[dict]
    awards: List[dict]
    publications: List[dict]
    auto_apply_enabled: bool
    auto_apply_threshold: int
    auto_apply_daily_limit: int
    require_apply_approval: bool
    notify_new_jobs: bool
    notify_applications: bool
    notify_interviews: bool
    notify_via_telegram: bool
    notify_via_email: bool
    telegram_chat_id: Optional[str] = None
    notification_email: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


# ── Jobs ──────────────────────────────────────────────────────────────────────

class JobAnalysisOut(BaseModel):
    id: str
    required_skills: List[str] = []
    preferred_skills: List[str] = []
    tech_stack: List[str] = []
    ats_keywords: List[str] = []
    min_years_experience: Optional[float] = None
    max_years_experience: Optional[float] = None
    education_requirement: Optional[str] = None
    key_responsibilities: List[str] = []
    role_category: Optional[str] = None
    seniority_detected: Optional[str] = None
    is_internship: bool = False
    match_score: Optional[float] = None
    skill_match_score: Optional[float] = None
    experience_match_score: Optional[float] = None
    semantic_similarity_score: Optional[float] = None
    matching_skills: List[str] = []
    missing_skills: List[str] = []
    skill_gap_count: int = 0
    competition_level: Optional[str] = None
    interview_probability: Optional[float] = None
    job_difficulty: Optional[str] = None
    priority_score: Optional[float] = None
    estimated_salary_min: Optional[int] = None
    estimated_salary_max: Optional[int] = None
    ai_summary: Optional[str] = None
    ai_recommendation: Optional[str] = None
    model_used: Optional[str] = None
    ai_provider: Optional[str] = None
    tokens_used: Optional[int] = None
    processing_time_ms: Optional[int] = None
    created_at: datetime
    model_config = {"from_attributes": True, "protected_namespaces": ()}


class JobOut(BaseModel):
    id: str
    source: str
    source_url: str
    title: str
    company_name: str
    company_logo_url: Optional[str] = None
    description_clean: Optional[str] = None
    location: Optional[str] = None
    work_mode: str = "unknown"
    job_type: str = "full_time"
    experience_level: str = "any"
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: Optional[str] = None
    posted_at: Optional[datetime] = None
    scraped_at: datetime
    status: str = "new"
    is_active: bool = True
    applicant_count: Optional[int] = None
    easy_apply: bool = False
    analysis: Optional[JobAnalysisOut] = None
    created_at: datetime
    model_config = {"from_attributes": True}


class JobCreate(BaseModel):
    source_url: str = Field(max_length=2000)
    title: str = Field(max_length=500)
    company_name: str = Field(max_length=255)
    description_raw: Optional[str] = None
    location: Optional[str] = Field(default=None, max_length=255)
    job_type: str = "full_time"
    work_mode: str = "unknown"
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None


class JobFilter(BaseModel):
    source: Optional[str] = None
    job_type: Optional[str] = None
    work_mode: Optional[str] = None
    min_match_score: Optional[float] = None
    keyword: Optional[str] = None
    status: Optional[str] = None


# ── Applications ──────────────────────────────────────────────────────────────

class ApplicationCreate(BaseModel):
    job_id: str
    resume_id: Optional[str] = None
    cover_letter_id: Optional[str] = None
    method: str = "auto_bot"
    notes: Optional[str] = None


class ApplicationStatusUpdate(BaseModel):
    status: str
    notes: Optional[str] = None
    recruiter_name: Optional[str] = None
    recruiter_email: Optional[str] = None
    interview_date: Optional[datetime] = None
    offer_salary: Optional[int] = None


class ApplicationOut(BaseModel):
    id: str
    user_id: str
    job_id: str
    resume_id: Optional[str] = None
    job: Optional[JobOut] = None
    status: str
    method: str
    applied_at: Optional[datetime] = None
    viewed_at: Optional[datetime] = None
    shortlisted_at: Optional[datetime] = None
    offer_received_at: Optional[datetime] = None
    rejected_at: Optional[datetime] = None
    match_score_at_apply: Optional[float] = None
    job_title_snapshot: Optional[str] = None
    company_snapshot: Optional[str] = None
    recruiter_name: Optional[str] = None
    recruiter_email: Optional[str] = None
    follow_up_status: str = "none"
    follow_up_count: int = 0
    interview_date: Optional[datetime] = None
    interview_type: Optional[str] = None
    interview_notes: Optional[str] = None
    offer_salary: Optional[int] = None
    notes: Optional[str] = None
    is_starred: bool = False
    bot_error: Optional[str] = None
    retry_count: int = 0
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


class ApplicationStats(BaseModel):
    total_sent: int = 0
    pending_approval: int = 0
    recruiter_responses: int = 0
    applied: int = 0
    viewed: int = 0
    shortlisted: int = 0
    interviews: int = 0
    offers: int = 0
    rejected: int = 0
    response_rate: float = 0.0
    interview_rate: float = 0.0
    offer_rate: float = 0.0


# ── Resumes ───────────────────────────────────────────────────────────────────

class ResumeGenerateRequest(BaseModel):
    job_id: str
    base_resume_id: Optional[str] = None


class ResumeOut(BaseModel):
    id: str
    user_id: str
    name: str
    version: int = 1
    resume_type: str = "tailored"
    role_category: Optional[str] = None
    ats_score: Optional[float] = None
    keyword_coverage: Optional[float] = None
    times_used: int = 0
    response_count: int = 0
    response_rate: Optional[float] = None
    keywords_injected: List[str] = []
    is_active: bool = True
    is_default: bool = False
    file_path: Optional[str] = None
    target_job_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    download_url: Optional[str] = None
    model_config = {"from_attributes": True}


class CoverLetterGenerateRequest(BaseModel):
    job_id: str
    tone: str = "professional"
    additional_context: Optional[str] = None


class CoverLetterOut(BaseModel):
    id: str
    user_id: str
    job_id: Optional[str] = None
    application_id: Optional[str] = None
    content: str
    tone: str = "professional"
    target_company: Optional[str] = None
    target_role: Optional[str] = None
    highlighted_skills: List[str] = []
    word_count: Optional[int] = None
    file_path: Optional[str] = None
    model_used: Optional[str] = None
    tokens_used: Optional[int] = None
    created_at: datetime
    model_config = {"from_attributes": True, "protected_namespaces": ()}


# ── Interviews ────────────────────────────────────────────────────────────────

class InterviewOut(BaseModel):
    id: str
    application_id: str
    user_id: str
    interview_type: str
    scheduled_at: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    platform: Optional[str] = None
    meeting_link: Optional[str] = None
    study_topics: List[str] = []
    completed_at: Optional[datetime] = None
    outcome: Optional[str] = None
    user_notes: Optional[str] = None
    created_at: datetime
    model_config = {"from_attributes": True}


# ── Agent / Tasks ─────────────────────────────────────────────────────────────

class AgentTaskOut(BaseModel):
    id: str
    task_type: str
    status: str
    result: Optional[Any] = None
    error: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class AgentStatusResponse(BaseModel):
    is_running: bool
    current_task: Optional[str] = None
    last_run: Optional[datetime] = None
    jobs_found_today: int = 0
    applications_today: int = 0
    active_workflow: Optional[WorkflowExecutionOut] = None


class ManualAgentRunRequest(BaseModel):
    task_type: str  # Required - which task to run
    payload: Optional[dict] = None
    scrape_linkedin: bool = True
    scrape_indeed: bool = True
    scrape_internshala: bool = True
    scrape_wellfound: bool = True
    analyze_jobs: bool = True
    max_jobs: Optional[int] = None

    model_config = {"extra": "ignore"}


class AgentCycleResponse(BaseModel):
    task_id: str
    status: str
    message: str


# ── Workflow Pipeline ─────────────────────────────────────────────────────────

class WorkflowStepOut(BaseModel):
    id: str
    step_index: int
    step_type: str
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result_summary: Optional[dict] = None
    error_message: Optional[str] = None
    tokens_used: Optional[int] = None
    model_config = {"from_attributes": True}


class WorkflowExecutionOut(BaseModel):
    id: str
    user_id: str
    status: str
    current_step_index: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    result_summary: Optional[dict] = None
    error_message: Optional[str] = None
    steps: List[WorkflowStepOut] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


class WorkflowRunResponse(BaseModel):
    workflow_id: str
    status: str
    message: str = "Workflow started"


# ── Chat ──────────────────────────────────────────────────────────────────────

class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    history: List[ChatMessage] = Field(default_factory=list)
    conversation_history: List[ChatMessage] = Field(default_factory=list)
    persona: Optional[str] = Field(default="general", description="AI persona: general, career_coach, resume_expert, job_scout, application_assistant")

class ChatResponse(BaseModel):
    response: str
    actions_taken: List[str] = Field(default_factory=list)


# ── Shared ────────────────────────────────────────────────────────────────────

class PaginatedResponse(BaseModel):
    total: int = 0
    page: int = 1
    page_size: int = 20
    pages: int = 0
    items: List[Any] = []


class MessageResponse(BaseModel):
    message: str


# ── Dashboard & Market ────────────────────────────────────────────────────────

class DashboardStats(BaseModel):
    total_jobs: int = 0
    jobs_today: int = 0
    high_match_jobs: int = 0
    total_applications: int = 0
    applications_today: int = 0
    pending_approval: int = 0
    interviews_scheduled: int = 0
    offers_received: int = 0
    response_rate: float = 0.0
    top_skill_gaps: List[dict] = []
    recent_activity: List[dict] = []


class MarketInsightResponse(BaseModel):
    snapshot_date: Optional[datetime] = None
    total_jobs_analyzed: int = 0
    top_skills: List[str] = []
    top_companies_hiring: List[str] = []
    emerging_roles: List[str] = []
    salary_data: Optional[dict] = None
    by_work_mode: Optional[dict] = None


class SkillGapOut(BaseModel):
    id: str
    skill_name: str
    demand_count: int = 0
    priority: Optional[str] = None
    learning_resources: Optional[List[str]] = None
    created_at: datetime
    model_config = {"from_attributes": True}

class ManualAgentRunRequest(BaseModel):
    task_type: str = ""  # Required - which task to run
    payload: Optional[dict] = None
    scrape_linkedin: bool = True
    scrape_indeed: bool = True
    scrape_internshala: bool = True
    scrape_wellfound: bool = True
    analyze_jobs: bool = True
    max_jobs: Optional[int] = None

    model_config = {"extra": "ignore"}