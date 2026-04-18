import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from sqlalchemy import text

from config import config
from database import Base, engine
from modules.subscriber.router import router as subscriber_router
from modules.story.router import router as story_router
from modules.mailer.router import router as mailer_router
from modules.mailer.models import MailLog  # noqa: F401 — tablonun create_all'a dahil olması için
from modules.blog.router import router as blog_router
from modules.blog.models import BlogPost  # noqa: F401 — create_all'a dahil olması için

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
        conn.commit()
        print("[Migration] Kolonlar kontrol edildi / eklendi.")

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


@app.get("/health")
def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(config.SERVER_PORT), reload=True)
