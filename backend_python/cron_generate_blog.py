"""
Günlük blog yazısı üretim scripti.
Crontab örneği (her gün sabah 08:00):
  0 8 * * * cd /path/to/backend_python && python cron_generate_blog.py >> /var/log/blog_gen.log 2>&1
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from database import SessionLocal
from modules.blog.generator import BlogGenerator, read_next_topic


def main():
    db = SessionLocal()
    try:
        topic = read_next_topic(db)
        if not topic:
            print("[blog-gen] Bekleyen konu yok. topics.md dosyasına yeni konu ekleyin.")
            return

        topic_tr, topic_en = topic
        print(f"[blog-gen] Konu: {topic_tr} | {topic_en}")

        post = BlogGenerator().generate_and_save(db)
        if post:
            print(f"[blog-gen] ✓ Yazı yayınlandı: [{post.id}] {post.title}")
        else:
            print("[blog-gen] Yazı oluşturulamadı.")
    except Exception as e:
        import traceback
        print(f"[blog-gen] HATA: {e}")
        print(traceback.format_exc())
    finally:
        db.close()


if __name__ == "__main__":
    main()
