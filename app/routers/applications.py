from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import InternApplication
from app.schemas.schemas import InternApplicationCreate, InternApplicationOut

router = APIRouter(prefix="/applications", tags=["applications"])


@router.post("", response_model=InternApplicationOut)
def create_application(payload: InternApplicationCreate, db: Session = Depends(get_db)):
    application = InternApplication(**payload.model_dump())
    db.add(application)
    db.commit()
    db.refresh(application)
    return application