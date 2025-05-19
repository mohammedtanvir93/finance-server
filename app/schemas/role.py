from datetime import datetime
from pydantic import BaseModel, constr
from typing import Optional, List
from uuid import UUID

class RoleBase(BaseModel):
    title: constr(min_length=2, max_length=255)
    permission: List[str]

class RoleCreate(RoleBase):
    pass

class RoleReadBase(BaseModel):
    id: UUID
    title: str

    class Config:
        orm_mode = True

class RoleRead(RoleReadBase):
    permission: List[str]
    created_at: datetime
    updated_at: Optional[datetime] = None

class RoleReadRelation(RoleReadBase):
    permission: List[str]
