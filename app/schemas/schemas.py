from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, model_validator

from app.models.enums import EnglishLevel, InternshipStatus, OrgRole


class DirectionBase(BaseModel):
    name: str


class DirectionCreate(DirectionBase):
    pass


class DirectionOut(DirectionBase):
    id: int

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    refresh_token: str


class UserLogin(BaseModel):
    login: str
    password: str


class UserBase(BaseModel):
    email: EmailStr
    login: str
    first_name: str = Field(min_length=2, max_length=50)
    last_name: str = Field(min_length=2, max_length=50)


class OrgUserCreate(UserBase):
    password: str = Field(min_length=8)
    role: OrgRole
    direction_id: int
    is_admin: bool = False


class OrgUserUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=2, max_length=50)
    last_name: Optional[str] = Field(None, min_length=2, max_length=50)
    email: Optional[EmailStr] = None
    login: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)
    role: Optional[OrgRole] = None
    direction_id: Optional[int] = None
    is_admin: Optional[bool] = None


class UserOut(BaseModel):
    id: int
    email: EmailStr
    login: str
    first_name: str
    last_name: str
    is_admin: bool
    role: Optional[OrgRole] = None
    direction: Optional[DirectionOut] = None

    class Config:
        from_attributes = True


class InternApplicationCreate(BaseModel):
    first_name: str = Field(min_length=2, max_length=50)
    last_name: str = Field(min_length=2, max_length=50)
    email: Optional[EmailStr] = None
    telegram: Optional[str] = None
    phone: Optional[str] = None
    birth_date: date
    gender: str = Field(min_length=1, max_length=20)
    country: str = Field(min_length=2, max_length=50)
    city: str = Field(min_length=2, max_length=50)
    education: Optional[str] = None
    about: Optional[str] = None
    specialization_id: int
    english_level: EnglishLevel

    @model_validator(mode="after")
    def validate_contacts(self):
        if not any([self.email, self.telegram, self.phone]):
            raise ValueError("At least one contact (email/telegram/phone) is required")
        return self


class InternApplicationOut(InternApplicationCreate):
    id: int
    created_at: datetime
    specialization: DirectionOut

    class Config:
        from_attributes = True


class InternCreate(BaseModel):
    """Создание стажера из заявки (только для admin)"""
    application_id: int
    mentor_id: Optional[int] = None


class InternStatusUpdate(BaseModel):
    status: InternshipStatus


class InternOut(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: Optional[EmailStr] = None
    specialization: DirectionOut
    mentor_id: Optional[int] = None
    status: InternshipStatus
    internship_start_date: Optional[datetime] = None
    internship_end_date: Optional[datetime] = None

    class Config:
        from_attributes = True