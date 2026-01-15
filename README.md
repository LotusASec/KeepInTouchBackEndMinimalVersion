# Hayvan Sahiplendirme Takip Sistemi

Animal Adoption Tracking System - FastAPI ile yapılmış, SQLite veritabanı kullanan, JWT tabanlı güvenliği olan kapsamlı REST API.

## 📋 Özellikler

- ✅ **Kullanıcı Yönetimi**: Admin & regular user rolleri, JWT authentication
- ✅ **Hayvan Kaydı**: Hayvan bilgileri, sahip bilgileri, form periyodu
- ✅ **Form Yönetimi**: Periyodik form üretimi, durum takibi (gönder/kontrol)
- ✅ **Otomatik Scheduler**: APScheduler ile arka planda periyodik form üretimi
- ✅ **Durum Senkronizasyonu**: Form durumu otomatik hayvan durumuna yansıtılır
- ✅ **Filtreleme Endpoint'leri**: need-review, pending-send, pending-control
- ✅ **Cascade Delete**: Hayvan silinince formları da silinir
- ✅ **Token-based Security**: OAuth2 + JWT, Swagger UI entegrasyonu

## 🛠 Teknoloji Stack

- **Framework**: FastAPI 0.109.0
- **Database**: SQLite + SQLAlchemy 2.0.25
- **Authentication**: JWT (python-jose) + bcrypt
- **Scheduler**: APScheduler 3.10.4
- **Validation**: Pydantic 2.5.3
- **Server**: Uvicorn 0.27.0

## 📦 Kurulum

### 1. Virtual Environment Oluştur

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# veya
venv\Scripts\activate  # Windows
```

### 2. Bağımlılıkları Kur

```bash
pip install -r requirements.txt
```

### 3. Database Başlat

```bash
python init_db.py
```

**Varsayılan Admin Kullanıcısı:**
- Username: `admin`
- Password: `admin123`
- ⚠️ İlk girişten sonra şifreyi değiştirin

### 4. Sunucuyu Başlat

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🔐 Authentication

### Login - Token Al

```bash
curl -X POST http://localhost:8000/users/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

Token'ı environment variable'a kaydet:

```bash
TOKEN="your_token_here"
```

Tüm endpoint'lerde kullan:

```bash
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/animals/
```

## 📚 API Endpoints

### Users (Kullanıcı)

**Yeni Kullanıcı Oluştur** (Admin only)
```bash
curl -X POST http://localhost:8000/users/register \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "operator1",
    "password": "pass123",
    "role": "regular"
  }'
```

**Tüm Kullanıcıları Listele** (Admin only)
```bash
curl -X GET http://localhost:8000/users/ \
  -H "Authorization: Bearer $TOKEN"
```

**Kullanıcı Detayı**
```bash
curl -X GET http://localhost:8000/users/{user_id} \
  -H "Authorization: Bearer $TOKEN"
```

**Kullanıcı Güncelle** (Admin only)
```bash
curl -X PUT http://localhost:8000/users/{user_id} \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"role": "admin"}'
```

**Kullanıcı Sil** (Admin only)
```bash
curl -X DELETE http://localhost:8000/users/{user_id} \
  -H "Authorization: Bearer $TOKEN"
```

### Animals (Hayvan)

**Yeni Hayvan Kaydı**
```bash
curl -X POST http://localhost:8000/animals/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Minnoş",
    "responsible_user_id": 1,
    "owner_name": "Ahmet Yılmaz",
    "owner_contact_number": "+90 555 123 4567",
    "owner_contact_email": "ahmet@example.com",
    "form_generation_period": 3
  }'
```

**Tüm Hayvanları Listele**
```bash
curl -X GET http://localhost:8000/animals/ \
  -H "Authorization: Bearer $TOKEN"
```

**Hayvan Detayı**
```bash
curl -X GET http://localhost:8000/animals/{animal_id} \
  -H "Authorization: Bearer $TOKEN"
```

**Hayvan Güncelle**
```bash
curl -X PUT http://localhost:8000/animals/{animal_id} \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "is_sent": true,
    "is_controlled": false,
    "owner_name": "Yeni İsim"
  }'
```

**Hayvan Sil**
```bash
curl -X DELETE http://localhost:8000/animals/{animal_id} \
  -H "Authorization: Bearer $TOKEN"
```

### Forms (Form)

**Yeni Form Oluştur**
```bash
curl -X POST http://localhost:8000/forms/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"animal_id": 1}'
```

**Hayvanın Formlarını Listele**
```bash
curl -X GET http://localhost:8000/forms/animal/{animal_id} \
  -H "Authorization: Bearer $TOKEN"
```

