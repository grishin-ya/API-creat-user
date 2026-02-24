from datetime import date, datetime
import re
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

from app.models.enums import EnglishLevel, InternshipStatus, OrgRole
from app.schemas.direction import DirectionOut

# Регулярные выражения для валидации
NAME_RE = re.compile(r"^[A-Za-zА-Яа-яЁё\-\s]{2,50}$")
TG_RE = re.compile(r"^@?[a-zA-Z][a-zA-Z0-9_]{3,30}[a-zA-Z0-9]$")
PHONE_RE = re.compile(r"^\+[0-9]{6,14}$")
COUNTRY_CITY_RE = re.compile(r"^[^\d]{2,50}$")


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserLogin(BaseModel):
    login: str
    password: str


class OrgUserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    login: str
    password: str = Field(min_length=8)
    role: OrgRole
    direction_id: int
    is_admin: bool = False

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not NAME_RE.match(v):
            raise ValueError("Only russian/english letters, spaces and hyphens, 2-50 chars")
        return v


class OrgUserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    login: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)
    role: Optional[OrgRole] = None
    direction_id: Optional[int] = None
    is_admin: Optional[bool] = None

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not NAME_RE.match(v):
            raise ValueError("Only russian/english letters, spaces and hyphens, 2-50 chars")
        return v


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
    first_name: str
    last_name: str
    email: Optional[EmailStr] = None
    telegram: Optional[str] = None
    phone: Optional[str] = None
    birth_date: date
    gender: str
    country: str
    city: str
    education: Optional[str] = None
    about: Optional[str] = None
    specialization_id: int
    english_level: EnglishLevel

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not NAME_RE.match(v):
            raise ValueError("Only letters allowed, length 2-50")
        return v

    @field_validator("telegram")
    @classmethod
    def validate_tg(cls, v: Optional[str]) -> Optional[str]:
        if v and not TG_RE.match(v):
            raise ValueError("Invalid telegram username")
        return v

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v and not PHONE_RE.match(v):
            raise ValueError("Phone must start with + and have 7-15 digits")
        return v

    @field_validator("country", "city")
    @classmethod
    def validate_country_city(cls, v: str) -> str:
        if not COUNTRY_CITY_RE.match(v):
            raise ValueError("2-50 chars, no digits")
        return v

    @field_validator("birth_date")
    @classmethod
    def validate_birth_date(cls, v: date) -> date:
        today = date.today()
        age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
        if age < 16 or age > 100:
            raise ValueError("Age must be between 16 and 100")
        return v

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


class InternCreateFromApplication(BaseModel):
    application_id: int
    login: str
    password: str = Field(min_length=8)
    mentor_id: Optional[int] = None


class InternStatusUpdate(BaseModel):
    status: InternshipStatus


class InternOut(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    specialization: DirectionOut
    mentor_id: Optional[int] = None
    status: InternshipStatus
    internship_start_date: Optional[datetime] = None
    internship_end_date: Optional[datetime] = None