"""
Utility functions for the todo application.
"""


def is_valid_task_id(task_id_str: str) -> bool:
    """
    Check if the provided string is a valid task ID (positive integer).

    Args:
        task_id_str: String representation of a potential task ID

    Returns:
        True if the string represents a positive integer, False otherwise
    """
    try:
        task_id = int(task_id_str)
        return task_id > 0
    except ValueError:
        return False


def parse_task_id(task_id_str: str) -> int:
    """
    Parse a string to an integer task ID.

    Args:
        task_id_str: String representation of a task ID

    Returns:
        The integer task ID

    Raises:
        ValueError: If the string cannot be converted to a positive integer
    """
    task_id = int(task_id_str)
    if task_id <= 0:
        raise ValueError("Task ID must be a positive integer")
    return task_id