"""Tasks API routes with search, filter, sort, and Dapr integration.

Enhanced for Phase V with:
- T068-T070: Due date and reminder support
- T078-T079: Priority filter and sort
- T091: Tag filtering
- T099-T101: Search, date range, pagination
- T109-T110: Multi-field sorting
- Event publishing via Dapr
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlmodel import Session, select, col, or_, and_
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime
import math

from ..database.session import get_session
from ..models.task import (
    Task, TaskCreate, TaskUpdate, TaskRead, TaskStatus, TaskPriority,
    TaskCreateWithTags, TaskListQuery, TaskListResponse
)
from ..models.tag import Tag, TaskTagLink
from ..models.user import User
from ..middleware.auth import get_current_user
from ..services.task_service import calculate_next_due_date
from ..services.event_publisher import (
    publish_task_created, publish_task_updated,
    publish_task_completed, publish_task_deleted
)
from ..services.job_scheduler import (
    schedule_reminder_job, cancel_reminder_job, reschedule_reminder_job
)

router = APIRouter()


def _get_tag_names(session: Session, task: Task) -> List[str]:
    """Get tag names for a task."""
    return [tag.name for tag in task.tags] if task.tags else []


@router.get("/", response_model=TaskListResponse)
async def list_tasks(
    q: Optional[str] = Query(None, description="Search keyword for title/description"),
    status_filter: Optional[TaskStatus] = Query(None, alias="status"),
    priority: Optional[TaskPriority] = Query(None, description="Filter by priority"),
    tags: Optional[List[int]] = Query(None, description="Filter by tag IDs (AND logic)"),
    due_before: Optional[datetime] = Query(None, description="Due date before"),
    due_after: Optional[datetime] = Query(None, description="Due date after"),
    sort_by: str = Query("created_at", description="Sort by field"),
    sort_order: str = Query("desc", description="Sort order (asc/desc)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """List tasks with search, filter, sort, and pagination.

    T096-T101: Implements search, date range, and combined filtering.
    T107-T110: Implements multi-field sorting.
    """
    # Base query with user isolation
    query = select(Task).where(Task.owner_id == current_user.id)

    # T096: Case-insensitive keyword search on title/description
    if q:
        search_term = f"%{q}%"
        query = query.where(
            or_(
                col(Task.title).ilike(search_term),
                col(Task.description).ilike(search_term)
            )
        )

    # Status filter
    if status_filter:
        query = query.where(Task.status == status_filter)

    # T078: Priority filter
    if priority:
        query = query.where(Task.priority == priority)

    # T097: Due date range filters
    if due_before:
        query = query.where(Task.due_datetime <= due_before)
    if due_after:
        query = query.where(Task.due_datetime >= due_after)

    # T087: Tag intersection filter (AND logic)
    if tags:
        # Tasks must have ALL specified tags
        for tag_id in tags:
            subquery = select(TaskTagLink.task_id).where(TaskTagLink.tag_id == tag_id)
            query = query.where(Task.id.in_(subquery))

    # Get total count before pagination
    count_query = select(func.count()).select_from(query.subquery())
    total_count = session.exec(count_query).one()

    # T107-T108: Multi-field sorting with NULLS LAST
    sort_fields = sort_by.split(",")
    for field in sort_fields:
        field = field.strip()
        if hasattr(Task, field):
            column = getattr(Task, field)
            if sort_order.lower() == "asc":
                # NULLS LAST for ascending
                query = query.order_by(column.asc().nullslast())
            else:
                # NULLS LAST for descending
                query = query.order_by(column.desc().nullslast())

    # T77: Priority-aware sorting (high=3, medium=2, low=1)
    if "priority" in sort_by:
        # Already handled above with enum ordering
        pass

    # Pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    tasks = session.exec(query).all()
    total_pages = math.ceil(total_count / page_size) if total_count > 0 else 1

    return TaskListResponse(
        items=tasks,
        total_count=total_count,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.post("/", response_model=TaskRead)
async def create_task(
    task: TaskCreateWithTags,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Create a new task with optional tags and reminder scheduling.

    T068: Accept due_at and remind_at fields.
    T059: Schedule reminder job when remind_at is set.
    """
    # T070: Validate remind_at is before due_at
    if task.remind_at and task.due_datetime:
        if task.remind_at >= task.due_datetime:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="remind_at must be before due_datetime"
            )

    now = datetime.utcnow()
    db_task = Task(
        title=task.title,
        description=task.description,
        status=task.status,
        priority=task.priority,
        due_datetime=task.due_datetime,
        remind_at=task.remind_at,
        recurrence_rule=task.recurrence_rule,
        owner_id=current_user.id,
        created_at=now,
        updated_at=now
    )
    session.add(db_task)
    session.flush()  # Get the ID

    # Attach tags if provided
    tag_names = []
    if task.tag_ids:
        for tag_id in task.tag_ids:
            tag = session.get(Tag, tag_id)
            if tag and tag.user_id == current_user.id:
                db_task.tags.append(tag)
                tag_names.append(tag.name)

    session.commit()
    session.refresh(db_task)

    # T059: Schedule reminder job if remind_at is set
    if task.remind_at:
        background_tasks.add_task(
            schedule_reminder_job,
            task_id=db_task.id,
            user_id=current_user.id,
            remind_at=task.remind_at,
            title=db_task.title
        )

    # Publish task_created event
    background_tasks.add_task(
        publish_task_created,
        task=db_task,
        user_id=current_user.id,
        tags=tag_names
    )

    return db_task


