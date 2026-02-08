"""Complete task tool implementation."""

from typing import Dict, Any, Optional
from datetime import datetime
from sqlmodel import Session, select

from ..models.task import Task, TaskStatus
from ..services.task_service import calculate_next_due_date


def find_task(
    session: Session,
    user_id: int,
    task_id: Optional[int] = None,
    task_title: Optional[str] = None
) -> Optional[Task]:
    """
    Find a task by ID or title.

    SECURITY: Always filters by user_id to prevent cross-user access.
    """
    if task_id:
        # Find by ID
        statement = select(Task).where(
            Task.id == task_id,
            Task.owner_id == user_id  # CRITICAL: user_id filter
        )
        return session.exec(statement).first()

    if task_title:
        # Find by title (case-insensitive partial match)
        statement = select(Task).where(
            Task.owner_id == user_id,  # CRITICAL: user_id filter
            Task.title.ilike(f"%{task_title}%")
        )
        tasks = session.exec(statement).all()

        if len(tasks) == 1:
            return tasks[0]
        elif len(tasks) > 1:
            # Multiple matches - return None to trigger clarification
            return None

    return None


def create_recurring_instance(
    session: Session,
    original_task: Task
) -> Optional[Task]:
    """Create next instance of a recurring task."""
    if not original_task.recurrence_rule or not original_task.due_datetime:
        return None

    # Calculate next due date
    next_due = calculate_next_due_date(
        original_task.due_datetime,
        original_task.recurrence_rule
    )

    # Create new task
    now = datetime.utcnow()
    new_task = Task(
        title=original_task.title,
        description=original_task.description,
        status=TaskStatus.PENDING,
        priority=original_task.priority,
        due_datetime=next_due,
        recurrence_rule=original_task.recurrence_rule,
        recurrence_parent_id=original_task.id,
        owner_id=original_task.owner_id,
        created_at=now,
        updated_at=now
    )

    session.add(new_task)
    session.commit()
    session.refresh(new_task)

    return new_task


def complete_task_handler(
    parameters: Dict[str, Any],
    user_id: int,
    session: Session
) -> str:
    """
    Mark a task as completed.

    Args:
        parameters: Tool parameters from Cohere
        user_id: Authenticated user ID (from JWT)
        session: Database session

    Returns:
        Confirmation message or error
    """
    task_id = parameters.get("task_id")
    task_title = parameters.get("task_title")

    # Need at least one identifier
    if not task_id and not task_title:
        return "I need to know which task to complete. Please provide the task ID or title."

    # Convert task_id to int if provided
    if task_id:
        try:
            task_id = int(task_id)
        except (ValueError, TypeError):
            return f"Invalid task ID: {task_id}. Please provide a valid number."

    # Find the task
    task = find_task(session, user_id, task_id, task_title)

    if not task:
        # Check if there are multiple matches
        if task_title:
            statement = select(Task).where(
                Task.owner_id == user_id,
                Task.title.ilike(f"%{task_title}%")
            )
            matches = session.exec(statement).all()

            if len(matches) > 1:
                match_list = "\n".join([f"- #{t.id}: {t.title}" for t in matches[:5]])
                return f"I found multiple tasks matching '{task_title}':\n{match_list}\n\nPlease specify the task ID."

        return f"I couldn't find a task matching your request. Please check the task ID or title."

    # Check if already completed
    if task.status == TaskStatus.COMPLETED:
        return f"Task #{task.id} '{task.title}' is already completed."

    # Mark as completed
    task.status = TaskStatus.COMPLETED
    task.completed_at = datetime.utcnow()
    task.updated_at = datetime.utcnow()

    session.add(task)
    session.commit()

    # Handle recurring task
    response = f"Completed task #{task.id}: **{task.title}**"

    if task.recurrence_rule and task.due_datetime:
        new_task = create_recurring_instance(session, task)
        if new_task:
            response += f"\n\nCreated next recurring instance:\n"
            response += f"- #{new_task.id}: {new_task.title}\n"
            response += f"- Due: {new_task.due_datetime.strftime('%Y-%m-%d %H:%M')}"

    return response
