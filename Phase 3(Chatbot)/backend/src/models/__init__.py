"""SQLModel database models."""

from sqlmodel import SQLModel
from .user import User, UserBase, UserCreate, UserUpdate, UserRead, UserLogin, UserResponse
from .task import Task, TaskBase, TaskCreate, TaskUpdate, TaskRead, TaskStatus, TaskPriority
from .tag import Tag, TagBase, TagCreate, TagRead, TaskTagLink

# Re-export models for easier imports
__all__ = [
    "User",
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserRead",
    "UserLogin",
    "UserResponse",
    "Task",
    "TaskBase",
    "TaskCreate",
    "TaskUpdate",
    "TaskRead",
    "TaskStatus",
    "TaskPriority",
    "Tag",
    "TagBase",
    "TagCreate",
    "TagRead",
    "TaskTagLink",
]
