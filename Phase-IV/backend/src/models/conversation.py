"""Conversation model for chat sessions."""

from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User
    from .message import Message


class ConversationBase(SQLModel):
    """Base conversation model with common fields."""
    title: Optional[str] = Field(default=None, max_length=255)


class Conversation(ConversationBase, table=True):
    """Conversation database model - represents a chat session."""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: "User" = Relationship(back_populates="conversations")
    messages: List["Message"] = Relationship(back_populates="conversation")


class ConversationCreate(ConversationBase):
    """Schema for creating a new conversation."""
    pass


class ConversationRead(ConversationBase):
    """Schema for reading conversation data."""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    message_count: Optional[int] = None


class ConversationWithMessages(ConversationRead):
    """Schema for conversation with messages included."""
    messages: List["MessageRead"] = []


# Import at end to avoid circular imports
from .message import MessageRead
ConversationWithMessages.model_rebuild()
