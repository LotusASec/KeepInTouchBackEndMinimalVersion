from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


# User Schemas
class UserBase(BaseModel):
    name: str
    role: str = "regular"


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    name: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None


class User(UserBase):
    id: int

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    name: str
    password: str


# Animal Schemas
class AnimalBase(BaseModel):
    name: str
    responsible_user_id: int
    owner_name: str
    owner_contact_number: str
    owner_contact_email: EmailStr
    form_generation_period: int  # Months


class AnimalCreate(AnimalBase):
    pass


class AnimalUpdate(BaseModel):
    name: Optional[str] = None
    responsible_user_id: Optional[int] = None
    owner_name: Optional[str] = None
    owner_contact_number: Optional[str] = None
    owner_contact_email: Optional[EmailStr] = None
    form_generation_period: Optional[int] = None
    last_form_sent_date: Optional[datetime] = None
    last_form_created_date: Optional[datetime] = None


class Animal(AnimalBase):
    id: int
    form_ids: List[int] = []
    form_status: str = "created"
    last_form_sent_date: Optional[datetime] = None
    last_form_created_date: Optional[datetime] = None

    class Config:
        from_attributes = True


# Form Schemas
class FormBase(BaseModel):
    animal_id: int


class FormCreate(FormBase):
    pass


class FormUpdate(BaseModel):
    form_status: Optional[str] = None


class Form(FormBase):
    id: int
    form_status: str = "created"
    created_date: datetime
    assigned_date: Optional[datetime] = None
    filled_date: Optional[datetime] = None
    controlled_date: Optional[datetime] = None
    control_due_date: Optional[datetime] = None

    class Config:
        from_attributes = True


# Token Schema
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[int] = None
    role: Optional[str] = None
