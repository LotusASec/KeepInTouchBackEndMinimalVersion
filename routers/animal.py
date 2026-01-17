from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import models
import schemas
from database import get_db
from auth import get_current_user

router = APIRouter(prefix="/animals", tags=["animals"])


@router.post("/", response_model=schemas.Animal, status_code=status.HTTP_201_CREATED)
def create_animal(
    animal: schemas.AnimalCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Yeni hayvan kaydı oluştur"""
    # Verify responsible user exists
    responsible_user = db.query(models.User).filter(
        models.User.id == animal.responsible_user_id
    ).first()
    if not responsible_user:
        raise HTTPException(status_code=404, detail="Responsible user not found")
    
    db_animal = models.Animal(
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


@router.get("/", response_model=List[schemas.Animal])
def read_animals(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Tüm hayvanları listele"""
    animals = db.query(models.Animal).offset(skip).limit(limit).all()
    return animals


@router.get("/{animal_id}", response_model=schemas.Animal)
def read_animal(
    animal_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """ID'ye göre hayvan bilgilerini getir"""
    db_animal = db.query(models.Animal).filter(models.Animal.id == animal_id).first()
    if db_animal is None:
        raise HTTPException(status_code=404, detail="Animal not found")
    return db_animal


@router.put("/{animal_id}", response_model=schemas.Animal)
def update_animal(
    animal_id: int,
    animal_update: schemas.AnimalUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Hayvan bilgilerini güncelle"""
    db_animal = db.query(models.Animal).filter(models.Animal.id == animal_id).first()
    if db_animal is None:
        raise HTTPException(status_code=404, detail="Animal not found")
    
    update_data = animal_update.dict(exclude_unset=True)
    
    # If responsible_user_id is being updated, verify it exists
    if "responsible_user_id" in update_data:
        responsible_user = db.query(models.User).filter(
            models.User.id == update_data["responsible_user_id"]
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
    current_user: models.User = Depends(get_current_user)
):
    """Hayvan kaydını sil (ölme veya takipten çıkma durumu)"""
    db_animal = db.query(models.Animal).filter(models.Animal.id == animal_id).first()
    if db_animal is None:
        raise HTTPException(status_code=404, detail="Animal not found")
    
    # Also delete all related forms
    db.query(models.Form).filter(models.Form.animal_id == animal_id).delete()
    
    db.delete(db_animal)
    db.commit()
    return None


@router.post("/{animal_id}/create-form", response_model=schemas.Form)
def create_form_for_animal(
    animal_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Hayvan için yeni form oluştur (periyodik tetikleme için)"""
    db_animal = db.query(models.Animal).filter(models.Animal.id == animal_id).first()
    if db_animal is None:
        raise HTTPException(status_code=404, detail="Animal not found")
    
    # Create new form
    db_form = models.Form(animal_id=animal_id)
    db.add(db_form)
    db.commit()
    db.refresh(db_form)
    
    # Update animal's form_ids list
    current_form_ids = db_animal.form_ids  # Get current list
    current_form_ids.append(db_form.id)
    db_animal.form_ids = current_form_ids  # Set back to trigger setter
    db_animal.last_form_created_date = db_form.created_date
    db.commit()
    db.refresh(db_animal)
    
    return db_form
