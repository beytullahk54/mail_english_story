import os
import re
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

    def _add_text_overlay(self, image_bytes: bytes, text: str, slide_label: str | None = None) -> bytes:
        img = Image.open(BytesIO(image_bytes)).convert("RGBA")
        w, h = img.size

        font_size = max(26, w // 22)
        font = None

        # 1. Bilinen sistem font yollarını dene
        for font_path in [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
            "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf",
            "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
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

        # 2. glob ile sistemde herhangi bir Bold TTF ara
        if font is None:
            import glob
            for pattern in [
                "/usr/share/fonts/**/*Bold*.ttf",
                "/usr/share/fonts/**/*bold*.ttf",
                "/usr/share/fonts/**/*.ttf",
            ]:
                matches = glob.glob(pattern, recursive=True)
                if matches:
                    try:
                        font = ImageFont.truetype(matches[0], font_size)
                        break
                    except Exception:
                        continue

        # 3. Pillow >= 10 load_default(size=n) destekler
        if font is None:
            try:
                font = ImageFont.load_default(size=font_size)
            except TypeError:
                font = ImageFont.load_default()

        # Metni satırlara böl — genişliğe göre karakter sayısı hesapla
        char_width = max(20, int(w / (font_size * 0.6)))
        wrapped = textwrap.fill(text, width=char_width)
        lines = wrapped.split("\n")

        line_height = font_size + 10
        padding = 20
        max_banner_h = h // 3
        banner_h = min(line_height * len(lines) + padding * 2, max_banner_h)

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

        # Sol üst köşeye slide numarası ekle
        if slide_label:
            badge_font_size = max(28, w // 20)
            badge_font = None
            for fp in [
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
                "/System/Library/Fonts/Helvetica.ttc",
            ]:
                if os.path.exists(fp):
                    try:
                        badge_font = ImageFont.truetype(fp, badge_font_size)
                        break
                    except Exception:
                        continue
            if badge_font is None:
                try:
                    badge_font = ImageFont.load_default(size=badge_font_size)
                except TypeError:
                    badge_font = ImageFont.load_default()

            draw2 = ImageDraw.Draw(img)
            pad = 14
            bbox = draw2.textbbox((0, 0), slide_label, font=badge_font)
            bw = bbox[2] - bbox[0] + pad * 2
            bh = bbox[3] - bbox[1] + pad * 2
            margin = 20
            # Yarı saydam arka plan pill
            draw2.rounded_rectangle(
                [margin, margin, margin + bw, margin + bh],
                radius=bh // 2,
                fill=(10, 10, 20, 180),
            )
            draw2.text(
                (margin + pad, margin + pad),
                slide_label,
                font=badge_font,
                fill=(255, 255, 255, 255),
            )

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

        # 3. İlk 2 cümleyi al ve görsele yaz
        sentences = [s.strip() for s in content_preview.strip().split(".") if s.strip()]
        overlay_text = sentences[0] + "." if sentences else ""
        try:
            image_bytes = self._add_text_overlay(image_bytes, overlay_text)
        except Exception as e:
            print(f"[StoryService] Metin overlay hatası: {e}")

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

    def generate_carousel_images(self, story_id: int, topic: str, content: str) -> list[str]:
        """
        Hikayenin ilk 5 cümlesini ayrı ayrı görsele dönüştürür.
        Her cümle için Pollinations'tan görsel üretir ve cümleyi overlay olarak yazar.
        Döner: ["static/images/{id}_slide_1.jpg", ..., "static/images/{id}_slide_5.jpg"]
        Cache: Tüm dosyalar diskte mevcutsa tekrar üretmez.
        """
        import requests as http_requests
        from urllib.parse import quote

        # Nokta/ünlem/soru işaretine göre böl, kısaltmaları (Mr. Dr. vs) atla
        raw = re.split(r'(?<![A-Z][a-z])(?<!\b[A-Z])(?<!\b\w\.\w)(?<=[.!?])\s+', content.strip())
        sentences = [s.strip() for s in raw if len(s.strip()) > 20]
        sentences = sentences[:5]  # İlk 5 cümle

        os.makedirs(IMAGES_DIR, exist_ok=True)

        # Mevcut tüm slide dosyalarını temizle
        import glob as _glob
        for old_file in _glob.glob(os.path.join(IMAGES_DIR, f"{story_id}_slide_*.jpg")):
            os.remove(old_file)
            print(f"[StoryService] Eski slide silindi: {old_file}")

        paths = []

        for i, sentence in enumerate(sentences, start=1):
            filename = f"{story_id}_slide_{i}.jpg"
            file_path = os.path.join(IMAGES_DIR, filename)

            # Her cümle için konuya özel görsel üret
            prompt = (
                f"watercolor illustration: {sentence}. "
                f"Topic: {topic}. "
                f"Storytelling atmosphere, warm vivid colors, no text, no words, no letters"
            )
            seed = story_id * 10 + i
            url = (
                f"https://image.pollinations.ai/prompt/{quote(prompt)}"
                f"?width=800&height=1000&nologo=true&seed={seed}"
            )
            try:
                response = http_requests.get(url, timeout=60)
                if response.status_code != 200:
                    raise Exception(f"HTTP {response.status_code}")
                image_bytes = response.content
            except Exception as e:
                print(f"[StoryService] Slide {i} görsel üretim hatası: {e}")
                continue

            # Cümleyi ve hikaye numarasını görsele yaz
            try:
                slide_label = f"#{story_id}"
                image_bytes = self._add_text_overlay(image_bytes, sentence + ".", slide_label=slide_label)
            except Exception as e:
                print(f"[StoryService] Slide {i} overlay hatası: {e}")

            # JPEG olarak kaydet
            try:
                img_obj = Image.open(BytesIO(image_bytes)).convert("RGB")
                jpeg_buf = BytesIO()
                img_obj.save(jpeg_buf, format="JPEG", quality=92)
                with open(file_path, "wb") as f:
                    f.write(jpeg_buf.getvalue())
                print(f"[StoryService] Slide {i} kaydedildi: {filename}")
                paths.append(f"static/images/{filename}")
            except Exception as e:
                print(f"[StoryService] Slide {i} kayıt hatası: {e}")

        return paths

    def get_random_today_story(self, db: Session) -> StoryItem | None:
        """Bugüne ait a1/a2/b1/b2 seviyeli hikayelerden rastgele birini döner."""
        import random
        from datetime import date
        from sqlalchemy import func, cast, Date

        today = date.today()
        stories = (
            db.query(Story)
            .filter(cast(Story.created_at, Date) == today)
            .filter(func.lower(Story.level).in_(["a1", "a2", "b1", "b2"]))
            .all()
        )

        if not stories:
            return None

        story = random.choice(stories)
        return StoryItem.model_validate(story)

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