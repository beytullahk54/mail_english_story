from fastapi import APIRouter, HTTPException, status
from .models import StoryRequest, StoryResponse
from .service import StoryService

router = APIRouter(prefix="/story", tags=["story"])


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
