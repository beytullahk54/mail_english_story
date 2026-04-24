from datetime import datetime
from pydantic import BaseModel
from sqlalchemy import Boolean, Integer, String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from database import Base


class BlogGenerationJob(Base):
    __tablename__ = "blog_generation_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    topic: Mapped[str | None] = mapped_column(String(500), nullable=True)
    # pending → running → done | error | idle
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    post_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class BlogPost(Base):
    __tablename__ = "blog_posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    title_tr: Mapped[str | None] = mapped_column(String(200), nullable=True)
    slug: Mapped[str] = mapped_column(String(200), unique=True, nullable=False, index=True)
    slug_tr: Mapped[str | None] = mapped_column(String(200), unique=True, nullable=True, index=True)
    excerpt: Mapped[str] = mapped_column(Text, nullable=False)
    excerpt_tr: Mapped[str | None] = mapped_column(Text, nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    content_tr: Mapped[str | None] = mapped_column(Text, nullable=True)
    author: Mapped[str] = mapped_column(String(100), nullable=False, default="English Story Team")
    cover_image: Mapped[str | None] = mapped_column(String(500), nullable=True)
    tags: Mapped[str | None] = mapped_column(Text, nullable=True)
    meta_description: Mapped[str | None] = mapped_column(String(300), nullable=True)
    meta_description_tr: Mapped[str | None] = mapped_column(String(300), nullable=True)
    topic_key: Mapped[str | None] = mapped_column(String(500), nullable=True, index=True)
    published: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class BlogPostCreate(BaseModel):
    title: str
    title_tr: str | None = None
    slug: str
    slug_tr: str | None = None
    excerpt: str
    excerpt_tr: str | None = None
    content: str
    content_tr: str | None = None
    author: str = "English Story Team"
    cover_image: str | None = None
    tags: list[str] | None = None
    meta_description: str | None = None
    meta_description_tr: str | None = None
    published: bool = True


class BlogPostItem(BaseModel):
    id: int
    title: str
    title_tr: str | None = None
    slug: str
    slug_tr: str | None = None
    excerpt: str
    excerpt_tr: str | None = None
    author: str
    cover_image: str | None = None
    tags: list[str] = []
    published_at: datetime

    class Config:
        from_attributes = True


class BlogPostDetail(BaseModel):
    id: int
    title: str
    title_tr: str | None = None
    slug: str
    slug_tr: str | None = None
    excerpt: str
    excerpt_tr: str | None = None
    content: str
    content_tr: str | None = None
    author: str
    cover_image: str | None = None
    tags: list[str] = []
    meta_description: str | None = None
    meta_description_tr: str | None = None
    published_at: datetime

    class Config:
        from_attributes = True


class BlogListResponse(BaseModel):
    items: list[BlogPostItem]
    total: int
    page: int
    page_size: int
