import json
import re
import os
from datetime import date
from google import genai
from sqlalchemy.orm import Session
from config import config
from .models import BlogPost

TOPICS_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "..", "topics.md")

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


def read_next_topic() -> tuple[str, str] | None:
    """Read the first unchecked topic from topics.md. Returns (topic_tr, topic_en) or None."""
    if not os.path.exists(TOPICS_FILE):
        return None
    with open(TOPICS_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    for line in content.splitlines():
        match = re.match(r"^- \[ \] (.+?) \| (.+)$", line.strip())
        if match:
            return match.group(1).strip(), match.group(2).strip()
    return None


def mark_topic_done(topic_tr: str, topic_en: str) -> None:
    """Mark the topic as published in topics.md."""
    if not os.path.exists(TOPICS_FILE):
        return
    with open(TOPICS_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    old_line = f"- [ ] {topic_tr} | {topic_en}"
    new_line = f"- [x] {topic_tr} | {topic_en} ({date.today().isoformat()})"
    content = content.replace(old_line, new_line, 1)

    with open(TOPICS_FILE, "w", encoding="utf-8") as f:
        f.write(content)


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
        topic = read_next_topic()
        if not topic:
            return None

        topic_tr, topic_en = topic

        # Check if slug already exists
        existing = db.query(BlogPost).filter(
            BlogPost.slug == _to_slug(topic_en)
        ).first()
        if existing:
            mark_topic_done(topic_tr, topic_en)
            return existing

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
            published=True,
        )
        db.add(post)
        db.commit()
        db.refresh(post)

        mark_topic_done(topic_tr, topic_en)
        return post
