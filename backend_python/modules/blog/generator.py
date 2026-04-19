import json
import re
import os
from datetime import date
from pathlib import Path
from google import genai
from sqlalchemy.orm import Session
from config import config
from .models import BlogPost

# Path(__file__).resolve() her zaman mutlak path verir, çalışma dizininden bağımsız
TOPICS_FILE = str(Path(__file__).resolve().parent.parent.parent / "topics.md")
TOPICS_DONE_FILE = str(Path(__file__).resolve().parent.parent.parent / ".topics_done")

PROMPT = """You are a professional bilingual content writer specializing in English language learning.

Write a complete blog article about the topic below.
Return ONLY a valid JSON object — no markdown, no explanation, no code fences.

Topic (TR): {topic_tr}
Topic (EN): {topic_en}

JSON structure to return:
{{
  "title": "English article title (compelling, SEO-friendly)",
  "title_tr": "Türkçe makale başlığı",
  "slug": "english-url-slug-max-60-chars",
  "slug_tr": "turkce-url-slug-max-60-chars",
  "excerpt": "English excerpt, 1-2 sentences, max 200 chars",
  "excerpt_tr": "Türkçe özet, 1-2 cümle, max 200 karakter",
  "meta_description": "English SEO meta description, max 155 chars",
  "meta_description_tr": "Türkçe SEO meta açıklaması, max 155 karakter",
  "tags": ["tag1", "tag2", "tag3"],
  "content": "Full English article as HTML (600-800 words). Use <p>, <h2>, <strong>, <em>, <ul>, <li>. End with a CTA linking to /.",
  "content_tr": "Tam Türkçe makale HTML olarak (600-800 kelime). Aynı HTML etiketlerini kullan. Sona / linkiyle CTA ekle."
}}

Rules:
- slug: lowercase, only a-z 0-9 and hyphens, no Turkish chars
- slug_tr: lowercase, no Turkish special chars (ç→c, ğ→g, ı→i, ö→o, ş→s, ü→u), only a-z 0-9 hyphens
- tags: 3-5 lowercase English words
- HTML content: no <html>, <body>, <head> tags, just the article body HTML
- Make the article informative, practical, and engaging
"""


def _to_slug(text: str) -> str:
    replacements = {"ç": "c", "ğ": "g", "ı": "i", "i̇": "i", "ö": "o", "ş": "s", "ü": "u",
                    "Ç": "c", "Ğ": "g", "İ": "i", "Ö": "o", "Ş": "s", "Ü": "u"}
    for orig, rep in replacements.items():
        text = text.replace(orig, rep)
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"\s+", "-", text.strip())
    text = re.sub(r"-+", "-", text)
    return text[:80]


def read_next_topic(db: Session) -> tuple[str, str] | None:
    """Read the first unprocessed topic from topics.md. Returns (topic_tr, topic_en) or None.

    "Done" state is determined solely from the database (topic_key column).
    topics.md is read-only; git pull never affects which topics are considered done.

    Also skips [x] lines in topics.md for backward compatibility with old entries.
    """
    print(f"[BlogGen] topics.md yolu: {TOPICS_FILE}")
    if not os.path.exists(TOPICS_FILE):
        print(f"[BlogGen] HATA: topics.md bulunamadı: {TOPICS_FILE}")
        return None

    with open(TOPICS_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    for line in content.splitlines():
        stripped = line.strip()
        # [x] satırlarını atla (geriye dönük uyum)
        if re.match(r"^- \[x\]", stripped):
            continue
        match = re.match(r"^- \[ \] (.+?) \| (.+?)(?:\s+\(\d{4}-\d{2}-\d{2}\))?$", stripped)
        if match:
            topic_tr = match.group(1).strip()
            topic_en = match.group(2).strip()
            key = f"{topic_tr} | {topic_en}"
            exists = db.query(BlogPost).filter(BlogPost.topic_key == key).first()
            if exists:
                continue
            print(f"[BlogGen] Konu bulundu: {topic_tr} | {topic_en}")
            return topic_tr, topic_en

    print("[BlogGen] Bekleyen konu bulunamadı.")
    return None


def mark_topic_done(topic_tr: str, topic_en: str) -> None:
    """No-op: topic state is now tracked via topic_key in the database."""
    pass


class BlogGenerator:
    def __init__(self):
        self.client = genai.Client(api_key=config.GEMINI_API_KEY)

    def generate(self, topic_tr: str, topic_en: str) -> dict:
        prompt = PROMPT.format(topic_tr=topic_tr, topic_en=topic_en)
        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        raw = response.text.strip()

        # Strip markdown code fences if present
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)

        return json.loads(raw)

    def generate_and_save(self, db: Session) -> BlogPost | None:
        topic = read_next_topic(db)
        if not topic:
            return None

        topic_tr, topic_en = topic
        topic_key = f"{topic_tr} | {topic_en}"

        data = self.generate(topic_tr, topic_en)

        post = BlogPost(
            title=data.get("title", topic_en),
            title_tr=data.get("title_tr", topic_tr),
            slug=data.get("slug") or _to_slug(topic_en),
            slug_tr=data.get("slug_tr") or _to_slug(topic_tr),
            excerpt=data.get("excerpt", ""),
            excerpt_tr=data.get("excerpt_tr", ""),
            content=data.get("content", ""),
            content_tr=data.get("content_tr", ""),
            author="English Story Team",
            tags=json.dumps(data.get("tags", [])),
            meta_description=data.get("meta_description"),
            meta_description_tr=data.get("meta_description_tr"),
            topic_key=topic_key,
            published=True,
        )
        db.add(post)
        db.commit()
        db.refresh(post)
        return post
