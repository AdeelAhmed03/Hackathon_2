# Data Model: Phase V Schema Updates

**Feature**: 001-event-driven-cloud
**Date**: 2026-02-09
**Status**: Complete

## Overview

Phase V extends the existing Task model with new fields for advanced task management (due dates, reminders, recurring tasks, priorities) and introduces Tag entities for multi-label categorization. The schema supports event-driven architecture with audit logging capabilities.

## Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              DATABASE SCHEMA                                     │
└─────────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────┐       ┌──────────────────────┐       ┌──────────────────────┐
│        User          │       │        Task          │       │         Tag          │
├──────────────────────┤       ├──────────────────────┤       ├──────────────────────┤
│ id: UUID (PK)        │──────▶│ id: UUID (PK)        │       │ id: UUID (PK)        │
│ email: VARCHAR       │       │ user_id: UUID (FK)   │◀──────│ user_id: UUID (FK)   │
│ name: VARCHAR        │       │ title: VARCHAR       │       │ name: VARCHAR        │
│ password_hash: TEXT  │       │ description: TEXT    │       │ created_at: TIMESTAMP│
│ created_at: TIMESTAMP│       │ status: ENUM         │       └──────────────────────┘
│ updated_at: TIMESTAMP│       │ priority: ENUM (NEW) │                │
└──────────────────────┘       │ due_at: TIMESTAMPTZ  │                │
                               │   (NEW, nullable)    │                │
                               │ remind_at: TIMESTAMPTZ│               │
                               │   (NEW, nullable)    │                │
                               │ recurring_interval:  │                │
                               │   ENUM (NEW, nullable)│               │
                               │ parent_task_id: UUID │                │
                               │   (NEW, nullable, FK)│                │
                               │ created_at: TIMESTAMP│                │
                               │ updated_at: TIMESTAMP│                │
                               └──────────┬───────────┘                │
                                          │                            │
                                          │ many-to-many               │
                                          ▼                            ▼
                               ┌──────────────────────┐
                               │      TaskTag         │
                               ├──────────────────────┤
                               │ task_id: UUID (FK)   │
                               │ tag_id: UUID (FK)    │
                               │ (PK: task_id, tag_id)│
                               └──────────────────────┘

┌──────────────────────┐       ┌──────────────────────┐
│    Conversation      │       │      Message         │
├──────────────────────┤       ├──────────────────────┤
│ id: UUID (PK)        │──────▶│ id: UUID (PK)        │
│ user_id: UUID (FK)   │       │ conversation_id (FK) │
│ title: VARCHAR       │       │ role: ENUM           │
│ created_at: TIMESTAMP│       │ content: TEXT        │
│ updated_at: TIMESTAMP│       │ tool_calls: JSONB    │
└──────────────────────┘       │ created_at: TIMESTAMP│
                               └──────────────────────┘

┌──────────────────────┐       ┌──────────────────────┐
│   ProcessedEvent     │       │     AuditLog         │
│   (NEW - optional)   │       │   (NEW - optional)   │
├──────────────────────┤       ├──────────────────────┤
│ id: UUID (PK)        │       │ id: UUID (PK)        │
│ event_key: VARCHAR   │       │ user_id: UUID (FK)   │
│   (UNIQUE)           │       │ event_type: VARCHAR  │
│ processed_at:        │       │ entity_type: VARCHAR │
│   TIMESTAMP          │       │ entity_id: UUID      │
└──────────────────────┘       │ old_data: JSONB      │
                               │ new_data: JSONB      │
                               │ created_at: TIMESTAMP│
                               └──────────────────────┘
```

## Entity Definitions

### Task (Enhanced)

**Purpose**: Represents a user's todo item with enhanced fields for due dates, reminders, priorities, and recurring behavior.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, NOT NULL | Unique identifier |
| user_id | UUID | FK(User), NOT NULL, INDEX | Owner of the task |
| title | VARCHAR(255) | NOT NULL | Task title |
| description | TEXT | NULLABLE | Detailed description |
| status | ENUM('pending', 'completed') | NOT NULL, DEFAULT 'pending' | Current status |
| **priority** | ENUM('low', 'medium', 'high') | NOT NULL, DEFAULT 'medium' | **NEW**: Task priority |
| **due_at** | TIMESTAMPTZ | NULLABLE, INDEX | **NEW**: When task is due (UTC) |
| **remind_at** | TIMESTAMPTZ | NULLABLE | **NEW**: When to send reminder (UTC) |
| **recurring_interval** | ENUM('daily', 'weekly', 'monthly', 'yearly') | NULLABLE | **NEW**: Recurrence pattern |
| **parent_task_id** | UUID | FK(Task), NULLABLE | **NEW**: Original task for recurring chain |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Indexes**:
- `idx_task_user_id` on (user_id)
- `idx_task_user_due` on (user_id, due_at) - for filtering by due date
- `idx_task_user_priority` on (user_id, priority) - for priority sorting
- `idx_task_user_status` on (user_id, status) - for status filtering
- `idx_task_parent` on (parent_task_id) - for recurring task chains

**Validation Rules**:
- `due_at` must be in the future when creating (warn if past)
- `remind_at` must be before `due_at` if both set
- `recurring_interval` requires `due_at` to be set
- `parent_task_id` must reference a task owned by same user

**State Transitions**:
```
pending ─────────────────────▶ completed
   │                               │
   │ (if recurring_interval set)   │
   │                               ▼
   │                    [Create new task with
   │                     due_at += interval]
   │                               │
   └───────────────────────────────┘
