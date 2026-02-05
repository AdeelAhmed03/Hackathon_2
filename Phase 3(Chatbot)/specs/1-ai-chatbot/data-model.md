# Data Model: AI Todo Chatbot (Phase III)

**Feature**: AI Todo Chatbot
**Date**: 2026-02-04
**Status**: Design Complete

## Overview

Phase III adds two new database tables to support conversation persistence:
- `Conversation` - Chat sessions between users and AI
- `Message` - Individual messages within conversations

These tables extend the existing schema without modifying existing tables (Task, User, Tag).

---

## Entity Relationship Diagram

```
┌──────────────┐       ┌──────────────────┐       ┌──────────────────┐
│    User      │       │   Conversation   │       │     Message      │
├──────────────┤       ├──────────────────┤       ├──────────────────┤
│ id (PK)      │◄──────│ user_id (FK)     │       │ id (PK)          │
│ email        │  1:N  │ id (PK)          │◄──────│ conversation_id  │
│ name         │       │ title            │  1:N  │ role             │
│ ...          │       │ created_at       │       │ content          │
└──────────────┘       │ updated_at       │       │ tool_calls       │
       │               └──────────────────┘       │ tool_results     │
       │                                          │ created_at       │
       │ 1:N                                      └──────────────────┘
       ▼
┌──────────────┐
│    Task      │
├──────────────┤
│ id (PK)      │
│ owner_id(FK) │
│ title        │
│ ...          │
└──────────────┘
```

---

## New Tables

### Conversation

Represents a chat session between a user and the AI assistant.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO | Unique identifier |
| `user_id` | INTEGER | FOREIGN KEY → User.id, NOT NULL, INDEX | Owner of the conversation |
| `title` | VARCHAR(255) | NULLABLE | Optional title (auto-generated or user-set) |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | When conversation started |
| `updated_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Last activity timestamp |

**Indexes**:
- `ix_conversation_user_id` on `user_id` (query by user)
- `ix_conversation_updated_at` on `updated_at` (sort by recent)

**SQLModel Definition**:
```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User
    from .message import Message

class Conversation(SQLModel, table=True):
    """Chat conversation session."""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    title: Optional[str] = Field(default=None, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: "User" = Relationship(back_populates="conversations")
    messages: List["Message"] = Relationship(back_populates="conversation")
```

---

### Message

Represents a single message in a conversation (user, assistant, or tool).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO | Unique identifier |
| `conversation_id` | INTEGER | FOREIGN KEY → Conversation.id, NOT NULL, INDEX | Parent conversation |
| `role` | VARCHAR(20) | NOT NULL | Message role: 'user', 'assistant', 'tool' |
| `content` | TEXT | NULLABLE | Message text content |
| `tool_calls` | JSON | NULLABLE | Tool calls from assistant (Cohere format) |
| `tool_results` | JSON | NULLABLE | Results from tool execution |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | When message was created |

**Indexes**:
- `ix_message_conversation_id` on `conversation_id` (query messages by conversation)
- `ix_message_created_at` on `created_at` (sort chronologically)

**SQLModel Definition**:
```python
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

class Message(SQLModel, table=True):
    """Single message in a conversation."""
    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversation.id", index=True)
    role: MessageRole = Field(...)
    content: Optional[str] = Field(default=None)
    tool_calls: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    tool_results: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    conversation: "Conversation" = Relationship(back_populates="messages")
```

---

## User Model Update

Add relationship to conversations (no schema change, just SQLModel relationship):

```python
# In user.py, add to User class:
conversations: List["Conversation"] = Relationship(back_populates="user")
```

---

## JSON Field Schemas

### tool_calls (stored when assistant requests tool execution)

```json
[
    {
        "name": "add_task",
        "parameters": {
            "title": "Buy groceries",
            "priority": "medium"
        }
    }
]
```

### tool_results (stored after tool execution)

```json
[
    {
        "tool_name": "add_task",
        "success": true,
        "result": {
            "task_id": 42,
            "title": "Buy groceries",
            "message": "Task created successfully"
        }
    }
]
```

---

## Migration Strategy

Since we're using SQLModel with `create_tables()` on startup, new tables will be created automatically when the models are imported.

**Steps**:
1. Add `conversation.py` and `message.py` to `backend/src/models/`
2. Import them in `backend/src/models/__init__.py`
3. Update `User` model with `conversations` relationship
4. Restart backend - tables created automatically

**For production with existing data**:
```sql
-- Manual migration if needed
CREATE TABLE IF NOT EXISTS conversation (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES "user"(id),
    title VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX ix_conversation_user_id ON conversation(user_id);
CREATE INDEX ix_conversation_updated_at ON conversation(updated_at);

CREATE TABLE IF NOT EXISTS message (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER NOT NULL REFERENCES conversation(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,
    content TEXT,
    tool_calls JSONB,
    tool_results JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX ix_message_conversation_id ON message(conversation_id);
CREATE INDEX ix_message_created_at ON message(created_at);
```

---

## Query Patterns

### Get or Create Conversation for User
```python
def get_or_create_conversation(session: Session, user_id: int) -> Conversation:
    # Get most recent active conversation
    statement = (
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
        .limit(1)
    )
    conversation = session.exec(statement).first()

    if not conversation:
        conversation = Conversation(user_id=user_id)
        session.add(conversation)
        session.commit()
        session.refresh(conversation)

    return conversation
```

### Load Conversation History
```python
def get_conversation_messages(
    session: Session,
    conversation_id: int,
    limit: int = 20
) -> List[Message]:
    statement = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    messages = session.exec(statement).all()
    return list(reversed(messages))  # Chronological order
```

### Add Message to Conversation
```python
def add_message(
    session: Session,
    conversation_id: int,
    role: MessageRole,
    content: Optional[str] = None,
    tool_calls: Optional[dict] = None,
    tool_results: Optional[dict] = None
) -> Message:
    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
        tool_calls=tool_calls,
        tool_results=tool_results
    )
    session.add(message)

    # Update conversation timestamp
    conversation = session.get(Conversation, conversation_id)
    if conversation:
        conversation.updated_at = datetime.utcnow()

    session.commit()
    session.refresh(message)
    return message
```

---

## Validation Rules

| Field | Validation |
|-------|------------|
| `conversation.user_id` | Must exist in User table |
| `message.role` | Must be one of: 'user', 'assistant', 'tool' |
| `message.content` | Max 10,000 characters (prevent abuse) |
| `message.tool_calls` | Valid JSON if present |
| `message.tool_results` | Valid JSON if present |

---

## Security Constraints

1. **User Isolation**: All conversation queries MUST filter by `user_id`
2. **Cascade Delete**: Messages deleted when conversation deleted
3. **No Cross-Reference**: Messages cannot reference conversations owned by other users
4. **Content Sanitization**: Tool results sanitized before storage (no raw exceptions)
