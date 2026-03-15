from typing import Optional, List
from pydantic import BaseModel


class SendStoryRequest(BaseModel):
    story: str
    topic: str
    level: str
    language: str = "English"
    level_filter: Optional[str] = None
    language_filter: Optional[str] = None


class SendStoryResponse(BaseModel):
    sent: int
    failed: int
    recipients: List[str]
