"""Main FastAPI application entry point.

Phase V: Event-driven architecture with Dapr integration.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Load environment variables first
load_dotenv()

from .database.engine import create_tables
from .api import router as api_router
from .api.dapr_subscriptions import router as dapr_router
from .api.jobs_callback import router as jobs_router
from .middleware.auth import security
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("todo-backend")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("Starting Todo Backend (Phase V)...")
    create_tables()
    logger.info("Database tables created successfully!")
    yield
    logger.info("Shutting down Todo Backend...")


# Create FastAPI app
app = FastAPI(
    title="Todo API",
    description="Event-driven todo application API with Dapr integration",
    version="5.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# Include Dapr subscription routes (at root level for Dapr discovery)
app.include_router(dapr_router)

# Include Jobs callback routes
app.include_router(jobs_router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Todo API is running!", "version": "5.0.0"}


@app.get("/health")
async def health_check():
    """Health check endpoint for Kubernetes probes."""
    return {"status": "healthy", "service": "todo-backend"}


if __name__ == "__main__":
    # Run with uvicorn for development
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True
    )