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

    def generate_story(self, request: StoryRequest) -> StoryResponse:
        level_desc = LEVEL_DESCRIPTIONS.get(request.level.lower(), "simple sentences, basic vocabulary")
        
        # We always generate English stories as requested
        prompt = (
            f"Write an English story about '{request.topic}'. "
            f"The story should be approximately {request.word_count} words long. "
            f"Use {level_desc}. "
            f"Only return the story text, no titles or extra explanations."
        )

        response = self.model.generate_content(prompt)
        story_text = response.text.strip()

        return StoryResponse(
            story=story_text,
            topic=request.topic,
            level=request.level,
            language="English" # The content language is always English
        )

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