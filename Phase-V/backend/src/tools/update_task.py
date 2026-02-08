"""Update task tool implementation."""

from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlmodel import Session, select

from ..models.task import Task, TaskPriority, RecurrenceRule
from ..models.tag import Tag, TaskTagLink
from .add_task import parse_priority, parse_recurrence, parse_due_datetime, parse_tag_names, get_or_create_tags
from .complete_task import find_task


def update_task_handler(
    parameters: Dict[str, Any],
    user_id: int,
    session: Session
) -> str:
    """
    Update properties of an existing task.

    Args:
        parameters: Tool parameters from Cohere
        user_id: Authenticated user ID (from JWT)
        session: Database session

    Returns:
        Confirmation message with updated fields or error
    """
    task_id = parameters.get("task_id")
    task_title = parameters.get("task_title")

    # Need at least one identifier
    if not task_id and not task_title:
        return "I need to know which task to update. Please provide the task ID or title."

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

    # Track what was updated
    updates = []
    old_values = {}

    # Update title
    new_title = parameters.get("new_title")
    if new_title:
        old_values["title"] = task.title
        task.title = new_title
        updates.append(f"Title: '{old_values['title']}' → '{new_title}'")

    # Update description
    new_description = parameters.get("new_description")
    if new_description is not None:  # Allow empty string to clear
        old_values["description"] = task.description
        task.description = new_description if new_description else None
        if new_description:
            updates.append(f"Description updated")
        else:
            updates.append(f"Description cleared")

    # Update priority
    new_priority_str = parameters.get("new_priority")
    if new_priority_str:
        new_priority = parse_priority(new_priority_str)
        if new_priority != task.priority:
            old_values["priority"] = task.priority.value
            task.priority = new_priority
            updates.append(f"Priority: {old_values['priority']} → {new_priority.value}")

    # Update due datetime
    new_due_str = parameters.get("new_due_datetime")
    if new_due_str:
        new_due = parse_due_datetime(new_due_str)
        if new_due:
            old_due = task.due_datetime.strftime('%Y-%m-%d %H:%M') if task.due_datetime else "none"
            task.due_datetime = new_due
            updates.append(f"Due date: {old_due} → {new_due.strftime('%Y-%m-%d %H:%M')}")
        elif new_due_str.lower() in ["none", "null", "clear", "remove"]:
            task.due_datetime = None
            updates.append("Due date cleared")

    # Update recurrence
    new_recurrence_str = parameters.get("new_recurrence_rule")
    if new_recurrence_str:
        if new_recurrence_str.lower() in ["none", "null", "clear", "remove"]:
            if task.recurrence_rule:
                task.recurrence_rule = None
                updates.append("Recurrence removed")
        else:
            new_recurrence = parse_recurrence(new_recurrence_str)
            if new_recurrence:
                old_rec = task.recurrence_rule.value if task.recurrence_rule else "none"
                task.recurrence_rule = new_recurrence
                updates.append(f"Recurrence: {old_rec} → {new_recurrence.value}")

    # Handle tag additions
    add_tags_str = parameters.get("add_tags")
    if add_tags_str:
        tag_names_to_add = parse_tag_names(add_tags_str)
        if tag_names_to_add:
            tags = get_or_create_tags(session, tag_names_to_add, user_id)
            for tag in tags:
                # Check if link exists
                existing_link = session.exec(
                    select(TaskTagLink).where(
                        TaskTagLink.task_id == task.id,
                        TaskTagLink.tag_id == tag.id
                    )
                ).first()

                if not existing_link:
                    link = TaskTagLink(task_id=task.id, tag_id=tag.id)
                    session.add(link)

            updates.append(f"Added tags: {', '.join(tag_names_to_add)}")

    # Handle tag removals
    remove_tags_str = parameters.get("remove_tags")
    if remove_tags_str:
        tag_names_to_remove = parse_tag_names(remove_tags_str)
        if tag_names_to_remove:
            removed = []
            for tag_name in tag_names_to_remove:
                # Find tag
                tag = session.exec(
                    select(Tag).where(Tag.name.ilike(tag_name))
                ).first()

                if tag:
                    # Find and remove link
                    link = session.exec(
                        select(TaskTagLink).where(
                            TaskTagLink.task_id == task.id,
                            TaskTagLink.tag_id == tag.id
                        )
                    ).first()

                    if link:
                        session.delete(link)
                        removed.append(tag_name)

            if removed:
                updates.append(f"Removed tags: {', '.join(removed)}")

    # Check if anything was updated
    if not updates:
        return f"No changes were made to task #{task.id}: **{task.title}**. Please specify what you'd like to update."

    # Save changes
    task.updated_at = datetime.utcnow()
    session.add(task)
    session.commit()

    # Build response
    response = f"Updated task #{task.id}: **{task.title}**\n\nChanges:\n"
    response += "\n".join([f"- {update}" for update in updates])

    return response
