"""
Task data model for the todo application.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Task:
    """
    Represents a single task in the todo application.

    Attributes:
        id: Unique identifier for the task
        title: Required title of the task
        description: Optional description of the task
        completed: Boolean indicating if the task is completed
    """
    id: int
    title: str
    description: str
    completed: bool = False

    def __str__(self) -> str:
        """
        Returns a string representation of the task with status indicator.
        """
        status = "[x]" if self.completed else "[ ]"
        return f"{status} {self.id}: {self.title}"