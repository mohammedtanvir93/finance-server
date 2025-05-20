from app.models.user import UserStatus
from app.schemas.role import RoleReadBase, RoleReadRelation
from datetime import datetime
from email_validator import validate_email, EmailNotValidError
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from uuid import UUID

class UserBase(BaseModel):
    email: str = Field(..., description="Email address")
    fullname: str = Field(..., description="Fullname")
    role_id: UUID

    @field_validator("email")
    def validate_email(cls, v: str) -> str:
        if len(v) < 2:
            raise ValueError("Email must be at least 2 characters long")
        if len(v) > 255:
            raise ValueError("Email must not exceed 255 characters")
        try:
            validate_email(v)
        except EmailNotValidError:
            raise ValueError("Please provide a valid email address")
        return v

    @field_validator("fullname")
    def validate_fullname(cls, v: str) -> str:
        if len(v) < 2:
            raise ValueError("Full name must be at least 2 characters long")
        if len(v) > 255:
            raise ValueError("Full name must not exceed 255 characters")
        return v

class UserCreate(UserBase):
    pass

class UserUpdate(UserBase):
    status: UserStatus

class UserReadBase(BaseModel):
    id: UUID
    email: str
    fullname: str
    status: UserStatus
    joined_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class UserReadDetails(UserReadBase):
    change_password_token: Optional[str] = None
    role: RoleReadRelation

class UserReadList(UserReadBase):
    role: RoleReadBase
