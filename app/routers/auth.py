from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from app.core.database import get_db
from app.core.security import create_access_token, create_refresh_token, verify_password
from app.core.config import settings
from app.schemas.schemas import Token, TokenRefresh, UserLogin
from app.models.models import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.login == payload.login).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid login or password"
        )
    
    return Token(
        access_token=create_access_token(user.login),
        refresh_token=create_refresh_token(user.login)
    )


@router.post("/refresh", response_model=Token)
def refresh(payload: TokenRefresh, db: Session = Depends(get_db)):
    try:
        payload_data = jwt.decode(
            payload.refresh_token, 
            settings.refresh_secret_key, 
            algorithms=[settings.algorithm]
        )
        login: str = payload_data.get("sub")
        if login is None or payload_data.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user = db.query(User).filter(User.login == login).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return Token(
        access_token=create_access_token(user.login),
        refresh_token=create_refresh_token(user.login)
    )