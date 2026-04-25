import requests
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from google import genai

from config import config
from .models import PsychologyBook

SEED_BOOKS = [
    ("Hızlı ve Yavaş Düşünme", "Daniel Kahneman"),
    ("Sessiz: İçe Dönüklerin Gücü", "Susan Cain"),
    ("Muhabbet Tılsımı", "Hüseyin Rahmi Gürpınar"),
    ("10x Kuralı", "Grant Cardone"),
    ("Öz Saygı Dersleri", "Nathaniel Branden"),
    ("Zihnin Geleceği", "Michio Kaku"),
    ("Genişletilmiş Zihin", "Annie Murphy Paul"),
    ("Sayısal Zeka", "Stanislas Dehaene"),
    ("Beynin Bilimi", "David Eagleman"),
    ("Hayatımızdaki Algoritmalar", "Brian Christian & Tom Griffiths"),
    ("Factfulness", "Hans Rosling"),
    ("Sugestopedi: Hızlı ve Sağlıklı Öğrenme", "Georgi Lozanov"),
]

PROMPT_TEMPLATE = """Sen bir psikoloji kitabı uzmanısın. Aşağıdaki kitabı Türkçe olarak özetle.

Kitap: "{title}"
Yazar: {author}

Şu yapıyı kullan:
1. **Ana Fikir** (2-3 cümle): Kitabın özü nedir?
2. **3 Temel Öğreti**: Her biri 2-3 cümle, numaralı liste
3. **Bugün Uygulayabileceğin 1 Şey**: Somut, pratik bir eylem önerisi
4. **Unutulmaz Alıntı**: Kitaptan çarpıcı bir cümle (İngilizce orijinal + Türkçe çeviri)

Toplam 350-450 kelime. Akıcı, ilgi çekici bir dil kullan.
HTML formatında yaz: <h3>, <p>, <ol>, <li>, <blockquote>, <strong> etiketleri kullan.
<html>, <body>, <head> etiketi kullanma."""


class BookSummaryService:
    def __init__(self):
        self.client = genai.Client(api_key=config.GEMINI_API_KEY)

    def seed_books(self, db: Session) -> int:
        existing = db.query(PsychologyBook).count()
        if existing > 0:
            return 0
        for title, author in SEED_BOOKS:
            db.add(PsychologyBook(title=title, author=author))
        db.commit()
        return len(SEED_BOOKS)

    def get_next_book(self, db: Session) -> PsychologyBook | None:
        """En uzun süredir gönderilmemiş kitabı seç. Liste bitince başa döner."""
        # Önce hiç gönderilmemiş olanlar
        book = (
            db.query(PsychologyBook)
            .filter(PsychologyBook.last_sent_at.is_(None))
            .order_by(PsychologyBook.id.asc())
            .first()
        )
        if book:
            return book
        # Hepsi gönderilmişse en eskiye dön
        return (
            db.query(PsychologyBook)
            .order_by(PsychologyBook.last_sent_at.asc())
            .first()
        )

    def generate_summary(self, title: str, author: str) -> str:
        prompt = PROMPT_TEMPLATE.format(title=title, author=author)
        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        return response.text.strip()

    def _build_email_html(self, title: str, author: str, summary_html: str) -> str:
        return f"""
<!DOCTYPE html>
<html lang="tr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>📚 Günlük Kitap Özeti</title>
</head>
<body style="margin:0;padding:0;background:#0f172a;font-family:'Segoe UI',sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#0f172a;padding:40px 0;">
    <tr>
      <td align="center">
        <table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;">

          <!-- Header -->
          <tr>
            <td style="background:linear-gradient(135deg,#6366f1,#8b5cf6);border-radius:16px 16px 0 0;padding:32px 40px;text-align:center;">
              <p style="margin:0 0 8px;font-size:13px;color:rgba(255,255,255,0.7);letter-spacing:2px;text-transform:uppercase;">Günlük Kitap Özeti</p>
              <h1 style="margin:0 0 6px;font-size:24px;color:#fff;line-height:1.3;">{title}</h1>
              <p style="margin:0;font-size:15px;color:rgba(255,255,255,0.8);">— {author}</p>
            </td>
          </tr>

          <!-- Content -->
          <tr>
            <td style="background:#1e293b;padding:36px 40px;border-radius:0 0 16px 16px;color:#cbd5e1;font-size:15px;line-height:1.8;">
              {summary_html}
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="padding:24px 0;text-align:center;color:#475569;font-size:12px;">
              Sadece sana özel · English Story Admin
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""

    def send_daily(self, db: Session) -> dict:
        """Günün kitabını seç, özet üret, ADMIN_EMAIL'e gönder."""
        if not config.ADMIN_EMAIL:
            return {"status": "skipped", "reason": "ADMIN_EMAIL tanımlı değil"}

        book = self.get_next_book(db)
        if not book:
            return {"status": "skipped", "reason": "Kitap listesi boş. /api/v1/books/seed çağırın."}

        print(f"[BookSummary] Kitap: {book.title} — {book.author}")

        summary_html = self.generate_summary(book.title, book.author)
        html = self._build_email_html(book.title, book.author, summary_html)

        payload = {
            "sender": {"name": "English Story", "email": config.SMTP_USER},
            "to": [{"email": config.ADMIN_EMAIL}],
            "subject": f"📚 {book.title} — Günlük Kitap Özeti",
            "htmlContent": html,
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "api-key": config.SMTP_PASSWORD,
        }
        response = requests.post("https://api.brevo.com/v3/smtp/email", json=payload, headers=headers)
        if response.status_code not in [200, 201, 202]:
            raise Exception(f"Brevo API Error: {response.text}")

        book.last_sent_at = datetime.now(timezone.utc)
        db.commit()

        print(f"[BookSummary] ✓ Gönderildi → {config.ADMIN_EMAIL} ({book.title})")
        return {"status": "sent", "book": book.title, "author": book.author, "to": config.ADMIN_EMAIL}
