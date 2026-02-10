"""Task completed event handler.

T049: Process task_completed events for recurring tasks.
"""

import logging
from typing import Any

logger = logging.getLogger("recurring-service.handlers.task_completed")


async def process_task_completed(
    user_id: str,
    task_id: str,
    task_data: dict[str, Any],
    recurring_interval: str
) -> None:
    """Process a task_completed event and spawn next recurring instance.

    Args:
        user_id: The user who owns the task
        task_id: The completed task ID
        task_data: Task information including title, priority, tags, due_at
        recurring_interval: The recurrence interval (daily, weekly, monthly, yearly)
    """
    logger.info(
        f"Processing completed recurring task: {task_id} "
        f"(interval: {recurring_interval})"
    )

    # Import spawner service
    from src.services.task_spawner import spawn_next_task

    # Spawn the next recurring task instance
    new_task_id = await spawn_next_task(
        user_id=user_id,
        parent_task_id=task_id,
        task_data=task_data,
        recurring_interval=recurring_interval
    )

    if new_task_id:
        logger.info(
            f"Spawned next recurring task {new_task_id} from parent {task_id}"
        )
    else:
        logger.warning(f"Failed to spawn next task for parent {task_id}")
