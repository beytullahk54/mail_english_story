import google.generativeai as genai
from sqlalchemy.orm import Session
from config import config
from .models import Story, StoryRequest, StoryResponse, StoryItem, StoriesListResponse

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

    def generate_story_image(self, topic: str, content_preview: str) -> bytes:
        import requests as http_requests
        from urllib.parse import quote

        prompt = (
            f"watercolor illustration for an English story about {topic}, "
            f"storytelling atmosphere, warm vivid colors, no text, no words"
        )
        url = f"https://image.pollinations.ai/prompt/{quote(prompt)}?width=800&height=450&nologo=true&seed=42"
        response = http_requests.get(url, timeout=60)
        if response.status_code != 200:
            raise Exception(f"Görsel servisi hata döndürdü: {response.status_code}")
        return response.content

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