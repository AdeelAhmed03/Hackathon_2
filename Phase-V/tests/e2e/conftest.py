"""E2E Test Configuration and Fixtures.

Provides shared fixtures for end-to-end testing of the Phase V
event-driven architecture.
"""

import os
import time
from datetime import datetime, timedelta
from typing import Generator, Optional

import httpx
import pytest

# Test configuration - can be overridden via environment variables
BACKEND_URL = os.getenv("E2E_BACKEND_URL", "http://localhost:8000")
FRONTEND_URL = os.getenv("E2E_FRONTEND_URL", "http://localhost:3000")
ZIPKIN_URL = os.getenv("E2E_ZIPKIN_URL", "http://localhost:9411")

# Test user credentials (should be created before running E2E tests)
TEST_USER_EMAIL = os.getenv("E2E_TEST_USER_EMAIL", "e2e-test@example.com")
TEST_USER_PASSWORD = os.getenv("E2E_TEST_USER_PASSWORD", "e2e-test-password-123")


class TestConfig:
    """Test configuration singleton."""

    backend_url: str = BACKEND_URL
    frontend_url: str = FRONTEND_URL
    zipkin_url: str = ZIPKIN_URL
    test_user_email: str = TEST_USER_EMAIL
    test_user_password: str = TEST_USER_PASSWORD
    auth_token: Optional[str] = None
    user_id: Optional[str] = None


config = TestConfig()


@pytest.fixture(scope="session")
def test_config() -> TestConfig:
    """Provide test configuration."""
    return config


@pytest.fixture(scope="session")
def api_client() -> Generator[httpx.Client, None, None]:
    """Create an HTTP client for API calls."""
    with httpx.Client(
        base_url=config.backend_url,
        timeout=30.0
    ) as client:
        yield client


@pytest.fixture(scope="session")
def authenticated_client(api_client: httpx.Client) -> httpx.Client:
    """Get an authenticated HTTP client.

    Attempts to sign in with test credentials.
    If user doesn't exist, creates one first.
    """
    # Try to login
    login_response = api_client.post(
        "/api/v1/auth/login",
        json={
            "email": config.test_user_email,
            "password": config.test_user_password
        }
    )

    if login_response.status_code in [401, 404]:
        # User doesn't exist, create one
        register_response = api_client.post(
            "/api/v1/auth/register",
            json={
                "email": config.test_user_email,
                "password": config.test_user_password,
                "name": "E2E Test User"
            }
        )
        if register_response.status_code not in [200, 201]:
            pytest.fail(f"Failed to create test user: {register_response.text}")

        # Login again
        login_response = api_client.post(
            "/api/v1/auth/login",
            json={
                "email": config.test_user_email,
                "password": config.test_user_password
            }
        )

    if signin_response.status_code != 200:
        pytest.fail(f"Failed to authenticate: {signin_response.text}")

    auth_data = signin_response.json()
    config.auth_token = auth_data.get("token") or auth_data.get("access_token")
    config.user_id = auth_data.get("user", {}).get("id") or auth_data.get("user_id")

    # Update client headers
    api_client.headers["Authorization"] = f"Bearer {config.auth_token}"

    return api_client


@pytest.fixture
def clean_test_tasks(authenticated_client: httpx.Client) -> Generator[None, None, None]:
    """Clean up test tasks before and after tests."""
    # Get all tasks
    response = authenticated_client.get("/api/v1/tasks")
    if response.status_code == 200:
        data = response.json()
        tasks = data.get("items", []) if isinstance(data, dict) else data

        # Delete tasks created by E2E tests (by title prefix)
        for task in tasks:
            if task.get("title", "").startswith("[E2E]"):
                authenticated_client.delete(f"/api/v1/tasks/{task['id']}")

    yield

    # Cleanup after test
    response = authenticated_client.get("/api/v1/tasks")
    if response.status_code == 200:
        data = response.json()
        tasks = data.get("items", []) if isinstance(data, dict) else data

        for task in tasks:
            if task.get("title", "").startswith("[E2E]"):
                authenticated_client.delete(f"/api/v1/tasks/{task['id']}")


@pytest.fixture
def create_test_task(authenticated_client: httpx.Client):
    """Factory fixture to create test tasks."""
    created_task_ids = []

    def _create_task(
        title: str,
        priority: str = "medium",
        due_datetime: Optional[datetime] = None,
        remind_at: Optional[datetime] = None,
        recurrence_rule: Optional[str] = None,
        tag_ids: Optional[list[int]] = None,
        description: Optional[str] = None
    ) -> dict:
        payload = {
            "title": f"[E2E] {title}",
            "priority": priority,
            "description": description or f"E2E test task created at {datetime.utcnow().isoformat()}"
        }

        if due_datetime:
            payload["due_datetime"] = due_datetime.isoformat()
        if remind_at:
            payload["remind_at"] = remind_at.isoformat()
        if recurrence_rule:
            payload["recurrence_rule"] = recurrence_rule
        if tag_ids:
            payload["tag_ids"] = tag_ids

        response = authenticated_client.post("/api/v1/tasks", json=payload)

        if response.status_code not in [200, 201]:
            pytest.fail(f"Failed to create task: {response.text}")

        task = response.json()
        created_task_ids.append(task["id"])
        return task

    yield _create_task

    # Cleanup created tasks
    for task_id in created_task_ids:
        try:
            authenticated_client.delete(f"/api/v1/tasks/{task_id}")
        except Exception:
            pass


@pytest.fixture
def create_test_tag(authenticated_client: httpx.Client):
    """Factory fixture to create test tags."""
    created_tag_ids = []

    def _create_tag(name: str) -> dict:
        response = authenticated_client.post(
            "/api/v1/tags",
            json={"name": f"[E2E] {name}"}
        )

        if response.status_code not in [200, 201]:
            pytest.fail(f"Failed to create tag: {response.text}")

        tag = response.json()
        created_tag_ids.append(tag["id"])
        return tag

    yield _create_tag

    # Cleanup created tags
    for tag_id in created_tag_ids:
        try:
            authenticated_client.delete(f"/api/v1/tags/{tag_id}")
        except Exception:
            pass


def wait_for_condition(
    condition_fn,
    timeout_seconds: float = 30.0,
    poll_interval: float = 1.0,
    description: str = "condition"
) -> bool:
    """Wait for a condition to become true.

    Args:
        condition_fn: Callable that returns True when condition is met
        timeout_seconds: Maximum time to wait
        poll_interval: Time between polls
        description: Description for error messages

    Returns:
        True if condition was met, raises TimeoutError otherwise
    """
    start_time = time.time()

    while time.time() - start_time < timeout_seconds:
        if condition_fn():
            return True
        time.sleep(poll_interval)

    raise TimeoutError(f"Timeout waiting for {description} after {timeout_seconds}s")
