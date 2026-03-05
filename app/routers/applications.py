from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.deps import get_current_user, require_admin
from app.models.models import InternApplication, User
from app.models.enums import OrgRole
from app.schemas.schemas import InternApplicationCreate, InternApplicationOut

router = APIRouter(prefix="/applications", tags=["applications"])


@router.post("", response_model=InternApplicationOut)
def create_application(payload: InternApplicationCreate, db: Session = Depends(get_db)):
    application = InternApplication(**payload.model_dump())
    db.add(application)
    db.commit()
    db.refresh(application)
    return application


@router.get("", response_model=List[InternApplicationOut])
def list_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not (current_user.is_admin or current_user.org_role == OrgRole.hr):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    applications = db.query(InternApplication).order_by(InternApplication.created_at.desc()).all()
    return applications


@router.get("/{application_id}", response_model=InternApplicationOut)
def get_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not (current_user.is_admin or current_user.org_role == OrgRole.hr):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    application = db.get(InternApplication, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    return application