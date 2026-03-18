import requests
from sqlalchemy.orm import Session

from config import config
from .models import Subscriber, SubscriberInput
from modules.mailer.template import build_welcome_email_html


class SubscriberService:
    def __init__(self, db: Session):
        self.db = db

    def subscribe_user(self, input: SubscriberInput) -> Subscriber:
        subscriber = Subscriber(
            email=input.email,
            level=input.level,
            language=input.language
        )
        self.db.add(subscriber)
        self.db.commit()
        self.db.refresh(subscriber)

        # Hoş geldin maili gönder
        try:
            self._send_welcome_email(subscriber)
            print(f"[Subscriber] Hoş geldin maili gönderildi: {subscriber.email}")
        except Exception as e:
            print(f"[Subscriber] Hoş geldin maili gönderilemedi: {e}")

        return subscriber

    def _send_welcome_email(self, subscriber: Subscriber) -> None:
        level = subscriber.level or "A2"
        language = subscriber.language or "English"

        html = build_welcome_email_html(
            email=subscriber.email,
            level=level,
            language=language,
        )

        payload = {
            "sender": {
                "name": config.MAIL_FROM_NAME,
                "email": config.SMTP_USER,
            },
            "to": [{"email": subscriber.email}],
            "subject": "🎉 Welcome to English Story!",
            "htmlContent": html,
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "api-key": config.SMTP_PASSWORD,
        }

        response = requests.post(
            "https://api.brevo.com/v3/smtp/email",
            json=payload,
            headers=headers,
        )

        if response.status_code not in [200, 201, 202]:
            raise Exception(f"Brevo API Error: {response.text}")
