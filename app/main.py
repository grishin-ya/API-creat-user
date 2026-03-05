from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import Base, engine
from app.core.security import get_password_hash
from app.models.direction import Direction
from app.models.enums import UserType
from app.models.models import User
from app.routers import applications, auth, directions, interns, org_users


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    
    db = Session(bind=engine)
    try:
        for name in ["Python", "Angular", "React"]:
            if not db.query(Direction).filter(Direction.name == name).first():
                db.add(Direction(name=name))
        db.commit()

        if not db.query(User).filter(User.login == settings.first_admin_login).first():
            admin = User(
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
            db.add(admin)
            db.commit()
    finally:
        db.close()
    
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(org_users.router)
app.include_router(applications.router)
app.include_router(interns.router)
app.include_router(directions.router)