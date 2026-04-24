"""
Günlük blog yazısı üretim scripti.

Railway Cron kurulumu:
  Dashboard → Deployments → Cron Jobs → "0 8 * * *" → "python cron_generate_blog.py"

Crontab örneği (her gün sabah 08:00):
  0 8 * * * cd /path/to/backend_python && python cron_generate_blog.py >> /var/log/blog_gen.log 2>&1
"""
import sys
import os
import time
import traceback

sys.path.insert(0, os.path.dirname(__file__))

from database import SessionLocal
from modules.blog.generator import BlogGenerator, read_next_topic
from modules.blog.models import BlogGenerationJob


def main():
    db = SessionLocal()
    start = time.time()
    job = None
    try:
        topic = read_next_topic(db)
        if not topic:
            print("[blog-gen] Bekleyen konu yok. topics.md dosyasına yeni konu ekleyin.")
            return

        topic_tr, topic_en = topic
        topic_key = f"{topic_tr} | {topic_en}"
        print(f"[blog-gen] Konu: {topic_key}")

        job = BlogGenerationJob(topic=topic_key, status="running")
        db.add(job)
        db.commit()
        db.refresh(job)

        post = BlogGenerator().generate_and_save(db)
        elapsed = round(time.time() - start, 1)

        db.expire(job)
        job = db.query(BlogGenerationJob).filter(BlogGenerationJob.id == job.id).first()

        if post:
            job.status = "done"
            job.post_id = post.id
            db.commit()
            print(f"[blog-gen] ✓ Yazı yayınlandı ({elapsed}s): [{post.id}] {post.title}")
        else:
            job.status = "idle"
            db.commit()
            print(f"[blog-gen] Yazı oluşturulamadı ({elapsed}s).")

    except Exception as e:
        elapsed = round(time.time() - start, 1)
        print(f"[blog-gen] HATA ({elapsed}s): {e}")
        print(traceback.format_exc())
        try:
            if job:
                db.rollback()
                job = db.query(BlogGenerationJob).filter(BlogGenerationJob.id == job.id).first()
                if job:
                    job.status = "error"
                    job.error = str(e)[:500]
                    db.commit()
        except Exception as inner:
            print(f"[blog-gen] Job güncelleme hatası: {inner}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
