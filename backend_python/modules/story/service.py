import google.generativeai as genai
from config import config
from .models import StoryRequest, StoryResponse

LEVEL_DESCRIPTIONS = {
    "beginner": "simple sentences, basic vocabulary (A1-A2 level)",
    "intermediate": "varied sentence structures, everyday vocabulary (B1-B2 level)",
    "advanced": "complex sentences, rich vocabulary and idioms (C1-C2 level)",
}


class StoryService:
    def __init__(self):
        genai.configure(api_key=config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel("gemini-2.5-flash")

    def generate_story(self, request: StoryRequest) -> StoryResponse:
        level_desc = LEVEL_DESCRIPTIONS[request.level]
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
        )