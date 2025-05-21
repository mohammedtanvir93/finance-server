from app.core.database import Base
from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
import uuid

class UserStatus(enum.Enum):
    ACTIVE = "ACTIVE"
    PENDING = "PENDING"
    INACTIVE = "INACTIVE"

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    fullname = Column(String(255), nullable=False)
    password = Column(String(255), nullable=True)
    change_password_token = Column(String(255), nullable=True)
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"), nullable=False)
    status = Column(Enum(UserStatus, name="user_status"), nullable=False, default=UserStatus.PENDING)
    joined_at = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP, nullable=False)
    updated_at = Column(TIMESTAMP, nullable=True)
    
    role = relationship("Role", back_populates="users")
