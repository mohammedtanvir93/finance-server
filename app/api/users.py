from app.core.database import SessionLocal
from app.crud import user as crud_user
from app.models.role import Role
from app.models.user import User
from app.schemas.user import UserCreate, UserReadDetails, UserReadList, UserUpdate
from app.utils.emails.welcome import send_welcome_email
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID, uuid4
import os

class PaginatedUserListResponse(BaseModel):
    data: List[UserReadList]
    total: int
    limit: int
    skip: int

router = APIRouter(
    prefix="/users", 
    tags=["users"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def ensure_role_exists(db: Session, role_id: UUID) -> None:
    if not db.query(Role).filter(Role.id == role_id).first():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"errors": {"role_id": "Role does not exist"}}
        )

def ensure_email_unique(db: Session, email: str, exclude_user_id: UUID = None) -> None:
    query = db.query(User).filter(User.email == email)
    if exclude_user_id:
        query = query.filter(User.id != exclude_user_id)
    if query.first():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"errors": {"email": "Email already registered"}}
        )

@router.post("/", response_model=UserReadDetails)
def create_user(user: UserCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    ensure_role_exists(db, user.role_id)
    ensure_email_unique(db, user.email)
    
    verification_token = str(uuid4())
    verification_link = f"{os.getenv('CLIENT_APP_HOST')}/verify-email?token={verification_token}"

    created_user = crud_user.create_user(db, user, verification_token)
    
    background_tasks.add_task(
        send_welcome_email,
        email=created_user.email,
        username=created_user.fullname,
        verification_link=verification_link
    )
    
    return created_user

@router.patch("/{user_id}", response_model=UserReadDetails)
def update_user(user_id: UUID, user_data: UserUpdate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if user_data.email:
        ensure_email_unique(db, user_data.email, exclude_user_id=user_id)

    if user_data.role_id:
        ensure_role_exists(db, user_data.role_id)

    updated_user = crud_user.update_user(db, db_user, user_data)
    return updated_user

@router.get("/{user_id}", response_model=UserReadDetails)
def read_user(user_id: UUID, db: Session = Depends(get_db)):
    db_user = crud_user.get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.get("/", response_model=PaginatedUserListResponse)
def read_users(
    skip: int = 0,
    limit: int = 10,
    search: Optional[str] = Query(None, description="Search by name, email, role title, or status"),
    db: Session = Depends(get_db)
):
    users, total = crud_user.get_users(db, skip=skip, limit=limit, search=search)
    return {
        "data": users,
        "total": total,
        "limit": limit,
        "skip": skip
    }
    
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: UUID, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    crud_user.delete_user(db, db_user)
    return
