"""Dapr Pub/Sub Subscription Endpoints.

T028: Dapr subscription endpoint /dapr/subscribe
T114: Task-updates subscription endpoint
"""

import logging
from typing import List
from fastapi import APIRouter, Request

logger = logging.getLogger(__name__)

router = APIRouter()

# Dapr configuration
PUBSUB_NAME = "kafka-pubsub"


@router.get("/dapr/subscribe")
async def subscribe() -> List[dict]:
    """Dapr subscription discovery endpoint.

    T028: Create Dapr subscription endpoint /dapr/subscribe.

    Dapr sidecar calls this endpoint on startup to discover
    which topics the application wants to subscribe to.
    """
    subscriptions = [
        {
            "pubsubname": PUBSUB_NAME,
            "topic": "task-updates",
            "route": "/events/task-updates"
        }
    ]
    logger.info(f"Dapr subscriptions registered: {subscriptions}")
    return subscriptions


@router.post("/events/task-updates")
async def handle_task_update_event(request: Request) -> dict:
    """Handle task update events for real-time sync.

    T114: Create task-updates subscription endpoint for backend.

    This endpoint receives task update events from other services
    and can be used for cache invalidation or real-time updates.
    """
    try:
        event = await request.json()
        logger.info(f"Received task-update event: {event.get('event_type')}")

        # Extract event data
        event_type = event.get("event_type", "unknown")
        task_id = event.get("task_id")
        user_id = event.get("user_id")

        # Process the update (cache invalidation, WebSocket broadcast, etc.)
        # For now, just log it
        logger.info(
            f"Task update: type={event_type}, task={task_id}, user={user_id}"
        )

        return {"status": "SUCCESS"}

    except Exception as e:
        logger.exception(f"Error processing task-update event: {e}")
        return {"status": "RETRY", "reason": str(e)}
