from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    name: str
    email: EmailStr


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None


class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        orm_mode = True


class UserInDB(UserOut):
    must_change_password: bool


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class ChangePasswordIn(BaseModel):
    old_password: Optional[str]
    new_password: str


class ArticleBase(BaseModel):
    title_en: str
    title_kin: Optional[str]
    title_lug: Optional[str]
    content_en: str
    content_kin: Optional[str]
    content_lug: Optional[str]
    cover_image_url: Optional[str]


class ArticleOut(ArticleBase):
    id: int
    status: str
    publisher_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class AskIn(BaseModel):
    question: str
    language: str
