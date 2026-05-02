import requests
import json
from urllib.parse import quote
from sqlalchemy.orm import Session
from datetime import datetime

from config import config
from modules.subscriber.models import Subscriber
from .models import SendStoryRequest, SendStoryResponse, MailLog
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

    def _get_active_combos(self, language_filter: str | None = None) -> list[tuple[str, str]]:
        """DB'deki aktif (level, genre) kombinasyonlarını döner."""
        query = self.db.query(Subscriber.level, Subscriber.genre).distinct()
        if language_filter and language_filter.lower() not in ["string", ""]:
            query = query.filter(Subscriber.language == language_filter)
        combos = []
        for level, genre in query.all():
            if level and level.strip():
                combos.append((level.strip(), (genre or "travel").strip()))
        return combos

    def _get_subscribers_by_combo(self, level: str, genre: str, language_filter: str | None = None) -> list[str]:
        query = self.db.query(Subscriber.email).filter(
            Subscriber.level == level,
            Subscriber.genre == genre,
        )
        if language_filter and language_filter.lower() not in ["string", ""]:
            query = query.filter(Subscriber.language == language_filter)
        emails = []
        for row in query.all():
            target = row[0] if isinstance(row, (tuple, list)) else row
            clean = str(target).strip().strip("()',")
            if clean:
                emails.append(clean)
        return emails

    def send_story(self, request: SendStoryRequest):
        combos = self._get_active_combos(request.language_filter)
        print(f"[Mailer] Aktif (seviye, tür) kombinasyonları: {combos}")

        total_sent, total_failed, all_recipients = 0, 0, []
        last_topic = "General"

        for level, genre in combos:
            topic = genre  # genre doğrudan hikaye konusu olarak kullanılır
            last_topic = topic
            print(f"\n[Mailer] {level.upper()} / {genre} için hikaye üretiliyor...")

            story_req = StoryRequest(topic=topic, level=level, language="English", word_count=200)
            try:
                generated = self.story_service.generate_story(story_req)
                level_story = generated.story
            except Exception as e:
                error_msg = str(e).lower()
                print(f"[Mailer] {level}/{genre} hikayesi üretilemedi: {e}")
                if any(k in error_msg for k in ["quota", "rate", "limit", "429", "resource_exhausted"]):
                    self._send_admin_alert(
                        subject="⚠️ Gemini API Limiti Doldu",
                        body=(
                            f"Gemini API kotası aşıldı.<br><br>"
                            f"<b>Seviye:</b> {level.upper()}<br>"
                            f"<b>Tür:</b> {genre}<br>"
                            f"<b>Hata:</b> {e}"
                        )
                    )
                total_failed += len(self._get_subscribers_by_combo(level, genre, request.language_filter))
                continue

            story_url = None
            try:
                db_story = Story(topic=topic, level=level, language="English", content=level_story)
                self.db.add(db_story)
                self.db.commit()
                self.db.refresh(db_story)
                story_url = f"{config.APP_BASE_URL}/stories/{db_story.id}"
            except Exception as e:
                print(f"[Mailer] {level}/{genre} hikayesi kaydedilemedi: {e}")
                self.db.rollback()

            emails = self._get_subscribers_by_combo(level, genre, request.language_filter)
            subject = f"📖 Daily Story: {topic.title()}"
            print(f"[Mailer] {level.upper()}/{genre} için {len(emails)} abone bulundu.")

            for email in emails:
                try:
                    unsubscribe_url = f"{config.APP_BASE_URL}/api/v1/unsubscribe?email={quote(email)}"
                    html = build_email_html(topic, level, level_story, unsubscribe_url, story_url)
                    self._send_one(email, subject, html)
                    total_sent += 1
                    all_recipients.append(email)
                except Exception as e:
                    print(f"[Mailer] {email} gönderilemedi: {e}")
                    total_failed += 1

        print(f"\n{'='*40}")
        print(f"[Mailer] ÖZET: {total_sent} başarılı, {total_failed} başarısız")
        print(f"[Mailer] Alıcılar: {', '.join(all_recipients) if all_recipients else '-'}")
        print(f"{'='*40}\n")

        # Veritabanına log kaydet
        try:
            log = MailLog(
                topic=", ".join({g for _, g in combos}) or last_topic,
                total_sent=total_sent,
                total_failed=total_failed,
                recipients=", ".join(all_recipients) if all_recipients else None,
            )
            self.db.add(log)
            self.db.commit()
            print(f"[Mailer] Log kaydedildi (id={log.id})")
        except Exception as e:
            self.db.rollback()
            print(f"[Mailer] Log kaydedilemedi: {e}")

        # Tüm mailler gittikten sonra bugünün hikayelerinden rastgele birini Instagram'a paylaş
        try:
            from modules.instagram.service import InstagramService
            print("[Mailer] Tüm mailler gönderildi, Instagram paylaşımı başlatılıyor...")
            story = self.story_service.get_random_today_story(self.db)
            if story:
                instagram = InstagramService()
                result = instagram.post(
                    story_id=story.id,
                    topic=story.topic,
                    level=story.level,
                    content=story.content,
                )
                print(f"[Mailer] Instagram paylaşıldı: {result.get('permalink', '')}")
            else:
                print("[Mailer] Instagram için bugüne ait hikaye bulunamadı.")
        except Exception as e:
            import traceback
            print(f"[Mailer] Instagram paylaşım hatası: {e}")
            print(traceback.format_exc())

        # Mailler gittikten sonra topics.md'deki sıradaki konuyu arka planda üret
        try:
            from modules.blog.generator import read_next_topic
            from modules.blog.models import BlogGenerationJob
            from modules.blog.router import _run_blog_generation_job
            import threading

            # Zaten çalışan bir job varsa başlatma
            active = self.db.query(BlogGenerationJob).filter(
                BlogGenerationJob.status.in_(["pending", "running"])
            ).first()

            if active:
                print(f"[Mailer] Blog üretimi zaten devam ediyor (job #{active.id}), atlanıyor.")
            else:
                topic = read_next_topic(self.db)
                if topic:
                    topic_key = f"{topic[0]} | {topic[1]}"
                    job = BlogGenerationJob(topic=topic_key, status="pending")
                    self.db.add(job)
                    self.db.commit()
                    self.db.refresh(job)
                    threading.Thread(
                        target=_run_blog_generation_job, args=(job.id,), daemon=False
                    ).start()
                    print(f"[Mailer] Blog üretimi başlatıldı (job #{job.id}): {topic_key}")
                else:
                    print("[Mailer] Bekleyen blog konusu yok (topics.md).")
        except Exception as e:
            print(f"[Mailer] Blog üretim başlatma hatası (mail gönderimi etkilenmedi): {e}")

        # Günlük psikoloji kitabı özetini admin'e gönder
        try:
            from modules.book_summary.service import BookSummaryService
            BookSummaryService().send_daily(self.db)
        except Exception as e:
            print(f"[Mailer] Kitap özeti gönderilemedi (mail gönderimi etkilenmedi): {e}")

        return SendStoryResponse(sent=total_sent, failed=total_failed, recipients=all_recipients)
