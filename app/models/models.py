from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import EnglishLevel, InternshipStatus, OrgRole, UserType
from app.models.direction import Direction


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    login: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    user_type: Mapped[UserType] = mapped_column(Enum(UserType), default=UserType.organization)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)

    org_role: Mapped[OrgRole | None] = mapped_column(Enum(OrgRole), nullable=True)
    direction_id: Mapped[int | None] = mapped_column(ForeignKey("directions.id"), nullable=True)
    direction: Mapped[Direction | None] = relationship()


class InternApplication(Base):
    __tablename__ = "intern_applications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    telegram: Mapped[str | None] = mapped_column(String(32), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(15), nullable=True)
    birth_date: Mapped[date] = mapped_column(Date)
    gender: Mapped[str] = mapped_column(String(20))
    country: Mapped[str] = mapped_column(String(50))
    city: Mapped[str] = mapped_column(String(50))
    education: Mapped[str | None] = mapped_column(Text, nullable=True)
    about: Mapped[str | None] = mapped_column(Text, nullable=True)
    specialization_id: Mapped[int] = mapped_column(ForeignKey("directions.id"), nullable=False)
    specialization: Mapped[Direction] = relationship()
    english_level: Mapped[EnglishLevel] = mapped_column(Enum(EnglishLevel))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class InternProfile(Base):
    __tablename__ = "intern_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    application_id: Mapped[int] = mapped_column(ForeignKey("intern_applications.id"), unique=True)
    role: Mapped[str | None] = mapped_column(String(50), nullable=True, default=None)
    mentor_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    status: Mapped[InternshipStatus] = mapped_column(Enum(InternshipStatus), default=InternshipStatus.pending)
    internship_start_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    internship_end_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    user: Mapped[User] = relationship(foreign_keys=[user_id])