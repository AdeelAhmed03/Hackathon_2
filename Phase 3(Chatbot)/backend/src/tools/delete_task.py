"""Delete task tool implementation."""

from typing import Dict, Any, Optional
from sqlmodel import Session, select

from ..models.task import Task
from ..models.tag import TaskTagLink
from .complete_task import find_task


def delete_task_handler(
    parameters: Dict[str, Any],
    user_id: int,
    session: Session
) -> str:
    """
    Delete a task with confirmation.

    Args:
        parameters: Tool parameters from Cohere
        user_id: Authenticated user ID (from JWT)
        session: Database session

    Returns:
        Confirmation request, deletion confirmation, or error
    """
    task_id = parameters.get("task_id")
    task_title = parameters.get("task_title")
    confirmed = parameters.get("confirmed", False)

    # Convert confirmed to bool
    if isinstance(confirmed, str):
        confirmed = confirmed.lower() in ["true", "yes", "1"]

    # Need at least one identifier
    if not task_id and not task_title:
        return "I need to know which task to delete. Please provide the task ID or title."

    # Convert task_id to int if provided
    if task_id:
        try:
            task_id = int(task_id)
        except (ValueError, TypeError):
            return f"Invalid task ID: {task_id}. Please provide a valid number."

    # Find the task
    task = find_task(session, user_id, task_id, task_title)

    if not task:
        # Check for multiple matches
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

    # If not confirmed, ask for confirmation
    if not confirmed:
        details = [f"**{task.title}**"]
        details.append(f"- ID: #{task.id}")
        details.append(f"- Priority: {task.priority.value}")
        details.append(f"- Status: {task.status.value}")

        if task.due_datetime:
            details.append(f"- Due: {task.due_datetime.strftime('%Y-%m-%d')}")

        return (
            f"Are you sure you want to delete this task?\n\n"
            + "\n".join(details)
            + "\n\n**This action cannot be undone.** Reply 'yes' to confirm deletion."
        )

    # Confirmed - proceed with deletion
    task_info = f"#{task.id}: {task.title}"

    # Delete tag links first
    tag_links = session.exec(
        select(TaskTagLink).where(TaskTagLink.task_id == task.id)
    ).all()
    for link in tag_links:
        session.delete(link)

    # Delete the task
    session.delete(task)
    session.commit()

    return f"Deleted task {task_info}"
