"""
Instagram oturumu başlat ve session dosyasını kaydet.
Sadece bir kez çalıştırılır. Sonrasında servis session dosyasını kullanır.

Kullanım:
    cd backend_python
    python instagram_login.py

IP engeli varsa proxy ile:
    INSTAGRAM_PROXY=socks5://user:pass@host:port python instagram_login.py
    INSTAGRAM_PROXY=http://user:pass@host:port python instagram_login.py
"""

import os
import sys
from dotenv import load_dotenv
from instagrapi import Client
from instagrapi.exceptions import LoginRequired, TwoFactorRequired, ChallengeRequired

load_dotenv()

USERNAME = os.getenv("INSTAGRAM_USERNAME", "")
PASSWORD = os.getenv("INSTAGRAM_PASSWORD", "")
PROXY    = os.getenv("INSTAGRAM_PROXY", "")
SESSION_FILE = "instagram_session.json"

if not USERNAME or not PASSWORD:
    print("❌ .env dosyasında INSTAGRAM_USERNAME ve INSTAGRAM_PASSWORD eksik.")
    sys.exit(1)

client = Client()
client.delay_range = [1, 3]

if PROXY:
    client.set_proxy(PROXY)
    print(f"🌐 Proxy kullanılıyor: {PROXY}")
else:
    print("ℹ️  Proxy yok. IP engeli hatası alırsan:")
    print("   INSTAGRAM_PROXY=socks5://user:pass@host:port python instagram_login.py")

# Var olan session'ı dene
if os.path.exists(SESSION_FILE):
    print(f"📂 Mevcut session bulundu: {SESSION_FILE}")
    try:
        client.load_settings(SESSION_FILE)
        client.login(USERNAME, PASSWORD)
        print("✅ Mevcut session ile giriş başarılı.")
        sys.exit(0)
    except Exception as e:
        print(f"⚠️  Session geçersiz ({e}), yeniden giriş yapılıyor...")

# Yeni giriş
try:
    client.login(USERNAME, PASSWORD)
    client.dump_settings(SESSION_FILE)
    print(f"✅ Giriş başarılı. Session kaydedildi: {SESSION_FILE}")

except TwoFactorRequired:
    code = input("📱 2FA kodu girin: ").strip()
    client.login(USERNAME, PASSWORD, verification_code=code)
    client.dump_settings(SESSION_FILE)
    print(f"✅ 2FA ile giriş başarılı. Session kaydedildi: {SESSION_FILE}")

except ChallengeRequired:
    print("⚠️  Instagram güvenlik doğrulaması istiyor...")
    client.challenge_resolve(client.last_json)
    choice = input("   Doğrulama yöntemi (0=SMS, 1=Email): ").strip()
    client.challenge_send_code(int(choice))
    code = input("   Gelen kodu girin: ").strip()
    client.challenge_code(code)
    client.dump_settings(SESSION_FILE)
    print(f"✅ Challenge ile giriş başarılı. Session kaydedildi: {SESSION_FILE}")

except LoginRequired as e:
    print(f"❌ Giriş başarısız: {e}")
    sys.exit(1)

except Exception as e:
    print(f"❌ Beklenmeyen hata: {e}")
    print()
    print("💡 IP engeli mi? Şunları dene:")
    print("   1. Mobil hotspot'a geç ve tekrar çalıştır")
    print("   2. VPN'i kapat/değiştir")
    print("   3. Proxy kullan:")
    print("      INSTAGRAM_PROXY=socks5://user:pass@host:port python instagram_login.py")
    sys.exit(1)
