from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from security import verify_token
from .models import PsychologyBook
from .service import BookSummaryService

router = APIRouter(prefix="/books", tags=["books"])


@router.get("", dependencies=[Depends(verify_token)])
def list_books(db: Session = Depends(get_db)):
    books = db.query(PsychologyBook).order_by(PsychologyBook.id.asc()).all()
    return {
        "total": len(books),
        "items": [
            {
                "id": b.id,
                "title": b.title,
                "author": b.author,
                "last_sent_at": b.last_sent_at.isoformat() if b.last_sent_at else None,
            }
            for b in books
        ],
    }


@router.post("", status_code=status.HTTP_201_CREATED, dependencies=[Depends(verify_token)])
def add_book(data: dict, db: Session = Depends(get_db)):
    title = (data.get("title") or "").strip()
    author = (data.get("author") or "").strip()
    if not title or not author:
        raise HTTPException(status_code=400, detail="title ve author zorunlu")
    book = PsychologyBook(title=title, author=author)
    db.add(book)
    db.commit()
    db.refresh(book)
    return {"id": book.id, "title": book.title, "author": book.author}


@router.delete("/{book_id}", dependencies=[Depends(verify_token)])
def delete_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(PsychologyBook).filter(PsychologyBook.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Kitap bulunamadı")
    db.delete(book)
    db.commit()
    return {"message": "Silindi"}


@router.post("/suggest-ai", dependencies=[Depends(verify_token)])
def suggest_books_ai(db: Session = Depends(get_db)):
    try:
        added = BookSummaryService().suggest_books_ai(db, count=10)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {
        "added": len(added),
        "items": [{"id": b.id, "title": b.title, "author": b.author} for b in added],
        "message": f"{len(added)} kitap AI ile eklendi." if added else "AI yeni kitap önermedi.",
    }


@router.post("/seed", dependencies=[Depends(verify_token)])
def seed_books(db: Session = Depends(get_db)):
    count = BookSummaryService().seed_books(db)
    return {
        "seeded": count,
        "message": f"{count} kitap eklendi." if count else "Kitaplar zaten mevcut.",
    }


@router.post("/send-daily", dependencies=[Depends(verify_token)])
def send_daily(db: Session = Depends(get_db)):
    """Manuel tetikleme — mailer'dan da otomatik çağrılır."""
    try:
        result = BookSummaryService().send_daily(db)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
