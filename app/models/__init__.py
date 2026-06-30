"""
app/models/__init__.py
Import all models here so Alembic can detect them all.
"""
from app.core.database import Base  # noqa: F401
from app.models.user_settings import UserSettings, SettingsAuditLog  # noqa: F401
from app.models.base import TimestampMixin, UUIDMixin, SoftDeleteMixin  # noqa: F401
from app.models.user import User, UserProfile, UserSkill, UserSession  # noqa: F401
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
from app.models.chat_usage import ChatUsage  # noqa: F401
from app.models.platform_message import PlatformMessage  # noqa: F401
from app.models.ai_usage import AIUsageLog  # noqa: F401
from app.models.chat_message import ChatMessage  # noqa: F401
from app.models.outreach import (  # noqa: F401
    OutreachCompany, OutreachIntelligence, OutreachContact,
    OutreachCampaign, OutreachEmail, OutreachConversation,
    OutreachEmailConnector, OutreachGitHubConnector, OutreachFollowUp,
)

__all__ = [
    "UserSettings", "SettingsAuditLog",
    "Base",
    "User", "UserProfile", "UserSkill", "UserSession",
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
    "ChatUsage",
    "PlatformMessage",
    "ChatMessage",
    "AIUsageLog",
    "OutreachCompany", "OutreachIntelligence", "OutreachContact",
    "OutreachCampaign", "OutreachEmail", "OutreachConversation",
    "OutreachEmailConnector", "OutreachGitHubConnector", "OutreachFollowUp",
]
