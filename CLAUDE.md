# Mail English Story — CLAUDE.md

Proje mimarisi ve geliştirme rehberi. Bu dosya Claude Code ile çalışırken bağlam sağlamak için tutulur.

---

## Proje Özeti

Günlük İngilizce hikaye bülteni. Aboneler e-posta ile kaydolur, Google Gemini API her gün hikayeler üretir ve Brevo SMTP üzerinden abone seviyelerine göre filtrelenmiş e-postalar gönderilir.

**Canlı URL:** `https://englishstory.kodsey.com`

---

## Teknoloji Stack

| Katman | Teknoloji |
|--------|-----------|
| Frontend | Nuxt 4, Vue 3, PrimeVue 4 (Aura tema), PrimeIcons |
| Backend (aktif) | Python FastAPI + SQLAlchemy + psycopg2 |
| Backend (alternatif) | Go + Fiber + GORM (sadece subscriber modülü mevcut) |
| Veritabanı | PostgreSQL |
| AI | Google Gemini (`gemini-2.5-flash`) |
| E-posta | Brevo SMTP API v3 |
| Hosting | Railway / Render desteği (DATABASE_URL otomatik tanınır) |

---

## Dizin Yapısı

```
mail_english_story/
├── backend_python/          # Ana backend (FastAPI)
│   ├── main.py              # Uygulama giriş noktası, router kayıtları, migration
│   ├── config.py            # .env okuma (Config sınıfı)
│   ├── database.py          # SQLAlchemy engine, SessionLocal, get_db()
│   ├── security.py          # X-Api-Token doğrulama
│   └── modules/
│       ├── subscriber/      # Abone yönetimi
│       │   ├── models.py    # Subscriber ORM + Pydantic modeller
│       │   ├── router.py    # POST /subscribe, GET /unsubscribe
│       │   └── service.py   # İş mantığı + welcome e-posta
│       ├── story/           # Hikaye üretimi ve listeleme
│       │   ├── models.py    # Story ORM + StoryRequest/Response + StoriesListResponse
│       │   ├── router.py    # POST /generate, GET /list
│       │   └── service.py   # Gemini API çağrısı + DB sorgulama
│       └── mailer/          # Toplu e-posta gönderimi
│           ├── models.py    # MailerRequest Pydantic modeli
│           ├── router.py    # POST /send (X-Api-Token korumalı)
│           ├── service.py   # Seviyeye göre hikaye üret + filtreli gönderim
│           └── template.py  # HTML e-posta şablonları (welcome + story)
│
├── backend_go/              # Alternatif backend (sadece subscriber)
│   ├── cmd/api/main.go
│   └── internal/modules/subscriber/
│
├── frontend/                # Nuxt 4 uygulaması
│   ├── nuxt.config.ts       # PrimeVue, CORS-free config, runtimeConfig
│   ├── app/
│   │   ├── app.vue          # Root bileşen (Toast provider)
│   │   ├── pages/
│   │   │   ├── index.vue    # Landing sayfası (abone formu)
│   │   │   ├── story.vue    # AI hikaye üretici
│   │   │   └── stories.vue  # Hikaye arşivi (listeleme + pagination)
│   │   └── assets/css/main.css  # Global stiller (glassmorphism, animasyonlar)
│   └── .env.example
│
└── CLAUDE.md                # Bu dosya
```

---

## Veritabanı Şeması

