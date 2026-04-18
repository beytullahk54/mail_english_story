from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from database import get_db
from security import verify_token
from .models import BlogListResponse, BlogPostCreate, BlogPostDetail
from .service import BlogService

router = APIRouter(prefix="/blog", tags=["blog"])


@router.get("", response_model=BlogListResponse, status_code=status.HTTP_200_OK)
def list_posts(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=50),
    tag: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    return BlogService().get_posts(db, page=page, page_size=page_size, tag=tag)


@router.get("/{slug}", response_model=BlogPostDetail, status_code=status.HTTP_200_OK)
def get_post(slug: str, db: Session = Depends(get_db)):
    post = BlogService().get_post_by_slug(db, slug)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post


@router.post("", status_code=status.HTTP_201_CREATED, dependencies=[Depends(verify_token)])
def create_post(data: BlogPostCreate, db: Session = Depends(get_db)):
    return BlogService().create_post(db, data)


@router.post("/seed", status_code=status.HTTP_200_OK, dependencies=[Depends(verify_token)])
def seed_posts(db: Session = Depends(get_db)):
    count = BlogService().seed_posts(db)
    return {"seeded": count, "message": f"{count} sample posts created." if count else "Posts already exist."}
