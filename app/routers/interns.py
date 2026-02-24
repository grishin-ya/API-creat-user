from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_admin
from app.core.security import get_password_hash
from app.models.enums import InternshipStatus, OrgRole, UserType
from app.models.models import InternApplication, InternProfile, User
from app.schemas.schemas import InternCreateFromApplication, InternOut, InternStatusUpdate

router = APIRouter(prefix="/interns", tags=["interns"])


@router.post("", response_model=InternOut)
def create_intern_from_application(
    payload: InternCreateFromApplication,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    app = db.query(InternApplication).filter(InternApplication.id == payload.application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    if db.query(User).filter((User.login == payload.login) | (User.email == app.email)).first():
        raise HTTPException(status_code=400, detail="Login or email already exists")

    mentor_id = payload.mentor_id
    if mentor_id:
        mentor = db.query(User).filter(User.id == mentor_id, User.org_role == OrgRole.mentor).first()
        if not mentor:
            raise HTTPException(status_code=400, detail="Mentor not found or invalid")

    intern_user = User(
        email=app.email or f"intern_{app.id}@no-email.local",
        login=payload.login,
        hashed_password=get_password_hash(payload.password),
        first_name=app.first_name,
        last_name=app.last_name,
        user_type=UserType.intern,
        is_admin=False,
        org_role=None,
        direction_id=app.specialization_id,
    )
    db.add(intern_user)
    db.flush()

    start_date = datetime.utcnow() if mentor_id else None
    profile = InternProfile(
        user_id=intern_user.id,
        application_id=app.id,
        role=None,
        mentor_id=mentor_id,
        status=InternshipStatus.pending,
        internship_start_date=start_date,
    )
    db.add(profile)
    db.commit()
    db.refresh(intern_user)
    db.refresh(profile)

    return InternOut(
        id=intern_user.id,
        first_name=intern_user.first_name,
        last_name=intern_user.last_name,
        email=intern_user.email,
        specialization=intern_user.direction,
        mentor_id=profile.mentor_id,
        status=profile.status,
        internship_start_date=profile.internship_start_date,
        internship_end_date=profile.internship_end_date,
    )


@router.patch("/{intern_id}/status", response_model=InternOut)
def update_status(
    intern_id: int,
    payload: InternStatusUpdate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    intern = db.query(User).filter(User.id == intern_id, User.user_type == UserType.intern).first()
    profile = db.query(InternProfile).filter(InternProfile.user_id == intern_id).first()
    if not intern or not profile:
        raise HTTPException(status_code=404, detail="Intern not found")

    profile.status = payload.status
    if payload.status in (InternshipStatus.approved, InternshipStatus.rejected):
        profile.internship_end_date = datetime.utcnow()

    db.commit()
    db.refresh(profile)
    return InternOut(
        id=intern.id,
        first_name=intern.first_name,
        last_name=intern.last_name,
        email=intern.email,
        specialization=intern.direction,
        mentor_id=profile.mentor_id,
        status=profile.status,
        internship_start_date=profile.internship_start_date,
        internship_end_date=profile.internship_end_date,
    )


@router.get("", response_model=list[InternOut])
def list_interns(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    query = (
        db.query(User, InternProfile)
        .join(InternProfile, InternProfile.user_id == User.id)
        .filter(User.user_type == UserType.intern)
    )

    if current_user.is_admin or current_user.org_role == OrgRole.hr:
        pass
    elif current_user.org_role == OrgRole.lead:
        query = query.filter(User.direction_id == current_user.direction_id)
    elif current_user.org_role == OrgRole.mentor:
        query = query.filter(InternProfile.mentor_id == current_user.id)
    else:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    rows = query.all()
    return [
        InternOut(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            specialization=user.direction,
            mentor_id=profile.mentor_id,
            status=profile.status,
            internship_start_date=profile.internship_start_date,
            internship_end_date=profile.internship_end_date,
        )
        for user, profile in rows
    ]