import os
import uvicorn
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles

from sqlalchemy import text
from sqlalchemy.orm import Session

from config import config
from database import Base, engine, get_db
from modules.subscriber.router import router as subscriber_router
from modules.story.router import router as story_router
from modules.mailer.router import router as mailer_router
from modules.mailer.models import MailLog  # noqa: F401 — tablonun create_all'a dahil olması için
from modules.blog.router import router as blog_router
from modules.blog.models import BlogPost, BlogGenerationJob  # noqa: F401 — create_all'a dahil olması için
from modules.admin.router import router as admin_router
from modules.book_summary.router import router as book_summary_router
from modules.book_summary.models import PsychologyBook  # noqa: F401 — create_all'a dahil olması için

# Görsel klasörünü oluştur
IMAGES_DIR = os.path.join(os.path.dirname(__file__), "static", "images")
os.makedirs(IMAGES_DIR, exist_ok=True)

# Auto migrate: create tables
Base.metadata.create_all(bind=engine)

# Manuel migration: eksik kolonları ekle
def run_migrations():
    with engine.connect() as conn:
        conn.execute(text(
            "ALTER TABLE subscribers "
            "ADD COLUMN IF NOT EXISTS language VARCHAR(20) DEFAULT 'English';"
        ))
        conn.execute(text(
            "ALTER TABLE stories "
            "ADD COLUMN IF NOT EXISTS image_path VARCHAR(255);"
        ))
        conn.execute(text(
            "ALTER TABLE stories "
            "ADD COLUMN IF NOT EXISTS view_count INTEGER NOT NULL DEFAULT 0;"
        ))
        conn.execute(text(
            "ALTER TABLE blog_posts "
            "ADD COLUMN IF NOT EXISTS topic_key VARCHAR(500);"
        ))
        conn.commit()
        print("[Migration] Kolonlar kontrol edildi / eklendi.")

    # topics.md'deki [x] satırlarını DB'deki topic_key kolonuna aktar
    _migrate_topic_keys_from_file()


def _migrate_topic_keys_from_file():
    """topics.md'deki [x] satırlarını blog_posts.topic_key kolonuna aktar.

    Her deploy'da çalışır ama sadece topic_key'i NULL olan kayıtları günceller.
    Railway gibi otomatik deploy ortamlarında güvenli çalışması için tasarlandı.
    """
    import re as _re
    from modules.blog.generator import TOPICS_FILE, _to_slug
    from modules.blog.models import BlogPost as _BlogPost

    if not os.path.exists(TOPICS_FILE):
        return

    with open(TOPICS_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    done_topics = []
    for line in lines:
        match = _re.match(
            r"^- \[x\] (.+?) \| (.+?)(?:\s+\(\d{4}-\d{2}-\d{2}\))?$",
            line.strip(),
        )
        if match:
            done_topics.append((match.group(1).strip(), match.group(2).strip()))

    if not done_topics:
        return

    from database import SessionLocal
    db = SessionLocal()
    updated = 0
    try:
        for topic_tr, topic_en in done_topics:
            key = f"{topic_tr} | {topic_en}"
            if db.query(_BlogPost).filter(_BlogPost.topic_key == key).first():
                continue  # zaten işlenmiş
            post = db.query(_BlogPost).filter(
                _BlogPost.slug == _to_slug(topic_en),
                _BlogPost.topic_key.is_(None),
            ).first()
            if post:
                post.topic_key = key
                updated += 1
        if updated:
            db.commit()
            print(f"[Migration] {updated} blog yazısına topic_key atandı.")
    finally:
        db.close()


run_migrations()

app = FastAPI(redirect_slashes=False)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")

app.include_router(subscriber_router, prefix="/api/v1")
app.include_router(story_router, prefix="/api/v1")
app.include_router(mailer_router, prefix="/api/v1")
app.include_router(blog_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")
app.include_router(book_summary_router, prefix="/api/v1")


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/sitemap.xml", response_class=Response)
def sitemap(db: Session = Depends(get_db)):
    from modules.blog.models import BlogPost

    site_url = (config.APP_BASE_URL or "https://englishstory.kodsey.com").rstrip("/")

    static_urls = [
        {"loc": f"{site_url}/", "changefreq": "weekly", "priority": "1.0"},
        {"loc": f"{site_url}/en/blog", "changefreq": "daily", "priority": "0.9"},
        {"loc": f"{site_url}/tr/blog", "changefreq": "daily", "priority": "0.9"},
        {"loc": f"{site_url}/stories", "changefreq": "daily", "priority": "0.8"},
        {"loc": f"{site_url}/story", "changefreq": "monthly", "priority": "0.5"},
    ]

    posts = (
        db.query(BlogPost.slug, BlogPost.slug_tr, BlogPost.updated_at)
        .filter(BlogPost.published == True)  # noqa: E712
        .order_by(BlogPost.published_at.desc())
        .all()
    )

    url_entries = []

    for entry in static_urls:
        url_entries.append(
            f"  <url>\n"
            f"    <loc>{entry['loc']}</loc>\n"
            f"    <changefreq>{entry['changefreq']}</changefreq>\n"
            f"    <priority>{entry['priority']}</priority>\n"
            f"  </url>"
        )

    for slug, slug_tr, updated_at in posts:
        lastmod = updated_at.strftime("%Y-%m-%d") if updated_at else ""
        lastmod_tag = f"\n    <lastmod>{lastmod}</lastmod>" if lastmod else ""

        # English URL
        url_entries.append(
            f"  <url>\n"
            f"    <loc>{site_url}/en/blog/{slug}</loc>{lastmod_tag}\n"
            f"    <changefreq>monthly</changefreq>\n"
            f"    <priority>0.7</priority>\n"
            f"  </url>"
        )

        # Turkish URL (only if slug_tr exists)
        if slug_tr:
            url_entries.append(
                f"  <url>\n"
                f"    <loc>{site_url}/tr/blog/{slug_tr}</loc>{lastmod_tag}\n"
                f"    <changefreq>monthly</changefreq>\n"
                f"    <priority>0.7</priority>\n"
                f"  </url>"
            )

    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(url_entries)
        + "\n</urlset>"
    )

    return Response(content=xml, media_type="application/xml")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(config.SERVER_PORT), reload=True)
