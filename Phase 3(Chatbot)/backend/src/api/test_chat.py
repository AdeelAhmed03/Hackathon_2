"""Test chat endpoint without database dependency."""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional
import os

router = APIRouter()


class TestChatRequest(BaseModel):
    """Test request schema."""
    message: str


class TestChatResponse(BaseModel):
    """Test response schema."""
    message: str
    cohere_available: bool
    api_key_configured: bool


@router.post("/test-chat")
async def test_chat_endpoint(request: TestChatRequest):
    """
    Test endpoint to verify Cohere integration without database.

    This endpoint checks:
    1. Cohere API key is configured
    2. Cohere SDK can be imported
    3. Basic chat call works
    """
    # Check API key
    api_key = os.getenv("COHERE_API_KEY")
    if not api_key:
        return TestChatResponse(
            message="COHERE_API_KEY not configured",
            cohere_available=False,
            api_key_configured=False
        )

    # Try to import cohere
    try:
        import cohere
    except ImportError:
        return TestChatResponse(
            message="Cohere SDK not installed",
            cohere_available=False,
            api_key_configured=True
        )

    # Try a simple chat call
    try:
        client = cohere.Client(api_key=api_key)
        response = client.chat(
            model="command-nightly",
            message=request.message,
            preamble="You are a helpful assistant."
        )

        return TestChatResponse(
            message=f"Cohere response: {response.text}",
            cohere_available=True,
            api_key_configured=True
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Cohere API error: {str(e)}"
        )


@router.get("/test-chat/status")
async def test_chat_status():
    """Check Cohere configuration status."""
    api_key = os.getenv("COHERE_API_KEY")

    try:
        import cohere
        cohere_installed = True
    except ImportError:
        cohere_installed = False

    return {
        "cohere_api_key_configured": bool(api_key),
        "cohere_sdk_installed": cohere_installed,
        "api_key_preview": f"{api_key[:10]}..." if api_key else None
    }
