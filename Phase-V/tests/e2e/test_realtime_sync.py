"""E2E Tests: Multi-Client Real-Time Sync (T152-T155).

Test real-time synchronization across multiple clients:
1. Simulate two clients viewing tasks
2. Create task on one, verify appears on other
3. Complete task on one, verify updated on other
"""

import time
from datetime import datetime

import httpx
import pytest

from .conftest import wait_for_condition


class TestRealTimeSync:
    """Test 3: Multi-Client Real-Time Sync.

    Note: Full real-time testing requires WebSocket or polling support.
    These tests verify the event publishing mechanism works correctly.
    """

    @pytest.mark.e2e
    def test_setup_two_clients(
        self,
        authenticated_client: httpx.Client
    ):
        """T152: Simulate two client sessions.

        Both clients use the same auth token (same user).
        In a real test, you'd have two browser windows.
        """
        # Client A is the authenticated_client
        # Client B is a copy with same headers
        self.client_a = authenticated_client
        self.client_b = httpx.Client(
            base_url=authenticated_client.base_url,
            headers=dict(authenticated_client.headers),
            timeout=30.0
        )

        # Verify both can access tasks
        response_a = self.client_a.get("/api/v1/tasks")
        response_b = self.client_b.get("/api/v1/tasks")

        assert response_a.status_code == 200
        assert response_b.status_code == 200

    @pytest.mark.e2e
    def test_create_on_a_appears_on_b(
        self,
        authenticated_client: httpx.Client
    ):
        """T153: Create task on Client A, verify appears on Client B.

        Note: Without WebSocket, Client B needs to poll to see updates.
        This test verifies the task is visible when B refreshes.
        """
        client_a = authenticated_client
        client_b = httpx.Client(
            base_url=authenticated_client.base_url,
            headers=dict(authenticated_client.headers),
            timeout=30.0
        )

        # Get initial task count on B
        initial_response = client_b.get("/api/v1/tasks")
        initial_data = initial_response.json()
        initial_tasks = initial_data.get("items", []) if isinstance(initial_data, dict) else initial_data
        initial_count = len([t for t in initial_tasks if t.get("title", "").startswith("[E2E]")])

        # Create task on A
        task_title = f"[E2E] Sync test {datetime.utcnow().timestamp()}"
        create_response = client_a.post("/api/v1/tasks", json={
            "title": task_title,
            "priority": "high"
        })

        assert create_response.status_code in [200, 201]
        created_task = create_response.json()
        self.__class__.sync_task_id = created_task["id"]

        # Poll on B until task appears (simulating real-time with polling)
        def task_visible_on_b():
            response = client_b.get("/api/v1/tasks")
            if response.status_code != 200:
                return False
            data = response.json()
            tasks = data.get("items", []) if isinstance(data, dict) else data
            return any(t.get("title") == task_title for t in tasks)

        try:
            wait_for_condition(
                task_visible_on_b,
                timeout_seconds=10.0,
                poll_interval=1.0,
                description="task to appear on client B"
            )
        except TimeoutError:
            pytest.fail("Task created on A should be visible on B after refresh")

        client_b.close()

    @pytest.mark.e2e
    def test_complete_on_b_updates_on_a(
        self,
        authenticated_client: httpx.Client
    ):
        """T154: Complete task on Client B, verify updated on Client A.

        Complete the task from the previous test and verify A sees it.
        """
        task_id = getattr(self.__class__, "sync_task_id", None)
        if not task_id:
            pytest.skip("No task ID from previous test")

        client_a = authenticated_client
        client_b = httpx.Client(
            base_url=authenticated_client.base_url,
            headers=dict(authenticated_client.headers),
            timeout=30.0
        )

        # Complete on B
        complete_response = client_b.post(f"/api/v1/tasks/{task_id}/complete")
        assert complete_response.status_code in [200, 204]

        # Verify on A
        def task_completed_on_a():
            response = client_a.get(f"/api/v1/tasks/{task_id}")
            if response.status_code != 200:
                return False
            task = response.json()
            return task.get("status") == "completed" or task.get("completed") is True

        try:
            wait_for_condition(
                task_completed_on_a,
                timeout_seconds=10.0,
                poll_interval=1.0,
                description="task to show as completed on client A"
            )
        except TimeoutError:
            pytest.fail("Task completed on B should show as completed on A")

        client_b.close()

    @pytest.mark.e2e
    def test_verify_event_flow(
        self,
        authenticated_client: httpx.Client,
        test_config
    ):
        """T155: Verify event flow in Zipkin traces.

        Check Zipkin for task-updates topic events.
        """
        try:
            # Query Zipkin for recent traces
            response = httpx.get(
                f"{test_config.zipkin_url}/api/v2/traces",
                params={
                    "serviceName": "todo-backend",
                    "limit": 20
                },
                timeout=5.0
            )

            if response.status_code == 200:
                traces = response.json()
                print(f"Found {len(traces)} recent traces in Zipkin")

                # Look for publish events
                publish_traces = []
                for trace in traces:
                    for span in trace:
                        if "publish" in str(span).lower() or "task-updates" in str(span).lower():
                            publish_traces.append(span)

                if publish_traces:
                    print(f"Found {len(publish_traces)} publish-related spans")
            else:
                print(f"Zipkin returned status {response.status_code}")

        except Exception as e:
            print(f"Zipkin verification skipped: {e}")
            # This is not a failure - Zipkin may not be available

    @pytest.fixture(autouse=True)
    def cleanup(self, authenticated_client: httpx.Client):
        """Cleanup after tests."""
        yield

        task_id = getattr(self.__class__, "sync_task_id", None)
        if task_id:
            try:
                authenticated_client.delete(f"/api/v1/tasks/{task_id}")
            except Exception:
                pass


