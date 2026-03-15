from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from .models import SendStoryRequest, SendStoryResponse
from .service import MailerService

router = APIRouter(prefix="/mailer", tags=["mailer"])


@router.post("/send",  status_code=status.HTTP_200_OK)
def send_story(request: SendStoryRequest, db: Session = Depends(get_db)):
    print("\n[ROUTER] /send isteği geldi!")
    
    service = MailerService(db)
    result = service.send_story(request)
    

    """if result.sent == 0 and result.failed == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gönderilecek abone bulunamadı",
        )"""
    #result = ""

    return result
