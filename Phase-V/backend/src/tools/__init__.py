"""MCP-style tools for AI chatbot task management."""

from .definitions import ALL_TOOLS, TOOL_DEFINITIONS
from .add_task import add_task_handler
from .list_tasks import list_tasks_handler
from .complete_task import complete_task_handler
from .update_task import update_task_handler
from .delete_task import delete_task_handler

__all__ = [
    "ALL_TOOLS",
    "TOOL_DEFINITIONS",
    "add_task_handler",
    "list_tasks_handler",
    "complete_task_handler",
    "update_task_handler",
    "delete_task_handler",
]
