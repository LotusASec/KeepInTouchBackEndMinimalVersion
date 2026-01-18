"""
Database initialization script
Creates tables and adds initial admin user with staggered historical dates
"""
from sqlalchemy.orm import Session
import os
import random
from datetime import datetime, timedelta

from app.db.database import engine, SessionLocal, Base
from app.models.user import User
from app.models.animal import Animal
from app.models.form import Form
from app.auth.auth import get_password_hash
from app.api.routers.form import update_animal_from_latest_form


def init_database(force_recreate: bool = False):
    """Veritabanını ilklendirir ve tabloları oluşturur"""
    if force_recreate and os.path.exists("animal_tracking.db"):
        print("Mevcut veritabanı kaldırılıyor...")
        os.remove("animal_tracking.db")
        print("✓ Eski veritabanı silindi")
    
    print("Veritabanı tabloları oluşturuluyor...")
    Base.metadata.create_all(bind=engine)
    print("✓ Tablolar başarıyla oluşturuldu")


def create_admin_user(db: Session, username: str = "admin", password: str = "admin123"):
    """Eğer yoksa başlangıç admin kullanıcısını oluşturur"""
    existing_user = db.query(User).filter(User.name == username).first()
    
    if existing_user:
        print(f"✓ Admin kullanıcısı '{username}' zaten mevcut")
        return existing_user
    
    admin_user = User(
        name=username,
        password=get_password_hash(password),
        role="admin"
    )
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    
    print(f"✓ Admin kullanıcısı oluşturuldu:")
    print(f"  Kullanıcı Adı: {username}")
    print(f"  Şifre: {password}")
    print(f"  ⚠️  ÖNEMLİ: İlk girişten sonra şifreyi değiştirin!")
    
    return admin_user


def create_sample_data(db: Session, admin_user: User, count: int = 5):
    """Örnek hayvan ve form verisi oluşturur"""
    now = datetime.utcnow()
    
    print(f"\n📦 {count} örnek hayvan oluşturuluyor...")
    
    for i in range(1, count + 1):
        # Hayvan oluştur
        animal = Animal(
            name=f"Hayvan_{i}",
            responsible_user_id=admin_user.id,
            owner_name=f"Sahip {i}",
            owner_contact_number=f"+90 555 000 00{i:02d}",
            owner_contact_email=f"sahip{i}@example.com",
            form_generation_period=3,  # 3 aylık periyot
            form_ids=[]
        )
        db.add(animal)
        db.commit()
        db.refresh(animal)
        
        # Her hayvana 2-4 arasında form oluştur
        form_count = random.randint(2, 4)
        form_ids = []
        
        for j in range(form_count):
            # Tarihleri geriye doğru dağıt
            days_ago = (form_count - j) * 30  # Her form 30 gün arayla
            created_date = now - timedelta(days=days_ago + random.randint(0, 5))
            
            # Form durumunu rastgele belirle
            if j == form_count - 1:  # En son form
                status = random.choice(["created", "sent", "filled"])
            else:  # Eski formlar genelde tamamlanmış
                status = "controlled"
            
            form = Form(
                animal_id=animal.id,
                form_status=status,
                created_date=created_date
            )
            
            # Durum tarihlerini ayarla
            if status in ["sent", "filled", "controlled"]:
                form.assigned_date = created_date + timedelta(hours=random.randint(1, 48))
                form.control_due_date = form.assigned_date + timedelta(days=7)
            
            if status in ["filled", "controlled"]:
                form.filled_date = form.assigned_date + timedelta(days=random.randint(1, 5))
            
            if status == "controlled":
                form.controlled_date = form.filled_date + timedelta(days=random.randint(1, 3))
            
            db.add(form)
            db.commit()
            db.refresh(form)
            
            form_ids.append(form.id)
        
        # Hayvanı güncelle
        animal.form_ids = form_ids
        animal.last_form_created_date = created_date
        db.commit()
        
        # Hayvanın durumunu son formdan güncelle
        update_animal_from_latest_form(db, animal.id)
        
        print(f"  ✓ {animal.name}: {form_count} form oluşturuldu")
    
    print(f"✓ {count} hayvan ve formları başarıyla oluşturuldu")


def main():
    """Ana başlatma fonksiyonu"""
    print("=" * 60)
    print("🐾 Hayvan Sahiplendirme Takip Sistemi - Veritabanı Başlatma")
    print("=" * 60)
    
    # Veritabanı oluştur
    init_database(force_recreate=False)
    
    # Session aç
    db = SessionLocal()
    
    try:
        # Admin kullanıcı oluştur
        admin_user = create_admin_user(db)
        
        # Örnek veri oluşturmak ister misiniz?
        print("\n" + "=" * 60)
        print("📊 Örnek veri oluşturulsun mu? (5 hayvan + formları)")
        response = input("E/H (varsayılan: H): ").strip().upper()
        
        if response == "E":
            create_sample_data(db, admin_user, count=5)
        else:
            print("⏭️  Örnek veri oluşturma atlandı")
        
        print("\n" + "=" * 60)
        print("✅ Veritabanı başlatma tamamlandı!")
        print("=" * 60)
        print("\n🚀 Uygulamayı başlatmak için:")
        print("   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        print("\n📖 API Docs:")
        print("   http://localhost:8000/docs")
        print("=" * 60)
        
    finally:
        db.close()


if __name__ == "__main__":
    main()
