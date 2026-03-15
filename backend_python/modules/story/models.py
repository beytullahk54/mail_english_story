from datetime import datetime
from pydantic import BaseModel
from sqlalchemy import Integer, String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from database import Base


class Story(Base):
    __tablename__ = "stories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    topic: Mapped[str] = mapped_column(String(100), nullable=False)
    level: Mapped[str] = mapped_column(String(20), nullable=False)
    language: Mapped[str] = mapped_column(String(20), nullable=False, default="English")
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class StoryRequest(BaseModel):
    topic: str
    level: str = "beginner"
    language: str = "English"
    word_count: int = 200


class StoryResponse(BaseModel):
    story: str
    topic: str
    level: str
    language: str