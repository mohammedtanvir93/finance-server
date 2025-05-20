from app.models.role import Role
from app.models.user import User
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from datetime import datetime
from datetime import datetime
from sqlalchemy import or_, func, String
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

def create_user(db: Session, user: UserCreate, change_password_token: str) -> User:
    db_user = User(**user.dict(), created_at=datetime.utcnow(), change_password_token=change_password_token)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, db_user: User, user_data: UserUpdate) -> User:
    for field, value in user_data.dict(exclude_unset=True).items():
        setattr(db_user, field, value)

    db_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user(db: Session, user_id: UUID) -> User:
    return db.query(User).filter(User.id == user_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 10, search: Optional[str] = None):
    query = db.query(User).join(User.role)

    if search:
        ilike_value = f"%{search}%"
        query = query.filter(
            or_(
                func.lower(User.email).ilike(func.lower(ilike_value)),
                func.lower(User.fullname).ilike(func.lower(ilike_value)),
                func.lower(Role.title).ilike(func.lower(ilike_value)),
                func.lower(User.status.cast(String)).ilike(func.lower(ilike_value)),
            )
        )

    total = query.count()
    users = query.offset(skip).limit(limit).all()

    return users, total

def delete_user(db: Session, user: User):
    db.delete(user)
    db.commit()
