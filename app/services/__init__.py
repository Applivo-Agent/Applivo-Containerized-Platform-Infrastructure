"""
app/services/__init__.py
─────────────────────────
Exports all service classes for easy importing.
"""

from app.services.job_analyzer import JobAnalyzerService
from app.services.notification_service import NotificationService
from app.services.resume_service import ResumeService
from app.services.cover_letter_service import CoverLetterService
from app.services.application_service import ApplicationService
from app.services.follow_up_service import FollowUpService
from app.services.market_service import MarketIntelligenceService
from app.services.interview_service import InterviewPrepService
from app.services.ai_assistant import CareerAssistant

__all__ = [
    "JobAnalyzerService",
    "NotificationService",
    "ResumeService",
    "CoverLetterService",
    "ApplicationService",
    "FollowUpService",
    "MarketIntelligenceService",
    "InterviewPrepService",
    "CareerAssistant",
]
