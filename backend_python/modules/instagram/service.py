"""
Instagram Graph API ile tek görsel paylaşımı.
Business/Creator hesap + Facebook App token gerektirir.

Akış:
  1. Görselin public URL'ini al (BACKEND_URL/static/images/{id}.jpg)
  2. Media container oluştur → FINISHED bekle → yayınla
  3. Story olarak da paylaş
"""

import time
import requests
from config import config

GRAPH_API = "https://graph.instagram.com/v21.0"


class InstagramService:

    def _build_caption(self, topic: str, level: str, content: str, story_url: str) -> str:
        level_label = level.upper()
        hashtags = (
            "#EnglishStory #LearnEnglish #EnglishReading "
            f"#{level_label}English #DailyEnglish #ESL "
            "#EnglishLearning #ReadInEnglish"
        )
        header = f"📖 {topic.title()} — {level_label}\n\n"
        footer = f"\n\n👉 Read more: {story_url}\n\n{hashtags}"

        # Instagram caption limiti 2200 karakter
        max_content = 2200 - len(header) - len(footer)
        body = content if len(content) <= max_content else content[:max_content].rsplit(" ", 1)[0] + "…"

        return f"{header}{body}{footer}"

    def _wait_until_ready(self, container_id: str, token: str, max_wait: int = 60) -> None:
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
        container_resp = requests.post(
            f"{GRAPH_API}/{user_id}/media",
            data={**params, "access_token": token},
            timeout=30,
        )
        container_data = container_resp.json()
        if "id" not in container_data:
            error = container_data.get("error", {}).get("message", str(container_data))
            raise Exception(f"Media container oluşturulamadı: {error}")

        container_id = container_data["id"]
        self._wait_until_ready(container_id, token)

        publish_resp = requests.post(
            f"{GRAPH_API}/{user_id}/media_publish",
            data={"creation_id": container_id, "access_token": token},
            timeout=30,
        )
        publish_data = publish_resp.json()
        if "id" not in publish_data:
            error = publish_data.get("error", {}).get("message", str(publish_data))
            raise Exception(f"Gönderi yayınlanamadı: {error}")

        return publish_data["id"]

    def _pollinations_url(self, topic: str, story_id: int, width: int, height: int, seed_offset: int = 0) -> str:
        """Pollinations.ai'den her zaman erişilebilir bir görsel URL'i üretir."""
        from urllib.parse import quote
        prompt = (
            f"A beautiful scene illustrating a story about: {topic}. "
            f"Storytelling atmosphere, warm vivid colors, no text, no words, no letters"
        )
        seed = story_id + seed_offset
        return (
            f"https://image.pollinations.ai/prompt/{quote(prompt)}"
            f"?width={width}&height={height}&nologo=true&seed={seed}"
        )

    def post(self, story_id: int, topic: str, level: str, content: str) -> dict:
        """
        Hikayeyi tek görsel olarak feed + Story'ye gönderir.
        Görsel olarak Pollinations.ai URL'i kullanılır — Railway filesystem bağımlılığı yok.
        """
        token = config.INSTAGRAM_TOKEN
        user_id = config.INSTAGRAM_USER_ID

        if not token or not user_id:
            raise ValueError("INSTAGRAM_TOKEN veya INSTAGRAM_USER_ID eksik (.env)")

        story_url = f"{config.APP_BASE_URL}/stories/{story_id}"
        caption = self._build_caption(topic, level, content, story_url)

        # Feed post — 4:5 oran (800x1000)
        image_url = self._pollinations_url(topic, story_id, width=800, height=1000)
        print(f"[Instagram] Feed görsel URL: {image_url}")

        post_id = self._create_and_publish(user_id, token, {
            "image_url": image_url,
            "caption": caption,
        })
        print(f"[Instagram] Feed post paylaşıldı: {post_id}")

        # Permalink al
        permalink_resp = requests.get(
            f"{GRAPH_API}/{post_id}",
            params={"fields": "permalink", "access_token": token},
            timeout=15,
        )
        permalink = permalink_resp.json().get("permalink", "")

        # Story — 9:16 dikey (800x1422)
        ig_story_id = None
        try:
            vertical_url = self._pollinations_url(topic, story_id, width=800, height=1422, seed_offset=999)
            print(f"[Instagram] Story görsel URL: {vertical_url}")
            ig_story_id = self._create_and_publish(user_id, token, {
                "image_url": vertical_url,
                "media_type": "STORIES",
            })
            print(f"[Instagram] Story paylaşıldı: {ig_story_id}")
        except Exception as e:
            print(f"[Instagram] Story paylaşım hatası: {e}")

        return {
            "success": True,
            "post_id": post_id,
            "permalink": permalink,
            "ig_story_id": ig_story_id,
            "story_id": story_id,
        }
