from typing import Literal
from pydantic import BaseModel


class StoryRequest(BaseModel):
    topic: str
    level: Literal["beginner", "intermediate", "advanced"] = "beginner"
    word_count: int = 150


class StoryResponse(BaseModel):
    story: str
    topic: str
    level: str