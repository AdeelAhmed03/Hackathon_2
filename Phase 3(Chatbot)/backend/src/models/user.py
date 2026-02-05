"""User model definition."""

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from enum import Enum

if TYPE_CHECKING:
    from .task import Task
    from .conversation import Conversation

class UserRole(str, Enum):
    """User roles for authorization."""
    USER = "user"
    ADMIN = "admin"

class UserBase(SQLModel):
    """Base user model with common fields."""
    email: str = Field(unique=True, index=True)
    name: str
    role: UserRole = UserRole.USER

class User(UserBase, table=True):
    """User database model."""
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    tasks: List["Task"] = Relationship(back_populates="owner")
    conversations: List["Conversation"] = Relationship(back_populates="user")

class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str

class UserUpdate(SQLModel):
    """Schema for updating a user."""
    name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[UserRole] = None

class UserLogin(SQLModel):
    """Schema for user login."""
    email: str
    password: str

class UserRead(UserBase):
    """Schema for reading user data."""
    id: int
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime

class UserResponse(UserBase):
    """Response schema for user data."""
    id: int

    @classmethod
    def from_orm(cls, user: User):
        """Convert User ORM object to response schema."""
        return cls(
            id=user.id,
            email=user.email,
            name=user.name,
            role=user.role
        )