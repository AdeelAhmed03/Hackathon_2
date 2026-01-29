"""Task model definition."""

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, TIMESTAMP
from .tag import TaskTagLink
from .user import User

if TYPE_CHECKING:
    from .user import User
    from .tag import Tag
    from .task import Task

class TaskPriority(str, Enum):
    """Task priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class TaskStatus(str, Enum):
    """Task status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class RecurrenceRule(str, Enum):
    """Task recurrence rules."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"

class TaskBase(SQLModel):
    """Base task model with common fields."""
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    due_datetime: Optional[datetime] = None
    recurrence_rule: Optional[RecurrenceRule] = None

class Task(TaskBase, table=True):
    """Task database model."""
    id: Optional[int] = Field(default=None, primary_key=True)
    owner_id: int = Field(foreign_key="user.id", index=True)

    created_at: datetime = Field(sa_column=Column(TIMESTAMP(timezone=True), default_factory=datetime.utcnow))
    updated_at: datetime = Field(sa_column=Column(TIMESTAMP(timezone=True), default_factory=datetime.utcnow, onupdate=datetime.utcnow))
    completed_at: Optional[datetime] = Field(default=None, sa_column=Column(TIMESTAMP(timezone=True), nullable=True))

    # New fields
    recurrence_parent_id: Optional[int] = Field(default=None, foreign_key="task.id")

    # Relationships
    owner: "User" = Relationship(back_populates="tasks")
    tags: List["Tag"] = Relationship(back_populates="tasks", link_model=TaskTagLink)

    # Self-referencing relationships
    recurrence_parent: Optional["Task"] = Relationship(back_populates="recurrence_children")
    recurrence_children: List["Task"] = Relationship(back_populates="recurrence_parent")

class TaskCreate(TaskBase):
    """Schema for creating a new task."""
    pass

class TaskUpdate(SQLModel):
    """Schema for updating a task."""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_datetime: Optional[datetime] = None
    recurrence_rule: Optional[RecurrenceRule] = None

class TaskRead(TaskBase):
    """Schema for reading task data."""
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    recurrence_parent_id: Optional[int] = None
