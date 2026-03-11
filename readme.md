# Mail English Story

Her gün bir İngilizce hikaye gönderen bülten projesinin tanıtım sayfası ve kayıt sistemi.

## Proje Yapısı

- **frontend:** Nuxt.js & PrimeVue (Tanıtım Sayfası)
- **backend:** Go (Fiber) & PostgreSQL (Abonelik API)

## Kurulum ve Çalıştırma

### 1. Veritabanı (PostgreSQL)
- PostgreSQL üzerinde `mail_english_story` adında bir veritabanı oluşturun.
- `backend/.env` dosyasını düzenleyerek veritabanı bağlantı bilgilerini girin.

### 2. Backend (Go)
```bash
cd backend
go mod tidy
go run cmd/api/main.go
```
- API varsayılan olarak `localhost:8000` portunda çalışır.

### 3. Frontend (Nuxt.js)
```bash
cd frontend
npm install
npm run dev
```
- Uygulama varsayılan olarak `localhost:3000` (veya uygun ilk port) üzerinde çalışır.

## Özellikler
- Modern ve responsive UI (PrimeVue Aura).
- Dil seviyesi seçimi (A1-B2).
- Modüler monolit backend yapısı.
- PostgreSQL ile veritabanı kalıcılığı.