```

### Tag (NEW)

**Purpose**: Represents a user-defined label for categorizing tasks.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, NOT NULL | Unique identifier |
| user_id | UUID | FK(User), NOT NULL, INDEX | Owner of the tag |
| name | VARCHAR(50) | NOT NULL | Tag name (e.g., "work", "urgent") |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Creation timestamp |

**Indexes**:
- `idx_tag_user_id` on (user_id)
- `idx_tag_user_name` UNIQUE on (user_id, name) - prevents duplicate tags per user

**Validation Rules**:
- `name` must be unique per user (enforced by unique index)
- `name` max length 50 characters
- `name` should be lowercase (application-level normalization)

### TaskTag (NEW)

**Purpose**: Junction table for many-to-many relationship between Task and Tag.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| task_id | UUID | FK(Task), NOT NULL | Reference to task |
| tag_id | UUID | FK(Tag), NOT NULL | Reference to tag |

**Indexes**:
- Primary Key on (task_id, tag_id)
- `idx_tasktag_tag_id` on (tag_id) - for reverse lookups

**Validation Rules**:
- Both task and tag must belong to same user (application-level check)
- Deleting a task cascades to TaskTag entries
- Deleting a tag cascades to TaskTag entries

### ProcessedEvent (NEW - Optional)

**Purpose**: Tracks processed Kafka events for idempotency.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, NOT NULL | Unique identifier |
| event_key | VARCHAR(255) | UNIQUE, NOT NULL | Composite key: task_id:event_type:timestamp |
| processed_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | When event was processed |

**Indexes**:
- Primary Key on (id)
- `idx_processed_event_key` UNIQUE on (event_key)

**Retention**:
- Events older than 7 days can be purged (background job)

### AuditLog (NEW - Optional)

**Purpose**: Stores audit trail of all task operations for compliance.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, NOT NULL | Unique identifier |
| user_id | UUID | FK(User), NOT NULL, INDEX | User who performed action |
| event_type | VARCHAR(50) | NOT NULL | Type: task_created, task_updated, etc. |
| entity_type | VARCHAR(50) | NOT NULL | Type: task, tag, etc. |
| entity_id | UUID | NOT NULL | ID of affected entity |
| old_data | JSONB | NULLABLE | Previous state (for updates/deletes) |
| new_data | JSONB | NULLABLE | New state (for creates/updates) |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | When action occurred |

**Indexes**:
- `idx_audit_user_id` on (user_id)
- `idx_audit_entity` on (entity_type, entity_id)
- `idx_audit_created` on (created_at) - for time-based queries

## SQLModel Definitions

### Task Model (Updated)

```python
from enum import Enum
from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4

class TaskStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"

class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class RecurringInterval(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True, nullable=False)
    title: str = Field(max_length=255, nullable=False)
    description: Optional[str] = Field(default=None)
    status: TaskStatus = Field(default=TaskStatus.PENDING)

    # NEW Phase V fields
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM)
    due_at: Optional[datetime] = Field(default=None, index=True)
    remind_at: Optional[datetime] = Field(default=None)
    recurring_interval: Optional[RecurringInterval] = Field(default=None)
    parent_task_id: Optional[UUID] = Field(
        default=None,
        foreign_key="tasks.id"
    )

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    tags: List["Tag"] = Relationship(
        back_populates="tasks",
        link_model="TaskTag"
    )
    parent_task: Optional["Task"] = Relationship(
        sa_relationship_kwargs={"remote_side": "Task.id"}
    )

    class Config:
        use_enum_values = True
