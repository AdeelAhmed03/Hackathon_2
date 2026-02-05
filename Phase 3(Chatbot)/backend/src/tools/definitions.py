"""Cohere-compatible tool definitions for MCP-style task management."""

from typing import List, Dict, Any

# Tool definition for add_task
ADD_TASK_TOOL = {
    "name": "add_task",
    "description": "Create a new task for the user. Use this when the user wants to add, create, or remember something as a task.",
    "parameter_definitions": {
        "title": {
            "description": "The title or name of the task (required)",
            "type": "str",
            "required": True
        },
        "description": {
            "description": "Optional detailed description of the task",
            "type": "str",
            "required": False
        },
        "priority": {
            "description": "Priority level: 'low', 'medium' (default), or 'high'",
            "type": "str",
            "required": False
        },
        "due_datetime": {
            "description": "Due date and time in ISO format (e.g., '2024-12-25T10:00:00')",
            "type": "str",
            "required": False
        },
        "recurrence_rule": {
            "description": "Recurrence pattern: 'daily', 'weekly', 'monthly', or 'yearly'",
            "type": "str",
            "required": False
        },
        "tag_names": {
            "description": "List of tag names to attach to the task (e.g., ['work', 'urgent'])",
            "type": "str",
            "required": False
        }
    }
}

# Tool definition for list_tasks
LIST_TASKS_TOOL = {
    "name": "list_tasks",
    "description": "List and search the user's tasks. Use this when the user wants to see, show, find, or query their tasks.",
    "parameter_definitions": {
        "status": {
            "description": "Filter by status: 'pending', 'in_progress', or 'completed'",
            "type": "str",
            "required": False
        },
        "priority": {
            "description": "Filter by priority: 'low', 'medium', or 'high'",
            "type": "str",
            "required": False
        },
        "tag_names": {
            "description": "Filter by tag names (tasks must have ALL specified tags)",
            "type": "str",
            "required": False
        },
        "search_query": {
            "description": "Search text in task titles and descriptions",
            "type": "str",
            "required": False
        },
        "limit": {
            "description": "Maximum number of tasks to return (default: 20)",
            "type": "int",
            "required": False
        }
    }
}

# Tool definition for complete_task
COMPLETE_TASK_TOOL = {
    "name": "complete_task",
    "description": "Mark a task as completed. Use this when the user says they finished, completed, or done with a task.",
    "parameter_definitions": {
        "task_id": {
            "description": "The ID number of the task to complete",
            "type": "int",
            "required": False
        },
        "task_title": {
            "description": "The title of the task to complete (used if ID is not known)",
            "type": "str",
            "required": False
        }
    }
}

# Tool definition for update_task
UPDATE_TASK_TOOL = {
    "name": "update_task",
    "description": "Update properties of an existing task. Use this when the user wants to change, modify, rename, or update a task.",
    "parameter_definitions": {
        "task_id": {
            "description": "The ID number of the task to update",
            "type": "int",
            "required": False
        },
        "task_title": {
            "description": "The current title of the task to update (used if ID is not known)",
            "type": "str",
            "required": False
        },
        "new_title": {
            "description": "New title for the task",
            "type": "str",
            "required": False
        },
        "new_description": {
            "description": "New description for the task",
            "type": "str",
            "required": False
        },
        "new_priority": {
            "description": "New priority: 'low', 'medium', or 'high'",
            "type": "str",
            "required": False
        },
        "new_due_datetime": {
            "description": "New due date in ISO format",
            "type": "str",
            "required": False
        },
        "new_recurrence_rule": {
            "description": "New recurrence: 'daily', 'weekly', 'monthly', 'yearly', or null to remove",
            "type": "str",
            "required": False
        },
        "add_tags": {
            "description": "Tag names to add to the task",
            "type": "str",
            "required": False
        },
        "remove_tags": {
            "description": "Tag names to remove from the task",
            "type": "str",
            "required": False
        }
    }
}

# Tool definition for delete_task
DELETE_TASK_TOOL = {
    "name": "delete_task",
    "description": "Delete a task. Use this when the user wants to remove or delete a task. Always ask for confirmation first.",
    "parameter_definitions": {
        "task_id": {
            "description": "The ID number of the task to delete",
            "type": "int",
            "required": False
        },
        "task_title": {
            "description": "The title of the task to delete (used if ID is not known)",
            "type": "str",
            "required": False
        },
        "confirmed": {
            "description": "Whether the user has confirmed the deletion (default: false)",
            "type": "bool",
            "required": False
        }
    }
}

# Export all tools as a list
ALL_TOOLS: List[Dict[str, Any]] = [
    ADD_TASK_TOOL,
    LIST_TASKS_TOOL,
    COMPLETE_TASK_TOOL,
    UPDATE_TASK_TOOL,
    DELETE_TASK_TOOL,
]

# Tool name to definition mapping
TOOL_DEFINITIONS: Dict[str, Dict[str, Any]] = {
    "add_task": ADD_TASK_TOOL,
    "list_tasks": LIST_TASKS_TOOL,
    "complete_task": COMPLETE_TASK_TOOL,
    "update_task": UPDATE_TASK_TOOL,
    "delete_task": DELETE_TASK_TOOL,
}
