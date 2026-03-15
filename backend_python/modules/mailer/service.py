import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

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
        print(f"   --> {to_email} adresine gönderiliyor...")
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{config.MAIL_FROM_NAME} <{config.SMTP_USER}>"
        msg["To"] = to_email
        msg.attach(MIMEText(html, "html"))

        try:
            # Port 465 ise doğrudan SSL, değilse (587 vb) STARTTLS kullanıyoruz
            if int(config.SMTP_PORT) == 465:
                server_class = smtplib.SMTP_SSL
            else:
                server_class = smtplib.SMTP

            with server_class(config.SMTP_HOST, config.SMTP_PORT) as server:
                if int(config.SMTP_PORT) != 465:
                    server.starttls()
                server.login(config.SMTP_USER, config.SMTP_PASSWORD)
                server.sendmail(config.SMTP_USER, to_email, msg.as_string())
            print(f"   [BAŞARILI] {to_email}")
        except Exception as e:
            print(f"   [HATA] {to_email} gönderilemedi! Hata: {str(e)}")
            raise e # Üst fonksiyona hatayı fırlat ki failed sayacı artsın

    def send_story(self, request: SendStoryRequest):
        print(f"\n--- MAIL GÖNDERİMİ BAŞLADI: {request.topic} ---")
        
        # 1. Eğer hikaye boşsa AI'dan üret
        current_story = request.story.strip()
        if not current_story or current_story == "string":
            print(f"Hikaye boş, AI üretimi başlatılıyor: {request.topic} ({request.level})")
            story_req = StoryRequest(
                topic=request.topic,
                level=request.level if request.level in ["beginner", "intermediate", "advanced"] else "beginner",
                word_count=200 # Varsayılan uzunluk
            )
            generated = self.story_service.generate_story(story_req)
            current_story = generated.story
            print("AI Hikayeyi başarıyla üretti.")

        emails = self._get_subscribers(request.level_filter)
        
        print(f"Gönderilecek Toplam Email Sayısı: {len(emails)}")
        subject = f"📖 Your English Story: {request.topic}"
        html = build_email_html(request.topic, request.level, current_story)

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
