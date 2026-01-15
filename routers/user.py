from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta
import models
import schemas
from database import get_db
from auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user,
    get_admin_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/token", response_model=schemas.Token)
def token(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    """OAuth2 Token Endpoint - Swagger UI authorize'ı buradan kullanır"""
    user = db.query(models.User).filter(models.User.name == username).first()
    if not user or not verify_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login", response_model=schemas.Token)
def login(user_login: schemas.UserLogin, db: Session = Depends(get_db)):
    """Kullanıcı girişi - Tüm kullanıcılar erişebilir"""
    user = db.query(models.User).filter(models.User.name == user_login.name).first()
    if not user or not verify_password(user_login.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def register_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_admin_user)
):
    """Yeni kullanıcı kaydı - Sadece admin erişebilir"""
    # Check if user already exists
    db_user = db.query(models.User).filter(models.User.name == user.name).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        name=user.name,
        password=hashed_password,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.get("/", response_model=List[schemas.User])
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_admin_user)
):
    """Tüm kullanıcıları listele - Sadece admin erişebilir"""
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users


@router.get("/{user_id}", response_model=schemas.User)
def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Kullanıcı bilgilerini getir (profil için) - Giriş yapmış kullanıcılar erişebilir"""
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.put("/{user_id}", response_model=schemas.User)
def update_user(
    user_id: int,
    user_update: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_admin_user)
):
    """Kullanıcı güncelleme - Sadece admin erişebilir"""
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = user_update.dict(exclude_unset=True)
    if "password" in update_data:
        update_data["password"] = get_password_hash(update_data["password"])
    
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_admin_user)
):
    """Kullanıcı silme - Sadece admin erişebilir"""
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(db_user)
    db.commit()
    return None
