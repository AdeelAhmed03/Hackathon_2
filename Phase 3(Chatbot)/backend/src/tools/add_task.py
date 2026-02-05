"""Add task tool implementation."""

from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlmodel import Session, select

from ..models.task import Task, TaskPriority, RecurrenceRule
from ..models.tag import Tag, TaskTagLink


def parse_priority(priority_str: Optional[str]) -> TaskPriority:
    """Parse priority string to enum."""
    if not priority_str:
        return TaskPriority.MEDIUM

    priority_lower = priority_str.lower().strip()
    if priority_lower == "high":
        return TaskPriority.HIGH
    elif priority_lower == "low":
        return TaskPriority.LOW
    return TaskPriority.MEDIUM


def parse_recurrence(recurrence_str: Optional[str]) -> Optional[RecurrenceRule]:
    """Parse recurrence string to enum."""
    if not recurrence_str:
        return None

    recurrence_lower = recurrence_str.lower().strip()
    mapping = {
        "daily": RecurrenceRule.DAILY,
        "weekly": RecurrenceRule.WEEKLY,
        "monthly": RecurrenceRule.MONTHLY,
        "yearly": RecurrenceRule.YEARLY,
    }
    return mapping.get(recurrence_lower)


def parse_due_datetime(due_str: Optional[str]) -> Optional[datetime]:
    """Parse due datetime string to datetime object."""
    if not due_str:
        return None

    try:
        # Try ISO format first
        return datetime.fromisoformat(due_str.replace("Z", "+00:00"))
    except ValueError:
        pass

    # Try common formats
    formats = [
        "%Y-%m-%d",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d %H:%M:%S",
        "%m/%d/%Y",
        "%d/%m/%Y",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(due_str, fmt)
        except ValueError:
            continue

    return None


def parse_tag_names(tag_names_str: Optional[str]) -> List[str]:
    """Parse tag names from string (could be JSON array or comma-separated)."""
    if not tag_names_str:
        return []

    # Try to parse as JSON array
    import json
    try:
        tags = json.loads(tag_names_str)
        if isinstance(tags, list):
            return [str(t).strip() for t in tags if t]
    except (json.JSONDecodeError, TypeError):
        pass

    # Fall back to comma-separated
    return [t.strip() for t in tag_names_str.split(",") if t.strip()]


def get_or_create_tags(session: Session, tag_names: List[str], user_id: int) -> List[Tag]:
    """Get existing tags or create new ones."""
    tags = []
    for name in tag_names:
        # Check if tag exists
        statement = select(Tag).where(Tag.name == name)
        tag = session.exec(statement).first()

        if not tag:
            # Create new tag
            tag = Tag(name=name)
            session.add(tag)
            session.commit()
            session.refresh(tag)

        tags.append(tag)

    return tags


def add_task_handler(
    parameters: Dict[str, Any],
    user_id: int,
    session: Session
) -> str:
    """
    Create a new task for the authenticated user.

    Args:
        parameters: Tool parameters from Cohere
        user_id: Authenticated user ID (from JWT)
        session: Database session

    Returns:
        Confirmation message with task details
    """
    # Extract required parameter
    title = parameters.get("title")
    if not title:
        return "I need a title for the task. What would you like to call it?"

    # Extract optional parameters
    description = parameters.get("description")
    priority = parse_priority(parameters.get("priority"))
    due_datetime = parse_due_datetime(parameters.get("due_datetime"))
    recurrence_rule = parse_recurrence(parameters.get("recurrence_rule"))
    tag_names = parse_tag_names(parameters.get("tag_names"))

    # Create the task
    now = datetime.utcnow()
    task = Task(
        title=title,
        description=description,
        priority=priority,
        due_datetime=due_datetime,
        recurrence_rule=recurrence_rule,
        owner_id=user_id,
        created_at=now,
        updated_at=now
    )

    session.add(task)
    session.commit()
    session.refresh(task)

    # Add tags if specified
    if tag_names:
        tags = get_or_create_tags(session, tag_names, user_id)
        for tag in tags:
            # Create link
            link = TaskTagLink(task_id=task.id, tag_id=tag.id)
            session.add(link)
        session.commit()

    # Build confirmation message
    details = [f"**{task.title}**"]
    details.append(f"- Priority: {priority.value}")

    if due_datetime:
        details.append(f"- Due: {due_datetime.strftime('%Y-%m-%d %H:%M')}")

    if recurrence_rule:
        details.append(f"- Recurrence: {recurrence_rule.value}")

    if tag_names:
        details.append(f"- Tags: {', '.join(tag_names)}")

    if description:
        details.append(f"- Description: {description}")

    details.append(f"- Task ID: #{task.id}")

    return f"Created task:\n" + "\n".join(details)
