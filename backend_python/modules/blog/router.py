from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from database import get_db
from security import verify_token
from .models import BlogListResponse, BlogPostCreate, BlogPostDetail, BlogPostItem
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


# Admin: list all posts (including unpublished)
@router.get("/admin/all", response_model=BlogListResponse, status_code=status.HTTP_200_OK,
            dependencies=[Depends(verify_token)])
def list_all_posts(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return BlogService().get_all_posts(db, page=page, page_size=page_size)


@router.get("/{slug}", response_model=BlogPostDetail, status_code=status.HTTP_200_OK)
def get_post(slug: str, db: Session = Depends(get_db)):
    post = BlogService().get_post_by_slug(db, slug)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post


@router.post("", status_code=status.HTTP_201_CREATED, dependencies=[Depends(verify_token)])
def create_post(data: BlogPostCreate, db: Session = Depends(get_db)):
    return BlogService().create_post(db, data)


@router.put("/{post_id}", response_model=BlogPostDetail, status_code=status.HTTP_200_OK,
            dependencies=[Depends(verify_token)])
def update_post(post_id: int, data: BlogPostCreate, db: Session = Depends(get_db)):
    post = BlogService().update_post(db, post_id, data)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post


@router.delete("/{post_id}", status_code=status.HTTP_200_OK, dependencies=[Depends(verify_token)])
def delete_post(post_id: int, db: Session = Depends(get_db)):
    ok = BlogService().delete_post(db, post_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return {"message": "Deleted"}


@router.post("/generate-next", status_code=status.HTTP_200_OK, dependencies=[Depends(verify_token)])
def generate_next_post(db: Session = Depends(get_db)):
    """topics.md'deki bir sonraki konuyu Gemini ile üretir ve yayınlar."""
    from .generator import BlogGenerator, read_next_topic
    topic = read_next_topic()
    if not topic:
        return {"message": "Bekleyen konu yok. topics.md dosyasına yeni konu ekleyin."}
    try:
        post = BlogGenerator().generate_and_save(db)
        if not post:
            return {"message": "Oluşturulamadı."}
        return {
            "message": "Yazı oluşturuldu.",
            "id": post.id,
            "title": post.title,
            "slug": post.slug,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Üretim hatası: {str(e)}")


@router.post("/seed", status_code=status.HTTP_200_OK, dependencies=[Depends(verify_token)])
def seed_posts(db: Session = Depends(get_db)):
    count = BlogService().seed_posts(db)
    return {"seeded": count, "message": f"{count} sample posts created." if count else "Posts already exist."}
