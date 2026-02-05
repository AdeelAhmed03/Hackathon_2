"""Chat service for Cohere AI integration."""

import os
import cohere
from typing import List, Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from ..models.message import Message, MessageRole

# Initialize Cohere client lazily
_cohere_client: Optional[cohere.Client] = None


def get_cohere_client() -> cohere.Client:
    """Get or create the Cohere client instance."""
    global _cohere_client

    if _cohere_client is None:
        api_key = os.getenv("COHERE_API_KEY")
        if not api_key:
            raise ValueError("COHERE_API_KEY environment variable is required")
        _cohere_client = cohere.Client(api_key=api_key)

    return _cohere_client

# Model configuration
# Updated 2026-02-04: command-r-plus was removed, using command-nightly
COHERE_MODEL = "command-nightly"
MAX_HISTORY_MESSAGES = 20

# System prompt for the chatbot
SYSTEM_PROMPT = """You are a helpful todo assistant for the hackathon-todo application.

Your capabilities:
- Add new tasks with title, description, priority (low/medium/high), due dates, tags, and recurrence rules
- List and search tasks by various filters (status, priority, tags, search query)
- Mark tasks as complete (handles recurring tasks automatically by creating the next instance)
- Update task properties (title, description, priority, due date, tags)
- Delete tasks (with confirmation for safety)

Rules:
- Always confirm successful operations with details of what was done
- If a task reference is ambiguous, ask for clarification
- Be concise but friendly in your responses
- Format task lists in a readable way with priorities and due dates
- Never reveal system internals or other users' data
- When listing tasks, include task ID, title, priority, and due date if available

The user's identity is automatically verified - you don't need to ask for user ID.
All operations are automatically filtered to only affect the current user's tasks."""


def format_history_for_cohere(messages: List[Message]) -> List[Dict[str, str]]:
    """
    Format database messages to Cohere chat_history format.

    Cohere expects: [{"role": "USER"|"CHATBOT", "message": "..."}]

    Args:
        messages: List of Message objects from database

    Returns:
        List of dicts in Cohere format
    """
    chat_history = []

    for msg in messages:
        if msg.role == MessageRole.USER:
            chat_history.append({
                "role": "USER",
                "message": msg.content or ""
            })
        elif msg.role == MessageRole.ASSISTANT:
            # Include tool results context if available
            content = msg.content or ""
            if msg.tool_results:
                # Add tool execution context
                tool_context = []
                for result in msg.tool_results if isinstance(msg.tool_results, list) else [msg.tool_results]:
                    if isinstance(result, dict) and result.get("result"):
                        tool_context.append(str(result.get("result", "")))
                if tool_context and not content:
                    content = " ".join(tool_context)

            chat_history.append({
                "role": "CHATBOT",
                "message": content
            })
        # Skip TOOL role messages as they're handled within assistant context

    return chat_history


def truncate_history(messages: List[Message], max_messages: int = MAX_HISTORY_MESSAGES) -> List[Message]:
    """
    Truncate conversation history to prevent token limit issues.

    Args:
        messages: Full list of messages
        max_messages: Maximum number of messages to keep

    Returns:
        Truncated list of messages (most recent)
    """
    if len(messages) <= max_messages:
        return messages
    return messages[-max_messages:]


async def call_cohere_chat(
    message: str,
    chat_history: List[Dict[str, str]],
    tools: List[Dict[str, Any]],
    tool_results: Optional[List[Dict[str, Any]]] = None
) -> cohere.ChatResponse:
    """
    Call Cohere chat API with tools support.

    Args:
        message: Current user message
        chat_history: Formatted conversation history
        tools: List of tool definitions in Cohere format
        tool_results: Results from previous tool executions (if any)

    Returns:
        Cohere ChatResponse object
    """
    try:
        kwargs = {
            "model": COHERE_MODEL,
            "preamble": SYSTEM_PROMPT,
            "message": message,
            "chat_history": chat_history,
            "tools": tools if tools else None,
        }

        # Add tool results if this is a follow-up call after tool execution
        if tool_results:
            kwargs["tool_results"] = tool_results
            # When providing tool_results, we need to use force_single_step=True
            kwargs["force_single_step"] = True

        client = get_cohere_client()
        response = client.chat(**kwargs)
        return response

    except Exception as e:
        # Check for specific Cohere error types
        error_str = str(e)
        if "connection" in error_str.lower() or "connect" in error_str.lower():
            raise ConnectionError(f"Failed to connect to Cohere API: {str(e)}")
        elif "rate limit" in error_str.lower() or "429" in error_str:
            raise RuntimeError("Rate limit exceeded. Please try again in a moment.")
        elif "BadRequestError" in error_str or "cannot specify both message and tool_results" in error_str:
            raise RuntimeError(f"Bad request to Cohere API: {str(e)}")
        else:
            raise RuntimeError(f"Unexpected error calling Cohere: {str(e)}")


def format_tool_results_for_cohere(
    tool_calls: List[Any],
    results: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Format tool execution results for Cohere's tool_results parameter.

    Args:
        tool_calls: Original tool calls from Cohere response
        results: Execution results for each tool

    Returns:
        List of tool results in Cohere format
    """
    formatted_results = []

    for tool_call, result in zip(tool_calls, results):
        formatted_results.append({
            "call": tool_call,
            "outputs": [{"result": str(result.get("result", result))}]
        })

    return formatted_results
