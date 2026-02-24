from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import require_admin
from app.core.security import get_password_hash
from app.models.enums import UserType
from app.models.models import User, InternProfile
from app.schemas.schemas import OrgUserCreate, OrgUserUpdate, UserOut

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/organization", response_model=UserOut)
def create_org_user(payload: OrgUserCreate, db: Session = Depends(get_db), _admin: User = Depends(require_admin)):
    if db.query(User).filter((User.login == payload.login) | (User.email == payload.email)).first():
        raise HTTPException(status_code=400, detail="Login or email already exists")

    user = User(
        email=payload.email,
        login=payload.login,
        hashed_password=get_password_hash(payload.password),
        first_name=payload.first_name,
        last_name=payload.last_name,
        user_type=UserType.organization,
        is_admin=payload.is_admin,
        org_role=payload.role,
        direction_id=payload.direction_id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserOut(
        id=user.id,
        email=user.email,
        login=user.login,
        first_name=user.first_name,
        last_name=user.last_name,
        is_admin=user.is_admin,
        role=user.org_role,
        direction=user.direction,
    )


@router.put("/{user_id}", response_model=UserOut)
def update_org_user(
    user_id: int,
    payload: OrgUserUpdate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    user = db.get(User, user_id)
    if not user or user.user_type != UserType.organization:
        raise HTTPException(status_code=404, detail="Organization user not found")

    if payload.login and payload.login != user.login:
        if db.query(User).filter(User.login == payload.login).first():
            raise HTTPException(status_code=400, detail="Login already exists")
    if payload.email and payload.email != user.email:
        if db.query(User).filter(User.email == payload.email).first():
            raise HTTPException(status_code=400, detail="Email already exists")

    if payload.first_name is not None:
        user.first_name = payload.first_name
    if payload.last_name is not None:
        user.last_name = payload.last_name
    if payload.email is not None:
        user.email = payload.email
    if payload.login is not None:
        user.login = payload.login
    if payload.password is not None:
        user.hashed_password = get_password_hash(payload.password)
    if payload.role is not None:
        user.org_role = payload.role
    if payload.direction_id is not None:
        user.direction_id = payload.direction_id
    if payload.is_admin is not None:
        user.is_admin = payload.is_admin

    db.commit()
    db.refresh(user)
    return UserOut(
        id=user.id,
        email=user.email,
        login=user.login,
        first_name=user.first_name,
        last_name=user.last_name,
        is_admin=user.is_admin,
        role=user.org_role,
        direction=user.direction,
    )


@router.delete("/{user_id}")
def delete_org_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin),
):
    if user_id == current_admin.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")

    user = db.get(User, user_id)
    if not user or user.user_type != UserType.organization:
        raise HTTPException(status_code=404, detail="Organization user not found")

    mentor_of = db.query(InternProfile).filter(InternProfile.mentor_id == user_id).first()
    if mentor_of:
        raise HTTPException(
            status_code=400,
            detail="User is a mentor for one or more interns. Reassign or delete interns first."
        )

    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}