import os
from pathlib import Path
from instagrapi import Client
from config import config

SESSION_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "instagram_session.json")

LEVEL_EMOJIS = {
    "a1": "🟢", "a2": "🟢",
    "b1": "🔵", "b2": "🔵",
    "beginner": "🟢",
    "intermediate": "🔵",
    "advanced": "🔴",
}


class InstagramService:
    def __init__(self):
        self.client = Client()
        self.client.delay_range = [1, 3]

    def _restore_session_from_env(self):
        """Railway gibi ortamlarda session dosyası yoksa env var'dan yeniden oluşturur."""
        if os.path.exists(SESSION_FILE):
            return
        if config.INSTAGRAM_SESSION:
            with open(SESSION_FILE, "w") as f:
                f.write(config.INSTAGRAM_SESSION)
            print("[Instagram] Session env var'dan yüklendi.")

    def _login(self):
        self._restore_session_from_env()

        if os.path.exists(SESSION_FILE):
            try:
                self.client.load_settings(SESSION_FILE)
                self.client.login(config.INSTAGRAM_USERNAME, config.INSTAGRAM_PASSWORD)
                print("[Instagram] Mevcut session ile giriş yapıldı.")
                return
            except Exception:
                print("[Instagram] Session geçersiz, yeniden giriş yapılıyor...")

        self.client.login(config.INSTAGRAM_USERNAME, config.INSTAGRAM_PASSWORD)
        self.client.dump_settings(SESSION_FILE)
        print("[Instagram] Giriş başarılı, session kaydedildi.")

    def _build_caption(self, topic: str, level: str, content: str, story_url: str) -> str:
        emoji = LEVEL_EMOJIS.get(level.lower(), "📖")
        # Cümle ortasında kesmemek için en yakın nokta/boşluğa göre kes
        preview = content[:400].rsplit(".", 1)[0] + "."
        hashtags = (
            "#EnglishStory #LearnEnglish #DailyEnglish "
            f"#{level.capitalize()}English #ESL #EnglishLearning "
            "#ReadingPractice #EnglishForBeginners"
        )
        return (
            f"{emoji} {topic}\n"
            f"{'─' * 30}\n\n"
            f"{preview}\n\n"
            f"📖 Devamını okumak için sayfamızı ziyaret edin:\n"
            f"👉 {story_url}\n\n"
            f"{'─' * 30}\n"
            f"{hashtags}"
        )

    def post_story_image(self, image_path: str, topic: str, level: str, content: str, story_id: int) -> str | None:
        """
        Görsel dosya yolunu alır, Instagram'a yükler.
        Başarılıysa post URL'ini döndürür, hata durumunda None.
        """
        if not config.INSTAGRAM_USERNAME or not config.INSTAGRAM_PASSWORD:
            print("[Instagram] Kullanıcı adı veya şifre eksik, paylaşım atlandı.")
            return None

        if not os.path.exists(image_path):
            print(f"[Instagram] Görsel bulunamadı: {image_path}")
            return None

        try:
            self._login()
            story_url = f"{config.APP_BASE_URL}/stories/{story_id}"
            caption = self._build_caption(topic, level, content, story_url)
            media = self.client.photo_upload(Path(image_path), caption=caption)
            post_url = f"https://www.instagram.com/p/{media.code}/"
            print(f"[Instagram] Paylaşıldı: {post_url}")
            return post_url
        except Exception as e:
            print(f"[Instagram] Paylaşım hatası: {e}")
            return None
