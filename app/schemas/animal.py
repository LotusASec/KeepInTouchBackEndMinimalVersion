"""Animal schemas for request/response validation"""
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


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
