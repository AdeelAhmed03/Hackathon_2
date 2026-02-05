"""Tool execution service for MCP-style tools."""

from typing import Dict, Any, List, Callable, Optional
from sqlmodel import Session

from ..tools.add_task import add_task_handler
from ..tools.list_tasks import list_tasks_handler
from ..tools.complete_task import complete_task_handler
from ..tools.update_task import update_task_handler
from ..tools.delete_task import delete_task_handler

# Tool handler registry
TOOL_HANDLERS: Dict[str, Callable] = {
    "add_task": add_task_handler,
    "list_tasks": list_tasks_handler,
    "complete_task": complete_task_handler,
    "update_task": update_task_handler,
    "delete_task": delete_task_handler,
}

# Maximum iterations to prevent infinite loops
MAX_TOOL_ITERATIONS = 10


def execute_tool(
    tool_name: str,
    parameters: Dict[str, Any],
    user_id: int,
    session: Session
) -> Dict[str, Any]:
    """
    Execute a single tool with the given parameters.

    Args:
        tool_name: Name of the tool to execute
        parameters: Tool parameters from Cohere
        user_id: Authenticated user ID (from JWT, NOT from AI)
        session: Database session

    Returns:
        Dict with 'success', 'result', and optionally 'error' keys
    """
    handler = TOOL_HANDLERS.get(tool_name)

    if not handler:
        return {
            "success": False,
            "error": f"Unknown tool: {tool_name}",
            "result": f"I don't know how to handle '{tool_name}'. Available tools: {list(TOOL_HANDLERS.keys())}"
        }

    try:
        # Execute the tool handler with user_id from authenticated context
        result = handler(
            parameters=parameters,
            user_id=user_id,
            session=session
        )
        return {
            "success": True,
            "result": result
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "result": f"Sorry, I encountered an error while executing {tool_name}: {str(e)}"
        }


def execute_tool_calls(
    tool_calls: List[Any],
    user_id: int,
    session: Session
) -> List[Dict[str, Any]]:
    """
    Execute multiple tool calls from a Cohere response.

    Args:
        tool_calls: List of tool calls from Cohere response
        user_id: Authenticated user ID
        session: Database session

    Returns:
        List of execution results
    """
    results = []

    for tool_call in tool_calls:
        tool_name = tool_call.name
        parameters = tool_call.parameters or {}

        result = execute_tool(
            tool_name=tool_name,
            parameters=parameters,
            user_id=user_id,
            session=session
        )
        results.append(result)

    return results


async def run_tool_loop(
    initial_message: str,
    chat_history: List[Dict[str, str]],
    tools: List[Dict[str, Any]],
    user_id: int,
    session: Session,
    call_cohere_func: Callable
) -> Dict[str, Any]:
    """
    Run the tool calling loop until no more tools are requested.

    This implements the runner pattern:
    1. Call Cohere with message and tools
    2. If tool_calls in response, execute them
    3. Call Cohere again with tool results
    4. Repeat until no tool_calls or max iterations

    Args:
        initial_message: User's original message
        chat_history: Formatted conversation history
        tools: Tool definitions
        user_id: Authenticated user ID
        session: Database session
        call_cohere_func: Function to call Cohere API

    Returns:
        Dict with 'text', 'tool_calls', 'tool_results', 'iterations'
    """
    from .chat_service import format_tool_results_for_cohere

    iterations = 0
    all_tool_calls = []
    all_tool_results = []

    # Initial call
    response = await call_cohere_func(
        message=initial_message,
        chat_history=chat_history,
        tools=tools,
        tool_results=None
    )

    # Loop while there are tool calls
    while response.tool_calls and iterations < MAX_TOOL_ITERATIONS:
        iterations += 1

        # Execute all tool calls
        tool_calls = response.tool_calls
        results = execute_tool_calls(
            tool_calls=tool_calls,
            user_id=user_id,
            session=session
        )

        # Store for return
        all_tool_calls.extend([{
            "name": tc.name,
            "parameters": tc.parameters
        } for tc in tool_calls])
        all_tool_results.extend(results)

        # Format results for Cohere
        formatted_results = format_tool_results_for_cohere(
            tool_calls=tool_calls,
            results=results
        )

        # Call Cohere again with tool results
        response = await call_cohere_func(
            message=initial_message,
            chat_history=chat_history,
            tools=tools,
            tool_results=formatted_results
        )

    # Return final state
    return {
        "text": response.text or "",
        "tool_calls": all_tool_calls if all_tool_calls else None,
        "tool_results": all_tool_results if all_tool_results else None,
        "iterations": iterations
    }
