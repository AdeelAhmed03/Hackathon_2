"""Message model for chat messages."""

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, JSON
from datetime import datetime
from typing import Optional, Any, TYPE_CHECKING
from enum import Enum

if TYPE_CHECKING:
    from .conversation import Conversation


class MessageRole(str, Enum):
    """Message role enumeration."""
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class MessageBase(SQLModel):
    """Base message model with common fields."""
    role: MessageRole
    content: Optional[str] = Field(default=None)


class Message(MessageBase, table=True):
    """Message database model - represents a single message in a conversation."""
    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversation.id", index=True)
    tool_calls: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    tool_results: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    conversation: "Conversation" = Relationship(back_populates="messages")


class MessageCreate(MessageBase):
    """Schema for creating a new message."""
    tool_calls: Optional[dict] = None
    tool_results: Optional[dict] = None


class MessageRead(MessageBase):
    """Schema for reading message data."""
    id: int
    conversation_id: int
    tool_calls: Optional[dict] = None
    tool_results: Optional[dict] = None
    created_at: datetime
