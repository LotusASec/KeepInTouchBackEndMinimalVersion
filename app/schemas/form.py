"""Form schemas for request/response validation"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


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
