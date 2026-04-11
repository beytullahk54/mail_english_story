import os
import textwrap
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import google.generativeai as genai
from sqlalchemy.orm import Session
from config import config
from .models import Story, StoryRequest, StoryResponse, StoryItem, StoriesListResponse

IMAGES_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "static", "images")

LEVEL_DESCRIPTIONS = {
    "a1": "very simple sentences, basic vocabulary (A1 level)",
    "beginner": "simple sentences, basic vocabulary (A1-A2 level)",
    "a2": "simple sentences, basic everyday vocabulary (A2 level)",
    "b1": "varied sentence structures, intermediate vocabulary (B1 level)",
    "intermediate": "varied sentence structures, everyday vocabulary (B1-B2 level)",
    "b2": "complex sentence structures, upper-intermediate vocabulary (B2 level)",
    "advanced": "complex sentences, rich vocabulary and idioms (C1-C2 level)",
}


class StoryService:
    def __init__(self):
        genai.configure(api_key=config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel("gemini-2.5-flash")

    def generate_story(self, request: StoryRequest, db: Session | None = None) -> StoryResponse:
        level_desc = LEVEL_DESCRIPTIONS.get(request.level.lower(), "simple sentences, basic vocabulary")

        prompt = (
            f"Write an English story about '{request.topic}'. "
            f"The story should be approximately {request.word_count} words long. "
            f"Use {level_desc}. "
            f"Only return the story text, no titles or extra explanations."
        )

        response = self.model.generate_content(prompt)
        story_text = response.text.strip()

        # DB'ye kaydet
        story_id = None
        if db is not None:
            try:
                db_story = Story(
                    topic=request.topic,
                    level=request.level,
                    language="English",
                    content=story_text,
                )
                db.add(db_story)
                db.commit()
                db.refresh(db_story)
                story_id = db_story.id
            except Exception as e:
                db.rollback()
                print(f"[StoryService] DB kayıt hatası: {e}")

        return StoryResponse(
            id=story_id,
            story=story_text,
            topic=request.topic,
            level=request.level,
            language="English",
        )

    def _add_text_overlay(self, image_bytes: bytes, text: str) -> bytes:
        img = Image.open(BytesIO(image_bytes)).convert("RGBA")
        w, h = img.size

        # Yazı tipi — sistem fontlarını dene, bulamazsan PIL default'a dön
        font_size = max(22, w // 28)
        font = None
        for font_path in [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "/System/Library/Fonts/Arial.ttf",
            "C:/Windows/Fonts/arialbd.ttf",
        ]:
            if os.path.exists(font_path):
                try:
                    font = ImageFont.truetype(font_path, font_size)
                    break
                except Exception:
                    continue
        if font is None:
            font = ImageFont.load_default()

        # Metni satırlara böl (max ~55 karakter)
        wrapped = textwrap.fill(text, width=55)
        lines = wrapped.split("\n")

        draw_tmp = ImageDraw.Draw(img)
        line_height = font_size + 8
        padding = 20
        banner_h = line_height * len(lines) + padding * 2

        # Alt kısımda yarı saydam koyu şerit
        overlay = Image.new("RGBA", (w, banner_h), (0, 0, 0, 0))
        draw_ov = ImageDraw.Draw(overlay)
        draw_ov.rectangle([(0, 0), (w, banner_h)], fill=(10, 10, 20, 195))
        img.paste(overlay, (0, h - banner_h), overlay)

        # Metni yaz
        draw = ImageDraw.Draw(img)
        y = h - banner_h + padding
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            text_w = bbox[2] - bbox[0]
            x = (w - text_w) // 2
            # Hafif gölge
            draw.text((x + 2, y + 2), line, font=font, fill=(0, 0, 0, 160))
            draw.text((x, y), line, font=font, fill=(255, 248, 220, 255))
            y += line_height

        out = BytesIO()
        img.convert("RGB").save(out, format="JPEG", quality=92)
        return out.getvalue()

    def get_or_generate_story_image(self, db: Session, story_id: int, topic: str, content_preview: str) -> bytes:
        import requests as http_requests
        from urllib.parse import quote

        # 1. DB'de kayıtlı path var mı?
        story = db.query(Story).filter(Story.id == story_id).first()
        if story and story.image_path:
            image_abs = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", story.image_path))
            if os.path.exists(image_abs):
                with open(image_abs, "rb") as f:
                    return f.read()

        # 2. Yoksa Pollinations'tan üret
        # Hikayenin ilk 2 paragrafından bağlam çıkar
        paragraphs = [p.strip() for p in content_preview.strip().split("\n\n") if p.strip()]
        story_context = " ".join(paragraphs[:2])[:400]  # max 400 karakter

        prompt = (
            f"watercolor illustration: {story_context}. "
            f"Topic: {topic}. "
            f"Storytelling atmosphere, warm vivid colors, no text, no words, no letters"
        )
        url = f"https://image.pollinations.ai/prompt/{quote(prompt)}?width=800&height=800&nologo=true&seed={story_id}"
        response = http_requests.get(url, timeout=60)
        if response.status_code != 200:
            raise Exception(f"Görsel servisi hata döndürdü: {response.status_code}")
        image_bytes = response.content

        # 5. Diske kaydet (JPEG — Instagram uyumlu)
        os.makedirs(IMAGES_DIR, exist_ok=True)
        filename = f"{story_id}.jpg"
        file_path = os.path.join(IMAGES_DIR, filename)
        # JPEG olarak yeniden encode et
        from PIL import Image as PilImage
        img_obj = PilImage.open(BytesIO(image_bytes)).convert("RGB")
        jpeg_buf = BytesIO()
        img_obj.save(jpeg_buf, format="JPEG", quality=92)
        image_bytes = jpeg_buf.getvalue()
        with open(file_path, "wb") as f:
            f.write(image_bytes)

        # 6. DB'yi güncelle
        if story:
            try:
                story.image_path = f"static/images/{filename}"
                db.commit()
                print(f"[StoryService] Görsel kaydedildi: {story.image_path}")
            except Exception as e:
                db.rollback()
                print(f"[StoryService] DB görsel path güncelleme hatası: {e}")

        return image_bytes

    def get_story_by_id(self, db: Session, story_id: int) -> StoryItem | None:
        story = db.query(Story).filter(Story.id == story_id).first()
        if not story:
            return None
        return StoryItem.model_validate(story)

    def get_stories(self, db: Session, page: int, page_size: int, level: str | None, language: str | None) -> StoriesListResponse:
        query = db.query(Story)
        if level:
            query = query.filter(Story.level == level)
        if language:
            query = query.filter(Story.language == language)

        total = query.count()
        items = query.order_by(Story.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

        return StoriesListResponse(
            items=[StoryItem.model_validate(s) for s in items],
            total=total,
            page=page,
            page_size=page_size,
        )