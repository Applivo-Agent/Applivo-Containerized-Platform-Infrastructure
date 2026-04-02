"""
app/models/__init__.py
Import all models here so Alembic can detect them all.
"""
from app.core.database import Base  # noqa: F401
from app.models.base import TimestampMixin, UUIDMixin, SoftDeleteMixin  # noqa: F401
from app.models.user import User, UserProfile, UserSkill  # noqa: F401
from app.models.job import Job, JobAnalysis  # noqa: F401
from app.models.resume import Resume, CoverLetter  # noqa: F401
from app.models.application import Application, ApplicationEvent  # noqa: F401
from app.models.interview import (  # noqa: F401
    Interview, MockInterviewSession, Recruiter, RecruiterMessage,
    Notification, AgentTask, SkillGap, MarketSnapshot, LearningPlan, GeneratedProject,
)
from app.models.credential import CredentialVault, CredentialUseLog  # noqa: F401
from app.models.consent import UserConsent, ConsentVersion  # noqa: F401
from app.models.audit import AuditLog  # noqa: F401
from app.models.subscription import Subscription, Payment  # noqa: F401
from app.models.cookie import PlatformCookie  # noqa: F401

__all__ = [
    "Base",
    "User", "UserProfile", "UserSkill",
    "Job", "JobAnalysis",
    "Resume", "CoverLetter",
    "Application", "ApplicationEvent",
    "Interview", "MockInterviewSession", "Recruiter", "RecruiterMessage",
    "Notification", "AgentTask", "SkillGap", "MarketSnapshot",
    "LearningPlan", "GeneratedProject",
    "CredentialVault", "CredentialUseLog",
    "UserConsent", "ConsentVersion",
    "AuditLog",
    "Subscription", "Payment",
    "PlatformCookie",
]
