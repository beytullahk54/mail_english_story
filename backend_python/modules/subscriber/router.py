from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import traceback

from database import get_db
from .models import SubscriberInput
from .service import SubscriberService

router = APIRouter(tags=["subscriber"])

@router.post("/subscribe", status_code=status.HTTP_201_CREATED)
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
    except Exception as e:
        db.rollback()
        error_detail = traceback.format_exc()
        print(f"[SUBSCRIBE ERROR] {e}\n{error_detail}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sunucu hatası: {str(e)}",
        )

    return {"message": "Başarıyla kayıt olundu!"}
