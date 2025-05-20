from app.core.database import SessionLocal
from app.crud import role as crud_role
from app.schemas.role import RoleReadBase
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

router = APIRouter(
    prefix="/roles",
    tags=["roles"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[RoleReadBase])
def read_roles(db: Session = Depends(get_db)):
    return crud_role.get_roles(db)
