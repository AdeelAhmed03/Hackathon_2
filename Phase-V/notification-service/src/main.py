"""Notification Service - Dapr Pub/Sub Consumer for Reminders.

T006: FastAPI application scaffold for notification-service.
T165: Enhanced with structured logging.
Subscribes to the 'reminders' topic via Dapr Pub/Sub and sends notifications.
"""

import logging
import os
import json
from contextlib import asynccontextmanager
from typing import Any
from datetime import datetime

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware


class StructuredLogFormatter(logging.Formatter):
    """JSON structured log formatter for cloud-native observability."""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "service": "notification-service"
        }

        # Add extra fields if present
        if hasattr(record, "task_id"):
            log_data["task_id"] = record.task_id
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        if hasattr(record, "event_type"):
            log_data["event_type"] = record.event_type
        if hasattr(record, "processing_time_ms"):
            log_data["processing_time_ms"] = record.processing_time_ms

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
logger = logging.getLogger("notification-service")

# Configuration
DAPR_HTTP_PORT = int(os.getenv("DAPR_HTTP_PORT", "3500"))
PUBSUB_NAME = os.getenv("PUBSUB_NAME", "kafka-pubsub")
TOPIC_NAME = "reminders"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("Starting notification-service...")
    logger.info(f"Subscribing to topic: {TOPIC_NAME} via pubsub: {PUBSUB_NAME}")
    yield
    logger.info("Shutting down notification-service...")


app = FastAPI(
    title="Notification Service",
    description="Event-driven notification service for Todo reminders",
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
    return {"status": "healthy", "service": "notification-service"}


@app.get("/dapr/subscribe")
async def subscribe() -> list[dict[str, str]]:
    """Dapr subscription discovery endpoint.

    T064: Define subscription to reminders topic.
    Dapr sidecar calls this endpoint to discover subscriptions.
    """
    subscriptions = [
        {
            "pubsubname": PUBSUB_NAME,
            "topic": TOPIC_NAME,
            "route": "/events/reminders"
        }
    ]
    logger.info(f"Dapr subscriptions: {subscriptions}")
    return subscriptions


@app.post("/events/reminders")
async def handle_reminder_event(request: Request) -> dict[str, str]:
    """Handle reminder events from Kafka via Dapr Pub/Sub.

    T065: Process reminder_due events and trigger notifications.

    Event schema:
    {
        "event_type": "reminder_due",
        "task_id": "uuid",
        "task_data": {
            "title": "string",
            "due_at": "ISO8601",
            "reminder_message": "string"
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

        # Create log adapter with context
        log_extra = {
            "task_id": task_id,
            "user_id": user_id,
            "event_type": event_type
        }

        logger.info(
            "Received reminder event",
            extra=log_extra
        )

        if event_type != "reminder_due":
            logger.warning(
                f"Unexpected event type received: {event_type}",
                extra=log_extra
            )
            return {"status": "IGNORED", "reason": f"Unexpected event type: {event_type}"}

        if not task_id or not user_id:
            logger.error(
                "Missing required fields in event",
                extra={**log_extra, "missing_fields": [
                    f for f in ["task_id", "user_id"]
                    if not event.get(f)
                ]}
            )
            return {"status": "RETRY", "reason": "Missing required fields"}

        # Extract notification details
        title = task_data.get("title", "Unknown Task")
        due_at = task_data.get("due_at", "Unknown")
        message = task_data.get("reminder_message", f"Task '{title}' is due!")

        logger.info(
            f"Processing reminder notification: {message}",
            extra={**log_extra, "task_title": title, "due_at": due_at}
        )

        # Import handlers when needed (lazy import to avoid circular deps)
        from src.handlers.reminder_handler import process_reminder
        await process_reminder(user_id=user_id, task_id=task_id, task_data=task_data)

        processing_time_ms = (time.time() - start_time) * 1000
        logger.info(
            "Reminder processed successfully",
            extra={**log_extra, "processing_time_ms": round(processing_time_ms, 2)}
        )

        return {"status": "SUCCESS"}

    except Exception as e:
        processing_time_ms = (time.time() - start_time) * 1000
        logger.exception(
            f"Error processing reminder event: {e}",
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
    uvicorn.run(app, host="0.0.0.0", port=8001)
