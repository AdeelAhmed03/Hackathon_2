# Quickstart: Organization Features

## Local Development Setup

### 1. Database Migrations
Run the backend migration script to apply the new schema (Tasks/Tags relationships).
```bash
docker-compose exec backend python -m src.scripts.migrate
```

### 2. Environment Variables
Ensure the following are set (defaults should work for local dev):
- `DATABASE_URL`: Connection string to Neon/Postgres.
- `JWT_SECRET`: Shared secret for authentication.

## Feature Testing Steps

### Backend
1.  **Add a Task with Priority/Tags**:
    `POST /api/tasks` with body `{"title": "Test", "priority": "high", "due_date": "2026-02-01", "tags": ["work"]}`.
2.  **Verify Search**:
    `GET /api/tasks?q=Test`.
3.  **Verify Multi-Tag**:
    `GET /api/tasks?tags=work&tags=urgent` (Should return only tasks with BOTH tags).

### Frontend
1.  Open the dashboard.
2.  Use the search input and observe real-time list updates.
3.  Check the sidebar filter groups and verify URL query params change accordingly.
