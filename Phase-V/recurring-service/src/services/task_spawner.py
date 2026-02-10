"""Task spawner service for recurring tasks.

T050-T052: Create next recurring task instance with proper interval calculation.
"""

import logging
import os
import hashlib
from datetime import datetime, timedelta
from typing import Any, Optional
from dateutil.relativedelta import relativedelta
import httpx

logger = logging.getLogger("recurring-service.services.task_spawner")

# Configuration
DAPR_HTTP_PORT = int(os.getenv("DAPR_HTTP_PORT", "3500"))
BACKEND_APP_ID = os.getenv("BACKEND_APP_ID", "todo-backend")

# Idempotency key cache (in production, use Redis or similar)
_processed_events: set[str] = set()


def calculate_next_due_date(
    current_due_date: Optional[str],
    recurring_interval: str
) -> datetime:
    """Calculate the next due date based on recurring interval.

    T052: Implement interval calculation logic.

    Args:
        current_due_date: ISO8601 string of current due date, or None
        recurring_interval: One of 'daily', 'weekly', 'monthly', 'yearly'

    Returns:
        The next due date as a datetime object
    """
    if current_due_date:
        try:
            base_date = datetime.fromisoformat(current_due_date.replace("Z", "+00:00"))
        except ValueError:
            base_date = datetime.utcnow()
    else:
        base_date = datetime.utcnow()

    interval_map = {
        "daily": timedelta(days=1),
        "weekly": timedelta(weeks=1),
        "monthly": relativedelta(months=1),
        "yearly": relativedelta(years=1)
    }

    delta = interval_map.get(recurring_interval, timedelta(days=1))

    if isinstance(delta, timedelta):
        return base_date + delta
    else:
        return base_date + delta


def generate_idempotency_key(task_id: str, user_id: str, timestamp: str) -> str:
    """Generate a unique idempotency key for event deduplication.

    T051: Implement idempotency check using event key deduplication.
    """
    data = f"{task_id}:{user_id}:{timestamp}"
    return hashlib.sha256(data.encode()).hexdigest()


def check_idempotency(key: str) -> bool:
    """Check if this event has already been processed.

    T051: Idempotency check to prevent duplicate task spawning.

    Returns:
        True if event was already processed (should skip), False otherwise
    """
    if key in _processed_events:
        logger.warning(f"Duplicate event detected, skipping: {key}")
        return True

    # Add to processed set (in production, use Redis with TTL)
    _processed_events.add(key)

    # Limit memory usage (simple cleanup)
    if len(_processed_events) > 10000:
        # Remove oldest half
        items = list(_processed_events)
        _processed_events.clear()
        _processed_events.update(items[5000:])

    return False


async def spawn_next_task(
    user_id: str,
    parent_task_id: str,
    task_data: dict[str, Any],
    recurring_interval: str
) -> Optional[str]:
    """Spawn the next instance of a recurring task.

    T050: Create next recurring instance via backend API.

    Args:
        user_id: The user who owns the task
        parent_task_id: The completed task ID (becomes parent)
        task_data: Original task data
        recurring_interval: The recurrence interval

    Returns:
        The new task ID if created, None on failure
    """
    # Generate idempotency key
    timestamp = task_data.get("timestamp", datetime.utcnow().isoformat())
    idempotency_key = generate_idempotency_key(parent_task_id, user_id, timestamp)

    # Check for duplicate processing
    if check_idempotency(idempotency_key):
        return None

    # Calculate next due date
    current_due = task_data.get("due_at")
    next_due = calculate_next_due_date(current_due, recurring_interval)

    # Prepare new task payload
    new_task = {
        "title": task_data.get("title", "Recurring Task"),
        "description": task_data.get("description"),
        "priority": task_data.get("priority", "medium"),
        "tags": task_data.get("tags", []),
        "due_at": next_due.isoformat(),
        "recurring_interval": recurring_interval,
        "parent_task_id": parent_task_id
    }

    logger.info(f"Creating next recurring task: {new_task}")

    # Call backend via Dapr service invocation
    try:
        url = f"http://localhost:{DAPR_HTTP_PORT}/v1.0/invoke/{BACKEND_APP_ID}/method/api/v1/tasks"

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json=new_task,
                headers={
                    "Content-Type": "application/json",
                    "X-User-Id": user_id,  # Pass user context
                    "X-Idempotency-Key": idempotency_key
                },
                timeout=30.0
            )

            if response.status_code in (200, 201):
                result = response.json()
                new_task_id = result.get("id") or result.get("task_id")
                logger.info(f"Successfully created recurring task: {new_task_id}")
                return str(new_task_id) if new_task_id else None
            else:
                logger.error(
                    f"Failed to create task: {response.status_code} - {response.text}"
                )
                return None

    except httpx.RequestError as e:
        logger.exception(f"HTTP error creating recurring task: {e}")
        return None
    except Exception as e:
        logger.exception(f"Unexpected error creating recurring task: {e}")
        return None
