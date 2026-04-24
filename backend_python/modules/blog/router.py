import re
import os
import threading
import traceback
import time

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from database import get_db, SessionLocal
from security import verify_token
from .models import BlogGenerationJob, BlogListResponse, BlogPostCreate, BlogPostDetail, BlogPostItem
from .service import BlogService

router = APIRouter(prefix="/blog", tags=["blog"])

# ---------------------------------------------------------------------------
# Public: list published posts
# ---------------------------------------------------------------------------

@router.get("", response_model=BlogListResponse, status_code=status.HTTP_200_OK)
def list_posts(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=50),
    tag: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    return BlogService().get_posts(db, page=page, page_size=page_size, tag=tag)


# ---------------------------------------------------------------------------
# Admin: list all posts (including unpublished)
# ---------------------------------------------------------------------------

@router.get("/admin/all", response_model=BlogListResponse, status_code=status.HTTP_200_OK,
            dependencies=[Depends(verify_token)])
def list_all_posts(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return BlogService().get_all_posts(db, page=page, page_size=page_size)


# ---------------------------------------------------------------------------
# Generation status — must be defined BEFORE /{slug} wildcard
# ---------------------------------------------------------------------------

@router.get("/generation-status", status_code=status.HTTP_200_OK, dependencies=[Depends(verify_token)])
def get_generation_status(db: Session = Depends(get_db)):
    """En son üretim işinin durumunu döndürür."""
    job = db.query(BlogGenerationJob).order_by(BlogGenerationJob.id.desc()).first()
    if not job:
        return {"status": "idle", "topic": None, "job_id": None, "error": None, "post_id": None}

    # Stuck job detection: running > 10 min → error
    if job.status == "running" and job.updated_at:
        from datetime import timezone
        now = time.time()
        updated_ts = job.updated_at.timestamp()
        if now - updated_ts > 600:
            job.status = "error"
            job.error = "İşlem 10 dakikadan uzun sürdü, zaman aşımı."
            db.commit()

    return {
        "status": job.status,
        "topic": job.topic,
        "job_id": job.id,
        "error": job.error,
        "post_id": job.post_id,
        "created_at": job.created_at.isoformat() if job.created_at else None,
    }


# ---------------------------------------------------------------------------
# topics/status — two segments after prefix, no conflict with /{slug}
# ---------------------------------------------------------------------------

@router.get("/topics/status", status_code=status.HTTP_200_OK, dependencies=[Depends(verify_token)])
def topics_status(db: Session = Depends(get_db)):
    """topics.md'deki tüm konuların durumunu gösterir."""
    from .generator import TOPICS_FILE
    from .models import BlogPost

    if not os.path.exists(TOPICS_FILE):
        raise HTTPException(status_code=404, detail="topics.md bulunamadı")

    with open(TOPICS_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    done_keys = {
        row.topic_key
        for row in db.query(BlogPost.topic_key).filter(BlogPost.topic_key.isnot(None)).all()
    }

    done, pending = [], []
    for line in lines:
        stripped = line.strip()
        m = re.match(r"^- \[x\] (.+?) \| (.+?)(?:\s+\((\d{4}-\d{2}-\d{2})\))?$", stripped)
        if m:
            key = f"{m.group(1).strip()} | {m.group(2).strip()}"
            done.append({"topic": key, "date": m.group(3), "source": "topics.md"})
            continue
        m = re.match(r"^- \[ \] (.+?) \| (.+?)(?:\s+\(\d{4}-\d{2}-\d{2}\))?$", stripped)
        if m:
            key = f"{m.group(1).strip()} | {m.group(2).strip()}"
            if key in done_keys:
                done.append({"topic": key, "source": "db"})
            else:
                pending.append(key)

    return {
        "done_count": len(done),
        "pending_count": len(pending),
        "done": done,
        "pending": pending,
        "next": pending[0] if pending else None,
    }


# ---------------------------------------------------------------------------
# Public: get single post by slug — wildcard, must be last among GETs
# ---------------------------------------------------------------------------

@router.get("/{slug}", response_model=BlogPostDetail, status_code=status.HTTP_200_OK)
def get_post(slug: str, db: Session = Depends(get_db)):
    post = BlogService().get_post_by_slug(db, slug)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post


# ---------------------------------------------------------------------------
# Admin: create / update / delete
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Generation
# ---------------------------------------------------------------------------

def _run_blog_generation_job(job_id: int) -> None:
    """Ayrı thread'de çalışır. Job durumunu DB'ye yazar."""
    from .generator import BlogGenerator

    db = SessionLocal()
    start = time.time()
    try:
        job = db.query(BlogGenerationJob).filter(BlogGenerationJob.id == job_id).first()
        if not job:
            return

        job.status = "running"
        db.commit()
        print(f"[BlogGen] Job #{job_id} başladı: {job.topic}")

        post = BlogGenerator().generate_and_save(db)
        elapsed = round(time.time() - start, 1)

        # Refresh job after generate_and_save (it might have changed the session)
        db.expire(job)
        job = db.query(BlogGenerationJob).filter(BlogGenerationJob.id == job_id).first()

        if post:
            job.status = "done"
            job.post_id = post.id
            print(f"[BlogGen] ✓ Job #{job_id} tamamlandı ({elapsed}s): [{post.id}] {post.title}")
        else:
            job.status = "idle"
            print(f"[BlogGen] Job #{job_id}: Bekleyen konu bulunamadı ({elapsed}s).")
        db.commit()

    except Exception as e:
        elapsed = round(time.time() - start, 1)
        print(f"[BlogGen] HATA Job #{job_id} ({elapsed}s): {e}")
        print(traceback.format_exc())
        try:
            db.rollback()
            job = db.query(BlogGenerationJob).filter(BlogGenerationJob.id == job_id).first()
            if job:
                job.status = "error"
                job.error = str(e)[:500]
                db.commit()
        except Exception as inner:
            print(f"[BlogGen] Job durum güncelleme hatası: {inner}")
    finally:
        db.close()


@router.post("/generate-next", status_code=status.HTTP_202_ACCEPTED, dependencies=[Depends(verify_token)])
def generate_next_post(db: Session = Depends(get_db)):
    """
    topics.md'deki sıradaki konuyu Gemini ile üretir.
    Üretim ayrı bir thread'de çalışır; iş durumu blog_generation_jobs tablosunda takip edilir.
    """
    from .generator import read_next_topic

    # Zaten çalışan bir iş var mı?
    active = db.query(BlogGenerationJob).filter(
        BlogGenerationJob.status.in_(["pending", "running"])
    ).order_by(BlogGenerationJob.id.desc()).first()
    if active:
        return {
            "message": "Zaten bir üretim devam ediyor.",
            "status": "already_running",
            "job_id": active.id,
            "topic": active.topic,
        }

    topic = read_next_topic(db)
    if not topic:
        return {"message": "Bekleyen konu yok. topics.md dosyasına yeni konu ekleyin.", "status": "idle"}

    topic_tr, topic_en = topic
    topic_key = f"{topic_tr} | {topic_en}"

    job = BlogGenerationJob(topic=topic_key, status="pending")
    db.add(job)
    db.commit()
    db.refresh(job)

    # daemon=False: request bitse de thread çalışmaya devam eder
    t = threading.Thread(target=_run_blog_generation_job, args=(job.id,), daemon=False)
    t.start()

    return {
        "message": "Üretim başlatıldı, arka planda çalışıyor.",
        "status": "started",
        "job_id": job.id,
        "topic": topic_key,
    }


@router.post("/seed", status_code=status.HTTP_200_OK, dependencies=[Depends(verify_token)])
def seed_posts(db: Session = Depends(get_db)):
    count = BlogService().seed_posts(db)
    return {"seeded": count, "message": f"{count} sample posts created." if count else "Posts already exist."}
