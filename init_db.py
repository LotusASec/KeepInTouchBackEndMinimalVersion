"""
Database initialization script
Creates tables and adds initial admin user with staggered historical dates
"""
from sqlalchemy.orm import Session
from database import engine, SessionLocal, Base
from models import User, Animal, Form
from auth import get_password_hash
from routers.form import update_animal_from_latest_form
import os
import random
from datetime import datetime, timedelta

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


def create_sample_data(db: Session):
    """15-90 gün aralığında değişen tarihlerle örnek veriler oluşturur"""
    admin = db.query(User).filter(User.role == "admin").first()
    if not admin:
        print("Admin kullanıcısı bulunamadı.")
        return
    
    if db.query(Animal).count() > 0:
        print("✓ Örnek veriler zaten mevcut")
        return
    
    # Operatör kullanıcısı
    regular_user = User(
        name="operator1",
        password=get_password_hash("operator123"),
        role="regular"
    )
    db.add(regular_user)
    db.commit()
    db.refresh(regular_user)
    
    animal_names = ["Minnoş", "Paşa", "Karabaş", "Pamuk", "Misi", "Rex", "Çıtır", "Gümüş", "Gofret", "Zeytin"]
    owners = [
        ("Ahmet Yılmaz", "+90 555 123 4567", "ahmet@example.com"),
        ("Ayşe Demir", "+90 555 987 6543", "ayse@example.com"),
        ("Mehmet Kaya", "+90 555 456 7890", "mehmet@example.com"),
        ("Fatma Çetin", "+90 555 789 0123", "fatma@example.com"),
        ("Ali Akşin", "+90 555 234 5678", "ali@example.com"),
        ("Zeynep Şahin", "+90 555 345 6789", "zeynep@example.com"),
        ("Mustafa Yıldız", "+90 555 567 8901", "mustafa@example.com"),
        ("Leyla Aydın", "+90 555 678 9012", "leyla@example.com"),
        ("Osman Başar", "+90 555 890 1234", "osman@example.com"),
        ("Seda Kürk", "+90 555 901 2345", "seda@example.com"),
    ]
    
    form_statuses = ["created", "sent", "filled", "controlled"]
    
    print("Örnek hayvanlar ve geçmişe dönük formlar oluşturuluyor...")
    
    for i in range(10):
        name = animal_names[i]
        owner_name, phone, email = owners[i]
        
        animal = Animal(
            name=name,
            responsible_user_id=admin.id if i % 2 == 0 else regular_user.id,
            owner_name=owner_name,
            owner_contact_number=phone,
            owner_contact_email=email,
            form_generation_period=(i % 6) + 1,
            form_status="created"
        )
        db.add(animal)
        db.commit()
        db.refresh(animal)

        # 1 ile 5 arasında rastgele sayıda form oluştur
        num_forms = random.randint(1, 5)
        
        # 15 ile 90 gün arasında rastgele tarihler oluştur ve sırala (eskiden yeniye)
        # days_ago listesi örneği: [85, 50, 20] -> 85 gün önce en eski, 20 gün önce en yeni
        days_ago_list = sorted([random.randint(15, 90) for _ in range(num_forms)], reverse=True)

        for idx, days_ago in enumerate(days_ago_list):
            form_date = datetime.now() - timedelta(days=days_ago)
            
            # Form durumunu sırayla veya rastgele seç
            status = form_statuses[idx % len(form_statuses)]
            
            new_form = Form(
                animal_id=animal.id,
                form_status=status,
                created_date=form_date 
            )
            db.add(new_form)
            db.commit()
            db.refresh(new_form)
            
            # Hayvanın form_ids listesini güncelle
            current_ids = animal.form_ids or []
            current_ids.append(new_form.id)
            animal.form_ids = current_ids
            
            # En son oluşturulan formun tarihini hayvana işle
            animal.last_form_created_date = form_date
            db.commit()

        # Hayvanın genel durumunu en son forma göre güncelle
        update_animal_from_latest_form(db, animal.id)
    
    print(f"✓ Başarıyla {len(animal_names)} hayvan ve geçmişe dönük formlar oluşturuldu.")
    print("  Tarih Aralığı: Bugünün 15 gün öncesi ile 90 gün öncesi arası.")


def main():
    """Ana kurulum fonksiyonu"""
    print("\n" + "="*50)
    print("  Veritabanı Yapılandırma Sistemi")
    print("="*50 + "\n")
    
    db_exists = os.path.exists("animal_tracking.db")
    force_recreate = False
    
    if db_exists:
        print("⚠️  Veritabanı zaten mevcut!")
        response = input("Silip yeniden oluşturmak istiyor musunuz? (e/h): ").strip().lower()
        if response == 'e':
            force_recreate = True
        print("-" * 50)
    
    init_database(force_recreate=force_recreate)
    
    db = SessionLocal()
    try:
        create_admin_user(db)
        
        print("\n" + "-"*50)
        response = input("Test için örnek veriler oluşturulsun mu? (e/h): ").strip().lower()
        if response == 'e':
            create_sample_data(db)
        
        print("\n" + "="*50)
        print("  ✓ İşlem Başarıyla Tamamlandı!")
        print("="*50 + "\n")
        
    except Exception as e:
        print(f"\n✗ Hata oluştu: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()