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

    def _post_carousel(self, user_id: str, token: str, image_urls: list[str], caption: str) -> str:
        """
        Birden fazla görseli carousel post olarak yayınlar. Post ID döner.
        """
        # 1. Her görsel için ayrı carousel item container oluştur
        item_ids = []
        for i, img_url in enumerate(image_urls, start=1):
            print(f"[Instagram] Slide {i} için görsel URL: {img_url}")
            container_resp = requests.post(
                f"{GRAPH_API}/{user_id}/media",
                data={
                    "image_url": img_url,
                    "is_carousel_item": "true",
                    "access_token": token,
                },
                timeout=30,
            )
            data = container_resp.json()
            print(f"[Instagram] Slide {i} API yanıtı: {data}")
            if "id" not in data:
                error = data.get("error", {}).get("message", str(data))
                print(f"[Instagram] Slide {i} container hatası: {error}")
                continue
            item_ids.append(data["id"])
            print(f"[Instagram] Slide {i} container oluşturuldu: {data['id']}")
            time.sleep(3)  # Rate limit koruması

        if len(item_ids) < 2:
            raise Exception(f"Carousel için en az 2 görsel gerekli, sadece {len(item_ids)} hazırlandı")

        # 2. Ana carousel container oluştur
        print(f"[Instagram] Carousel oluşturuluyor, {len(item_ids)} item: {item_ids}")
        carousel_resp = requests.post(
            f"{GRAPH_API}/{user_id}/media",
            data={
                "media_type": "CAROUSEL",
                "children": ",".join(item_ids),
                "caption": caption,
                "access_token": token,
            },
            timeout=30,
        )
        carousel_data = carousel_resp.json()
        print(f"[Instagram] Carousel API yanıtı: {carousel_data}")
        if "id" not in carousel_data:
            error = carousel_data.get("error", {}).get("message", str(carousel_data))
            raise Exception(f"Carousel container oluşturulamadı: {error}")

        carousel_id = carousel_data["id"]
        print(f"[Instagram] Carousel container: {carousel_id}")

        # 3. FINISHED bekle ve yayınla
        self._wait_until_ready(carousel_id, token)

        publish_resp = requests.post(
            f"{GRAPH_API}/{user_id}/media_publish",
            params={"creation_id": carousel_id, "access_token": token},
            timeout=30,
        )
        publish_data = publish_resp.json()
        if "id" not in publish_data:
            error = publish_data.get("error", {}).get("message", str(publish_data))
            raise Exception(f"Carousel yayınlanamadı: {error}")

        return publish_data["id"]

    def post(self, story_id: int, topic: str, level: str, content: str) -> dict:
        """
        Hikayenin 5 cümlesini carousel feed post + Story olarak paylaşır.
        Döndürür: {"success": True, "post_id": "...", "permalink": "...", "ig_story_id": "..."}
        """
        from modules.story.service import StoryService

        token = config.INSTAGRAM_TOKEN
        user_id = config.INSTAGRAM_USER_ID

        if not token or not user_id:
            raise ValueError("INSTAGRAM_TOKEN veya INSTAGRAM_USER_ID eksik (.env)")

        base = config.BACKEND_URL or config.APP_BASE_URL
        story_url = f"{config.APP_BASE_URL}/stories/{story_id}"
        caption = self._build_caption(topic, level, content, story_url)

        # 1. 5 ayrı slide görseli üret
        story_service = StoryService()
        slide_paths = story_service.generate_carousel_images(story_id, topic, content)
        if not slide_paths:
            raise Exception("Hiç carousel görseli üretilemedi")

        image_urls = [f"{base}/{path}" for path in slide_paths]
        print(f"[Instagram] {len(image_urls)} slide görseli hazır.")

        # 2. Carousel feed post
        post_id = self._post_carousel(user_id, token, image_urls, caption)
        print(f"[Instagram] Carousel feed post paylaşıldı: {post_id}")

        # 3. Permalink al
        permalink_resp = requests.get(
            f"{GRAPH_API}/{post_id}",
            params={"fields": "permalink", "access_token": token},
            timeout=15,
        )
        permalink = permalink_resp.json().get("permalink", "")

        # 4. İlk slide ile Story paylaş
        ig_story_id = None
        try:
            ig_story_id = self._create_and_publish(user_id, token, {
                "image_url": image_urls[0],
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
            "slides": len(image_urls),
        }
