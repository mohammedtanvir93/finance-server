from app.auth.security import decode_access_token
from app.core.database import SessionLocal
from app.models.user import User
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid authentication")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid authentication")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user

def check_permission(
    user: User,
    *,
    name: str,
    target_id: Optional[UUID] = None,
    provided_id: Optional[UUID] = None,
) -> bool:
    permissions = user.role.permission or []

    if target_id and provided_id:
        if str(target_id) == str(provided_id):
            return name in permissions
        else:
            return False
    else:
        return name in permissions
