"""
Instagram Graph API ile gönderi paylaşımı.
Business/Creator hesap + Facebook App token gerektirir.

Akış:
  1. Görselin public URL'ini al (BACKEND_URL/static/images/{id}.jpg)
  2. Feed post: container oluştur → yayınla
  3. Story post: container oluştur (media_type=STORIES) → yayınla
"""

import time
import requests
from config import config

GRAPH_API = "https://graph.instagram.com/v21.0"


class InstagramService:

    def _build_caption(self, topic: str, level: str, content: str, story_url: str) -> str:
        # İlk 3 cümleyi al (~350 karakter)
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

    def _wait_until_ready(self, container_id: str, token: str, max_wait: int = 60) -> None:
        """Container FINISHED durumuna gelene kadar bekle (max_wait saniye)."""
        interval = 5
        elapsed = 0
        while elapsed < max_wait:
            resp = requests.get(
                f"{GRAPH_API}/{container_id}",
                params={"fields": "status_code", "access_token": token},
                timeout=15,
            )
            status = resp.json().get("status_code", "")
            print(f"[Instagram] Container {container_id} durumu: {status}")
            if status == "FINISHED":
                return
            if status == "ERROR":
                raise Exception("Instagram container işleme hatası (ERROR)")
            if status == "EXPIRED":
                raise Exception("Instagram container süresi doldu (EXPIRED)")
            time.sleep(interval)
            elapsed += interval
        raise Exception(f"Instagram container {max_wait} saniyede hazır olmadı")

    def _create_and_publish(self, user_id: str, token: str, params: dict) -> str:
        """Container oluştur, hazır olmasını bekle ve yayınla. Post ID döner."""
        container_resp = requests.post(
            f"{GRAPH_API}/{user_id}/media",
            params={**params, "access_token": token},
            timeout=30,
        )
        container_data = container_resp.json()
        if "id" not in container_data:
            error = container_data.get("error", {}).get("message", str(container_data))
            raise Exception(f"Media container oluşturulamadı: {error}")

        container_id = container_data["id"]

        # Instagram görseli işleyene kadar bekle
        self._wait_until_ready(container_id, token)

        publish_resp = requests.post(
            f"{GRAPH_API}/{user_id}/media_publish",
            params={"creation_id": container_id, "access_token": token},
            timeout=30,
        )
        publish_data = publish_resp.json()
        if "id" not in publish_data:
            error = publish_data.get("error", {}).get("message", str(publish_data))
            raise Exception(f"Gönderi yayınlanamadı: {error}")

        return publish_data["id"]

    def post(self, story_id: int, topic: str, level: str, content: str) -> dict:
        """
        Hikayeyi Instagram feed'e ve Story'ye gönderir.
        Döndürür: {"success": True, "post_id": "...", "permalink": "...", "ig_story_id": "..."}
        """
        token = config.INSTAGRAM_TOKEN
        user_id = config.INSTAGRAM_USER_ID

        if not token or not user_id:
            raise ValueError("INSTAGRAM_TOKEN veya INSTAGRAM_USER_ID eksik (.env)")

        base = config.BACKEND_URL or config.APP_BASE_URL
        image_url = f"{base}/static/images/{story_id}.jpg"
        story_url = f"{config.APP_BASE_URL}/stories/{story_id}"
        caption = self._build_caption(topic, level, content, story_url)

        # 1. Feed post
        post_id = self._create_and_publish(user_id, token, {
            "image_url": image_url,
            "caption": caption,
        })
        print(f"[Instagram] Feed post paylaşıldı: {post_id}")

        # 2. Permalink al
        permalink_resp = requests.get(
            f"{GRAPH_API}/{post_id}",
            params={"fields": "permalink", "access_token": token},
            timeout=15,
        )
        permalink = permalink_resp.json().get("permalink", "")

        # 3. Instagram Story olarak da paylaş
        ig_story_id = None
        try:
            ig_story_id = self._create_and_publish(user_id, token, {
                "image_url": image_url,
                "media_type": "STORIES",
            })
            print(f"[Instagram] Story paylaşıldı: {ig_story_id}")
        except Exception as e:
            # Story başarısız olsa bile feed post geçerli sayılır
            print(f"[Instagram] Story paylaşım hatası: {e}")

        return {
            "success": True,
            "post_id": post_id,
            "permalink": permalink,
            "ig_story_id": ig_story_id,
        }
