import requests
import json
from sqlalchemy.orm import Session

from config import config
from modules.subscriber.models import Subscriber
from .models import SendStoryRequest, SendStoryResponse
from .template import build_email_html
from modules.story.service import StoryService # Story hizmetini içeri alıyoruz
from modules.story.models import StoryRequest


class MailerService:
    def __init__(self, db: Session):
        self.db = db
        self.story_service = StoryService() # AI servisini başlatıyoruz

    def _get_subscribers(self, level_filter: str | None):
        print("\n--- [SERVICE] _get_subscribers BAŞLADI ---")
        
        # Önce veritabanında toplamda biri var mı diye bakalım
        total_count = self.db.query(Subscriber).count()
        print(f"Veritabanındaki Toplam Abone Sayısı: {total_count}")

        query = self.db.query(Subscriber.email)
        if level_filter and level_filter != "string" and level_filter.strip() != "":
            print(f"Filtre uygulanıyor: {level_filter}")
            query = query.filter(Subscriber.level == level_filter)
        
        # Veritabanından gelen veriyi temizleme (Kesin çözüm)
        raw_emails = query.all()
        emails = []
        for row in raw_emails:
            if not row: continue
            
            # Eğer row bir tuple ise ilk elemanı al, değilse kendisini al
            target = row[0] if isinstance(row, (tuple, list)) else row
            
            # String'e çevir ve parantez/tırnak kalıntılarını temizle
            clean_email = str(target).replace("(", "").replace(")", "").replace("'", "").replace(",", "").strip()
            
            if clean_email:
                emails.append(clean_email)

        print(f"TEMİZLENMİŞ Email Listesi: {emails}")
        print("--- [SERVICE] _get_subscribers BİTTİ ---\n")
        
        return emails

    def _send_one(self, to_email: str, subject: str, html: str) -> None:
        print(f"   --> {to_email} adresine Brevo API ile gönderiliyor...")
        
        url = "https://api.brevo.com/v3/smtp/email"
        
        payload = {
            "sender": {
                "name": config.MAIL_FROM_NAME,
                "email": config.SMTP_USER
            },
            "to": [
                {
                    "email": to_email
                }
            ],
            "subject": subject,
            "htmlContent": html
        }
        
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "api-key": config.SMTP_PASSWORD # Artık .env'deki SMTP_PASSWORD'ü API Key olarak kullanıyoruz
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code in [201, 202, 200]:
                print(f"   [BAŞARILI] {to_email}")
            else:
                print(f"   [HATA] {to_email} Hata Kodu: {response.status_code}")
                print(f"   Detay: {response.text}")
                raise Exception(f"Brevo API Hatası: {response.text}")
        except Exception as e:
            print(f"   [KRİTİK HATA] {to_email} gönderilemedi: {str(e)}")
            raise e

    def send_story(self, request: SendStoryRequest):
        # 1. Konu, Level ve Hikaye temizliği
        current_topic = request.topic.strip()
        if not current_topic or current_topic.lower() == "string":
            current_topic = "Travel"
            
        # Seviyeyi doğrula
        clean_level = request.level.lower().strip()
        if clean_level not in ["beginner", "intermediate", "advanced"]:
            clean_level = "beginner"

        current_story = request.story.strip()
        
        # Eğer hikaye; boşsa, "string" ise veya konu ile aynıysa AI üretsin
        should_generate = (
            not current_story or 
            current_story.lower() == "string" or 
            current_story.lower() == current_topic.lower()
        )

        if should_generate:
            print(f"\n--- AI HİKAYE ÜRETİMİ BAŞLADI: {current_topic} ({clean_level}) ---")
            story_req = StoryRequest(
                topic=current_topic,
                level=clean_level,
                word_count=200 
            )
            generated = self.story_service.generate_story(story_req)
            current_story = generated.story
            print("AI Hikayeyi başarıyla üretti.\n")

        print(f"--- MAIL GÖNDERİMİ BAŞLADI: {current_topic} ---")
        emails = self._get_subscribers(request.level_filter)
        
        print(f"Gönderilecek Toplam Email Sayısı: {len(emails)}")
        subject = f"📖 Your English Story: {current_topic}"
        html = build_email_html(current_topic, clean_level, current_story)

        sent, failed, recipients = 0, 0, []

        for email in emails:
            try:
                self._send_one(email, subject, html)
                sent += 1
                recipients.append(email)
            except Exception as e:
                # _send_one içindeki print hatayı zaten yazacak, burada sadece sayıyoruz
                failed += 1

        print(f"\n--- GÖNDERİM TAMAMLANDI ---")
        print(f"Sonuç: {sent} Başarılı, {failed} Hatalı")
        print("---------------------------\n")

        return SendStoryResponse(sent=sent, failed=failed, recipients=recipients)
