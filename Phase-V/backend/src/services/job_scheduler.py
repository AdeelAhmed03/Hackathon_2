"""Dapr Jobs API Scheduler Service.

T029-T031: Job scheduling via Dapr Jobs API for exact-time reminders.
"""

import logging
import os
from datetime import datetime
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

# Dapr configuration
DAPR_HTTP_PORT = int(os.getenv("DAPR_HTTP_PORT", "3500"))


async def schedule_reminder_job(
    task_id: int,
    user_id: int,
    remind_at: datetime,
    title: str,
    reminder_message: Optional[str] = None
) -> bool:
    """Schedule reminder via Dapr Jobs API.

    T030: Implement schedule_reminder_job() for exact-time scheduling.

    Args:
        task_id: The task ID
        user_id: The user ID
        remind_at: The exact time to trigger the reminder
        title: The task title
        reminder_message: Optional custom reminder message

    Returns:
        True if scheduled successfully, False otherwise
    """
    job_name = f"reminder-{task_id}"
    url = f"http://localhost:{DAPR_HTTP_PORT}/v1.0-alpha1/jobs/{job_name}"

    # Format dueTime as ISO8601 with timezone
    if remind_at.tzinfo is None:
        # Assume UTC if no timezone
        due_time = remind_at.isoformat() + "Z"
    else:
        due_time = remind_at.isoformat()

    payload = {
        "dueTime": due_time,
        "data": {
            "@type": "type.googleapis.com/google.protobuf.StringValue",
            "value": {
                "task_id": str(task_id),
                "user_id": str(user_id),
                "title": title,
                "reminder_message": reminder_message or f"Reminder: {title} is due!"
            }
        }
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10.0
            )
            response.raise_for_status()
            logger.info(f"Scheduled reminder job {job_name} for {due_time}")
            return True
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error scheduling job {job_name}: {e.response.status_code}")
        return False
    except httpx.RequestError as e:
        logger.error(f"Request error scheduling job {job_name}: {e}")
        return False
    except Exception as e:
        logger.exception(f"Unexpected error scheduling job {job_name}: {e}")
        return False


async def cancel_reminder_job(task_id: int) -> bool:
    """Cancel a scheduled reminder job.

    T031: Implement cancel_reminder_job() for job cancellation.

    Args:
        task_id: The task ID whose reminder should be cancelled

    Returns:
        True if cancelled successfully (or job didn't exist), False on error
    """
    job_name = f"reminder-{task_id}"
    url = f"http://localhost:{DAPR_HTTP_PORT}/v1.0-alpha1/jobs/{job_name}"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(url, timeout=10.0)

            # 204 No Content = deleted, 404 = didn't exist (both are OK)
            if response.status_code in (204, 404):
                logger.info(f"Cancelled reminder job {job_name}")
                return True

            response.raise_for_status()
            return True
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            # Job doesn't exist, which is fine
            logger.info(f"Reminder job {job_name} not found (already cancelled or never existed)")
            return True
        logger.error(f"HTTP error cancelling job {job_name}: {e.response.status_code}")
        return False
    except httpx.RequestError as e:
        logger.error(f"Request error cancelling job {job_name}: {e}")
        return False
    except Exception as e:
        logger.exception(f"Unexpected error cancelling job {job_name}: {e}")
        return False


async def reschedule_reminder_job(
    task_id: int,
    user_id: int,
    remind_at: datetime,
    title: str,
    reminder_message: Optional[str] = None
) -> bool:
    """Reschedule a reminder by cancelling and creating a new one.

    Args:
        task_id: The task ID
        user_id: The user ID
        remind_at: The new remind time
        title: The task title
        reminder_message: Optional custom reminder message

    Returns:
        True if rescheduled successfully
    """
    # Cancel existing job first (ignore failure)
    await cancel_reminder_job(task_id)

    # Schedule new job
    return await schedule_reminder_job(
        task_id=task_id,
        user_id=user_id,
        remind_at=remind_at,
        title=title,
        reminder_message=reminder_message
    )


async def get_job_status(task_id: int) -> Optional[dict]:
    """Get the status of a scheduled reminder job.

    Args:
        task_id: The task ID

    Returns:
        Job status dict if exists, None otherwise
    """
    job_name = f"reminder-{task_id}"
    url = f"http://localhost:{DAPR_HTTP_PORT}/v1.0-alpha1/jobs/{job_name}"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10.0)
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"Error getting job status for {job_name}: {e}")
        return None
