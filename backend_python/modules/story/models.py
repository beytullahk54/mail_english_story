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
    image_path: Mapped[str | None] = mapped_column(String(255), nullable=True, default=None)
    view_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class StoryRequest(BaseModel):
    topic: str
    level: str = "beginner"
    language: str = "English"
    word_count: int = 200


class StoryResponse(BaseModel):
    id: int | None = None
    story: str
    topic: str
    level: str
    language: str


class StoryItem(BaseModel):
    id: int
    topic: str
    level: str
    language: str
    content: str
    image_path: str | None = None
    view_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True


class StoriesListResponse(BaseModel):
    items: list[StoryItem]
    total: int
    page: int
    page_size: int