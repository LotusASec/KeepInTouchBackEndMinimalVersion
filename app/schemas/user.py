"""User schemas for request/response validation"""
from pydantic import BaseModel
from typing import Optional


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


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[int] = None
    role: Optional[str] = None
