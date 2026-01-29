"""
Task management logic for the todo application.
"""

from typing import Dict, List, Optional
from .task import Task


class TaskManager:
    """
    Manages tasks in memory with operations to add, list, update, delete, and change status.
    """

    def __init__(self) -> None:
        """
        Initialize the task manager with an empty task collection and next ID counter.
        """
        self._tasks: Dict[int, Task] = {}
        self._next_id: int = 1

    def add_task(self, title: str, description: str = "") -> Task:
        """
        Add a new task with the given title and description.

        Args:
            title: Required title of the task
            description: Optional description of the task

        Returns:
            The newly created Task object
        """
        task_id = self._next_id
        self._next_id += 1
        task = Task(id=task_id, title=title, description=description, completed=False)
        self._tasks[task_id] = task
        return task

    def get_task(self, task_id: int) -> Optional[Task]:
        """
        Retrieve a task by its ID.

        Args:
            task_id: ID of the task to retrieve

        Returns:
            The Task object if found, None otherwise
        """
        return self._tasks.get(task_id)

    def list_tasks(self) -> List[Task]:
        """
        Return all tasks sorted by ID.

        Returns:
            List of all Task objects sorted by ID
        """
        return sorted(self._tasks.values(), key=lambda t: t.id)

    def update_task(self, task_id: int, title: Optional[str] = None, description: Optional[str] = None) -> bool:
        """
        Update the title or description of a task by its ID.

        Args:
            task_id: ID of the task to update
            title: New title (optional)
            description: New description (optional)

        Returns:
            True if the task was updated, False if task ID not found
        """
        if task_id not in self._tasks:
            return False

        task = self._tasks[task_id]
        if title is not None:
            task.title = title
        if description is not None:
            task.description = description
        return True

    def delete_task(self, task_id: int) -> bool:
        """
        Delete a task by its ID.

        Args:
            task_id: ID of the task to delete

        Returns:
            True if the task was deleted, False if task ID not found
        """
        if task_id not in self._tasks:
            return False

        del self._tasks[task_id]
        return True

    def toggle_task_status(self, task_id: int) -> bool:
        """
        Toggle the completion status of a task by its ID.

        Args:
            task_id: ID of the task to toggle

        Returns:
            True if the task status was toggled, False if task ID not found
        """
        if task_id not in self._tasks:
            return False

        task = self._tasks[task_id]
        task.completed = not task.completed
        return True

    def get_next_id(self) -> int:
        """
        Get the next available ID for a new task.

        Returns:
            The next available task ID
        """
        return self._next_id