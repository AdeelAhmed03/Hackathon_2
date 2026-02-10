"""Dapr Event Publisher Service.

T025-T027: Event publishing via Dapr Pub/Sub HTTP API.
T164, T167: Enhanced with structured logging and retry logic.
"""

import asyncio
import logging
import os
import json
from datetime import datetime
from typing import Optional, List, Any

import httpx

from ..models.event import (
    TaskEvent,
    TaskEventData,
    EventType,
    ReminderEvent,
    ReminderEventData,
    TaskUpdateEvent
)
from ..models.task import Task

# Configure structured logger
logger = logging.getLogger("event_publisher")

# Dapr configuration
DAPR_HTTP_PORT = int(os.getenv("DAPR_HTTP_PORT", "3500"))
PUBSUB_NAME = os.getenv("PUBSUB_NAME", "kafka-pubsub")

# Topics
TASK_EVENTS_TOPIC = "task-events"
REMINDERS_TOPIC = "reminders"
TASK_UPDATES_TOPIC = "task-updates"

# Retry configuration
MAX_RETRIES = int(os.getenv("EVENT_PUBLISHER_MAX_RETRIES", "3"))
INITIAL_BACKOFF_SECONDS = float(os.getenv("EVENT_PUBLISHER_INITIAL_BACKOFF", "0.5"))
MAX_BACKOFF_SECONDS = float(os.getenv("EVENT_PUBLISHER_MAX_BACKOFF", "10.0"))


def _log_event_context(event: dict, topic: str, extra: dict = None) -> dict:
    """Create structured log context for events.

    T164: Structured logging format.
    """
    context = {
        "topic": topic,
        "event_type": event.get("event_type"),
        "task_id": event.get("task_id"),
        "user_id": event.get("user_id"),
        "timestamp": event.get("timestamp"),
    }
    if extra:
        context.update(extra)
    return context


async def _publish_event_with_retry(topic: str, event: dict) -> bool:
    """Publish event to Kafka via Dapr Pub/Sub with exponential backoff retry.

    T167: Retry logic with exponential backoff for Kafka unavailability.

    Args:
        topic: The Kafka topic to publish to
        event: The event payload as a dictionary

    Returns:
        True if published successfully, False otherwise
    """
    url = f"http://localhost:{DAPR_HTTP_PORT}/v1.0/publish/{PUBSUB_NAME}/{topic}"
    log_ctx = _log_event_context(event, topic)

    for attempt in range(MAX_RETRIES):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json=event,
                    headers={"Content-Type": "application/json"},
                    timeout=10.0
                )
                response.raise_for_status()

                logger.info(
                    "Event published successfully",
                    extra={**log_ctx, "attempt": attempt + 1}
                )
                return True

        except httpx.HTTPStatusError as e:
            log_ctx["http_status"] = e.response.status_code
            log_ctx["attempt"] = attempt + 1

            # Don't retry on 4xx client errors (except 429 Too Many Requests)
            if 400 <= e.response.status_code < 500 and e.response.status_code != 429:
                logger.error(
                    f"Client error publishing event - not retrying",
                    extra=log_ctx
                )
                return False

            logger.warning(
                f"HTTP error publishing event - will retry",
                extra=log_ctx
            )

        except httpx.RequestError as e:
            log_ctx["error_type"] = type(e).__name__
            log_ctx["error_message"] = str(e)
            log_ctx["attempt"] = attempt + 1

            logger.warning(
                f"Request error publishing event - will retry",
                extra=log_ctx
            )

        except Exception as e:
            log_ctx["error_type"] = type(e).__name__
            log_ctx["error_message"] = str(e)
            log_ctx["attempt"] = attempt + 1

            logger.exception(
                f"Unexpected error publishing event",
                extra=log_ctx
            )
            return False

        # Calculate backoff with exponential increase and jitter
        if attempt < MAX_RETRIES - 1:
            backoff = min(
                INITIAL_BACKOFF_SECONDS * (2 ** attempt),
                MAX_BACKOFF_SECONDS
            )
            # Add small random jitter (10%)
            import random
            backoff += random.uniform(0, backoff * 0.1)

            logger.debug(
                f"Waiting {backoff:.2f}s before retry",
                extra={**log_ctx, "backoff_seconds": backoff}
            )
            await asyncio.sleep(backoff)

    # All retries exhausted
    logger.error(
        f"Failed to publish event after {MAX_RETRIES} attempts",
        extra={**log_ctx, "max_retries": MAX_RETRIES}
    )
    return False


