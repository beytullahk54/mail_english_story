"""
Tek seferlik migrasyon: mevcut blog_posts kayıtlarına topic_key atar.

Sunucuda git pull ÖNCESINDE çalıştırın:
    cd backend_python && python migrate_topic_keys.py

Nasıl çalışır:
  1. topics.md'deki tüm [x] satırlarını okur
  2. Her birinin slug'ını hesaplar
  3. DB'de eşleşen post varsa topic_key kolonunu günceller

Sonrasında bu script'e gerek kalmaz; yeni postlar topic_key'i otomatik kaydeder.
"""

import re
import sys
import os
from pathlib import Path

# Proje kökünü Python path'ine ekle
sys.path.insert(0, str(Path(__file__).resolve().parent))

from database import SessionLocal
from modules.blog.models import BlogPost
from modules.blog.generator import _to_slug, TOPICS_FILE


def main():
    if not os.path.exists(TOPICS_FILE):
        print(f"HATA: topics.md bulunamadı: {TOPICS_FILE}")
        return

    with open(TOPICS_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    done_topics = []
    for line in lines:
        match = re.match(
            r"^- \[x\] (.+?) \| (.+?)(?:\s+\(\d{4}-\d{2}-\d{2}\))?$",
            line.strip(),
        )
        if match:
            topic_tr = match.group(1).strip()
            topic_en = match.group(2).strip()
            done_topics.append((topic_tr, topic_en))

    if not done_topics:
        print("topics.md'de [x] ile işaretlenmiş konu bulunamadı.")
        return

    db = SessionLocal()
    updated = 0
    skipped = 0

    try:
        for topic_tr, topic_en in done_topics:
            key = f"{topic_tr} | {topic_en}"
            slug = _to_slug(topic_en)

            # topic_key zaten dolu olan kayıtları atla
            post = db.query(BlogPost).filter(BlogPost.topic_key == key).first()
            if post:
                skipped += 1
                continue

            # Slug ile eşleştir (Gemini bazen farklı slug üretebilir, en yakın eşleşme)
            post = db.query(BlogPost).filter(
                BlogPost.slug == slug,
                BlogPost.topic_key.is_(None),
            ).first()

            if not post:
                # Başlık içinde topic_en kelimelerini ara (slug uyuşmazlığı için)
                words = topic_en.lower().split()[:3]
                for p in db.query(BlogPost).filter(BlogPost.topic_key.is_(None)).all():
                    if all(w in p.title.lower() for w in words):
                        post = p
                        break

            if post:
                post.topic_key = key
                updated += 1
                print(f"  ✓ Güncellendi: [{post.id}] {post.title[:60]}")
            else:
                print(f"  ? Eşleşme bulunamadı: {key}")

        db.commit()
    finally:
        db.close()

    print(f"\nTamamlandı: {updated} güncellendi, {skipped} zaten doluydu.")


if __name__ == "__main__":
    main()
