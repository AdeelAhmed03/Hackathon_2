"""SQLModel database models."""

from sqlmodel import SQLModel
from .user import User, UserBase, UserCreate, UserUpdate, UserRead, UserLogin, UserResponse
from .task import Task, TaskBase, TaskCreate, TaskUpdate, TaskRead, TaskStatus, TaskPriority
from .tag import Tag, TagBase, TagCreate, TagRead, TaskTagLink
from .conversation import Conversation, ConversationBase, ConversationCreate, ConversationRead, ConversationWithMessages
from .message import Message, MessageBase, MessageCreate, MessageRead, MessageRole

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
    # Phase III: Chat models
    "Conversation",
    "ConversationBase",
    "ConversationCreate",
    "ConversationRead",
    "ConversationWithMessages",
    "Message",
    "MessageBase",
    "MessageCreate",
    "MessageRead",
    "MessageRole",
]