**Form Detayı**
```bash
curl -X GET http://localhost:8000/forms/{form_id} \
  -H "Authorization: Bearer $TOKEN"
```

**Form Güncelle** (Durum değiştir)
```bash
curl -X PUT http://localhost:8000/forms/{form_id} \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "is_sent": true,
    "is_controlled": false,
    "need_review": false
  }'
```

**Periyodik Formları Oluştur** (Manuel Tetik)
```bash
curl -X POST http://localhost:8000/forms/generate-periodic \
  -H "Authorization: Bearer $TOKEN"
```

**Review Gerektiren Formlar**
```bash
curl -X GET http://localhost:8000/forms/need-review \
  -H "Authorization: Bearer $TOKEN"
```

**Gönderilmeyi Bekleyen Formlar**
```bash
curl -X GET http://localhost:8000/forms/pending-send \
  -H "Authorization: Bearer $TOKEN"
```

**Kontrol Süresi Geçen Formlar**
```bash
curl -X GET http://localhost:8000/forms/pending-control \
  -H "Authorization: Bearer $TOKEN"
```

**Form Sil**
```bash
curl -X DELETE http://localhost:8000/forms/{form_id} \
  -H "Authorization: Bearer $TOKEN"
```

## 🔄 Periyodik Form Üretimi (Workflow)

### Akış

1. Her hayvan `form_generation_period` (ay cinsinden) tanımlanır
   - Örn: 3 ay → her 3 ayda 1 form üretilir

2. Scheduler otomatik çalışır:
   - Sunucu ayağa kalkınca başlıyor
   - Varsayılan 12 saatte 1 kez çalışır (env ile ayarlanabilir)

3. Kontrol Mantığı:
   - Hayvan `last_form_sent_date` yok → İlk form hemen oluştur
   - `last_form_sent_date + period` geçmişse → Yeni form oluştur

4. Örnek Senaryo:
   ```
   Hayvan: Minnoş (period=3 ay)
   
   2025-10-15: Form1 gönderildi → last_form_sent_date = 2025-10-15
   2026-01-01: Scheduler çalışıyor → 2025-10-15 + 3 ay = 2026-01-15 henüz değil
   2026-01-15: Scheduler çalışıyor → 2025-10-15 + 3 ay = 2026-01-15 geçti ✓ Form2 oluştur
   ```

### Form Gönderildiğinde Otomatik Işlemler

Form `is_sent=true` yapıldığında:
- `send_date` = şimdi
- `control_due_date` = şimdi + 7 gün
- `last_form_sent_date` = animal'a kopyalanır

Form `is_controlled=true` yapıldığında:
- `controlled_date` = şimdi

### Status Senkronizasyonu

Form güncellendiğinde hayvan otomatik senkronize edilir:

```json
Form Update:
{
  "is_sent": true,
  "is_controlled": false,
  "need_review": false
}

↓

Animal senkronize:
{
  "is_sent": true,
  "is_controlled": false,
  "need_review": false,
  "last_form_sent_date": "2026-01-15T10:30:00"
}
```

## 🧪 Testing

Tüm testleri çalıştır:

```bash
python smoke_test.py --url http://localhost:8000
```

**Test Coverage:**
- ✓ 3 Authentication test
- ✓ 5 User CRUD test
- ✓ 4 Animal CRUD test
- ✓ 5 Form CRUD test (Create, Read, Periodic Generation, Update, Delete)
- ✓ 1 Cascade Delete test

**Total: 19 test**

## 🚀 Environment Variables

```bash
FORM_GEN_INTERVAL_HOURS=12      # Scheduler interval (default: 12 saat)
DATABASE_URL=sqlite:///./animal_tracking.db
```

Interval değiştirmek:

```bash
export FORM_GEN_INTERVAL_HOURS=6
uvicorn main:app --reload
```

## 📁 Proje Yapısı

```
.
├── main.py                 # FastAPI + APScheduler
├── models.py              # SQLAlchemy modeller
├── schemas.py             # Pydantic schemas
├── auth.py                # JWT + password
├── database.py            # Database config
├── routers/
│   ├── user.py           # User endpoints
│   ├── animal.py         # Animal endpoints
│   └── form.py           # Form endpoints
├── init_db.py            # DB initialization
├── smoke_test.py         # Test suite
├── requirements.txt      # Dependencies
├── .gitignore           # Git ignore
├── README.md            # Documentation
├── LICENSE              # MIT License
└── animal_tracking.db   # SQLite (gitignore'da)
```

## 📄 License

MIT License - See [LICENSE](LICENSE) file

## 👤 Kontribüsyon

Pull requests welcome! Büyük değişiklikler için önce issue açın.

---

**Made with ❤️ for animal welfare**
