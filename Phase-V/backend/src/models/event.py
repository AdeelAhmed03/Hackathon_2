"""Event schema models for Kafka messages.

T022: Event schema model for Kafka messages.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime
from enum import Enum


class EventType(str, Enum):
    """Event types for task-events topic."""
    TASK_CREATED = "task_created"
    TASK_UPDATED = "task_updated"
    TASK_COMPLETED = "task_completed"
    TASK_DELETED = "task_deleted"
    REMINDER_DUE = "reminder_due"


class TaskEventData(BaseModel):
    """Task data embedded in events."""
    title: str
    description: Optional[str] = None
    priority: str = "medium"
    tags: List[str] = Field(default_factory=list)
    due_at: Optional[str] = None
    remind_at: Optional[str] = None
    recurring_interval: Optional[str] = None
    status: str = "pending"


class TaskEvent(BaseModel):
    """Event schema for task-events topic.

    Published when tasks are created, updated, completed, or deleted.
    """
    event_type: EventType
    task_id: str
    task_data: TaskEventData
    user_id: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

    class Config:
        use_enum_values = True


class ReminderEventData(BaseModel):
    """Reminder data embedded in events."""
    title: str
    due_at: Optional[str] = None
    reminder_message: str


class ReminderEvent(BaseModel):
    """Event schema for reminders topic.

    Published when a reminder is due (triggered by Dapr Jobs API).
    """
    event_type: str = "reminder_due"
    task_id: str
    task_data: ReminderEventData
    user_id: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class TaskUpdateEvent(BaseModel):
    """Event schema for task-updates topic (real-time sync).

    Published on any task mutation for real-time updates.
    """
    event_type: str
    task_id: str
    task_data: dict[str, Any]
    user_id: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
