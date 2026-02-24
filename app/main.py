from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import Base, engine
from app.core.security import get_password_hash
from app.models.direction import Direction
from app.models.enums import UserType
from app.models.models import User
from app.routers.applications import router as applications_router
from app.routers.auth import router as auth_router
from app.routers.directions import router as directions_router
from app.routers.interns import router as interns_router
from app.routers.org_users import router as org_users_router

app = FastAPI(title=settings.app_name)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Замените на конкретные домены в продакшене
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

    db = Session(bind=engine)

    # Создание направлений по умолчанию
    default_directions = ["Python", "Angular", "React"]
    for name in default_directions:
        if not db.query(Direction).filter(Direction.name == name).first():
            db.add(Direction(name=name))
    db.commit()

    # Создание администратора
    admin = db.query(User).filter(User.login == settings.first_admin_login).first()
    if not admin:
        db.add(
            User(
                email="admin@local.dev",
                login=settings.first_admin_login,
                hashed_password=get_password_hash(settings.first_admin_password),
                first_name="System",
                last_name="Admin",
                user_type=UserType.organization,
                is_admin=True,
                org_role=None,
                direction_id=None,
            )
        )
        db.commit()
    db.close()


app.include_router(auth_router)
app.include_router(org_users_router)
app.include_router(applications_router)
app.include_router(interns_router)
app.include_router(directions_router)