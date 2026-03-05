from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.deps import get_current_user, require_admin
from app.models.enums import InternshipStatus, OrgRole, UserType
from app.models.models import InternApplication, Intern, User
from app.schemas.schemas import InternCreate, InternOut, InternStatusUpdate

router = APIRouter(prefix="/interns", tags=["interns"])


@router.post("", response_model=InternOut)
def create_intern(
    payload: InternCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):

    application = db.query(InternApplication).filter(
        InternApplication.id == payload.application_id
    ).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    existing = db.query(Intern).filter(
        Intern.application_id == payload.application_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Intern already created from this application")

    if payload.mentor_id:
        mentor = db.query(User).filter(
            User.id == payload.mentor_id,
            User.user_type == UserType.organization,
            User.org_role == OrgRole.mentor
        ).first()
        if not mentor:
            raise HTTPException(status_code=400, detail="Mentor not found or invalid")

    intern = Intern(
        application_id=application.id,
        mentor_id=payload.mentor_id,
        status=InternshipStatus.pending,
        internship_start_date=datetime.now(timezone.utc) if payload.mentor_id else None,
    )
    db.add(intern)
    db.commit()
    db.refresh(intern)
    
    return InternOut(
        id=intern.id,
        first_name=application.first_name,
        last_name=application.last_name,
        email=application.email,
        specialization=application.specialization,
        mentor_id=intern.mentor_id,
        status=intern.status,
        internship_start_date=intern.internship_start_date,
        internship_end_date=intern.internship_end_date,
    )


@router.patch("/{intern_id}/status", response_model=InternOut)
def update_status(
    intern_id: int,
    payload: InternStatusUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    intern = db.get(Intern, intern_id)
    if not intern:
        raise HTTPException(status_code=404, detail="Intern not found")

    intern.status = payload.status
    if payload.status in (InternshipStatus.approved, InternshipStatus.rejected):
        intern.internship_end_date = datetime.now(timezone.utc)

    db.commit()
    db.refresh(intern)
    
    application = intern.application
    return InternOut(
        id=intern.id,
        first_name=application.first_name,
        last_name=application.last_name,
        email=application.email,
        specialization=application.specialization,
        mentor_id=intern.mentor_id,
        status=intern.status,
        internship_start_date=intern.internship_start_date,
        internship_end_date=intern.internship_end_date,
    )


@router.get("", response_model=List[InternOut])
def list_interns(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Intern).join(Intern.application)

    if current_user.is_admin or current_user.org_role == OrgRole.hr:

        pass
    elif current_user.org_role == OrgRole.lead:
 
        query = query.join(InternApplication).filter(
            InternApplication.specialization_id == current_user.direction_id
        )
    elif current_user.org_role == OrgRole.mentor:

        query = query.filter(Intern.mentor_id == current_user.id)
    else:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    interns = query.all()
    result = []
    for intern in interns:
        app = intern.application
        result.append(InternOut(
            id=intern.id,
            first_name=app.first_name,
            last_name=app.last_name,
            email=app.email,
            specialization=app.specialization,
            mentor_id=intern.mentor_id,
            status=intern.status,
            internship_start_date=intern.internship_start_date,
            internship_end_date=intern.internship_end_date,
        ))
    return result


@router.get("/{intern_id}", response_model=InternOut)
def get_intern(
    intern_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    intern = db.get(Intern, intern_id)
    if not intern:
        raise HTTPException(status_code=404, detail="Intern not found")
    
    if not current_user.is_admin and current_user.org_role != OrgRole.hr:
        if current_user.org_role == OrgRole.lead:
            if intern.application.specialization_id != current_user.direction_id:
                raise HTTPException(status_code=403, detail="Not enough permissions")
        elif current_user.org_role == OrgRole.mentor:
            if intern.mentor_id != current_user.id:
                raise HTTPException(status_code=403, detail="Not enough permissions")
        else:
            raise HTTPException(status_code=403, detail="Not enough permissions")
    
    app = intern.application
    return InternOut(
        id=intern.id,
        first_name=app.first_name,
        last_name=app.last_name,
        email=app.email,
        specialization=app.specialization,
        mentor_id=intern.mentor_id,
        status=intern.status,
        internship_start_date=intern.internship_start_date,
        internship_end_date=intern.internship_end_date,
    )