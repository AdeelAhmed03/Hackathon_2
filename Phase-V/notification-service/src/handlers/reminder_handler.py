"""Reminder event handler.

T065: Process reminder events and send notifications.
"""

import logging
from typing import Any

logger = logging.getLogger("notification-service.handlers.reminder")


async def process_reminder(
    user_id: str,
    task_id: str,
    task_data: dict[str, Any]
) -> None:
    """Process a reminder event and send notifications.

    Args:
        user_id: The user to notify
        task_id: The task that triggered the reminder
        task_data: Task information including title, due_at, reminder_message
    """
    title = task_data.get("title", "Unknown Task")
    due_at = task_data.get("due_at")
    message = task_data.get("reminder_message", f"Task '{title}' is due!")

    logger.info(f"Processing reminder for user {user_id}, task {task_id}")

    # TODO: Implement actual notification sending via email/push
    # For now, log the notification
    from src.services.email_sender import send_email_notification
    from src.services.push_sender import send_push_notification

    # Try to send email notification
    try:
        await send_email_notification(
            user_id=user_id,
            subject=f"Reminder: {title}",
            body=message
        )
        logger.info(f"Email notification sent for task {task_id}")
    except Exception as e:
        logger.warning(f"Failed to send email notification: {e}")

    # Try to send push notification
    try:
        await send_push_notification(
            user_id=user_id,
            title="Task Reminder",
            body=message,
            data={"task_id": task_id}
        )
        logger.info(f"Push notification sent for task {task_id}")
    except Exception as e:
        logger.warning(f"Failed to send push notification: {e}")

    logger.info(f"Reminder processing complete for task {task_id}")
