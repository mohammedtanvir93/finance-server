from app.auth.dependencies import check_permission, get_db, get_current_user
from app.core.database import SessionLocal
from app.crud import user as crud_user
from app.models.role import Role
from app.models.user import User
from app.schemas.user import UserCreate, UserReadDetails, UserReadList, UserUpdate, UserSelfUpdate
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
def create_user(
    user: UserCreate, 
    background_tasks: BackgroundTasks, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)):
    
    if not check_permission(current_user, name="create:users"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    ensure_role_exists(db, user.role_id)
    ensure_email_unique(db, user.email)
    
    verification_token = str(uuid4())
    verification_link = f"{os.getenv('CLIENT_APP_HOST')}/change-password/{verification_token}"

    created_user = crud_user.create_user(db, user, verification_token)
    
    background_tasks.add_task(
        send_welcome_email,
        email='mohammed.tanvir447@gmail.com',
        username=created_user.fullname,
        verification_link=verification_link
    )
    
    return created_user

@router.patch("/me", response_model=UserReadDetails)
def update_current_user(
    user_data: UserSelfUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_user = db.query(User).filter(User.id == current_user.id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if user_data.email and user_data.email != db_user.email:
        ensure_email_unique(db, user_data.email, exclude_user_id=db_user.id)

    updated_user = crud_user.update_user(db, db_user, user_data)
    return updated_user

@router.patch("/{user_id}", response_model=UserReadDetails)
def update_user(
    user_id: UUID, 
    user_data: UserUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)):
    
    if not (
        check_permission(current_user, name="edit:users") or
        (check_permission(current_user, name="editOwn:users", target_id=user_id, provided_id=current_user.id))
    ):
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if user_data.email:
        ensure_email_unique(db, user_data.email, exclude_user_id=user_id)

    if user_data.role_id:
        ensure_role_exists(db, user_data.role_id)

    updated_user = crud_user.update_user(db, db_user, user_data)
    return updated_user

@router.get("/me", response_model=UserReadDetails)
def get_profile(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/{user_id}", response_model=UserReadDetails)
def read_user(
    user_id: UUID, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)):
    
    if not (
        check_permission(current_user, name="viewDetails:users") or
        (check_permission(current_user, name="viewOwnDetails:users", target_id=user_id, provided_id=current_user.id))
    ):
        raise HTTPException(status_code=403, detail="Insufficient permissions")


    db_user = crud_user.get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.get("/", response_model=PaginatedUserListResponse)
def read_users(
    skip: int = 0,
    limit: int = 10,
    search: Optional[str] = Query(None, description="Search by name, email, role title, or status"),
    sort_by: Optional[str] = Query("created_at", description="Field to sort by (e.g., fullname, email, created_at)"),
    sort_order: Optional[str] = Query("desc", description="Sort order: asc or desc"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    
    view_own = check_permission(current_user, name="viewOwn:users")
    
    if not (
        check_permission(current_user, name="view:users") or view_own
    ):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    user_filter_id = current_user.id if view_own else None
    
    print(f"User ID : {user_filter_id}")
    
    users, total = crud_user.get_users(
        db,
        skip=skip,
        limit=limit,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
        user_id=user_filter_id
    )
    return {
        "data": users,
        "total": total,
        "limit": limit,
        "skip": skip
    }
    
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: UUID, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)):
    
    if not (
        check_permission(current_user, name="delete:users") or
        (check_permission(current_user, name="deleteOwn:users", target_id=user_id, provided_id=current_user.id))
    ):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    crud_user.delete_user(db, db_user)
    return