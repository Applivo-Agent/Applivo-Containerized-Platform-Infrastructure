from sqlalchemy import Column, String, Integer, DateTime, func
from app.core.database import Base
from app.models.base import UUIDMixin


class ChatUsage(Base, UUIDMixin):
    __tablename__ = "chat_usage"

    user_id = Column(String(36), nullable=False, index=True)
    month = Column(String(7), nullable=False, index=True)
    message_count = Column(Integer, default=0, nullable=False)