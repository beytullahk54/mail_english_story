"""
Instagram Graph API ile gönderi paylaşımı.
Business/Creator hesap + Facebook App token gerektirir.

Akış:
  1. Görselin public URL'ini al (APP_BASE_URL/static/images/{id}.png)
  2. Media container oluştur  → POST /{user_id}/media
  3. Yayınla               → POST /{user_id}/media_publish
"""

import requests
from config import config

GRAPH_API = "https://graph.instagram.com/v21.0"


class InstagramService:

    def _build_caption(self, topic: str, level: str, content: str, story_url: str) -> str:
        # İlk 3 cümleyi al (~300 karakter)
        sentences = [s.strip() for s in content.split(".") if s.strip()]
        preview = ""
        for s in sentences[:3]:
            candidate = preview + s + ". "
            if len(candidate) > 350:
                break
            preview = candidate

        level_label = level.upper()
        caption = (
            f"📖 {topic.title()} — {level_label}\n\n"
            f"{preview.strip()}\n\n"
            f"👉 Read the full story: {story_url}\n\n"
            "#EnglishStory #LearnEnglish #EnglishReading "
            f"#{level_label}English #DailyEnglish #ESL "
            "#EnglishLearning #ReadInEnglish"
        )
        return caption

    def post(self, story_id: int, topic: str, level: str, content: str) -> dict:
        """
        Hikayeyi Instagram'a gönderir.
        Döndürür: {"success": True, "post_id": "...", "permalink": "..."}
        Hata durumunda exception fırlatır.
        """
        token = config.INSTAGRAM_TOKEN
        user_id = config.INSTAGRAM_USER_ID

        if not token or not user_id:
            raise ValueError("INSTAGRAM_TOKEN veya INSTAGRAM_USER_ID eksik (.env)")

        image_url = f"{config.APP_BASE_URL}/static/images/{story_id}.jpg"
        story_url = f"{config.APP_BASE_URL}/stories/{story_id}"
        caption = self._build_caption(topic, level, content, story_url)

        # 1. Media container oluştur
        container_resp = requests.post(
            f"{GRAPH_API}/{user_id}/media",
            params={
                "image_url": image_url,
                "caption": caption,
                "access_token": token,
            },
            timeout=30,
        )
        container_data = container_resp.json()

        if "id" not in container_data:
            error = container_data.get("error", {}).get("message", str(container_data))
            raise Exception(f"Media container oluşturulamadı: {error}")

        creation_id = container_data["id"]

        # 2. Yayınla
        publish_resp = requests.post(
            f"{GRAPH_API}/{user_id}/media_publish",
            params={
                "creation_id": creation_id,
                "access_token": token,
            },
            timeout=30,
        )
        publish_data = publish_resp.json()

        if "id" not in publish_data:
            error = publish_data.get("error", {}).get("message", str(publish_data))
            raise Exception(f"Gönderi yayınlanamadı: {error}")

        post_id = publish_data["id"]

        # 3. Permalink al
        permalink_resp = requests.get(
            f"{GRAPH_API}/{post_id}",
            params={"fields": "permalink", "access_token": token},
            timeout=15,
        )
        permalink = permalink_resp.json().get("permalink", "")

        return {"success": True, "post_id": post_id, "permalink": permalink}
