"""Service for complex task queries including filtering and sorting."""

from typing import List, Optional
from sqlmodel import Session, select, or_, and_, text
from src.models.task import Task, TaskStatus, TaskPriority
from src.models.tag import Tag, TaskTagLink

class TaskQueryService:
    """Service to handle complex task retrieval logic."""

    @staticmethod
    def get_filtered_tasks(
        session: Session,
        user_id: int,
        q: Optional[str] = None,
        priority: Optional[List[TaskPriority]] = None,
        tags: Optional[List[str]] = None,
        status: Optional[TaskStatus] = None,
        sort_by: str = "created_at",
        order: str = "desc"
    ) -> List[Task]:
        """Fetch tasks with complex search, filter, and sort logic."""

        # Base query with user isolation
        query = select(Task).where(Task.owner_id == user_id)

        # Keyword search (ILIKE support via lowercase conversion in SQLite)
        if q:
            search = f"%{q.lower()}%"
            query = query.where(
                or_(
                    text("LOWER(task.title) LIKE :q"),
                    text("LOWER(task.description) LIKE :q")
                )
            ).params(q=search)

        # Priority filter (Multiple support)
        if priority:
            query = query.where(Task.priority.in_(priority))

        # Status filter
        if status:
            query = query.where(Task.status == status)

        # Tags filter (AND logic - must have all tags)
        if tags:
            for tag_name in tags:
                # Subquery to ensure task has this specific tag
                tag_subquery = (
                    select(TaskTagLink.task_id)
                    .join(Tag)
                    .where(Tag.name == tag_name)
                    .where(Tag.user_id == user_id)
                )
                query = query.where(Task.id.in_(tag_subquery))

        # Sorting logic
        order_fn = getattr(Task, sort_by).desc if order == "desc" else getattr(Task, sort_by).asc

        # Special handling for priority sort (High > Medium > Low)
        if sort_by == "priority":
            priority_map = {
                TaskPriority.HIGH: 3,
                TaskPriority.MEDIUM: 2,
                TaskPriority.LOW: 1
            }
            # Custom sorting using a mapping or numeric priorities if we migrated them
            # For now, default to alphabetical order of the enum values which isn't ideal
            # and should be improved in Phase 5.
            pass

        query = query.order_by(order_fn())

        return session.exec(query).all()
