from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, Text, DateTime
from sqlalchemy.sql import func
from database import Base


class MailLog(Base):
    __tablename__ = "mail_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    topic: Mapped[str] = mapped_column(String(100), nullable=False)
    total_sent: Mapped[int] = mapped_column(Integer, default=0)
    total_failed: Mapped[int] = mapped_column(Integer, default=0)
    recipients: Mapped[str | None] = mapped_column(Text, nullable=True)  # virgülle ayrılmış e-postalar
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class SendStoryRequest(BaseModel):
    story: str
    topic: str
    level: str
    language: str = "English"
    level_filter: Optional[str] = None
    language_filter: Optional[str] = None


class SendStoryResponse(BaseModel):
    sent: int
    failed: int
    recipients: List[str]
