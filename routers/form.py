from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import models
import schemas
from database import get_db
from auth import get_current_user

router = APIRouter(prefix="/forms", tags=["forms"])


def update_animal_from_latest_form(db: Session, animal_id: int):
    """Hayvanın durumunu en son formdan güncelle - son form'un status'unu alır"""
    animal = db.query(models.Animal).filter(models.Animal.id == animal_id).first()
    if not animal:
        return
    
    # En son formu getir (ID veya created_date'e göre)
    latest_form = db.query(models.Form).filter(
        models.Form.animal_id == animal_id
    ).order_by(models.Form.id.desc()).first()
    
    if latest_form:
        # En son formun durumunu hayvana aktar
        animal.form_status = latest_form.form_status
        
        # assigned_date varsa (form gönderildiyse) son gönderim tarihi güncelle
        if latest_form.assigned_date:
            animal.last_form_sent_date = latest_form.assigned_date
        
        db.commit()
        db.refresh(animal)


def run_periodic_form_generation(db: Session, now: Optional[datetime] = None) -> List[models.Form]:
    """form_generation_period süresi dolan hayvanlar için yeni form üret"""
    now = now or datetime.utcnow()
    created_forms: List[models.Form] = []
    animals = db.query(models.Animal).all()

    for animal in animals:
        if animal.form_generation_period is None or animal.form_generation_period <= 0:
            continue

        last_sent_date = animal.last_form_sent_date
        if last_sent_date is None:
            should_create = True
        else:
            next_form_date = last_sent_date + relativedelta(months=animal.form_generation_period)
            should_create = now >= next_form_date

        if should_create:
            new_form = models.Form(
                animal_id=animal.id,
                form_status="created",
                created_date=now
            )
            db.add(new_form)
            db.commit()
            db.refresh(new_form)

            # Setter'a tekrar atama yaparak JSON string'i güncelle
            current_ids = animal.form_ids or []
            current_ids.append(new_form.id)
            animal.form_ids = current_ids
            db.commit()

            created_forms.append(new_form)

    return created_forms


@router.post("/", response_model=schemas.Form, status_code=status.HTTP_201_CREATED)
def create_form(
    form: schemas.FormCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Yeni form oluştur"""
    # Verify animal exists
    db_animal = db.query(models.Animal).filter(
        models.Animal.id == form.animal_id
    ).first()
    if not db_animal:
        raise HTTPException(status_code=404, detail="Animal not found")
    
    db_form = models.Form(animal_id=form.animal_id)
    db.add(db_form)
    db.commit()
    db.refresh(db_form)
    
    # Update animal's form_ids list
    current_form_ids = db_animal.form_ids
    current_form_ids.append(db_form.id)
    db_animal.form_ids = current_form_ids
    db.commit()
    
    return db_form


@router.get("/{form_id}", response_model=schemas.Form)
def read_form(
    form_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """ID'ye göre form bilgilerini getir"""
    db_form = db.query(models.Form).filter(models.Form.id == form_id).first()
    if db_form is None:
        raise HTTPException(status_code=404, detail="Form not found")
    return db_form


@router.post("/by-ids", response_model=List[schemas.Form])
def read_forms_by_ids(
    form_ids: List[int],
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Çoklu formu liste olarak verilen ID listesinden çek"""
    db_forms = db.query(models.Form).filter(models.Form.id.in_(form_ids)).all()
    return db_forms


@router.get("/animal/{animal_id}", response_model=List[schemas.Form])
def read_forms_by_animal(
    animal_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Belirli bir hayvana ait tüm formları getir"""
    db_animal = db.query(models.Animal).filter(models.Animal.id == animal_id).first()
    if db_animal is None:
        raise HTTPException(status_code=404, detail="Animal not found")
    
    db_forms = db.query(models.Form).filter(models.Form.animal_id == animal_id).all()
    return db_forms


@router.put("/{form_id}", response_model=schemas.Form)
def update_form(
    form_id: int,
    form_update: schemas.FormUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Form bilgilerini güncelle - Her durum değişiminde otomatik tarih eklenir
    
    Akış:
    1. form_status=sent → assigned_date set (görev atama)
    2. form_status=filled → filled_date set (dönüş alındı)
    3. form_status=controlled → controlled_date set (incelendi)
    """
    db_form = db.query(models.Form).filter(models.Form.id == form_id).first()
    if db_form is None:
        raise HTTPException(status_code=404, detail="Form not found")
    
    update_data = form_update.dict(exclude_unset=True)
    
    # Form status'u güncelleniyor mu?
    if "form_status" in update_data:
        new_status = update_data["form_status"]
        old_status = db_form.form_status
        
        # created → sent
        if new_status == "sent" and old_status != "sent":
            db_form.assigned_date = datetime.utcnow()
            db_form.control_due_date = datetime.utcnow() + timedelta(days=7)
        
        # sent → filled
        elif new_status == "filled" and old_status != "filled":
            db_form.filled_date = datetime.utcnow()
        
        # filled → controlled
        elif new_status == "controlled" and old_status != "controlled":
            db_form.controlled_date = datetime.utcnow()
        
        db_form.form_status = new_status
    
    db.commit()
    db.refresh(db_form)
    
    # Hayvanın durumunu son formdan güncelle
    update_animal_from_latest_form(db, db_form.animal_id)
    
    return db_form


@router.delete("/{form_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_form(
    form_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Form sil"""
    db_form = db.query(models.Form).filter(models.Form.id == form_id).first()
    if db_form is None:
        raise HTTPException(status_code=404, detail="Form not found")
    
    animal_id = db_form.animal_id
    
    # Remove form_id from animal's form_ids list
    db_animal = db.query(models.Animal).filter(
        models.Animal.id == animal_id
    ).first()
    if db_animal and db_animal.form_ids and form_id in db_animal.form_ids:
        current_form_ids = db_animal.form_ids
        current_form_ids.remove(form_id)
        db_animal.form_ids = current_form_ids
        db.commit()
    
    db.delete(db_form)
    db.commit()
    
    # Hayvanın durumunu kalan formlardan güncelle
    update_animal_from_latest_form(db, animal_id)
    
    return None


@router.post("/generate-periodic", response_model=List[schemas.Form])
def generate_periodic_forms(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Period süresi dolmuş hayvanlar için yeni form oluştur.
    form_generation_period ay cinsinden, last_form_sent_date'ten itibaren hesaplanır.
    """
    return run_periodic_form_generation(db)


@router.get("/pending-send", response_model=List[schemas.Form])
def get_forms_pending_send(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Henüz görev verilmemiş formları getir (form_status=created)"""
    forms = db.query(models.Form).filter(models.Form.form_status == "created").all()
    return forms


@router.get("/pending-control", response_model=List[schemas.Form])
def get_forms_pending_control(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Kontrol edilmesi gereken formları getir (form_status=filled)"""
    forms = db.query(models.Form).filter(models.Form.form_status == "filled").all()
    return forms


@router.get("/pending-fill", response_model=List[schemas.Form])
def get_forms_pending_fill(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Doldurulması gereken formları getir (form_status=sent ve control_due_date'ten önce)"""
    now = datetime.utcnow()
    forms = db.query(models.Form).filter(
        models.Form.form_status == "sent",
        models.Form.control_due_date > now
    ).all()
    return forms

