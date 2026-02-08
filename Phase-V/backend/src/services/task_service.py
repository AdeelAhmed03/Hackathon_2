from datetime import datetime, timedelta, timezone
from dateutil.relativedelta import relativedelta
from typing import Optional, Dict, Any
from enum import Enum
from ..models.task import Task, TaskStatus  # Adjust import path as needed based on actual models location

class RecurrenceRule(str, Enum):
    """Recurrence rule enum for tasks."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


def calculate_next_due_date(current_due: datetime, recurrence_rule: RecurrenceRule) -> datetime:
    """
    Calculate the next due date for a recurring task based on the recurrence rule.

    This function adds the appropriate interval to the current due date while preserving
    the original timezone information.

    Args:
        current_due: The datetime of the current task's due date. Should be timezone-aware.
        recurrence_rule: The recurrence pattern (daily, weekly, monthly, or yearly).

    Returns:
        datetime: The next due date after the current one.

    Raises:
        ValueError: If an invalid recurrence_rule is provided.
    """
    if recurrence_rule == RecurrenceRule.DAILY:
        delta = timedelta(days=1)
    elif recurrence_rule == RecurrenceRule.WEEKLY:
        delta = timedelta(days=7)
    elif recurrence_rule == RecurrenceRule.MONTHLY:
        delta = relativedelta(months=1)
    elif recurrence_rule == RecurrenceRule.YEARLY:
        delta = relativedelta(years=1)
    else:
        raise ValueError(f"Invalid recurrence rule: {recurrence_rule}")

    return current_due + delta


def validate_due_date(due_datetime: Optional[datetime]) -> bool:
    """
    Validate if the due date is either None or a future date.

    Args:
        due_datetime: The optional due datetime to validate.

    Returns:
        bool: True if None or in the future (UTC), False otherwise.
    """
    if due_datetime is None:
        return True
    now_utc = datetime.now(timezone.utc)
    return due_datetime > now_utc


def compute_due_status(task: Task) -> Dict[str, bool]:
    """
    Compute due date status flags for a task.

    - is_overdue: due_datetime is past and task is pending
    - is_due_today: due_datetime falls on the same UTC day as now
    - is_due_soon: due_datetime is within 48 hours from now (future)

    Args:
        task: The task instance to compute status for.

    Returns:
        Dict[str, bool]: Dictionary with status flags.
    """
    now_utc = datetime.now(timezone.utc)
    due = task.due_datetime

    if due is None:
        return {
            "is_overdue": False,
            "is_due_today": False,
            "is_due_soon": False
        }

    # Assume due_datetime is timezone-aware (UTC); compare directly
    is_overdue = due < now_utc and task.status == TaskStatus.PENDING

    # Same day: normalize to date
    due_date = due.replace(hour=0, minute=0, second=0, microsecond=0)
    now_date = now_utc.replace(hour=0, minute=0, second=0, microsecond=0)
    is_due_today = due_date == now_date

    is_due_soon = now_utc <= due <= (now_utc + timedelta(hours=48))

    return {
        "is_overdue": is_overdue,
        "is_due_today": is_due_today,
        "is_due_soon": is_due_soon
    }


def validate_recurrence(task_data: dict) -> bool:
    """
    Basic validation for task recurrence data.

    Ensures:
    - If recurrence_rule is set, due_datetime must be provided
    - recurrence_rule is a valid RecurrenceRule value
    - Basic check for no invalid cycles (valid enum covers this)

    Args:
        task_data: Dictionary containing task data with 'recurrence_rule' and 'due_datetime' keys.

    Returns:
        bool: True if recurrence data is valid, False otherwise.
    """
    recurrence_rule = task_data.get('recurrence_rule')
    due_datetime = task_data.get('due_datetime')

    if recurrence_rule:
        if not due_datetime:
            return False
        valid_rules = {rule.value for rule in RecurrenceRule}
        if recurrence_rule not in valid_rules:
            return False
    return True


# Note: All methods in this service implement or will implement user isolation
# by filtering database queries on the authenticated user_id where applicable.
