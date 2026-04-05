from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from database import get_db
from .models import StoriesListResponse, StoryRequest, StoryResponse
from .service import StoryService

router = APIRouter(prefix="/story", tags=["story"])


@router.get("/list", response_model=StoriesListResponse, status_code=status.HTTP_200_OK)
def list_stories(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=50),
    level: str | None = Query(default=None),
    language: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    service = StoryService()
    return service.get_stories(db, page=page, page_size=page_size, level=level, language=language)


@router.post("/generate", response_model=StoryResponse, status_code=status.HTTP_200_OK)
def generate_story(request: StoryRequest):
    if not request.topic.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Konu boş bırakılamaz",
        )

    if not 50 <= request.word_count <= 1000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kelime sayısı 50 ile 1000 arasında olmalıdır",
        )

    service = StoryService()
    try:
        return service.generate_story(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hikaye oluşturulamadı: {str(e)}",
        )
