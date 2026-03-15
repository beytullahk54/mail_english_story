from typing import Optional
from pydantic import BaseModel


class SendStoryRequest(BaseModel):
    story: str
    topic: str
    level: str
    level_filter: Optional[str] = None  # Sadece belirli seviyeye gönder, None = herkese


class SendStoryResponse(BaseModel):
    sent: int
    failed: int
    recipients: list[str]
