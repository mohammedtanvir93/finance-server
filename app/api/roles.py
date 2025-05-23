from app.auth.dependencies import get_db, get_current_user
from app.core.database import SessionLocal
from app.crud import role as crud_role
from app.models.user import User
from app.schemas.role import RoleReadBase
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

router = APIRouter(
    prefix="/roles",
    tags=["roles"]
)

@router.get("/", response_model=List[RoleReadBase])
def read_roles(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return crud_role.get_roles(db)
