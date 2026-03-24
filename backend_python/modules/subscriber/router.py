from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import traceback

from database import get_db
from .models import SubscriberInput
from .service import SubscriberService

router = APIRouter(tags=["subscriber"])

@router.get("/unsubscribe", response_class=HTMLResponse)
def unsubscribe(email: str, db: Session = Depends(get_db)):
    service = SubscriberService(db)
    deleted = service.unsubscribe_user(email)
    if not deleted:
        return HTMLResponse(content="""
        <html><body style="font-family:sans-serif;text-align:center;padding:60px;background:#0f172a;color:#94a3b8;">
        <h2>⚠️ Email not found</h2>
        <p>This email is not subscribed or already unsubscribed.</p>
        </body></html>
        """, status_code=404)
    return HTMLResponse(content="""
    <html><body style="font-family:sans-serif;text-align:center;padding:60px;background:#0f172a;color:#94a3b8;">
    <h2 style="color:#f1f5f9;">✅ Unsubscribed successfully</h2>
    <p>You have been removed from the English Story mailing list.</p>
    </body></html>
    """)

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
