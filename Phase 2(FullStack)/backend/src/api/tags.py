"""Tag API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from ..database.session import get_session
from ..models.tag import Tag, TagRead, TagCreate
from ..models.user import User
from ..middleware.auth import get_current_user

router = APIRouter()

@router.get("/", response_model=List[TagRead])
def list_tags(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """List all tags for the current user."""
    statement = select(Tag).where(Tag.user_id == current_user.id)
    return session.exec(statement).all()

@router.post("/", response_model=TagRead)
def create_tag(
    tag: TagCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Create a new tag for the current user."""
    # Check if tag already exists for this user
    existing_tag = session.exec(
        select(Tag).where(Tag.name == tag.name, Tag.user_id == current_user.id)
    ).first()

    if existing_tag:
        return existing_tag

    db_tag = Tag.model_validate(tag)
    db_tag.user_id = current_user.id
    session.add(db_tag)
    session.commit()
    session.refresh(db_tag)
    return db_tag
