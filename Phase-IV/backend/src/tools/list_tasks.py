"""List tasks tool implementation."""

from typing import Dict, Any, Optional, List
from sqlmodel import Session, select
from sqlalchemy import or_

from ..models.task import Task, TaskStatus, TaskPriority
from ..models.tag import Tag, TaskTagLink


def parse_status(status_str: Optional[str]) -> Optional[TaskStatus]:
    """Parse status string to enum."""
    if not status_str:
        return None

    status_lower = status_str.lower().strip()
    mapping = {
        "pending": TaskStatus.PENDING,
        "in_progress": TaskStatus.IN_PROGRESS,
        "completed": TaskStatus.COMPLETED,
    }
    return mapping.get(status_lower)


def parse_priority(priority_str: Optional[str]) -> Optional[TaskPriority]:
    """Parse priority string to enum."""
    if not priority_str:
        return None

    priority_lower = priority_str.lower().strip()
    mapping = {
        "low": TaskPriority.LOW,
        "medium": TaskPriority.MEDIUM,
        "high": TaskPriority.HIGH,
    }
    return mapping.get(priority_lower)


def parse_tag_names(tag_names_str: Optional[str]) -> List[str]:
    """Parse tag names from string."""
    if not tag_names_str:
        return []

    import json
    try:
        tags = json.loads(tag_names_str)
        if isinstance(tags, list):
            return [str(t).strip() for t in tags if t]
    except (json.JSONDecodeError, TypeError):
        pass

    return [t.strip() for t in tag_names_str.split(",") if t.strip()]


def format_task(task: Task, tags: List[str] = None) -> str:
    """Format a single task for display."""
    parts = [f"#{task.id}"]
    parts.append(f"**{task.title}**")
    parts.append(f"[{task.priority.value}]")
    parts.append(f"({task.status.value})")

    if task.due_datetime:
        parts.append(f"Due: {task.due_datetime.strftime('%Y-%m-%d')}")

    if task.recurrence_rule:
        parts.append(f"[{task.recurrence_rule.value}]")

    if tags:
        parts.append(f"Tags: {', '.join(tags)}")

    return " | ".join(parts)


def list_tasks_handler(
    parameters: Dict[str, Any],
    user_id: int,
    session: Session
) -> str:
    """
    List tasks for the authenticated user with optional filters.

    Args:
        parameters: Tool parameters from Cohere
        user_id: Authenticated user ID (from JWT)
        session: Database session

    Returns:
        Formatted list of tasks or message if none found
    """
    # Parse filter parameters
    status = parse_status(parameters.get("status"))
    priority = parse_priority(parameters.get("priority"))
    tag_names = parse_tag_names(parameters.get("tag_names"))
    search_query = parameters.get("search_query")
    limit = parameters.get("limit", 20)

    # Ensure limit is reasonable
    try:
        limit = min(int(limit), 50)
    except (ValueError, TypeError):
        limit = 20

    # Build query - ALWAYS filter by user_id first
    statement = select(Task).where(Task.owner_id == user_id)

    # Apply status filter
    if status:
        statement = statement.where(Task.status == status)

    # Apply priority filter
    if priority:
        statement = statement.where(Task.priority == priority)

    # Apply search query
    if search_query:
        search_pattern = f"%{search_query}%"
        statement = statement.where(
            or_(
                Task.title.ilike(search_pattern),
                Task.description.ilike(search_pattern)
            )
        )

    # Order by priority (high first), then by created_at
    statement = statement.order_by(
        Task.priority.desc(),
        Task.created_at.desc()
    ).limit(limit)

    # Execute query
    tasks = session.exec(statement).all()

    # Filter by tags if specified (AND logic)
    if tag_names:
        filtered_tasks = []
        for task in tasks:
            # Get task's tags
            tag_statement = (
                select(Tag)
                .join(TaskTagLink)
                .where(TaskTagLink.task_id == task.id)
            )
            task_tags = session.exec(tag_statement).all()
            task_tag_names = {t.name.lower() for t in task_tags}

            # Check if task has ALL specified tags
            if all(tn.lower() in task_tag_names for tn in tag_names):
                filtered_tasks.append((task, [t.name for t in task_tags]))
        tasks_with_tags = filtered_tasks
    else:
        # Get tags for all tasks
        tasks_with_tags = []
        for task in tasks:
            tag_statement = (
                select(Tag)
                .join(TaskTagLink)
                .where(TaskTagLink.task_id == task.id)
            )
            task_tags = session.exec(tag_statement).all()
            tasks_with_tags.append((task, [t.name for t in task_tags]))

    # Build response
    if not tasks_with_tags:
        # Build descriptive "no tasks" message
        filters = []
        if status:
            filters.append(f"status: {status.value}")
        if priority:
            filters.append(f"priority: {priority.value}")
        if tag_names:
            filters.append(f"tags: {', '.join(tag_names)}")
        if search_query:
            filters.append(f"search: '{search_query}'")

        if filters:
            return f"No tasks found with filters: {', '.join(filters)}"
        return "You don't have any tasks yet. Would you like to create one?"

    # Format task list
    lines = [f"Found {len(tasks_with_tags)} task(s):\n"]
    for task, tags in tasks_with_tags:
        lines.append(format_task(task, tags))

    return "\n".join(lines)
