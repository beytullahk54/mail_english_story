# Mail English Story — Python FastAPI Backend

E-posta abonelik API'si. Go/Fiber projesinin Python/FastAPI karşılığı.

## Gereksinimler

- Python 3.10+
- PostgreSQL

---

## Kurulum

### 1. Bağımlılıkları yükle

```bash
cd backend_python
pip install -r requirements.txt
```

> Sanal ortam kullanmak önerilir:
> ```bash
> python -m venv venv
> source venv/bin/activate      # macOS/Linux
> venv\Scripts\activate         # Windows
> pip install -r requirements.txt
> ```

### 2. Ortam değişkenlerini ayarla

```bash
cp .env.example .env
```

`.env` dosyasını düzenle:

```env
DB_USER=postgres
DB_PASSWORD=sifren
DB_HOST=localhost
DB_PORT=5432
DB_NAME=mail_english_story
SERVER_PORT=8000
```

Railway, Render gibi platformlarda tek bir URL varsa:

```env
DATABASE_URL=postgresql://user:password@host:port/dbname
```

---

## Ayağa Kaldırma

```bash
python main.py
```

Veya doğrudan uvicorn ile:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Uygulama başladığında tablolar otomatik olarak oluşturulur (AutoMigrate).

---

## API Endpointleri

| Method | Path | Açıklama |
|--------|------|----------|
| `GET` | `/health` | Sağlık kontrolü |
| `POST` | `/api/v1/subscribe/` | Yeni abonelik |

### POST `/api/v1/subscribe/`

**Request Body:**
```json
{
  "email": "ornek@email.com",
  "level": "beginner"
}
```

**Responses:**

| Status | Açıklama |
|--------|----------|
| `201` | Başarıyla kayıt olundu |
| `400` | Email boş bırakılamaz |
| `409` | Email zaten kayıtlı |

---

## Swagger UI

Uygulama çalışırken tarayıcıdan erişilebilir:

```
http://localhost:8000/docs
```

---

## Proje Yapısı

```
backend_python/
├── main.py                  # Uygulama giriş noktası
├── config.py                # Ortam değişkenleri
├── database.py              # Veritabanı bağlantısı
├── modules/
│   └── subscriber/
│       ├── models.py        # SQLAlchemy model + Pydantic şema
│       ├── service.py       # İş mantığı
│       └── router.py        # HTTP endpoint'leri
├── requirements.txt
└── .env.example
```
