"""Dapr Jobs API Callback Endpoint.

T032: Jobs API callback endpoint /jobs/callback
T062: Handler to publish reminder_due event
"""

import logging
import json
from fastapi import APIRouter, Request
from ..services.event_publisher import publish_reminder_event

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/jobs/callback")
async def jobs_callback(request: Request) -> dict:
    """Handle Dapr Jobs API callback when a scheduled job fires.

    T032: Create Jobs API callback endpoint /jobs/callback.
    T062: Implement /jobs/callback handler to publish reminder_due event.

    When a reminder job's dueTime is reached, Dapr calls this endpoint
    with the job data. We then publish a reminder_due event to Kafka.
    """
    try:
        body = await request.body()
        logger.info(f"Jobs callback received: {body}")

        # Parse the job data
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            # Try to extract from Dapr's protobuf wrapper
            data = {"raw": body.decode("utf-8")}

        # Extract job data - Dapr wraps it in a "value" field
        job_data = data.get("value", data)

        # Handle nested value structure from Dapr
        if isinstance(job_data, str):
            try:
                job_data = json.loads(job_data)
            except json.JSONDecodeError:
                pass

        task_id = job_data.get("task_id")
        user_id = job_data.get("user_id")
        title = job_data.get("title", "Task Reminder")
        reminder_message = job_data.get("reminder_message")

        if not task_id or not user_id:
            logger.error(f"Missing task_id or user_id in job data: {job_data}")
            return {"status": "DROP", "reason": "Missing required fields"}

        logger.info(
            f"Processing reminder for task {task_id}, user {user_id}"
        )

        # Publish reminder_due event to Kafka
        success = await publish_reminder_event(
            task_id=int(task_id),
            user_id=int(user_id),
            title=title,
            reminder_message=reminder_message
        )

        if success:
            logger.info(f"Published reminder_due event for task {task_id}")
            return {"status": "SUCCESS"}
        else:
            logger.error(f"Failed to publish reminder event for task {task_id}")
            return {"status": "RETRY", "reason": "Failed to publish event"}

    except Exception as e:
        logger.exception(f"Error processing jobs callback: {e}")
        return {"status": "RETRY", "reason": str(e)}


@router.get("/jobs/callback")
async def jobs_callback_health() -> dict:
    """Health check for jobs callback endpoint."""
    return {"status": "healthy", "endpoint": "/jobs/callback"}
