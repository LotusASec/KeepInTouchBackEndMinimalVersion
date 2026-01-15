"""
Database initialization script
Creates tables and adds initial admin user
"""
from sqlalchemy.orm import Session
from database import engine, SessionLocal, Base
from models import User, Animal, Form
from auth import get_password_hash
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
    
    # Create sample animals
    animal1 = Animal(
        name="Minnoş",
        responsible_user_id=regular_user.id,
        owner_name="Ahmet Yılmaz",
        owner_contact_number="+90 555 123 4567",
        owner_contact_email="ahmet@example.com",
        form_generation_period=30,
        is_controlled=False,
        is_sent=False
    )
    
    animal2 = Animal(
        name="Paşa",
        responsible_user_id=admin.id,
        owner_name="Ayşe Demir",
        owner_contact_number="+90 555 987 6543",
        owner_contact_email="ayse@example.com",
        form_generation_period=15,
        is_controlled=True,
        is_sent=True
    )
    
    db.add(animal1)
    db.add(animal2)
    db.commit()
    db.refresh(animal1)
    db.refresh(animal2)
    
    # Create sample forms
    form1 = Form(animal_id=animal1.id, is_sent=False, is_controlled=False)
    form2 = Form(animal_id=animal2.id, is_sent=True, is_controlled=True)
    
    db.add(form1)
    db.add(form2)
    db.commit()
    db.refresh(form1)
    db.refresh(form2)
    
    # Update animal form_ids
    animal1.form_ids = [form1.id]
    animal2.form_ids = [form2.id]
    db.commit()
    
    print("✓ Sample data created:")
    print(f"  - User: operator1 (password: operator123)")
    print(f"  - Animals: {animal1.name}, {animal2.name}")
    print(f"  - Forms: 2 forms created")


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
