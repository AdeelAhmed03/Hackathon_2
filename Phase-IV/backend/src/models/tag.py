"""Tag model definition and join table."""

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from .task import Task

class TaskTagLink(SQLModel, table=True):
    """Many-to-many join table for Tasks and Tags."""
    task_id: Optional[int] = Field(
        default=None, foreign_key="task.id", primary_key=True
    )
    tag_id: Optional[int] = Field(
        default=None, foreign_key="tag.id", primary_key=True
    )

class TagBase(SQLModel):
    """Base tag model with common fields."""
    name: str = Field(index=True)

class Tag(TagBase, table=True):
    """Tag database model."""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)

    # Relationships
    tasks: List["Task"] = Relationship(back_populates="tags", link_model=TaskTagLink)

class TagCreate(TagBase):
    """Schema for creating a new tag."""
    pass

class TagRead(TagBase):
    """Schema for reading tag data."""
    id: int
    user_id: int