@router.get("/{task_id}", response_model=TaskRead)
def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get a specific task by ID."""
    statement = select(Task).where(Task.id == task_id, Task.owner_id == current_user.id)
    task = session.exec(statement).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return task


@router.put("/{task_id}", response_model=TaskRead)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Update a task with reminder rescheduling.

    T069: Handle due_at/remind_at updates.
    T060: Reschedule reminder on remind_at change.
    """
    statement = select(Task).where(Task.id == task_id, Task.owner_id == current_user.id)
    db_task = session.exec(statement).first()

    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Track if remind_at changed
    old_remind_at = db_task.remind_at
    new_remind_at = task_update.remind_at

    # T070: Validate remind_at is before due_at
    effective_due = task_update.due_datetime or db_task.due_datetime
    effective_remind = task_update.remind_at if task_update.remind_at is not None else db_task.remind_at
    if effective_remind and effective_due:
        if effective_remind >= effective_due:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="remind_at must be before due_datetime"
            )

    # Update task fields
    update_data = task_update.model_dump(exclude_unset=True, exclude={"tag_ids"})
    for field, value in update_data.items():
        setattr(db_task, field, value)

    # Update tags if provided
    tag_names = []
    if task_update.tag_ids is not None:
        # Clear existing tags
        db_task.tags.clear()
        # Add new tags
        for tag_id in task_update.tag_ids:
            tag = session.get(Tag, tag_id)
            if tag and tag.user_id == current_user.id:
                db_task.tags.append(tag)
                tag_names.append(tag.name)
    else:
        tag_names = [tag.name for tag in db_task.tags]

    db_task.updated_at = datetime.utcnow()
    session.add(db_task)
    session.commit()
    session.refresh(db_task)

    # T060: Reschedule reminder if remind_at changed
    if new_remind_at != old_remind_at:
        if new_remind_at:
            background_tasks.add_task(
                reschedule_reminder_job,
                task_id=db_task.id,
                user_id=current_user.id,
                remind_at=new_remind_at,
                title=db_task.title
            )
        elif old_remind_at:
            # remind_at was cleared, cancel the job
            background_tasks.add_task(cancel_reminder_job, task_id=db_task.id)

    # Publish task_updated event
    background_tasks.add_task(
        publish_task_updated,
        task=db_task,
        user_id=current_user.id,
        tags=tag_names
    )

    return db_task


@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Delete a task and cancel any scheduled reminder."""
    statement = select(Task).where(Task.id == task_id, Task.owner_id == current_user.id)
    db_task = session.exec(statement).first()

    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Cancel any scheduled reminder
    background_tasks.add_task(cancel_reminder_job, task_id=task_id)

    # Publish task_deleted event before deletion
    background_tasks.add_task(
        publish_task_deleted,
        task=db_task,
        user_id=current_user.id
    )

    session.delete(db_task)
    session.commit()
    return {"message": "Task deleted successfully"}


@router.patch("/{task_id}/complete", response_model=TaskRead)
async def complete_task(
    task_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Mark a task as complete with event publishing.

    T045: Publish task_completed event on completion.
    T061: Cancel reminder job on completion.
    """
    statement = select(Task).where(Task.id == task_id, Task.owner_id == current_user.id)
    db_task = session.exec(statement).first()

    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    if db_task.status == TaskStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task is already completed"
        )

    # Mark as completed
    db_task.status = TaskStatus.COMPLETED
    db_task.completed_at = datetime.utcnow()
    db_task.updated_at = datetime.utcnow()

    session.add(db_task)
    session.commit()
    session.refresh(db_task)

    tag_names = [tag.name for tag in db_task.tags] if db_task.tags else []

    # T061: Cancel any scheduled reminder
    background_tasks.add_task(cancel_reminder_job, task_id=task_id)

    # T045: Publish task_completed event (recurring-service will handle spawning)
    background_tasks.add_task(
        publish_task_completed,
        task=db_task,
        user_id=current_user.id,
        tags=tag_names
    )

    return db_task


@router.patch("/{task_id}/toggle-status", response_model=TaskRead)
async def toggle_task_status(
    task_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Toggle the completion status of a task."""
    statement = select(Task).where(Task.id == task_id, Task.owner_id == current_user.id)
    db_task = session.exec(statement).first()

    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    tag_names = [tag.name for tag in db_task.tags] if db_task.tags else []

    # Toggle status between pending and completed
    if db_task.status == TaskStatus.COMPLETED:
        db_task.status = TaskStatus.PENDING
        db_task.completed_at = None

        # Reschedule reminder if remind_at exists and is in the future
        if db_task.remind_at and db_task.remind_at > datetime.utcnow():
            background_tasks.add_task(
                schedule_reminder_job,
                task_id=db_task.id,
                user_id=current_user.id,
                remind_at=db_task.remind_at,
                title=db_task.title
            )

        background_tasks.add_task(
            publish_task_updated,
            task=db_task,
            user_id=current_user.id,
            tags=tag_names
        )
    else:
        db_task.status = TaskStatus.COMPLETED
        db_task.completed_at = datetime.utcnow()

        # Cancel reminder
        background_tasks.add_task(cancel_reminder_job, task_id=task_id)

        # Publish completion event
        background_tasks.add_task(
            publish_task_completed,
            task=db_task,
            user_id=current_user.id,
            tags=tag_names
        )

    db_task.updated_at = datetime.utcnow()
    session.add(db_task)
    session.commit()
    session.refresh(db_task)

    return db_task
