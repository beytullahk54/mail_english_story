from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from sqlalchemy.orm import Session
from database import get_db
from security import verify_token
from .models import StoriesListResponse, StoryItem, StoryRequest, StoryResponse
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


@router.get("/{story_id}/image")
def get_story_image(story_id: int, db: Session = Depends(get_db)):
    service = StoryService()
    story = service.get_story_by_id(db, story_id)
    if not story:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hikaye bulunamadı")
    try:
        image_bytes = service.get_or_generate_story_image(db, story_id, story.topic, story.content)
        return Response(content=image_bytes, media_type="image/jpeg")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Görsel üretilemedi: {str(e)}",
        )


@router.get("/{story_id}", response_model=StoryItem, status_code=status.HTTP_200_OK)
def get_story(story_id: int, db: Session = Depends(get_db)):
    service = StoryService()
    story = service.get_story_by_id(db, story_id)
    if not story:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hikaye bulunamadı")
    return story


@router.post("/instagram/daily", status_code=status.HTTP_200_OK, dependencies=[Depends(verify_token)])
def post_daily_to_instagram(db: Session = Depends(get_db)):
    """
    Bugüne ait hikayelerden (a1/a2/b1/b2) rastgele birini seçip
    görselini üretir ve Instagram'a paylaşır.
    """
    from modules.instagram.service import InstagramService

    service = StoryService()
    story = service.get_random_today_story(db)
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bugüne ait hikaye bulunamadı",
        )

    try:
        service.get_or_generate_story_image(db, story.id, story.topic, story.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Görsel üretilemedi: {str(e)}")

    try:
        instagram = InstagramService()
        result = instagram.post(
            story_id=story.id,
            topic=story.topic,
            level=story.level,
            content=story.content,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Instagram paylaşımı başarısız: {str(e)}")


@router.post("/{story_id}/instagram", status_code=status.HTTP_200_OK, dependencies=[Depends(verify_token)])
def post_to_instagram(story_id: int, db: Session = Depends(get_db)):
    """
    Hikayenin görselini Instagram'a paylaşır.
    Görsel yoksa önce üretir.
    Koruma: X-Api-Token header gerektirir.
    """
    from modules.instagram.service import InstagramService

    service = StoryService()
    story = service.get_story_by_id(db, story_id)
    if not story:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hikaye bulunamadı")

    # Görsel yoksa üret ve kaydet
    try:
        service.get_or_generate_story_image(db, story_id, story.topic, story.content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Görsel üretilemedi: {str(e)}",
        )

    # Instagram'a gönder
    try:
        instagram = InstagramService()
        result = instagram.post(
            story_id=story_id,
            topic=story.topic,
            level=story.level,
            content=story.content,
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Instagram paylaşımı başarısız: {str(e)}",
        )


@router.post("/generate", response_model=StoryResponse, status_code=status.HTTP_200_OK)
def generate_story(request: StoryRequest, db: Session = Depends(get_db)):
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
        return service.generate_story(request, db=db)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hikaye oluşturulamadı: {str(e)}",
        )