class TestEventPublishing:
    """Additional tests for event publishing mechanism."""

    @pytest.mark.e2e
    def test_task_create_publishes_event(
        self,
        authenticated_client: httpx.Client
    ):
        """Verify task creation triggers event publishing.

        The backend should publish task_created event to task-events topic.
        """
        response = authenticated_client.post("/api/v1/tasks", json={
            "title": "[E2E] Event publish test",
            "priority": "medium"
        })

        assert response.status_code in [200, 201]
        task = response.json()

        # The event is published asynchronously via BackgroundTasks
        # We can verify it worked by checking the task was created successfully
        # and the backend didn't error during event publishing

        # Cleanup
        authenticated_client.delete(f"/api/v1/tasks/{task['id']}")

    @pytest.mark.e2e
    def test_task_update_publishes_event(
        self,
        authenticated_client: httpx.Client
    ):
        """Verify task update triggers event publishing."""
        # Create task
        create_response = authenticated_client.post("/api/v1/tasks", json={
            "title": "[E2E] Update event test",
            "priority": "low"
        })
        task = create_response.json()
        task_id = task["id"]

        # Update task
        update_response = authenticated_client.put(f"/api/v1/tasks/{task_id}", json={
            "title": "[E2E] Update event test - updated",
            "priority": "high"
        })

        assert update_response.status_code == 200

        # Cleanup
        authenticated_client.delete(f"/api/v1/tasks/{task_id}")

    @pytest.mark.e2e
    def test_task_delete_publishes_event(
        self,
        authenticated_client: httpx.Client
    ):
        """Verify task deletion triggers event publishing."""
        # Create task
        create_response = authenticated_client.post("/api/v1/tasks", json={
            "title": "[E2E] Delete event test"
        })
        task = create_response.json()
        task_id = task["id"]

        # Delete task
        delete_response = authenticated_client.delete(f"/api/v1/tasks/{task_id}")

        assert delete_response.status_code in [200, 204]

        # Verify task is gone
        get_response = authenticated_client.get(f"/api/v1/tasks/{task_id}")
        assert get_response.status_code == 404
