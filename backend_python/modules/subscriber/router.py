from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from database import get_db
from .models import SubscriberInput
from .service import SubscriberService

router = APIRouter(prefix="/subscribe", tags=["subscriber"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def subscribe(input: SubscriberInput, db: Session = Depends(get_db)):
    if not input.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email Zorunludur",
        )

    service = SubscriberService(db)
    try:
        service.subscribe_user(input)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email zaten kayıtlı",
        )

    return {"message": "Başarıyla kayıt olundu!"}
