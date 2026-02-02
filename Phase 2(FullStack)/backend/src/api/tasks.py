"""Tasks API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from datetime import datetime
from ..database.session import get_session
from ..models.task import Task, TaskCreate, TaskUpdate, TaskRead, TaskStatus
from ..services.task_service import calculate_next_due_date

from ..models.user import User
from ..middleware.auth import get_current_user

router = APIRouter()

@router.get("/", response_model=List[TaskRead])
def list_tasks(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """List tasks for the current user."""
    statement = select(Task).where(Task.owner_id == current_user.id).offset(skip).limit(limit)
    tasks = session.exec(statement).all()
    return tasks

@router.post("/", response_model=TaskRead)
def create_task(
    task: TaskCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Create a new task for the current user."""
    now = datetime.utcnow()
    db_task = Task(
        title=task.title,
        description=task.description,
        status=task.status,
        priority=task.priority,
        due_datetime=task.due_datetime,
        recurrence_rule=task.recurrence_rule,
        owner_id=current_user.id,
        created_at=now,
        updated_at=now
    )
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
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
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Update a specific task by ID."""
    statement = select(Task).where(Task.id == task_id, Task.owner_id == current_user.id)
    db_task = session.exec(statement).first()

    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Update task fields
    for field, value in task_update.dict(exclude_unset=True).items():
        setattr(db_task, field, value)

    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task

@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Delete a specific task by ID."""
    statement = select(Task).where(Task.id == task_id, Task.owner_id == current_user.id)
    db_task = session.exec(statement).first()

    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    session.delete(db_task)
    session.commit()
    return {"message": "Task deleted successfully"}

@router.patch("/{task_id}/toggle-status", response_model=TaskRead)
def toggle_task_status(
    task_id: int,
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

    # Toggle status between pending and completed
    if db_task.status == "completed":
        db_task.status = "pending"
        db_task.completed_at = None
    else:
        db_task.status = "completed"
        db_task.completed_at = datetime.utcnow()

        # Handle recurring task creation
        if db_task.recurrence_rule and db_task.due_datetime:
            try:
                next_due = calculate_next_due_date(db_task.due_datetime, db_task.recurrence_rule)
                new_task_data = {
                    'title': db_task.title,
                    'description': db_task.description,
                    'status': 'pending',
                    'priority': db_task.priority,
                    'due_datetime': next_due,
                    'recurrence_rule': db_task.recurrence_rule,
                    'recurrence_parent_id': db_task.id
                }
                new_task = Task.model_validate(new_task_data)
                new_task.owner_id = current_user.id
                session.add(new_task)
                session.flush()  # Flush to get ID if needed
            except Exception as e:
                # Log error but don't fail the completion
                print(f"Failed to create recurring task instance: {e}")

    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task