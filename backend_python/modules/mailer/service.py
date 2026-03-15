import requests
import json
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

    def send_story(self, request: SendStoryRequest):
        # 1. Temizlik ve Varsayılanlar
        current_topic = request.topic.strip() if request.topic else "General"
        if current_topic.lower() == "string":
            current_topic = "General"
            
        # Level Boşsa A2 yapılsın
        clean_level = request.level.lower().strip() if request.level else "a2"
        if clean_level in ["none", "string", ""]:
            clean_level = "a2"

        current_story = request.story.strip()
        should_generate = (
            not current_story or 
            current_story.lower() == "string" or 
            current_story.lower() == current_topic.lower()
        )

        if should_generate:
            print(f"AI Hikaye Üretiliyor: {current_topic} ({clean_level})")
            story_req = StoryRequest(
                topic=current_topic,
                level=clean_level,
                language="English", # İçerik her zaman İngilizce
                word_count=200 
            )
            generated = self.story_service.generate_story(story_req)
            current_story = generated.story

        # 2. Hikayeyi Veritabanına Kaydet
        try:
            db_story = Story(
                topic=current_topic,
                level=clean_level,
                language="English",
                content=current_story
            )
            self.db.add(db_story)
            self.db.commit()
            print("Hikaye veritabanına kaydedildi.")
        except Exception as e:
            print(f"Hikaye kaydedilirken hata: {str(e)}")
            self.db.rollback()

        # 3. Mail Gönderimi
        emails = self._get_subscribers(request.level_filter, request.language_filter)
        subject = f"📖 Daily Story: {current_topic}"
        html = build_email_html(current_topic, clean_level, current_story)

        sent, failed, recipients = 0, 0, []
        for email in emails:
            try:
                self._send_one(email, subject, html)
                sent += 1
                recipients.append(email)
            except:
                failed += 1

        return SendStoryResponse(sent=sent, failed=failed, recipients=recipients)
