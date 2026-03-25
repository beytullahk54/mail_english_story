import requests
import json
from urllib.parse import quote
from sqlalchemy.orm import Session
from datetime import datetime

from config import config
from modules.subscriber.models import Subscriber
from .models import SendStoryRequest, SendStoryResponse
from .template import build_email_html
from modules.story.service import StoryService
from modules.story.models import StoryRequest, Story


class MailerService:
    def __init__(self, db: Session):
        self.db = db
        self.story_service = StoryService()

    def _get_subscribers(self, level_filter: str | None, language_filter: str | None = None):
        print("\n--- [SERVICE] _get_subscribers BAŞLADI ---")
        
        query = self.db.query(Subscriber.email)
        
        if level_filter and level_filter.lower() != "string" and level_filter.strip() != "":
            print(f"Level filtre uygulanıyor: {level_filter}")
            query = query.filter(Subscriber.level == level_filter)
            
        if language_filter and language_filter.lower() != "string" and language_filter.strip() != "":
            print(f"Dil filtre uygulanıyor: {language_filter}")
            query = query.filter(Subscriber.language == language_filter)
        
        raw_emails = query.all()
        emails = []
        for row in raw_emails:
            if not row: continue
            target = row[0] if isinstance(row, (tuple, list)) else row
            clean_email = str(target).replace("(", "").replace(")", "").replace("'", "").replace(",", "").strip()
            if clean_email:
                emails.append(clean_email)

        print(f"Abone Sayısı: {len(emails)}")
        return emails

    def _send_one(self, to_email: str, subject: str, html: str) -> None:
        url = "https://api.brevo.com/v3/smtp/email"
        payload = {
            "sender": {"name": config.MAIL_FROM_NAME, "email": config.SMTP_USER},
            "to": [{"email": to_email}],
            "subject": subject,
            "htmlContent": html
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "api-key": config.SMTP_PASSWORD
        }
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code not in [200, 201, 202]:
            raise Exception(f"Brevo API Error: {response.text}")

    def _send_admin_alert(self, subject: str, body: str) -> None:
        if not config.ADMIN_EMAIL:
            return
        payload = {
            "sender": {"name": config.MAIL_FROM_NAME, "email": config.SMTP_USER},
            "to": [{"email": config.ADMIN_EMAIL}],
            "subject": subject,
            "htmlContent": f"<p>{body}</p>"
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "api-key": config.SMTP_PASSWORD
        }
        try:
            requests.post("https://api.brevo.com/v3/smtp/email", json=payload, headers=headers)
            print(f"[Admin Alert] Gönderildi: {config.ADMIN_EMAIL}")
        except Exception as e:
            print(f"[Admin Alert] Gönderilemedi: {e}")

    def _get_active_levels(self, language_filter: str | None = None) -> list[str]:
        query = self.db.query(Subscriber.level).distinct()
        if language_filter and language_filter.lower() not in ["string", ""]:
            query = query.filter(Subscriber.language == language_filter)
        return [row[0] for row in query.all() if row[0] and row[0].strip()]

    def send_story(self, request: SendStoryRequest):
        current_topic = request.topic.strip() if request.topic else "General"
        if current_topic.lower() == "string":
            current_topic = "General"

        # Hangi seviyelere göndereceğimizi belirle
        level_filter = request.level_filter
        if level_filter and level_filter.lower() not in ["string", ""]:
            levels = [level_filter.lower().strip()]
        else:
            levels = self._get_active_levels(request.language_filter)

        print(f"[Mailer] Gönderilecek seviyeler: {levels}")

        subject = f"📖 Daily Story: {current_topic}"
        total_sent, total_failed, all_recipients = 0, 0, []

        for level in levels:
            print(f"\n[Mailer] {level.upper()} seviyesi için hikaye üretiliyor...")

            # Her seviye için ayrı hikaye üret
            story_req = StoryRequest(
                topic=current_topic,
                level=level,
                language="English",
                word_count=200
            )
            try:
                generated = self.story_service.generate_story(story_req)
                level_story = generated.story
            except Exception as e:
                error_msg = str(e).lower()
                print(f"[Mailer] {level} hikayesi üretilemedi: {e}")
                if any(k in error_msg for k in ["quota", "rate", "limit", "429", "resource_exhausted"]):
                    self._send_admin_alert(
                        subject="⚠️ Gemini API Limiti Doldu",
                        body=(
                            f"Gemini API kotası aşıldı, hikaye üretilemedi.<br><br>"
                            f"<b>Seviye:</b> {level.upper()}<br>"
                            f"<b>Konu:</b> {current_topic}<br><br>"
                            f"<b>Hata:</b> {e}"
                        )
                    )
                total_failed += len(self._get_subscribers(level, request.language_filter))
                continue

            # Veritabanına kaydet
            try:
                db_story = Story(topic=current_topic, level=level, language="English", content=level_story)
                self.db.add(db_story)
                self.db.commit()
            except Exception as e:
                print(f"[Mailer] {level} hikayesi kaydedilemedi: {e}")
                self.db.rollback()

            # O seviyedeki abonelere gönder
            emails = self._get_subscribers(level, request.language_filter)
            print(f"[Mailer] {level.upper()} için {len(emails)} abone bulundu.")

            for email in emails:
                try:
                    unsubscribe_url = f"{config.APP_BASE_URL}/api/v1/unsubscribe?email={quote(email)}"
                    html = build_email_html(current_topic, level, level_story, unsubscribe_url)
                    self._send_one(email, subject, html)
                    total_sent += 1
                    all_recipients.append(email)
                except Exception as e:
                    print(f"[Mailer] {email} gönderilemedi: {e}")
                    total_failed += 1

        return SendStoryResponse(sent=total_sent, failed=total_failed, recipients=all_recipients)