async def _publish_event(topic: str, event: dict) -> bool:
    """Publish event to Kafka via Dapr Pub/Sub.

    Wrapper around _publish_event_with_retry for backward compatibility.

    Args:
        topic: The Kafka topic to publish to
        event: The event payload as a dictionary

    Returns:
        True if published successfully, False otherwise
    """
    return await _publish_event_with_retry(topic, event)


def _task_to_event_data(task: Task, tags: Optional[List[str]] = None) -> TaskEventData:
    """Convert Task model to TaskEventData."""
    return TaskEventData(
        title=task.title,
        description=task.description,
        priority=task.priority.value if hasattr(task.priority, 'value') else str(task.priority),
        tags=tags or [],
        due_at=task.due_datetime.isoformat() if task.due_datetime else None,
        remind_at=getattr(task, 'remind_at', None),
        recurring_interval=task.recurrence_rule.value if task.recurrence_rule else None,
        status=task.status.value if hasattr(task.status, 'value') else str(task.status)
    )


async def publish_task_event(
    event_type: EventType,
    task: Task,
    user_id: int,
    tags: Optional[List[str]] = None
) -> bool:
    """Publish task event to task-events topic.

    T026: Implement publish_task_event() for task-events topic.

    Args:
        event_type: The type of task event
        task: The task object
        user_id: The user ID who owns the task
        tags: Optional list of tag names

    Returns:
        True if published successfully
    """
    event = TaskEvent(
        event_type=event_type,
        task_id=str(task.id),
        task_data=_task_to_event_data(task, tags),
        user_id=str(user_id),
        timestamp=datetime.utcnow().isoformat()
    )

    return await _publish_event(TASK_EVENTS_TOPIC, event.model_dump())


async def publish_reminder_event(
    task_id: int,
    user_id: int,
    title: str,
    due_at: Optional[datetime] = None,
    reminder_message: Optional[str] = None
) -> bool:
    """Publish reminder event to reminders topic.

    T027: Implement publish_reminder_event() for reminders topic.

    Args:
        task_id: The task ID
        user_id: The user ID
        title: The task title
        due_at: Optional due datetime
        reminder_message: Optional custom reminder message

    Returns:
        True if published successfully
    """
    event = ReminderEvent(
        event_type="reminder_due",
        task_id=str(task_id),
        task_data=ReminderEventData(
            title=title,
            due_at=due_at.isoformat() if due_at else None,
            reminder_message=reminder_message or f"Reminder: {title} is due!"
        ),
        user_id=str(user_id),
        timestamp=datetime.utcnow().isoformat()
    )

    return await _publish_event(REMINDERS_TOPIC, event.model_dump())


async def publish_task_update_event(
    event_type: str,
    task_id: int,
    user_id: int,
    task_data: dict[str, Any]
) -> bool:
    """Publish task update event for real-time sync.

    T113: Add publish to task-updates topic on all mutations.

    Args:
        event_type: The type of update
        task_id: The task ID
        user_id: The user ID
        task_data: The task data to sync

    Returns:
        True if published successfully
    """
    event = TaskUpdateEvent(
        event_type=event_type,
        task_id=str(task_id),
        task_data=task_data,
        user_id=str(user_id),
        timestamp=datetime.utcnow().isoformat()
    )

    return await _publish_event(TASK_UPDATES_TOPIC, event.model_dump())


# Convenience functions for specific event types
async def publish_task_created(task: Task, user_id: int, tags: Optional[List[str]] = None) -> bool:
    """Publish task_created event."""
    return await publish_task_event(EventType.TASK_CREATED, task, user_id, tags)


async def publish_task_updated(task: Task, user_id: int, tags: Optional[List[str]] = None) -> bool:
    """Publish task_updated event."""
    return await publish_task_event(EventType.TASK_UPDATED, task, user_id, tags)


async def publish_task_completed(task: Task, user_id: int, tags: Optional[List[str]] = None) -> bool:
    """Publish task_completed event."""
    return await publish_task_event(EventType.TASK_COMPLETED, task, user_id, tags)


async def publish_task_deleted(task: Task, user_id: int, tags: Optional[List[str]] = None) -> bool:
    """Publish task_deleted event."""
    return await publish_task_event(EventType.TASK_DELETED, task, user_id, tags)