```sql
-- Aboneler
CREATE TABLE subscribers (
    id          SERIAL PRIMARY KEY,
    email       VARCHAR UNIQUE NOT NULL,
    level       VARCHAR(10),
    language    VARCHAR(20) DEFAULT 'English',
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Hikayeler
CREATE TABLE stories (
    id          SERIAL PRIMARY KEY,
    topic       VARCHAR(100) NOT NULL,
    level       VARCHAR(20) NOT NULL,
    language    VARCHAR(20) NOT NULL DEFAULT 'English',
    content     TEXT NOT NULL,
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

> Migration `main.py` içinde `Base.metadata.create_all()` + manuel `ALTER TABLE` ile yönetilir. ORM migration aracı (Alembic vb.) kullanılmıyor.

---

## API Endpoint Listesi

### Subscriber

| Method | Endpoint | Auth | Açıklama |
|--------|----------|------|----------|
| POST | `/api/v1/subscribe` | - | Abone ol (welcome e-posta gönderir) |
| GET | `/api/v1/unsubscribe?email=` | - | Abonelikten çık (HTML response) |

### Story

| Method | Endpoint | Auth | Açıklama |
|--------|----------|------|----------|
| POST | `/api/v1/story/generate` | - | Gemini ile hikaye üret |
| GET | `/api/v1/story/list` | - | DB'den hikayeleri listele (pagination + filtre) |

**GET /api/v1/story/list query params:**
- `page` (int, default: 1)
- `page_size` (int, default: 10, max: 50)
- `level` (string, opsiyonel): `a1`, `a2`, `b1`, `b2`, `beginner`, `intermediate`, `advanced`
- `language` (string, opsiyonel)

### Mailer

| Method | Endpoint | Auth | Açıklama |
|--------|----------|------|----------|
| POST | `/api/v1/mailer/send` | `X-Api-Token` header | Tüm seviyelere hikaye üret + e-posta gönder |

---

## Frontend Sayfaları

| Sayfa | Route | Açıklama |
|-------|-------|----------|
| Landing | `/` | Abone formu, çok dilli (8 dil), seviye seçimi |
| Story Generator | `/story` | AI ile hikaye üret, kopyala |
| Story Archive | `/stories` | DB'deki hikayeleri listele, seviye filtresi, pagination |

**Çevre değişkeni:** `NUXT_PUBLIC_API_BASE` → backend URL'si (frontend `runtimeConfig.public.apiBase` olarak okur)

---

## Seviye Sistemi

Hikaye üretimde kullanılan seviyeler ve karşılıkları:

| Değer | CEFR | Prompt tanımı |
|-------|------|---------------|
| `a1` | A1 | very simple sentences, basic vocabulary |
| `beginner` | A1-A2 | simple sentences, basic vocabulary |
| `a2` | A2 | simple sentences, basic everyday vocabulary |
| `b1` | B1 | varied sentence structures, intermediate vocabulary |
| `intermediate` | B1-B2 | varied sentence structures, everyday vocabulary |
| `b2` | B2 | complex sentence structures, upper-intermediate vocabulary |
| `advanced` | C1-C2 | complex sentences, rich vocabulary and idioms |

> Hikayeler her zaman **İngilizce** üretilir. `language` alanı abonenin tercih ettiği arayüz dilini ifade eder.

---

## Ortam Değişkenleri (backend_python/.env)

```env
DB_USER=
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=5432
DB_NAME=

# Alternatif (Railway/Render):
# DATABASE_URL=postgresql://...

SERVER_PORT=8000
GEMINI_API_KEY=
SMTP_HOST=smtp-relay.brevo.com
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
MAIL_FROM_NAME=English Story
APP_SECRET_TOKEN=        # /mailer/send endpoint koruması
APP_BASE_URL=https://englishstory.kodsey.com
ADMIN_EMAIL=             # Gemini kota hatası bildirim adresi
```

---

## Önemli Notlar

- **İki backend var** ama sadece `backend_python` tam özellikli. `backend_go` yalnızca abone kayıt modülüne sahip.
- **CORS**: `allow_origins=["*"]` — tüm kaynaklara açık.
- **Mailer akışı**: `/mailer/send` çağrıldığında her seviye için ayrı hikaye üretilir, aboneler `level` ve `language`'a göre filtrelenir, her birine kendi seviyesine uygun hikaye gönderilir.
- **StoryService.get_stories()** veritabanından okur; Gemini'yi çağırmaz.
- **Frontend dil tespiti**: `onMounted` içinde `navigator.language` ile tarayıcı dili otomatik algılanır.
