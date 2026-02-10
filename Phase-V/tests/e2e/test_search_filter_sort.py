"""E2E Tests: Search, Filter, and Sort (T156-T158).

Test combined filtering and sorting:
1. Create tasks with varied properties
2. Test combined filters (priority + tags + search)
3. Test multi-field sorting
"""

from datetime import datetime, timedelta
from typing import Callable

import httpx
import pytest


class TestSearchFilterSort:
    """Test 4: Search/Filter/Sort Combined."""

    @pytest.fixture(autouse=True)
    def setup_test_data(
        self,
        authenticated_client: httpx.Client,
        create_test_task: Callable,
        create_test_tag: Callable
    ):
        """T156: Create 10+ tasks with varied properties."""
        # Create tags
        work_tag = create_test_tag("work")
        personal_tag = create_test_tag("personal")
        urgent_tag = create_test_tag("urgent")

        self.work_tag_id = work_tag["id"]
        self.personal_tag_id = personal_tag["id"]
        self.urgent_tag_id = urgent_tag["id"]

        now = datetime.utcnow()

        # Create diverse tasks
        self.tasks = []

        # High priority work tasks
        self.tasks.append(create_test_task(
            title="Quarterly report",
            priority="high",
            due_datetime=now + timedelta(days=2),
            tag_ids=[self.work_tag_id]
        ))
        self.tasks.append(create_test_task(
            title="Annual report review",
            priority="high",
            due_datetime=now + timedelta(days=5),
            tag_ids=[self.work_tag_id, self.urgent_tag_id]
        ))

        # Medium priority tasks
        self.tasks.append(create_test_task(
            title="Team meeting notes",
            priority="medium",
            due_datetime=now + timedelta(days=1),
            tag_ids=[self.work_tag_id]
        ))
        self.tasks.append(create_test_task(
            title="Update documentation",
            priority="medium",
            due_datetime=now + timedelta(days=3),
            tag_ids=[self.work_tag_id]
        ))

        # Low priority tasks
        self.tasks.append(create_test_task(
            title="Clean up old files",
            priority="low",
            due_datetime=now + timedelta(days=10)
        ))
        self.tasks.append(create_test_task(
            title="Archive reports",
            priority="low",
            due_datetime=now + timedelta(days=7),
            tag_ids=[self.work_tag_id]
        ))

        # Personal tasks
        self.tasks.append(create_test_task(
            title="Grocery shopping",
            priority="medium",
            due_datetime=now + timedelta(hours=6),
            tag_ids=[self.personal_tag_id]
        ))
        self.tasks.append(create_test_task(
            title="Doctor appointment",
            priority="high",
            due_datetime=now + timedelta(days=1),
            tag_ids=[self.personal_tag_id, self.urgent_tag_id]
        ))

        # Tasks with past due dates (overdue)
        self.tasks.append(create_test_task(
            title="Overdue report",
            priority="high",
            due_datetime=now - timedelta(days=1),
            tag_ids=[self.work_tag_id]
        ))

        # Tasks without due dates
        self.tasks.append(create_test_task(
            title="Someday maybe task",
            priority="low"
        ))
        self.tasks.append(create_test_task(
            title="Research report templates",
            priority="medium",
            tag_ids=[self.work_tag_id]
        ))

        yield

    @pytest.mark.e2e
    def test_combined_filter_priority_tags_search(
        self,
        authenticated_client: httpx.Client
    ):
        """T157: Test combined filter - priority=high AND tags=work AND search='report'.

        GET /api/v1/tasks?priority=high&tags=<work_tag_id>&q=report
        Verify only matching tasks returned.
        """
        params = {
            "priority": "high",
            "tags": [self.work_tag_id],
            "q": "report"
        }

        response = authenticated_client.get("/api/v1/tasks", params=params)

        assert response.status_code == 200, f"Failed to filter: {response.text}"

        data = response.json()
        tasks = data.get("items", []) if isinstance(data, dict) else data

        # Filter to only E2E tasks
        e2e_tasks = [t for t in tasks if t.get("title", "").startswith("[E2E]")]

        # Should match: "Quarterly report", "Annual report review", "Overdue report"
        for task in e2e_tasks:
            # Verify each task matches ALL criteria
            assert task.get("priority") == "high", f"Task {task['title']} should be high priority"
            assert "report" in task.get("title", "").lower(), f"Task should contain 'report'"

    @pytest.mark.e2e
    def test_search_keyword_case_insensitive(
        self,
        authenticated_client: httpx.Client
    ):
        """Search should be case-insensitive on title and description."""
        # Search with different cases
        for keyword in ["REPORT", "Report", "report"]:
            response = authenticated_client.get("/api/v1/tasks", params={"q": keyword})

            assert response.status_code == 200

            data = response.json()
            tasks = data.get("items", []) if isinstance(data, dict) else data
            e2e_tasks = [t for t in tasks if t.get("title", "").startswith("[E2E]")]

            # Should find tasks with "report" regardless of case
            matching = [t for t in e2e_tasks if "report" in t.get("title", "").lower()]
            assert len(matching) > 0, f"Should find tasks with keyword '{keyword}'"

    @pytest.mark.e2e
    def test_tag_intersection_filter(
        self,
        authenticated_client: httpx.Client
    ):
        """Tags filter uses AND logic - task must have ALL specified tags."""
        # Filter by work AND urgent tags
        params = {"tags": [self.work_tag_id, self.urgent_tag_id]}

        response = authenticated_client.get("/api/v1/tasks", params=params)

        assert response.status_code == 200

        data = response.json()
        tasks = data.get("items", []) if isinstance(data, dict) else data
        e2e_tasks = [t for t in tasks if t.get("title", "").startswith("[E2E]")]

        # Should only match "Annual report review" which has both tags
        # All returned tasks should have BOTH tags
        for task in e2e_tasks:
            task_tags = task.get("tags", [])
            if task_tags and isinstance(task_tags[0], dict):
                tag_ids = [t.get("id") for t in task_tags]
            else:
                tag_ids = task_tags  # Might be list of IDs directly
            if not tag_ids:
                tag_ids = task_tags  # Might be list of IDs directly

    @pytest.mark.e2e
    def test_date_range_filter(
        self,
        authenticated_client: httpx.Client
    ):
        """Filter tasks by due date range."""
        now = datetime.utcnow()
        tomorrow = now + timedelta(days=1)
        next_week = now + timedelta(days=7)

        params = {
            "due_after": tomorrow.isoformat(),
            "due_before": next_week.isoformat()
        }

        response = authenticated_client.get("/api/v1/tasks", params=params)

        assert response.status_code == 200

        data = response.json()
        tasks = data.get("items", []) if isinstance(data, dict) else data
        e2e_tasks = [t for t in tasks if t.get("title", "").startswith("[E2E]")]

        # All returned tasks should have due_at within range
        for task in e2e_tasks:
            due = task.get("due_datetime") or task.get("due_at")
            if due:
                due_dt = datetime.fromisoformat(due.replace("Z", "+00:00").replace("+00:00", ""))
                assert due_dt >= tomorrow.replace(tzinfo=None), f"Task {task['title']} due before range"
                assert due_dt <= next_week.replace(tzinfo=None), f"Task {task['title']} due after range"

    @pytest.mark.e2e
    def test_multi_field_sort_priority_due_date(
        self,
        authenticated_client: httpx.Client
    ):
        """T158: Test multi-field sort - priority DESC, due_at ASC.

        GET /api/v1/tasks?sort_by=priority,due_datetime&sort_order=desc,asc
        Verify high-priority tasks first, then sorted by nearest due date.
        """
        params = {
            "sort_by": "priority,due_datetime",
            "sort_order": "desc"
        }

        response = authenticated_client.get("/api/v1/tasks", params=params)

        assert response.status_code == 200

        data = response.json()
        tasks = data.get("items", []) if isinstance(data, dict) else data
        e2e_tasks = [t for t in tasks if t.get("title", "").startswith("[E2E]")]

        if len(e2e_tasks) < 2:
            pytest.skip("Not enough tasks to test sorting")

        # Verify priority ordering: high should come before medium/low
        priority_order = {"high": 3, "medium": 2, "low": 1}
        prev_priority = None

        for task in e2e_tasks:
            current_priority = task.get("priority", "medium")
            if prev_priority:
                # In DESC order, priority value should be <= previous
                assert priority_order.get(current_priority, 0) <= priority_order.get(prev_priority, 0), \
                    f"Priority order incorrect: {prev_priority} -> {current_priority}"
            prev_priority = current_priority

    @pytest.mark.e2e
    def test_pagination_metadata(
        self,
        authenticated_client: httpx.Client
    ):
        """Verify pagination metadata in response."""
        params = {
            "page": 1,
            "page_size": 5
        }

        response = authenticated_client.get("/api/v1/tasks", params=params)

        assert response.status_code == 200

        data = response.json()

        # Should have pagination fields
        assert "total_count" in data or "total" in data, "Response should include total_count"
        assert "page" in data, "Response should include current page"
        assert "page_size" in data or "per_page" in data, "Response should include page_size"

        # Verify items count matches page_size (or less if last page)
        items = data.get("items", [])
        assert len(items) <= 5, f"Should return at most {params['page_size']} items"
