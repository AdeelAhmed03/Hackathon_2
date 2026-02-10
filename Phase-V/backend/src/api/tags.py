"""Tag API routes.

T088-T090: Tag management endpoints.
"""

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
    """List all tags for the current user.

    T088: GET /api/tags endpoint for user's tags.
    """
    statement = select(Tag).where(Tag.user_id == current_user.id).order_by(Tag.name)
    return session.exec(statement).all()


@router.post("/", response_model=TagRead)
def create_tag(
    tag: TagCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Create a new tag for the current user.

    T089: POST /api/tags endpoint for creating tags.
    Returns existing tag if name already exists (get-or-create pattern).
    """
    # Check if tag already exists for this user
    existing_tag = session.exec(
        select(Tag).where(Tag.name == tag.name, Tag.user_id == current_user.id)
    ).first()

    if existing_tag:
        return existing_tag

    # Create Tag with user_id included to satisfy required field validation
    db_tag = Tag(
        name=tag.name,
        user_id=current_user.id
    )
    session.add(db_tag)
    session.commit()
    session.refresh(db_tag)
    return db_tag


@router.get("/{tag_id}", response_model=TagRead)
def get_tag(
    tag_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get a specific tag by ID."""
    statement = select(Tag).where(Tag.id == tag_id, Tag.user_id == current_user.id)
    tag = session.exec(statement).first()

    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )

    return tag


@router.delete("/{tag_id}")
def delete_tag(
    tag_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Delete a tag by ID.

    T090: DELETE /api/tags/:id endpoint for deleting tags.
    Note: This will remove the tag from all associated tasks.
    """
    statement = select(Tag).where(Tag.id == tag_id, Tag.user_id == current_user.id)
    tag = session.exec(statement).first()

    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )

    session.delete(tag)
    session.commit()
    return {"message": "Tag deleted successfully"}
