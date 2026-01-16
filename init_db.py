"""
Database initialization script
Creates tables and adds initial admin user
"""
from sqlalchemy.orm import Session
from database import engine, SessionLocal, Base
from models import User, Animal, Form
from auth import get_password_hash
from routers.form import update_animal_from_latest_form
import os


def init_database(force_recreate: bool = False):
    """Initialize database and create tables"""
    if force_recreate and os.path.exists("animal_tracking.db"):
        print("Removing existing database...")
        os.remove("animal_tracking.db")
        print("✓ Old database removed")
    
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Tables created successfully")


def create_admin_user(db: Session, username: str = "admin", password: str = "admin123"):
    """Create initial admin user if not exists"""
    existing_user = db.query(User).filter(User.name == username).first()
    
    if existing_user:
        print(f"✓ Admin user '{username}' already exists")
        return existing_user
    
    admin_user = User(
        name=username,
        password=get_password_hash(password),
        role="admin"
    )
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    
    print(f"✓ Admin user created:")
    print(f"  Username: {username}")
    print(f"  Password: {password}")
    print(f"  ⚠️  IMPORTANT: Change the password after first login!")
    
    return admin_user


def create_sample_data(db: Session):
    """Create some sample data for testing (optional)"""
    # Check if admin exists
    admin = db.query(User).filter(User.role == "admin").first()
    if not admin:
        print("No admin user found. Run create_admin_user first.")
        return
    
    # Check if sample data already exists
    existing_animals = db.query(Animal).count()
    if existing_animals > 0:
        print("✓ Sample data already exists")
        return
    
    # Create a regular user
    regular_user = User(
        name="operator1",
        password=get_password_hash("operator123"),
        role="regular"
    )
    db.add(regular_user)
    db.commit()
    db.refresh(regular_user)
    
    # Create 10 sample animals
    animals = []
    animal_names = ["Minnoş", "Paşa", "Karabaş", "Pamuk", "Misi", "Rex", "Kedi", "Köpek", "Tavşan", "Kuş"]
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
    
    for i, name in enumerate(animal_names):
        owner_name, phone, email = owners[i]
        animal = Animal(
            name=name,
            responsible_user_id=admin.id if i % 2 == 0 else regular_user.id,
            owner_name=owner_name,
            owner_contact_number=phone,
            owner_contact_email=email,
            form_generation_period=15 + (i * 5),  # 15, 20, 25, ... days
            form_status="created"
        )
        db.add(animal)
        db.commit()
        db.refresh(animal)
        animals.append(animal)
    
    # Create 20 sample forms with various statuses
    form_statuses = ["created", "sent", "filled", "controlled"]
    form_count = 0
    for i, animal in enumerate(animals):
        # Create 2 forms per animal
        for j in range(2):
            status = form_statuses[(i + j) % len(form_statuses)]
            form = Form(
                animal_id=animal.id,
                form_status=status
            )
            db.add(form)
            db.commit()
            db.refresh(form)
            
            # Update animal form_ids
            current_ids = animal.form_ids or []
            current_ids.append(form.id)
            animal.form_ids = current_ids
            db.commit()
            
            form_count += 1
            
            if form_count >= 20:
                break
        
        if form_count >= 20:
            break
    
    # Animal'ları en son form status'larından güncelle
    for animal in animals:
        update_animal_from_latest_form(db, animal.id)
    
    print("✓ Sample data created:")
    print(f"  - User: operator1 (password: operator123)")
    print(f"  - Animals: {len(animals)} animals created")
    print(f"  - Forms: {form_count} forms created with various statuses")
    print(f"\n  Form statuses: created, sent, filled, controlled")
    print(f"  Each animal has 2 forms with different statuses")



def main():
    """Main initialization function"""
    print("\n" + "="*50)
    print("  Database Initialization")
    print("="*50 + "\n")
    
    # Initialize database
    # Check if database exists and ask to recreate
    db_exists = os.path.exists("animal_tracking.db")
    force_recreate = False
    
    if db_exists:
        print("\n" + "⚠️ "*25)
        print("Database already exists!")
        response = input("Do you want to DELETE and recreate it? (y/n): ").strip().lower()
        if response == 'y':
            force_recreate = True
        print("="*50)
    
    init_database(force_recreate=force_recreate)
    
    # Create admin user
    db = SessionLocal()
    try:
        create_admin_user(db)
        
        # Ask if user wants to create sample data
        print("\n" + "-"*50)
        response = input("Create sample data for testing? (y/n): ").strip().lower()
        if response == 'y':
            create_sample_data(db)
        
        print("\n" + "="*50)
        print("  ✓ Initialization Complete!")
        print("="*50 + "\n")
        
    except Exception as e:
        print(f"\n✗ Error during initialization: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
