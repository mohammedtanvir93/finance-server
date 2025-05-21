from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User
from app.auth.security import verify_password, hash_password, create_access_token
from uuid import UUID

def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password or ""):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return user

def login_user(db: Session, email: str, password: str):
    user = authenticate_user(db, email, password)
    access_token = create_access_token({"sub": str(user.id)})
    return access_token

def change_user_password(db: Session, user_id: UUID, old_password: str, new_password: str):
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not verify_password(old_password, user.password or ""):
        raise HTTPException(status_code=401, detail="Old password is incorrect")

    user.password = hash_password(new_password)
    db.commit()
    db.refresh(user)
    return user

def change_user_password_with_token(db: Session, change_password_token: str, new_password: str, retype_new_password: str):
    user = db.query(User).filter(User.change_password_token == change_password_token).first()
    if not user:
        raise HTTPException(status_code=404, detail="Invalid token or user not found")
    
    if new_password != retype_new_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    
    user.change_password_token = None  
    user.password = hash_password(new_password)  
    
    db.commit()
    db.refresh(user)
    
    access_token = create_access_token({"sub": str(user.id)})
    return access_token
