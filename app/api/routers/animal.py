"""Animal router - animal management endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.models.user import User
from app.models.animal import Animal
from app.schemas.animal import Animal as AnimalSchema, AnimalCreate, AnimalUpdate
from app.auth.auth import get_current_user

router = APIRouter(prefix="/animals", tags=["animals"])


@router.post("/", response_model=AnimalSchema, status_code=status.HTTP_201_CREATED)
def create_animal(
    animal: AnimalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Yeni hayvan kaydı oluştur"""
    # Verify responsible user exists
    responsible_user = db.query(User).filter(
        User.id == animal.responsible_user_id
    ).first()
    if not responsible_user:
        raise HTTPException(status_code=404, detail="Responsible user not found")
    
    db_animal = Animal(
        name=animal.name,
        responsible_user_id=animal.responsible_user_id,
        owner_name=animal.owner_name,
        owner_contact_number=animal.owner_contact_number,
        owner_contact_email=animal.owner_contact_email,
        form_generation_period=animal.form_generation_period,
        form_ids=[]
    )
    db.add(db_animal)
    db.commit()
    db.refresh(db_animal)
    return db_animal


@router.get("/", response_model=List[AnimalSchema])
def read_animals(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Tüm hayvanları listele"""
    animals = db.query(Animal).offset(skip).limit(limit).all()
    return animals


@router.get("/{animal_id}", response_model=AnimalSchema)
def read_animal(
    animal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """ID'ye göre hayvan bilgilerini getir"""
    db_animal = db.query(Animal).filter(Animal.id == animal_id).first()
    if db_animal is None:
        raise HTTPException(status_code=404, detail="Animal not found")
    return db_animal


@router.put("/{animal_id}", response_model=AnimalSchema)
def update_animal(
    animal_id: int,
    animal_update: AnimalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Hayvan bilgilerini güncelle"""
    db_animal = db.query(Animal).filter(Animal.id == animal_id).first()
    if db_animal is None:
        raise HTTPException(status_code=404, detail="Animal not found")
    
    update_data = animal_update.dict(exclude_unset=True)
    
    # If responsible_user_id is being updated, verify it exists
    if "responsible_user_id" in update_data:
        responsible_user = db.query(User).filter(
            User.id == update_data["responsible_user_id"]
        ).first()
        if not responsible_user:
            raise HTTPException(status_code=404, detail="Responsible user not found")
    
    for field, value in update_data.items():
        setattr(db_animal, field, value)
    
    db.commit()
    db.refresh(db_animal)
    return db_animal


@router.delete("/{animal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_animal(
    animal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Hayvan sil - Cascade delete ile tüm formları da siler"""
    db_animal = db.query(Animal).filter(Animal.id == animal_id).first()
    if db_animal is None:
        raise HTTPException(status_code=404, detail="Animal not found")
    
    db.delete(db_animal)
    db.commit()
    return None
