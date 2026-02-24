from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_admin
from app.models.direction import Direction
from app.models.models import User, InternApplication
from app.schemas.direction import DirectionCreate, DirectionOut

router = APIRouter(prefix="/directions", tags=["directions"])


@router.get("", response_model=list[DirectionOut])
def list_directions(db: Session = Depends(get_db)):
    return db.query(Direction).all()


@router.post("", response_model=DirectionOut, dependencies=[Depends(require_admin)])
def create_direction(payload: DirectionCreate, db: Session = Depends(get_db)):
    existing = db.query(Direction).filter(Direction.name == payload.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Direction already exists")
    direction = Direction(name=payload.name)
    db.add(direction)
    db.commit()
    db.refresh(direction)
    return direction


@router.put("/{direction_id}", response_model=DirectionOut, dependencies=[Depends(require_admin)])
def update_direction(direction_id: int, payload: DirectionCreate, db: Session = Depends(get_db)):
    direction = db.get(Direction, direction_id)
    if not direction:
        raise HTTPException(status_code=404, detail="Direction not found")
    if payload.name != direction.name:
        existing = db.query(Direction).filter(Direction.name == payload.name).first()
        if existing:
            raise HTTPException(status_code=400, detail="Direction already exists")
    direction.name = payload.name
    db.commit()
    db.refresh(direction)
    return direction


@router.delete("/{direction_id}", dependencies=[Depends(require_admin)])
def delete_direction(direction_id: int, db: Session = Depends(get_db)):
    direction = db.get(Direction, direction_id)
    if not direction:
        raise HTTPException(status_code=404, detail="Direction not found")
    # Проверяем, используется ли направление
    if db.query(User).filter(User.direction_id == direction_id).first():
        raise HTTPException(status_code=400, detail="Direction is used by organization users")
    if db.query(InternApplication).filter(InternApplication.specialization_id == direction_id).first():
        raise HTTPException(status_code=400, detail="Direction is used by intern applications")
    db.delete(direction)
    db.commit()
    return {"ok": True}