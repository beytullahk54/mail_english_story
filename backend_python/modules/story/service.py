import google.generativeai as genai
from config import config
from .models import StoryRequest, StoryResponse

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
        self.model = genai.GenerativeModel("gemini-1.5-flash")

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