```

### Tag Model (NEW)

```python
class Tag(SQLModel, table=True):
    __tablename__ = "tags"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True, nullable=False)
    name: str = Field(max_length=50, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    tasks: List["Task"] = Relationship(
        back_populates="tags",
        link_model="TaskTag"
    )

    class Config:
        # Unique constraint on (user_id, name)
        __table_args__ = (
            UniqueConstraint("user_id", "name", name="uq_tag_user_name"),
        )
```

### TaskTag Model (NEW)

```python
class TaskTag(SQLModel, table=True):
    __tablename__ = "task_tags"

    task_id: UUID = Field(
        foreign_key="tasks.id",
        primary_key=True,
        ondelete="CASCADE"
    )
    tag_id: UUID = Field(
        foreign_key="tags.id",
        primary_key=True,
        ondelete="CASCADE"
    )
```

### ProcessedEvent Model (NEW)

```python
class ProcessedEvent(SQLModel, table=True):
    __tablename__ = "processed_events"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    event_key: str = Field(max_length=255, unique=True, nullable=False)
    processed_at: datetime = Field(default_factory=datetime.utcnow)
```

### AuditLog Model (NEW)

```python
from sqlalchemy.dialects.postgresql import JSONB

class AuditLog(SQLModel, table=True):
    __tablename__ = "audit_logs"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True, nullable=False)
    event_type: str = Field(max_length=50, nullable=False)
    entity_type: str = Field(max_length=50, nullable=False)
    entity_id: UUID = Field(nullable=False)
    old_data: Optional[dict] = Field(default=None, sa_column=Column(JSONB))
    new_data: Optional[dict] = Field(default=None, sa_column=Column(JSONB))
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
```

## Pydantic Schemas

### Task Schemas

```python
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    due_at: Optional[datetime] = None
    remind_at: Optional[datetime] = None
    recurring_interval: Optional[RecurringInterval] = None
    tags: Optional[List[str]] = Field(default_factory=list)

    @validator('remind_at')
    def remind_before_due(cls, v, values):
        if v and values.get('due_at') and v >= values['due_at']:
            raise ValueError('remind_at must be before due_at')
        return v

    @validator('recurring_interval')
    def recurring_requires_due(cls, v, values):
        if v and not values.get('due_at'):
            raise ValueError('recurring_interval requires due_at to be set')
        return v

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_at: Optional[datetime] = None
    remind_at: Optional[datetime] = None
    recurring_interval: Optional[RecurringInterval] = None
    tags: Optional[List[str]] = None

