"""Recurring Service - Dapr Pub/Sub Consumer for Task Events.

T009: FastAPI application scaffold for recurring-service.
T166: Enhanced with structured logging.
Subscribes to the 'task-events' topic via Dapr Pub/Sub and spawns
next instances of recurring tasks when they are completed.
"""

import logging
import os
import json
from contextlib import asynccontextmanager
from typing import Any
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware


class StructuredLogFormatter(logging.Formatter):
    """JSON structured log formatter for cloud-native observability."""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "service": "recurring-service"
        }

        # Add extra fields if present
        if hasattr(record, "task_id"):
            log_data["task_id"] = record.task_id
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        if hasattr(record, "event_type"):
            log_data["event_type"] = record.event_type
        if hasattr(record, "recurring_interval"):
            log_data["recurring_interval"] = record.recurring_interval
        if hasattr(record, "processing_time_ms"):
            log_data["processing_time_ms"] = record.processing_time_ms
        if hasattr(record, "new_task_id"):
            log_data["new_task_id"] = record.new_task_id

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


# Configure structured logging
def setup_logging():
    """Configure structured JSON logging for production."""
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    use_json = os.getenv("LOG_FORMAT", "json").lower() == "json"

    handler = logging.StreamHandler()

    if use_json:
        handler.setFormatter(StructuredLogFormatter())
    else:
        handler.setFormatter(logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        ))

    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        handlers=[handler]
    )


setup_logging()
logger = logging.getLogger("recurring-service")

# Configuration
DAPR_HTTP_PORT = int(os.getenv("DAPR_HTTP_PORT", "3500"))
PUBSUB_NAME = os.getenv("PUBSUB_NAME", "kafka-pubsub")
TOPIC_NAME = "task-events"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("Starting recurring-service...")
    logger.info(f"Subscribing to topic: {TOPIC_NAME} via pubsub: {PUBSUB_NAME}")
    yield
    logger.info("Shutting down recurring-service...")


app = FastAPI(
    title="Recurring Service",
    description="Event-driven service for spawning recurring task instances",
    version="5.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint for Kubernetes probes."""
    return {"status": "healthy", "service": "recurring-service"}


@app.get("/dapr/subscribe")
async def subscribe() -> list[dict[str, str]]:
    """Dapr subscription discovery endpoint.

    T048: Define subscription to task-events topic.
    Dapr sidecar calls this endpoint to discover subscriptions.
    """
    subscriptions = [
        {
            "pubsubname": PUBSUB_NAME,
            "topic": TOPIC_NAME,
            "route": "/events/task-events"
        }
    ]
    logger.info(f"Dapr subscriptions: {subscriptions}")
    return subscriptions


@app.post("/events/task-events")
async def handle_task_event(request: Request) -> dict[str, str]:
    """Handle task events from Kafka via Dapr Pub/Sub.

    T049: Process task_completed events for recurring tasks.

    Event schema:
    {
        "event_type": "task_created | task_updated | task_completed | task_deleted",
        "task_id": "uuid",
        "task_data": {
            "title": "string",
            "priority": "low | medium | high",
            "tags": ["string"],
            "due_at": "ISO8601",
            "recurring_interval": "daily | weekly | monthly | yearly | null"
        },
        "user_id": "uuid",
        "timestamp": "ISO8601"
    }
    """
    import time
    start_time = time.time()

    try:
        event = await request.json()

        # Extract event data first for structured logging
        event_type = event.get("event_type", "unknown")
        task_id = event.get("task_id")
        user_id = event.get("user_id")
        task_data = event.get("task_data", {})

        # Create log context
        log_extra = {
            "task_id": task_id,
            "user_id": user_id,
            "event_type": event_type
        }

        logger.info(
            "Received task event",
            extra=log_extra
        )

        # Only process task_completed events
        if event_type != "task_completed":
            logger.debug(
                f"Ignoring event type: {event_type}",
                extra=log_extra
            )
            return {"status": "SUCCESS", "reason": f"Event type {event_type} not handled"}

        if not task_id or not user_id:
            logger.error(
                "Missing required fields in event",
                extra={**log_extra, "missing_fields": [
                    f for f in ["task_id", "user_id"]
                    if not event.get(f)
                ]}
            )
            return {"status": "RETRY", "reason": "Missing required fields"}

        # Check if task is recurring
        recurring_interval = task_data.get("recurring_interval")
        log_extra["recurring_interval"] = recurring_interval

        if not recurring_interval:
            logger.info(
                "Task is not recurring, skipping spawn",
                extra=log_extra
            )
            return {"status": "SUCCESS", "reason": "Task is not recurring"}

        logger.info(
            f"Processing recurring task completion: {recurring_interval}",
            extra=log_extra
        )

        # Import handlers when needed (lazy import to avoid circular deps)
        from src.handlers.task_completed_handler import process_task_completed
        result = await process_task_completed(
            user_id=user_id,
            task_id=task_id,
            task_data=task_data,
            recurring_interval=recurring_interval
        )

        processing_time_ms = (time.time() - start_time) * 1000
        logger.info(
            "Recurring task spawn completed",
            extra={
                **log_extra,
                "processing_time_ms": round(processing_time_ms, 2),
                "new_task_id": result.get("new_task_id") if result else None
            }
        )

        return {"status": "SUCCESS"}

    except Exception as e:
        processing_time_ms = (time.time() - start_time) * 1000
        logger.exception(
            f"Error processing task event: {e}",
            extra={
                "task_id": locals().get("task_id"),
                "user_id": locals().get("user_id"),
                "processing_time_ms": round(processing_time_ms, 2),
                "error_type": type(e).__name__
            }
        )
        # Return RETRY to have Dapr retry the message
        return {"status": "RETRY", "reason": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
