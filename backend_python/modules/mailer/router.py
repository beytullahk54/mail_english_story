from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from security import verify_token
from .models import SendStoryRequest, SendStoryResponse
from .service import MailerService

router = APIRouter(prefix="/mailer", tags=["mailer"])


@router.post("/send", status_code=status.HTTP_200_OK, dependencies=[Depends(verify_token)])
def send_story(request: SendStoryRequest, db: Session = Depends(get_db)):
    print("\n[ROUTER] /send isteği geldi!")

    service = MailerService(db)
    result = service.send_story(request)

    return result