class TaskResponse(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    description: Optional[str]
    status: TaskStatus
    priority: TaskPriority
    due_at: Optional[datetime]
    remind_at: Optional[datetime]
    recurring_interval: Optional[RecurringInterval]
    parent_task_id: Optional[UUID]
    tags: List[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TaskListQuery(BaseModel):
    q: Optional[str] = Field(None, description="Search keyword")
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    tags: Optional[List[str]] = Field(default_factory=list)
    due_before: Optional[datetime] = None
    due_after: Optional[datetime] = None
    sort_by: str = Field("created_at", pattern="^(created_at|due_at|priority|title)$")
    sort_order: str = Field("desc", pattern="^(asc|desc)$")
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
```

### Tag Schemas

```python
class TagCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)

class TagResponse(BaseModel):
    id: UUID
    name: str
    created_at: datetime

    class Config:
        from_attributes = True
```

## Event Schemas

### Kafka Event Schema

```python
from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime
from uuid import UUID

class TaskEventData(BaseModel):
    title: str
    description: Optional[str] = None
    status: str
    priority: str
    tags: List[str] = []
    due_at: Optional[datetime] = None
    remind_at: Optional[datetime] = None
    recurring_interval: Optional[str] = None

class TaskEvent(BaseModel):
    event_type: str  # task_created, task_updated, task_completed, task_deleted
    task_id: UUID
    task_data: Optional[TaskEventData] = None
    user_id: UUID
    timestamp: datetime
    metadata: Optional[dict] = None

class ReminderEvent(BaseModel):
    event_type: str = "reminder_due"
    task_id: UUID
    user_id: UUID
    reminder_message: str
    timestamp: datetime
```

## Migration Script

### Alembic Migration (v5_schema_update.py)

```python
"""Phase V Schema Update

Revision ID: v5_001
Revises: v4_xxx
Create Date: 2026-02-09

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'v5_001'
down_revision = 'v4_xxx'  # Replace with actual previous revision
branch_labels = None
depends_on = None

def upgrade():
    # Add new columns to tasks table
    op.add_column('tasks', sa.Column('priority', sa.Enum('low', 'medium', 'high', name='taskpriority'), nullable=False, server_default='medium'))
    op.add_column('tasks', sa.Column('due_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('tasks', sa.Column('remind_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('tasks', sa.Column('recurring_interval', sa.Enum('daily', 'weekly', 'monthly', 'yearly', name='recurringinterval'), nullable=True))
    op.add_column('tasks', sa.Column('parent_task_id', postgresql.UUID(as_uuid=True), nullable=True))

    # Add foreign key for parent_task_id
    op.create_foreign_key('fk_task_parent', 'tasks', 'tasks', ['parent_task_id'], ['id'])

    # Create indexes
    op.create_index('idx_task_user_due', 'tasks', ['user_id', 'due_at'])
    op.create_index('idx_task_user_priority', 'tasks', ['user_id', 'priority'])
    op.create_index('idx_task_parent', 'tasks', ['parent_task_id'])

    # Create tags table
    op.create_table(
        'tags',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint('user_id', 'name', name='uq_tag_user_name')
    )
    op.create_index('idx_tag_user_id', 'tags', ['user_id'])

    # Create task_tags junction table
    op.create_table(
        'task_tags',
        sa.Column('task_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tasks.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('tag_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True)
    )
    op.create_index('idx_tasktag_tag_id', 'task_tags', ['tag_id'])

    # Create processed_events table (for idempotency)
    op.create_table(
        'processed_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('event_key', sa.String(255), unique=True, nullable=False),
        sa.Column('processed_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )

    # Create audit_logs table (optional)
    op.create_table(
        'audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('event_type', sa.String(50), nullable=False),
        sa.Column('entity_type', sa.String(50), nullable=False),
        sa.Column('entity_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('old_data', postgresql.JSONB, nullable=True),
        sa.Column('new_data', postgresql.JSONB, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )
    op.create_index('idx_audit_user_id', 'audit_logs', ['user_id'])
    op.create_index('idx_audit_entity', 'audit_logs', ['entity_type', 'entity_id'])
    op.create_index('idx_audit_created', 'audit_logs', ['created_at'])

def downgrade():
    # Drop tables
    op.drop_table('audit_logs')
    op.drop_table('processed_events')
    op.drop_table('task_tags')
    op.drop_table('tags')

    # Drop indexes
    op.drop_index('idx_task_parent', 'tasks')
    op.drop_index('idx_task_user_priority', 'tasks')
    op.drop_index('idx_task_user_due', 'tasks')

    # Drop foreign key
    op.drop_constraint('fk_task_parent', 'tasks', type_='foreignkey')

    # Drop columns
    op.drop_column('tasks', 'parent_task_id')
    op.drop_column('tasks', 'recurring_interval')
    op.drop_column('tasks', 'remind_at')
    op.drop_column('tasks', 'due_at')
    op.drop_column('tasks', 'priority')

    # Drop enums
    op.execute('DROP TYPE IF EXISTS recurringinterval')
    op.execute('DROP TYPE IF EXISTS taskpriority')
```

## Query Examples

### Search with Filters and Sort

```sql
-- Search tasks with keyword, priority filter, tag filter, sorted by priority and due date
SELECT t.*, array_agg(tg.name) as tags
FROM tasks t
LEFT JOIN task_tags tt ON t.id = tt.task_id
LEFT JOIN tags tg ON tt.tag_id = tg.id
WHERE t.user_id = :user_id
  AND (t.title ILIKE '%' || :keyword || '%' OR t.description ILIKE '%' || :keyword || '%')
  AND t.priority = :priority
  AND t.status = 'pending'
  AND t.id IN (
    SELECT task_id FROM task_tags
    WHERE tag_id IN (SELECT id FROM tags WHERE name IN (:tag1, :tag2) AND user_id = :user_id)
    GROUP BY task_id
    HAVING COUNT(DISTINCT tag_id) = 2  -- AND logic: must have all tags
  )
GROUP BY t.id
ORDER BY
  CASE t.priority
    WHEN 'high' THEN 3
    WHEN 'medium' THEN 2
    WHEN 'low' THEN 1
  END DESC,
  t.due_at ASC NULLS LAST
LIMIT :page_size OFFSET :offset;
```

### Get User's Tags

```sql
SELECT DISTINCT tg.id, tg.name, COUNT(tt.task_id) as task_count
FROM tags tg
LEFT JOIN task_tags tt ON tg.id = tt.tag_id
WHERE tg.user_id = :user_id
GROUP BY tg.id, tg.name
ORDER BY tg.name;
```

### Find Tasks Due Soon (for reminders)

```sql
SELECT t.*
FROM tasks t
WHERE t.remind_at <= NOW()
  AND t.remind_at > NOW() - INTERVAL '5 minutes'
  AND t.status = 'pending'
ORDER BY t.remind_at;
```

## Data Integrity Constraints

1. **User Isolation**: All queries MUST filter by user_id
2. **Tag Uniqueness**: Tags are unique per user (enforced by unique constraint)
3. **Cascading Deletes**: Deleting task removes TaskTag entries; deleting tag removes TaskTag entries
4. **Referential Integrity**: parent_task_id must reference existing task owned by same user
5. **Temporal Constraints**: remind_at < due_at (application-level validation)
6. **Recurring Constraint**: recurring_interval requires due_at (application-level validation)

